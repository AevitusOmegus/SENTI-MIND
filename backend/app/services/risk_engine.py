
import re

from app.core.constants import RISK_THRESHOLDS, SAFETY_PROTOCOL_THRESHOLD, CRISIS_KEYWORDS
from app.core.preprocessing import has_negated_crisis

HIGH_RISK_EMOTIONS = {"anger", "fear", "sadness", "disgust"}

# Crisis keywords are imported from constants.py (single source of truth)
# CRISIS_KEYWORDS contains all tiered keywords with severity weights.

# Past-tense patterns that indicate recovery or historical context
PAST_TENSE_PATTERNS = [
    r"\b(used to|i was|i had|years ago|months ago|last year|in the past)\b.{0,30}\b(suicidal|suicide|depressed|self.?harm|kill myself)\b",
    r"\b(suicidal|suicide|depressed|self.?harm)\b.{0,30}\b(years ago|months ago|last year|in the past|used to|i was|recovered|better now)\b",
    r"\b(no longer|not anymore|overcame|recovered from|got over)\b.{0,20}\b(suicidal|suicide|depressed|self.?harm)\b",
]
_PAST_TENSE_RES = [re.compile(p, re.IGNORECASE) for p in PAST_TENSE_PATTERNS]


def _is_past_tense_context(text: str) -> bool:
    for pat in _PAST_TENSE_RES:
        if pat.search(text):
            return True
    return False


def assess_risk(text: str, emotions: list[dict], clinical: dict) -> dict:
    text_lower = text.lower()

    triggers = []
    keyword_score = 0.0
    for kw, weight in CRISIS_KEYWORDS.items():
        if kw in text_lower:
            triggers.append(kw)
            keyword_score = max(keyword_score, weight)

    if triggers and has_negated_crisis(text):
        keyword_score *= 0.15
        triggers = [f"{t} (negated)" for t in triggers]

    if triggers and _is_past_tense_context(text):
        keyword_score *= 0.2
        triggers = [f"{t} (past)" if "(negated)" not in t else t for t in triggers]

    keyword_score = min(keyword_score, 1.0)

    emotion_score = 0.0
    if emotions:
        for emo in emotions[:3]:
            if emo["label"] in HIGH_RISK_EMOTIONS:
                position_weight = 1.0 if emo == emotions[0] else 0.5
                emotion_score += emo["score"] * position_weight
        emotion_score = min(emotion_score / 1.5, 1.0)

    suicidal_conf = 0.0
    for item in clinical.get("top_categories", []):
        if item["category"].lower() == "suicidal":
            suicidal_conf = item["confidence"]
            break

    category = clinical.get("category", "Unknown")

    if category == "Normal" and keyword_score > 0.3:
        risk_score = keyword_score * 0.60 + emotion_score * 0.25 + suicidal_conf * 0.15
    elif category == "Suicidal" and not triggers:
        risk_score = suicidal_conf * 0.55 + emotion_score * 0.30 + keyword_score * 0.15
    else:
        risk_score = suicidal_conf * 0.45 + emotion_score * 0.30 + keyword_score * 0.25

    risk_score = round(float(min(risk_score, 1.0)), 4)

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
