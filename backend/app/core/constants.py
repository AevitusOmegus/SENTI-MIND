"""
SENTI-MIND Core Constants
"""

# Mental Health Categories (7-class clinical classification)
MENTAL_HEALTH_CATEGORIES = [
    "Anxiety",
    "Depression",
    "Suicidal",
    "Stress",
    "Bipolar",
    "Normal",
    "Personality disorder",
]

# Risk Assessment Thresholds
RISK_THRESHOLDS = {
    "low": 0.25,
    "medium": 0.50,
    "high": 0.75,
}

# Safety Protocol - Triggers at 70% suicidal confidence
SAFETY_PROTOCOL_THRESHOLD = 0.70

# Risk Levels
RISK_LEVELS = ["low", "medium", "high", "critical"]
