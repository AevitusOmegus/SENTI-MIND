"""
Emotion Detection using HuggingFace Inference API.
Uses j-hartmann/emotion-english-distilroberta-base.
"""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

HF_EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"
HF_API_URL = f"https://router.huggingface.co/hf-inference/models/{HF_EMOTION_MODEL}"
HF_TIMEOUT = 15.0

_FALLBACK = ({"label": "neutral", "score": 1.0},)


async def detect_emotions(text: str) -> list[dict]:
    """
    Detect emotions using HuggingFace API.
    Returns list of emotion dicts with label and score (sorted by score desc).
    """
    if not isinstance(text, str) or not text.strip():
        return list(_FALLBACK)

    if not settings.HF_API_TOKEN:
        logger.warning("HF_API_TOKEN not set — returning fallback emotions.")
        return list(_FALLBACK)

    headers = {"Authorization": f"Bearer {settings.HF_API_TOKEN}"}

    try:
        async with httpx.AsyncClient(timeout=HF_TIMEOUT) as client:
            response = await client.post(HF_API_URL, headers=headers, json={"inputs": text})

        if response.status_code != 200:
            logger.warning("HF API returned %s: %s", response.status_code, response.text[:200])
            return list(_FALLBACK)

        results = response.json()

        if isinstance(results, list) and results:
            if isinstance(results[0], list):
                results = results[0]
            elif isinstance(results[0], dict) and "label" in results[0]:
                results = [{"label": r["label"], "score": r["score"]} for r in results]

        emotions = []
        for result in results:
            label = result.get("label", "").lower()
            score = result.get("score", 0.0)
            emotions.append({"label": label, "score": round(score, 4)})

        emotions.sort(key=lambda x: x["score"], reverse=True)
        return emotions

    except httpx.TimeoutException:
        logger.error("HF API timed out after %ss", HF_TIMEOUT)
        return list(_FALLBACK)
    except httpx.HTTPError as exc:
        logger.error("HF API HTTP error: %s", exc)
        return list(_FALLBACK)
    except Exception as exc:
        logger.exception("HF API unexpected error: %s", exc)
        return list(_FALLBACK)
