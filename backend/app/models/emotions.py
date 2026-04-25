"""
Emotion Detection using HuggingFace Inference API.
Uses j-hartmann/emotion-english-distilroberta-base (better accuracy than distilbert-base-uncased-emotion).
"""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Better emotion model: j-hartmann/emotion-english-distilroberta-base
# This model is specifically trained for emotion classification with 6 classes:
# anger, disgust, fear, joy, neutral, sadness, surprise
HF_EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"

HF_API_URL = f"https://router.huggingface.co/hf-inference/models/{HF_EMOTION_MODEL}"
HF_TIMEOUT = 15.0

_FALLBACK = [{"label": "neutral", "score": 1.0}]

# Model outputs 7 emotions: anger, disgust, fear, joy, neutral, sadness, surprise
# We keep all model outputs (no synthetic emotions)


async def detect_emotions(text: str) -> list[dict]:
    if not isinstance(text, str) or not text.strip():
        return _FALLBACK

    if not settings.HF_API_TOKEN:
        logger.warning("HF_API_TOKEN not set — returning fallback emotions.")
        return _FALLBACK

    # DistilRoBERTa has a 512-token limit; 1800 chars is a safe character proxy
    truncated = text[:1800]
    headers = {"Authorization": f"Bearer {settings.HF_API_TOKEN}"}

    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=HF_TIMEOUT) as client:
                response = await client.post(HF_API_URL, headers=headers, json={"inputs": truncated})

            if response.status_code == 429:
                logger.warning("HF API rate-limited (attempt %d)", attempt + 1)
                if attempt == 0:
                    import asyncio
                    await asyncio.sleep(2.0)
                    continue
                return _FALLBACK

            if response.status_code != 200:
                logger.warning("HF API returned %s: %s", response.status_code, response.text[:200])
                if attempt == 0:
                    continue
                return _FALLBACK

            results = response.json()
            if isinstance(results, list) and results:
                if isinstance(results[0], list):
                    results = results[0]
                elif isinstance(results[0], dict) and "label" in results[0]:
                    results = [{"label": r["label"], "score": r["score"]} for r in results]

            emotions = [
                {"label": r.get("label", "").lower(), "score": round(r.get("score", 0.0), 4)}
                for r in results
            ]
            emotions.sort(key=lambda x: x["score"], reverse=True)
            return emotions

        except httpx.TimeoutException:
            logger.error("HF API timed out (attempt %d)", attempt + 1)
        except httpx.HTTPError as exc:
            logger.error("HF API HTTP error: %s", exc)
        except Exception as exc:
            logger.exception("HF API unexpected error: %s", exc)
            return _FALLBACK

        if attempt == 0:
            import asyncio
            await asyncio.sleep(1.0)

    return _FALLBACK