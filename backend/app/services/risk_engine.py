from app.core.constants import RISK_THRESHOLDS, SAFETY_PROTOCOL_THRESHOLD

HIGH_RISK_EMOTIONS = {"anger", "fear", "sadness", "disgust"}

CRISIS_KEYWORDS = [
    "suicide", "suicidal", "self-harm", "self harm", "kill myself",
    "end my life", "end it all", "hopeless", "worthless", "want to die",
    "can't go on", "cannot go on", "no reason to live", "cut myself",
    "hurt myself",
]


def assess_risk(text: str, emotions: list[dict], clinical: dict) -> dict:
    text_lower = text.lower()

    triggers = [kw for kw in CRISIS_KEYWORDS if kw in text_lower]
    keyword_score = min(len(triggers) * 0.4, 1.0)

    top_emotion = emotions[0] if emotions else {"label": "neutral", "score": 0.0}
    emotion_score = (
        top_emotion["score"] if top_emotion["label"] in HIGH_RISK_EMOTIONS else 0.0
    )

    suicidal_conf = 0.0
    for item in clinical.get("top_categories", []):
        if item["category"].lower() == "suicidal":
            suicidal_conf = item["confidence"]
            break

    risk_score = round(float(min(suicidal_conf * 0.50 + emotion_score * 0.30 + keyword_score * 0.20, 1.0)), 4)  # type: ignore

    safety_protocol = suicidal_conf >= SAFETY_PROTOCOL_THRESHOLD

    if safety_protocol or risk_score >= RISK_THRESHOLDS["high"]:
        level = "critical"
    elif risk_score >= RISK_THRESHOLDS["medium"]:
        level = "high"
    elif risk_score >= RISK_THRESHOLDS["low"]:
        level = "medium"
    else:
        level = "low"

    return {
        "level": level,
        "score": risk_score,
        "triggers": triggers,
        "safety_protocol": safety_protocol,
    }
