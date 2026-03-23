import asyncio
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "xiaomi/mimo-v2-omni"
OPENROUTER_TIMEOUT = 30.0


def _build_prompt(text: str, emotions: list, clinical: dict, risk: dict) -> str:
    top_emotions = ", ".join(f"{e['label']} ({e['score']:.0%})" for e in emotions[:3])  # type: ignore
    category = clinical.get("category", "Unknown")
    category_conf = clinical.get("confidence", 0.0)
    risk_level = risk.get("level", "low")
    triggers = risk.get("triggers", [])
    safety = risk.get("safety_protocol", False)

    safety_note = (
        "\n⚠️  IMPORTANT: Analysis suggests high clinical risk. "
        "Recommend reaching out to a professional or a crisis resource."
        if safety
        else ""
    )

    return f"""You are a compassionate, clinically-informed mental-health analyst.

Analyzed text: "{text}"

Layer results:
- Top emotions detected: {top_emotions}
- Clinical classification: {category} (confidence {category_conf:.0%})
- Risk level: {risk_level.upper()}
- Crisis keywords found: {", ".join(triggers) if triggers else "none"}{safety_note}

Respond in exactly this structure:
**Insight:** [2-3 sentence empathetic observation about the emotional and psychological content]

**Coping Strategies:**
1. [Specific, actionable strategy]
2. [Specific, actionable strategy]

Keep the tone warm, non-judgmental, and professional. Do not use phrases like "As an AI"."""


async def generate_insight(text: str, emotions: list, clinical: dict, risk: dict) -> str:
    if not settings.OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set — using fallback insight.")
        return _fallback_insight(clinical)

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://sentimind.app",
        "X-Title": "SentiMind",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": _build_prompt(text, emotions, clinical, risk)}],
        "max_tokens": 512,
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient(timeout=OPENROUTER_TIMEOUT) as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)

        if response.status_code != 200:
            logger.warning("OpenRouter returned %s: %s", response.status_code, response.text)
            return _fallback_insight(clinical)

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    except asyncio.TimeoutError:
        logger.error("OpenRouter timed out after %ss", OPENROUTER_TIMEOUT)
        return _fallback_insight(clinical)
    except httpx.HTTPError as exc:
        logger.error("OpenRouter HTTP error: %s", exc)
        return _fallback_insight(clinical)
    except (KeyError, IndexError) as exc:
        logger.error("OpenRouter unexpected response shape: %s", exc)
        return _fallback_insight(clinical)
    except Exception as exc:
        logger.exception("OpenRouter unexpected error: %s", exc)
        return _fallback_insight(clinical)


def _fallback_insight(clinical: dict) -> str:
    cat = clinical.get("category", "your current state")
    return (
        f"**Insight:**\n"
        f"It sounds like you may be experiencing feelings related to {cat}. "
        "Your emotions are valid, and acknowledging them is an important first step. "
        "Please remember you are not alone in this.\n\n"
        "**Coping Strategies:**\n"
        "1. Practice grounding: name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, and 1 you taste.\n"
        "2. Reach out to a trusted person or a professional counselor — talking helps."
    )