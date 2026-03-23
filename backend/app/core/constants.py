HF_EMOTION_MODEL = "bhadresh-savani/distilbert-base-uncased-emotion"

MENTAL_HEALTH_CATEGORIES = [
    "Anxiety",
    "Depression",
    "Suicidal",
    "Stress",
    "Bipolar",
    "Normal",
    "Personality Disorder",
]

RISK_THRESHOLDS = {
    "low": 0.25,
    "medium": 0.50,
    "high": 0.75,
}

SAFETY_PROTOCOL_THRESHOLD = 0.70

RISK_LEVELS = ["low", "medium", "high", "critical"]
