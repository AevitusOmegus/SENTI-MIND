import logging

import httpx

from app.core.config import settings
from app.core.constants import HF_EMOTION_MODEL

logger = logging.getLogger(__name__)

HF_API_URL = f"https://router.huggingface.co/hf-inference/models/{HF_EMOTION_MODEL}"
HF_TIMEOUT = 15.0

_FALLBACK = [{"label": "neutral", "score": 1.0}]


async def detect_emotions(text: str) -> list[dict]:
    if not isinstance(text, str) or not text.strip():
        return _FALLBACK

    headers = {"Authorization": f"Bearer {settings.HF_API_TOKEN}"}

    try:
        async with httpx.AsyncClient(timeout=HF_TIMEOUT) as client:
            response = await client.post(HF_API_URL, headers=headers, json={"inputs": text})

        if response.status_code != 200:
            logger.warning("HF API returned %s: %s", response.status_code, response.text)
            return _FALLBACK

        results = response.json()
        if isinstance(results, list) and results and isinstance(results[0], list):
            results = results[0]

        return sorted(results, key=lambda x: x["score"], reverse=True)

    except httpx.TimeoutException:
        logger.error("HF API timed out after %ss", HF_TIMEOUT)
        return _FALLBACK
    except httpx.HTTPError as exc:
        logger.error("HF API HTTP error: %s", exc)
        return _FALLBACK
    except Exception as exc:
        logger.exception("HF API unexpected error: %s", exc)
        return _FALLBACK