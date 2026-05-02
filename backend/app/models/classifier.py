import logging
import os
from pathlib import Path

import joblib
import numpy as np

from app.core.preprocessing import preprocess

logger = logging.getLogger(__name__)

_data_dir = Path(__file__).parent.parent.parent / "data"
MODEL_PATH = Path(os.getenv("SENTIMIND_MODEL_PATH", _data_dir / "sentiment_model.joblib"))
VECTORIZER_PATH = Path(os.getenv("SENTIMIND_VECTORIZER_PATH", _data_dir / "vectorizer.joblib"))

_UNKNOWN_RESULT = {"category": "Unknown", "confidence": 0.0, "top_categories": [], "is_ambiguous": False, "alternative_category": None, "confidence_tier": "none"}

# Confidence thresholds
CONFIDENCE_THRESHOLD = 0.35        # Below this → "Uncertain"
AMBIGUITY_MARGIN = 0.10            # If top-2 within this margin → ambiguous
MIN_MEANINGFUL_WORDS = 3           # Fewer → "Insufficient"


class ClassifierNotLoadedError(RuntimeError):
    pass


class ClinicalClassifier:
    """
    Clinical classifier for mental health text classification (v3).
    Uses a calibrated LinearSVC model with TF-IDF features.

    Improvements over v2:
    - Shared preprocessor from app.core.preprocessing
    - Confidence thresholding (returns 'Uncertain' for low confidence)
    - Ambiguity detection (flags when top-2 predictions are close)
    - Minimum content filter (returns 'Insufficient' for very short text)
    """

    def __init__(self) -> None:
        self._model = None
        self._vectorizer = None
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
        logger.info("ClinicalClassifier v3 loaded. Classes: %s", list(self._classes))

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

        Returns dict with:
            category, confidence, top_categories,
            is_ambiguous, alternative_category, confidence_tier
        """
        if not self.is_loaded:
            raise ClassifierNotLoadedError("Call load() before predict().")

        if not isinstance(text, str) or not text.strip():
            return dict(_UNKNOWN_RESULT)

        # Preprocess using the shared pipeline (same as training)
        processed = preprocess(text)

        # Check minimum content after preprocessing
        words = [w for w in processed.split() if len(w) > 1 and not w.startswith(("NEG_", "INTENSE_", "DIM_", "PAST_", "CRISIS_"))]
        if len(words) < 1:
            return dict(_UNKNOWN_RESULT)

        if len(words) < MIN_MEANINGFUL_WORDS:
            return {
                "category": "Insufficient",
                "confidence": 0.0,
                "top_categories": [],
                "is_ambiguous": False,
                "alternative_category": None,
                "confidence_tier": "none",
            }

        vec = self._vectorizer.transform([processed])
        probs = self._model.predict_proba(vec)[0]

        sorted_indices = np.argsort(probs)[::-1]
        best_idx = sorted_indices[0]
        second_idx = sorted_indices[1]

        best_conf = float(probs[best_idx])
        second_conf = float(probs[second_idx])

        top_categories = sorted(
            [
                {"category": str(cls), "confidence": round(float(p), 4)}
                for cls, p in zip(self._classes, probs)
            ],
            key=lambda x: x["confidence"],
            reverse=True,
        )

        if best_conf >= 0.70:
            confidence_tier = "high"
        elif best_conf >= CONFIDENCE_THRESHOLD:
            confidence_tier = "medium"
        else:
            confidence_tier = "low"

        is_ambiguous = (best_conf - second_conf) < AMBIGUITY_MARGIN
        alternative_category = str(self._classes[second_idx]) if is_ambiguous else None

        return {
            "category": str(self._classes[best_idx]),
            "confidence": round(best_conf, 4),
            "top_categories": top_categories,
            "is_ambiguous": is_ambiguous,
            "alternative_category": alternative_category,
            "confidence_tier": confidence_tier,
        }


# Global classifier instance
classifier = ClinicalClassifier()
