#!/usr/bin/env python3
"""
SENTI-MIND Model Training Script v3
- GridSearchCV for optimal C and ngram_range
- CalibratedClassifierCV for probability estimates
- Stratified 5-fold cross-validation
- Saves best model as sentiment_model_v2.joblib (live model path)
"""

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

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "Combined Data.csv"

# These are the LIVE model paths the app uses — overwrite them directly.
MODEL_PATH = DATA_DIR / "sentiment_model_v2.joblib"
VECTORIZER_PATH = DATA_DIR / "vectorizer_v2.joblib"
METADATA_PATH = DATA_DIR / "model_metadata.json"


# ---------------------------------------------------------------------------
# Preprocessor (mirrors classifier.py — must stay in sync)
# ---------------------------------------------------------------------------

import re

NEGATION_PATTERNS = [
    r"\bnot\s+\w+", r"\bno\s+\w+", r"\bnever\s+\w+",
    r"\bdon'?t\s+\w+", r"\bdoesn'?t\s+\w+", r"\bdidn'?t\s+\w+",
    r"\bcan'?t\s+\w+", r"\bcannot\s+\w+", r"\bwon'?t\s+\w+",
    r"\bwouldn'?t\s+\w+", r"\bcouldn'?t\s+\w+", r"\bshouldn'?t\s+\w+",
    r"\bisn'?t\s+\w+", r"\baren'?t\s+\w+", r"\bwasn'?t\s+\w+",
    r"\bweren'?t\s+\w+", r"\bhaven'?t\s+\w+", r"\bhasn'?t\s+\w+",
    r"\bhadn'?t\s+\w+",
]

CRISIS_INDICATORS = {
    "suicide": 1.0, "suicidal": 1.0, "kill myself": 1.0,
    "killing myself": 1.0, "end my life": 1.0, "ending my life": 1.0,
    "want to die": 1.0, "wanting to die": 1.0, "better off dead": 1.0,
    "not worth living": 1.0, "final exit": 1.0, "ending it": 1.0,
    "end it all": 1.0, "self-harm": 0.9, "self harm": 0.9,
    "cut myself": 0.9, "cutting myself": 0.9, "hurt myself": 0.9,
    "hurting myself": 0.9, "harm myself": 0.9,
    "no reason to live": 0.8, "can't go on": 0.7,
    "cannot go on": 0.7, "tired of living": 0.7,
}


def preprocess(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    for pattern in NEGATION_PATTERNS:
        text = re.sub(
            pattern,
            lambda m: " NEG_" + m.group(0).replace(" ", "_").replace("'", "") + " ",
            text,
        )
    for indicator, weight in CRISIS_INDICATORS.items():
        if indicator in text:
            text += f" CRISIS_{indicator.replace(' ', '_')}_W{int(weight * 10)} "
    text = re.sub(r"\s+", " ", text).strip()
    return text


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

def build_base_pipeline(C: float = 1.0, ngram_range: tuple = (1, 3)) -> Pipeline:
    base_clf = LinearSVC(
        class_weight="balanced",
        max_iter=5000,
        random_state=42,
        dual="auto",
        C=C,
    )
    calibrated = CalibratedClassifierCV(base_clf, method="sigmoid", cv=3)
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            stop_words="english",
            lowercase=True,
            strip_accents="unicode",
            max_features=20000,
            ngram_range=ngram_range,
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
        )),
        ("clf", calibrated),
    ])
    return pipeline


def grid_search(X_train, y_train) -> dict:
    """Find the best C and ngram_range via cross-validated grid search."""
    logger.info("Running GridSearchCV...")

    param_grid = {
        "tfidf__ngram_range": [(1, 2), (1, 3)],
        "tfidf__max_features": [15000, 20000],
        "tfidf__min_df": [1, 2],
        "clf__estimator__C": [0.5, 1.0, 2.0, 5.0],
    }

    # Build a pipeline with a plain LinearSVC (not calibrated) for grid search
    # — calibration wraps after we find the best params.
    base = Pipeline([
        ("tfidf", TfidfVectorizer(
            stop_words="english",
            lowercase=True,
            strip_accents="unicode",
            sublinear_tf=True,
            max_df=0.95,
        )),
        ("clf", CalibratedClassifierCV(
            LinearSVC(class_weight="balanced", max_iter=5000, random_state=42, dual="auto"),
            method="sigmoid", cv=3,
        )),
    ])

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    gs = GridSearchCV(base, param_grid, cv=cv, scoring="f1_macro", n_jobs=-1, verbose=1)
    gs.fit(X_train, y_train)

    logger.info("Best params: %s", gs.best_params_)
    logger.info("Best CV F1-macro: %.4f", gs.best_score_)

    return gs.best_params_, gs.best_score_


