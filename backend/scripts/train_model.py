#!/usr/bin/env python3


import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

# Add project root to path so we can import from app.core
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.preprocessing import preprocess  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = PROJECT_ROOT / "data"
CSV_PATH = DATA_DIR / "Combined Data.csv"

# model artifact paths
MODEL_PATH = DATA_DIR / "sentiment_model.joblib"
VECTORIZER_PATH = DATA_DIR / "vectorizer.joblib"
METADATA_PATH = DATA_DIR / "model_metadata.json"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data(csv_path: Path):
    logger.info("Loading data from %s", csv_path)
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(subset=["statement", "status"])
    df["statement"] = df["statement"].astype(str).str.strip()
    df = df[df["statement"].str.len() > 0]

    logger.info("Loaded %d samples", len(df))
    dist = df["status"].value_counts()
    for cls, cnt in dist.items():
        logger.info("  %-25s %d (%.1f%%)", cls, cnt, cnt / len(df) * 100)
    return df


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def grid_search(X_train, y_train) -> tuple[dict, float]:
    """Find best hyperparameters via cross-validated grid search."""
    logger.info("Running GridSearchCV...")

    param_grid = {
        "tfidf__ngram_range": [(1, 2), (1, 3)],
        "tfidf__max_features": [15000, 20000, 30000],
        "clf__estimator__C": [0.1, 0.5, 1.0, 2.0, 5.0],
    }

    base = Pipeline([
        ("tfidf", TfidfVectorizer(
            stop_words="english",
            lowercase=True,
            strip_accents="unicode",
            sublinear_tf=True,
            min_df=2,
            max_df=0.95,
        )),
        ("clf", CalibratedClassifierCV(
            LinearSVC(class_weight="balanced", max_iter=10000, random_state=42, dual="auto"),
            method="sigmoid", cv=3,
        )),
    ])

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    gs = GridSearchCV(base, param_grid, cv=cv, scoring="f1_macro", n_jobs=-1, verbose=1)
    gs.fit(X_train, y_train)

    logger.info("Best params: %s", gs.best_params_)
    logger.info("Best CV F1-macro: %.4f", gs.best_score_)
    return gs.best_params_, gs.best_score_


def run_adversarial_check(pipeline, classes) -> tuple[int, int]:
    """Run 50+ adversarial edge cases and report pass rate."""
    logger.info("=" * 70)
    logger.info("ADVERSARIAL SPOT-CHECK")
    logger.info("=" * 70)

    spot_cases = [
        # Normal — clear
        ("I had a great day today", "Normal"),
        ("My mood was good yesterday", "Normal"),
        ("I enjoyed dinner with friends tonight", "Normal"),
        ("Life is going well and I feel content", "Normal"),
        ("I got a promotion and I'm really happy", "Normal"),
        # Normal — hard negatives (clinical words, non-clinical context)
        ("My friend's stress about exams is contagious", "Normal"),
        ("We discussed depression in psychology class", "Normal"),
        ("I used to be anxious about flying but got over it", "Normal"),
        ("My panic attacks stopped since starting medication", "Normal"),
        ("I was in a dark place last year but I've recovered", "Normal"),
        ("I talked about suicidal thoughts I had years ago with my therapist", "Normal"),
        ("My colleague mentioned her bipolar diagnosis openly", "Normal"),
        ("I'm no longer depressed thanks to good support", "Normal"),
        ("I felt hopeless about the job search but got an offer today", "Normal"),
        ("I used to struggle with self-worth but therapy helped a lot", "Normal"),
        # Stress — including negation patterns
        ("I'm not suicidal just really stressed", "Stress"),
        ("Work deadlines are overwhelming me completely", "Stress"),
        ("I can't keep up with all my responsibilities", "Stress"),
        ("I'm burnt out but I can't afford to slow down", "Stress"),
        ("I don't want to die I just need a break from work", "Stress"),
        ("The pressure at work is making me physically ill", "Stress"),
        # Depression — clear
        ("I feel empty and hopeless every single day", "Depression"),
        ("Nothing brings me joy anymore everything is grey", "Depression"),
        ("I can't get out of bed and I don't see the point", "Depression"),
        ("I feel numb and disconnected from everything", "Depression"),
        ("I've lost interest in all my hobbies", "Depression"),
        ("I feel like a burden to everyone around me", "Depression"),
        # Suicidal — clear
        ("I want to end my life", "Suicidal"),
        ("I've been thinking about killing myself", "Suicidal"),
        ("I have a plan to end it all tonight", "Suicidal"),
        ("I don't want to be alive anymore", "Suicidal"),
        ("I've been self-harming to cope with the pain", "Suicidal"),
        ("Nobody would miss me if I was gone", "Suicidal"),
        # Anxiety — clear
        ("My heart races before every meeting", "Anxiety"),
        ("I can't stop worrying about things that haven't happened", "Anxiety"),
        ("I had a panic attack in the grocery store", "Anxiety"),
        ("I avoid crowded places because they make me panic", "Anxiety"),
        ("I feel a constant sense of dread that won't go away", "Anxiety"),
        ("I check the door lock five times before leaving", "Anxiety"),
        # Bipolar — clear
        ("My moods swing from elated to crushing depression", "Bipolar"),
        ("I spent thousands impulsively during a manic phase", "Bipolar"),
        ("I cycle between feeling invincible and completely worthless", "Bipolar"),
        ("I barely slept for three days and felt amazing until I crashed", "Bipolar"),
        ("I feel like two different people depending on my phase", "Bipolar"),
        ("I go from extreme highs to devastating lows", "Bipolar"),
        # Personality disorder — clear
        ("I feel disconnected and don't know who I am", "Personality disorder"),
        ("I push everyone away before they can leave me", "Personality disorder"),
        ("My sense of self changes depending on who I'm with", "Personality disorder"),
        ("I idealize people then devalue them when they disappoint me", "Personality disorder"),
        ("I feel chronically empty even when things are fine", "Personality disorder"),
        ("I have an intense fear of abandonment that destroys relationships", "Personality disorder"),
    ]

    ok = 0
    for text, expected in spot_cases:
        processed = preprocess(text)
        pred = pipeline.predict([processed])[0]
        probs = pipeline.predict_proba([processed])[0]
        conf = float(probs.max())
        status = "OK  " if pred == expected else "FAIL"
        if pred == expected:
            ok += 1
        logger.info(
            "[%s] %-55s -> %-25s %.1f%%  (expected: %s)",
            status, f'"{text[:50]}"', pred, conf * 100, expected,
        )

    logger.info("Spot-check: %d/%d correct (%.0f%%)", ok, len(spot_cases), ok / len(spot_cases) * 100)
    return ok, len(spot_cases)


