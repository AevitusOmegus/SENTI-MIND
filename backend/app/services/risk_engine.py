import re
from app.core.constants import RISK_THRESHOLDS, SAFETY_PROTOCOL_THRESHOLD

HIGH_RISK_EMOTIONS = {"anger", "fear", "sadness", "disgust"}

# Tier 1 — unambiguous active crisis phrases (weight: 0.5 each)
CRISIS_KEYWORDS_HIGH = [
    "suicide", "suicidal", "kill myself", "killing myself",
    "end my life", "ending my life", "want to die", "wanting to die",
    "better off dead", "final exit", "end it all",
    "have a plan to", "planning to hurt", "planning to kill",
    "going to end it",
]

# Tier 2 — lower-specificity phrases (weight: 0.2 each)
CRISIS_KEYWORDS_MEDIUM = [
    "self-harm", "self harm", "cut myself", "cutting myself",
    "hurt myself", "hurting myself", "harm myself",
    "no reason to live", "can't go on", "cannot go on",
    "tired of living", "not worth living",
]

# 'hopeless' and 'worthless' removed — too fuzzy, now handled by clinical model only

_NEGATION_RE = re.compile(
    r"\b(not|never|no longer|don'?t|doesn'?t|didn'?t|won'?t|wouldn'?t|haven'?t|hasn'?t)\b"
)

# First-person markers — crisis keywords without these context signals are lower confidence
_FIRST_PERSON_RE = re.compile(
    r"\b(i am|i feel|i have|i've|i been|i'm|im|i think i|i want to|i need to|i'm going to)\b"
)

# Third-person context patterns — when a crisis keyword describes someone else
_THIRD_PERSON_CTX_RE = re.compile(
    r"\b(the|a|his|her|their|this|that|character|person|someone|friend|she is|he is|they are|was|were)\s+\w{0,10}\s*(suicidal|self.harm)\b"
)

# Confirmed active self-harm: past-tense act with time anchor
_ACTIVE_SELFHARM_RE = re.compile(
    r"\b(hurt|cut|harm|burned|burnt|hit|scratch|wound)\s+(myself|yourself)\s+"
    r"(today|tonight|yesterday|last night|earlier|just now|again|this morning|this week)\b"
)


def _is_negated(text_lower: str, keyword: str) -> bool:
    idx = text_lower.find(keyword)
    if idx == -1:
        return False
    window = text_lower[max(0, idx - 15):idx]
    return bool(_NEGATION_RE.search(window))


def _is_third_person_only(text_lower: str) -> bool:
    """Returns True if the text lacks first-person markers AND has third-person context."""
    has_first = bool(_FIRST_PERSON_RE.search(text_lower))
    has_third = bool(_THIRD_PERSON_CTX_RE.search(text_lower))
    return not has_first and has_third


def assess_risk(text: str, emotions: list[dict], clinical: dict) -> dict:
    text_lower = text.lower()
    third_person = _is_third_person_only(text_lower)

    # Apply negation and third-person filters to both tiers
    high_triggers = [
        kw for kw in CRISIS_KEYWORDS_HIGH
        if kw in text_lower
        and not _is_negated(text_lower, kw)
        and not (third_person and kw in ("suicide", "suicidal", "self-harm", "self harm"))
    ]
    medium_triggers = [
        kw for kw in CRISIS_KEYWORDS_MEDIUM
        if kw in text_lower
        and not _is_negated(text_lower, kw)
    ]
    all_triggers = high_triggers + medium_triggers

    keyword_score = min(len(high_triggers) * 0.5 + len(medium_triggers) * 0.2, 1.0)

    top_emotion = emotions[0] if emotions else {"label": "neutral", "score": 0.0}
    emotion_score = top_emotion["score"] if top_emotion["label"] in HIGH_RISK_EMOTIONS else 0.0

    suicidal_conf = 0.0
    for item in clinical.get("top_categories", []):
        if item["category"].lower() == "suicidal":
            suicidal_conf = item["confidence"]
            break

    risk_score = round(
        float(min(suicidal_conf * 0.55 + keyword_score * 0.30 + emotion_score * 0.15, 1.0)), 4
    )

    safety_protocol = (
        suicidal_conf >= SAFETY_PROTOCOL_THRESHOLD
        or len(high_triggers) >= 1
        or bool(_ACTIVE_SELFHARM_RE.search(text_lower))
    )

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
        "triggers": all_triggers,
        "safety_protocol": safety_protocol,
    }
