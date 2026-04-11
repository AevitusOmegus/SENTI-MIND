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
**What You Are Feeling:** [detailed analysis of their current emotional state, based on the text and emotions detected]

**Why You Might Be Feeling This:** [empathetic psychological reasoning behind their feelings]

**Potential Issues/Risks:** [gentle discussion of any risks or raised issues from their text, if none, mention it subtly]

**Exercises & Coping Strategies:**
1. [Specific, actionable exercise or strategy]
2. [Specific, actionable exercise or strategy]

Keep the tone warm, empathetic, non-judgmental, and highly professional. Do not use phrases like "As an AI"."""


async def generate_insight(text: str, emotions: list, clinical: dict, risk: dict) -> tuple[str, dict | None]:
    if not settings.OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set — using fallback insight.")
        return _fallback_insight(clinical), None

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
            return _fallback_insight(clinical), None

        data = response.json()
        insight_text = data["choices"][0]["message"]["content"].strip()
        usage = data.get("usage", {})
        return insight_text, {"model": data.get("model", OPENROUTER_MODEL), "usage": usage}

    except asyncio.TimeoutError:
        logger.error("OpenRouter timed out after %ss", OPENROUTER_TIMEOUT)
        return _fallback_insight(clinical), None
    except httpx.HTTPError as exc:
        logger.error("OpenRouter HTTP error: %s", exc)
        return _fallback_insight(clinical), None
    except (KeyError, IndexError) as exc:
        logger.error("OpenRouter unexpected response shape: %s", exc)
        return _fallback_insight(clinical), None
    except Exception as exc:
        logger.exception("OpenRouter unexpected error: %s", exc)
        return _fallback_insight(clinical), None


def _fallback_insight(clinical: dict) -> str:
    cat = clinical.get("category", "your current state")
    return (
        f"**What You Are Feeling:**\n"
        f"It sounds like you may be experiencing feelings related to {cat}. "
        "Your emotions are valid, and acknowledging them is an important first step.\n\n"
        f"**Why You Might Be Feeling This:**\n"
        "It's completely normal to feel this way, especially when navigating difficult situations "
        "or carrying unseen burdens.\n\n"
        f"**Potential Issues/Risks:**\n"
        "Please remember you are not alone in this. While everyone faces challenges, your well-being comes first.\n\n"
        "**Exercises & Coping Strategies:**\n"
        "1. Practice grounding: name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, and 1 you taste.\n"
        "2. Reach out to a trusted person or a professional counselor — talking helps."
    )