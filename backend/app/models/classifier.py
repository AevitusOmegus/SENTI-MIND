import logging
import os
import re
from pathlib import Path

import joblib
import numpy as np

logger = logging.getLogger(__name__)

_data_dir = Path(__file__).parent.parent.parent / "data"
MODEL_PATH = Path(os.getenv("SENTIMIND_MODEL_PATH", _data_dir / "sentiment_model_v2.joblib"))
VECTORIZER_PATH = Path(os.getenv("SENTIMIND_VECTORIZER_PATH", _data_dir / "vectorizer_v2.joblib"))

_UNKNOWN_RESULT = {"category": "Unknown", "confidence": 0.0, "top_categories": []}


class ClassifierNotLoadedError(RuntimeError):
    pass


class ClinicalTextPreprocessor:
    """
    Advanced clinical text preprocessor with negation detection,
    crisis indicators, and mental health term markers.
    """

    def __init__(self):
        # Negation patterns
        self.negation_patterns = [
            r"\bnot\s+\w+",
            r"\bno\s+\w+",
            r"\bnever\s+\w+",
            r"\bdon'?t\s+\w+",
            r"\bdoesn'?t\s+\w+",
            r"\bdidn'?t\s+\w+",
            r"\bcan'?t\s+\w+",
            r"\bcannot\s+\w+",
            r"\bwon'?t\s+\w+",
            r"\bwouldn'?t\s+\w+",
            r"\bcouldn'?t\s+\w+",
            r"\bshouldn'?t\s+\w+",
            r"\bisn'?t\s+\w+",
            r"\baren'?t\s+\w+",
            r"\bwasn'?t\s+\w+",
            r"\bweren'?t\s+\w+",
            r"\bhaven'?t\s+\w+",
            r"\bhasn'?t\s+\w+",
            r"\bhadn'?t\s+\w+",
        ]

        # Crisis indicators — only genuinely high-severity phrases
        # Low-weight fuzzy terms ('depressed', 'anxious', 'stressed') removed
        # to prevent false-positive classification of everyday language.
        self.crisis_indicators = {
            'suicide': 1.0,
            'suicidal': 1.0,
            'kill myself': 1.0,
            'killing myself': 1.0,
            'end my life': 1.0,
            'ending my life': 1.0,
            'want to die': 1.0,
            'wanting to die': 1.0,
            'better off dead': 1.0,
            'not worth living': 1.0,
            'final exit': 1.0,
            'ending it': 1.0,
            'end it all': 1.0,
            'self-harm': 0.9,
            'self harm': 0.9,
            'cut myself': 0.9,
            'cutting myself': 0.9,
            'hurt myself': 0.9,
            'hurting myself': 0.9,
            'harm myself': 0.9,
            'no reason to live': 0.8,
            'can\'t go on': 0.7,
            'cannot go on': 0.7,
            'tired of living': 0.7,
        }

    def preprocess(self, text: str) -> str:
        """Apply comprehensive preprocessing."""
        if not isinstance(text, str):
            return ""

        # Lowercase and strip
        text = text.lower().strip()

        # Handle negations
        for pattern in self.negation_patterns:
            text = re.sub(
                pattern,
                lambda m: " NEG_" + m.group(0).replace(' ', '_').replace("'", '').replace('"', '') + " ",
                text
            )

        # Add crisis indicator markers (high-severity phrases only)
        for indicator, weight in self.crisis_indicators.items():
            if indicator in text:
                text += f" CRISIS_{indicator.replace(' ', '_')}_W{int(weight*10)} "

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text


class ClinicalClassifier:
    """
    Clinical classifier for mental health text classification.
    Uses a calibrated LinearSVC model with TF-IDF features.
    """

    def __init__(self) -> None:
        self._model = None
        self._vectorizer = None
        self._preprocessor = ClinicalTextPreprocessor()
        self._classes = None

    def load(self) -> None:
        """Load model and vectorizer from disk."""
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model artifact not found: {MODEL_PATH}")
        if not VECTORIZER_PATH.exists():
            raise FileNotFoundError(f"Vectorizer artifact not found: {VECTORIZER_PATH}")

        try:
            self._model = joblib.load(MODEL_PATH)
            self._vectorizer = joblib.load(VECTORIZER_PATH)
        except Exception as exc:
            raise RuntimeError(f"Failed to load classifier artifacts: {exc}") from exc

        if not hasattr(self._model, "predict_proba"):
            raise RuntimeError(f"Model must support predict_proba: {type(self._model)}")
        if not hasattr(self._vectorizer, "transform"):
            raise RuntimeError(f"Unexpected vectorizer type: {type(self._vectorizer)}")

        self._classes = self._model.classes_
        logger.info("ClinicalClassifier v2 loaded. Classes: %s", list(self._classes))

    def unload(self) -> None:
        """Unload model and free memory."""
        self._model = None
        self._vectorizer = None
        self._classes = None

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model is not None and self._vectorizer is not None

    def predict(self, text: str) -> dict:
        """
        Predict clinical category for text.

        Args:
            text: Input text to classify

        Returns:
            Dictionary with category, confidence, and top_categories
        """
        if not self.is_loaded:
            raise ClassifierNotLoadedError("Call load() before predict().")

        if not isinstance(text, str) or not text.strip():
            return dict(_UNKNOWN_RESULT)

        # Check for meaningful content
        cleaned = re.sub(r'[^\w\s]', '', text.lower())
        words = [w for w in cleaned.split() if len(w) > 1]
        if len(words) < 1:
            return dict(_UNKNOWN_RESULT)

        # Preprocess text
        processed = self._preprocessor.preprocess(text)

        # Transform and predict
        vec = self._vectorizer.transform([processed])
        probs = self._model.predict_proba(vec)[0]
        best_idx = int(np.argmax(probs))

        # Build top categories list
        top_categories = sorted(
            [
                {"category": str(cls), "confidence": round(float(p), 4)}
                for cls, p in zip(self._classes, probs)
            ],
            key=lambda x: x["confidence"],
            reverse=True,
        )

        return {
            "category": str(self._classes[best_idx]),
            "confidence": round(float(probs[best_idx]), 4),
            "top_categories": top_categories,
        }


# Global classifier instance
classifier = ClinicalClassifier()
