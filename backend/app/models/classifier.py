import logging
import os
from pathlib import Path

import joblib
import numpy as np

logger = logging.getLogger(__name__)

_data_dir = Path(__file__).parent.parent.parent / "data"
MODEL_PATH = Path(os.getenv("SENTIMIND_MODEL_PATH", _data_dir / "sentiment_model.joblib"))
VECTORIZER_PATH = Path(os.getenv("SENTIMIND_VECTORIZER_PATH", _data_dir / "vectorizer.joblib"))

_UNKNOWN_RESULT = {"category": "Unknown", "confidence": 0.0, "top_categories": []}


class ClassifierNotLoadedError(RuntimeError):
    pass


from typing import Any

class ClinicalClassifier:
    def __init__(self) -> None:
        self._model: Any = None
        self._vectorizer: Any = None

    def load(self) -> None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model artifact not found: {MODEL_PATH}")
        if not VECTORIZER_PATH.exists():
            raise FileNotFoundError(f"Vectorizer artifact not found: {VECTORIZER_PATH}")

        try:
            model = joblib.load(MODEL_PATH)
            vectorizer = joblib.load(VECTORIZER_PATH)
        except Exception as exc:
            raise RuntimeError(f"Failed to load classifier artifacts: {exc}") from exc

        if not hasattr(model, "decision_function") or not hasattr(model, "classes_"):
            raise RuntimeError(f"Unexpected model type: {type(model)}")
        if not hasattr(vectorizer, "transform"):
            raise RuntimeError(f"Unexpected vectorizer type: {type(vectorizer)}")

        self._model = model
        self._vectorizer = vectorizer
        logger.info("ClinicalClassifier loaded. Classes: %s", list(self._model.classes_))

    def unload(self) -> None:
        self._model = None
        self._vectorizer = None

    @property
    def is_loaded(self) -> bool:
        return self._model is not None and self._vectorizer is not None

    def predict(self, text: str) -> dict:
        if not self.is_loaded:
            raise ClassifierNotLoadedError("Call load() before predict().")

        if not isinstance(text, str) or not text.strip():
            return dict(_UNKNOWN_RESULT)

        vec = self._vectorizer.transform([text])
        scores = self._model.decision_function(vec)[0]
        probs = self._softmax(scores)
        best_idx = int(np.argmax(probs))

        top_categories = sorted(
            [
                {"category": str(cls), "confidence": round(float(p), 4)}  # type: ignore
                for cls, p in zip(self._model.classes_, probs)
            ],
            key=lambda x: x["confidence"],
            reverse=True,
        )

        return {
            "category": str(self._model.classes_[best_idx]),
            "confidence": round(float(probs[best_idx]), 4),  # type: ignore
            "top_categories": top_categories,
        }

    @staticmethod
    def _softmax(scores: np.ndarray) -> np.ndarray:
        exp_s = np.exp(scores - scores.max())
        return exp_s / exp_s.sum()


classifier = ClinicalClassifier()