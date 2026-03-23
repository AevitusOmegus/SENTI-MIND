import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from pathlib import Path
import sys

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "Combined Data.csv"
MODEL_PATH = DATA_DIR / "sentiment_model.joblib"
VECTORIZER_PATH = DATA_DIR / "vectorizer.joblib"

def train():
    print(f"Loading data from {CSV_PATH}...")
    if not CSV_PATH.exists():
        print(f"Error: CSV file not found at {CSV_PATH}")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)
    
    # Clean up column names (strip spaces if any)
    df.columns = [c.strip() for c in df.columns]
    
    # We expect 'statement' and 'status'
    if 'statement' not in df.columns or 'status' not in df.columns:
        print("Error: Required columns 'statement' and 'status' not found.")
        sys.exit(1)

    # Drop NaNs
    df = df.dropna(subset=['statement', 'status'])
    
    X = df['statement']
    y = df['status']

    print(f"Total samples: {len(X)}")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples...")

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english')),
        ('clf', LinearSVC(class_weight='balanced', max_iter=3000, random_state=42))
    ])

    parameters = {
        'tfidf__max_features': [5000, 10000],
        'tfidf__ngram_range': [(1, 2), (1, 3)],
        'clf__C': [0.5, 1.0, 2.0]
    }

    print("Running GridSearchCV with 3-fold CV...")
    grid_search = GridSearchCV(pipeline, parameters, cv=3, n_jobs=-1, scoring='f1_macro', verbose=1)
    grid_search.fit(X_train, y_train)

    print("Best parameters found:")
    print(grid_search.best_params_)

    # Evaluate
    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy: {acc:.4f}\n")
    print("Classification Report:\n", classification_report(y_test, y_pred, digits=4))

    best_vectorizer = best_model.named_steps['tfidf']
    best_clf = best_model.named_steps['clf']

    print(f"Saving fine-tuned model to {MODEL_PATH}...")
    joblib.dump(best_clf, MODEL_PATH)
    
    print(f"Saving vectorizer to {VECTORIZER_PATH}...")
    joblib.dump(best_vectorizer, VECTORIZER_PATH)
    
    print("Training complete! Fine-tuned model and vectorizer are ready.")

if __name__ == "__main__":
    train()