def train():
    logger.info("=" * 70)
    logger.info("SENTI-MIND Model Training v3")
    logger.info("=" * 70)

    df = load_data(CSV_PATH)

    logger.info("Preprocessing text...")
    df["processed"] = df["statement"].apply(preprocess)

    X = df["processed"]
    y = df["status"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    logger.info("Train: %d | Test: %d", len(X_train), len(X_test))

    # --- Grid search on training set ---
    best_params, best_cv_score = grid_search(X_train, y_train)

    # --- Retrain final model on full training set with best params ---
    logger.info("Retraining final model with best params on full train set...")
    final_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            stop_words="english",
            lowercase=True,
            strip_accents="unicode",
            sublinear_tf=True,
            min_df=best_params.get("tfidf__min_df", 1),
            max_df=0.95,
            ngram_range=best_params["tfidf__ngram_range"],
            max_features=best_params["tfidf__max_features"],
        )),
        ("clf", CalibratedClassifierCV(
            LinearSVC(
                class_weight="balanced",
                max_iter=5000,
                random_state=42,
                dual="auto",
                C=best_params["clf__estimator__C"],
            ),
            method="sigmoid",
            cv=3,
        )),
    ])
    final_pipeline.fit(X_train, y_train)

    # --- Evaluate on held-out test set ---
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

    # --- Final cross-val on whole dataset ---
    logger.info("Running final 5-fold CV on full dataset...")
    cv_scores = cross_val_score(
        final_pipeline, X, y,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        scoring="f1_macro",
    )
    logger.info("CV F1-Macro: %.4f (+/- %.4f)", cv_scores.mean(), cv_scores.std() * 2)

    # --- Adversarial spot-check ---
    logger.info("=" * 70)
    logger.info("ADVERSARIAL SPOT-CHECK")
    logger.info("=" * 70)
    spot_cases = [
        ("I had a great day today",                             "Normal"),
        ("My mood was good yesterday",                          "Normal"),
        ("My friend's stress about exams is contagious",        "Normal"),
        ("I'm not suicidal just really stressed",               "Stress"),
        ("I feel empty and hopeless every single day",          "Depression"),
        ("I want to end my life",                               "Suicidal"),
        ("My moods swing from elated to crushing depression",   "Bipolar"),
        ("I spent thousands impulsively during a manic phase",  "Bipolar"),
        ("My heart races before every meeting",                 "Anxiety"),
        ("Work deadlines are overwhelming me completely",       "Stress"),
        ("I feel disconnected and don't know who I am",         "Personality disorder"),
        ("I push everyone away before they can leave me",       "Personality disorder"),
    ]
    ok = 0
    for text, expected in spot_cases:
        processed = preprocess(text)
        vec = final_pipeline.named_steps["tfidf"].transform([processed])
        probs = final_pipeline.named_steps["clf"].predict_proba(vec)[0]
        classes = final_pipeline.classes_
        pred = classes[int(np.argmax(probs))]
        conf = float(probs.max())
        status = "OK  " if pred == expected else "FAIL"
        if pred == expected:
            ok += 1
        logger.info("[%s] %-48s -> %-25s %.1f%%  (expected: %s)", status, f'"{text}"', pred, conf * 100, expected)

    logger.info("Spot-check: %d/%d correct", ok, len(spot_cases))

    # --- Save artifacts ---
    logger.info("=" * 70)
    logger.info("SAVING MODEL ARTIFACTS")
    logger.info("=" * 70)

    vectorizer = final_pipeline.named_steps["tfidf"]
    clf = final_pipeline.named_steps["clf"]

    joblib.dump(vectorizer, VECTORIZER_PATH)
    logger.info("Saved vectorizer → %s", VECTORIZER_PATH)

    joblib.dump(clf, MODEL_PATH)
    logger.info("Saved classifier → %s", MODEL_PATH)

    metadata = {
        "trained_at": datetime.now().isoformat(),
        "model_version": "v3",
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
        "has_calibration": True,
        "preprocessing": "negation_handling + crisis_markers (no crude keyword→class markers)",
    }

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Saved metadata → %s", METADATA_PATH)

    logger.info("=" * 70)
    logger.info("TRAINING COMPLETE — model ready at %s", MODEL_PATH)
    logger.info("=" * 70)


if __name__ == "__main__":
    train()