def train():
    logger.info("=" * 70)
    logger.info("SENTI-MIND Model Training v4")
    logger.info("=" * 70)

    df = load_data(CSV_PATH)

    logger.info("Preprocessing text with shared preprocessor...")
    df["processed"] = df["statement"].apply(preprocess)

    X = df["processed"]
    y = df["status"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    logger.info("Train: %d | Test: %d", len(X_train), len(X_test))

    # --- Grid search ---
    best_params, best_cv_score = grid_search(X_train, y_train)

    # --- Retrain final model with best params ---
    logger.info("Retraining final model with best params...")
    final_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            stop_words="english",
            lowercase=True,
            strip_accents="unicode",
            sublinear_tf=True,
            min_df=2,
            max_df=0.95,
            ngram_range=best_params["tfidf__ngram_range"],
            max_features=best_params["tfidf__max_features"],
        )),
        ("clf", CalibratedClassifierCV(
            LinearSVC(
                class_weight="balanced",
                max_iter=10000,
                random_state=42,
                dual="auto",
                C=best_params["clf__estimator__C"],
            ),
            method="sigmoid",
            cv=3,
        )),
    ])
    final_pipeline.fit(X_train, y_train)

    # --- Evaluate on test set ---
    y_pred = final_pipeline.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")
    weighted_f1 = f1_score(y_test, y_pred, average="weighted")
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_pred, average=None, labels=final_pipeline.classes_
    )

    logger.info("=" * 70)
    logger.info("TEST SET RESULTS")
    logger.info("=" * 70)
    logger.info("Accuracy:    %.4f", acc)
    logger.info("Macro F1:    %.4f", macro_f1)
    logger.info("Weighted F1: %.4f", weighted_f1)
    logger.info("\nPer-class breakdown:")
    for i, cls in enumerate(final_pipeline.classes_):
        logger.info(
            "  %-25s P=%.3f  R=%.3f  F1=%.3f  N=%d",
            cls, precision[i], recall[i], f1[i], int(support[i]),
        )
    logger.info("\n%s", classification_report(y_test, y_pred, digits=4))

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred, labels=final_pipeline.classes_)
    logger.info("Confusion Matrix:")
    logger.info("Classes: %s", list(final_pipeline.classes_))
    for i, row in enumerate(cm):
        logger.info("  %-25s %s", final_pipeline.classes_[i], row)

    # --- 10-fold CV on whole dataset ---
    logger.info("Running 10-fold CV on full dataset...")
    cv_scores = cross_val_score(
        final_pipeline, X, y,
        cv=StratifiedKFold(n_splits=10, shuffle=True, random_state=42),
        scoring="f1_macro",
    )
    logger.info("CV F1-Macro: %.4f (+/- %.4f)", cv_scores.mean(), cv_scores.std() * 2)

    # --- Adversarial spot-check ---
    spot_ok, spot_total = run_adversarial_check(final_pipeline, final_pipeline.classes_)

    # --- Save artifacts ---
    logger.info("=" * 70)
    logger.info("SAVING MODEL ARTIFACTS (v4)")
    logger.info("=" * 70)

    vectorizer = final_pipeline.named_steps["tfidf"]
    clf = final_pipeline.named_steps["clf"]

    joblib.dump(vectorizer, VECTORIZER_PATH)
    logger.info("Saved vectorizer -> %s", VECTORIZER_PATH)

    joblib.dump(clf, MODEL_PATH)
    logger.info("Saved classifier -> %s", MODEL_PATH)

    metadata = {
        "trained_at": datetime.now().isoformat(),
        "model_version": "v4",
        "samples_train": int(len(X_train)),
        "samples_test": int(len(X_test)),
        "classes": final_pipeline.classes_.tolist(),
        "best_params": {
            "C": best_params["clf__estimator__C"],
            "ngram_range": list(best_params["tfidf__ngram_range"]),
            "max_features": best_params["tfidf__max_features"],
        },
        "accuracy": float(acc),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "cv_f1_macro_mean": float(cv_scores.mean()),
        "cv_f1_macro_std": float(cv_scores.std()),
        "grid_search_best_cv_f1": float(best_cv_score),
        "per_class_metrics": {
            cls: {
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1": float(f1[i]),
                "support": int(support[i]),
            }
            for i, cls in enumerate(final_pipeline.classes_)
        },
        "adversarial_spot_check": f"{spot_ok}/{spot_total}",
        "has_calibration": True,
        "preprocessing": "shared app.core.preprocessing v3 (contractions + negation_scope + intensity + temporal + crisis)",
    }

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Saved metadata -> %s", METADATA_PATH)

    logger.info("=" * 70)
    logger.info("TRAINING COMPLETE — model ready at %s", MODEL_PATH)
    logger.info("=" * 70)


if __name__ == "__main__":
    train()
