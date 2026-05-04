

# Mental Health Categories (7-class clinical classification)
MENTAL_HEALTH_CATEGORIES = [
    "Anxiety",
    "Depression",
    "Suicidal",
    "Stress",
    "Bipolar",
    "Normal",
    "Personality Disorder",
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

# ── Consolidated Crisis Keywords (single source of truth) ──────────────
# Used by both the preprocessing pipeline and the risk engine.
# Keys are lowercase phrases; values are severity weights (0.0–1.0).
CRISIS_KEYWORDS = {
    # Tier 1 — Active planning / method (weight 1.0)
    "kill myself": 1.0,
    "killing myself": 1.0,
    "end my life": 1.0,
    "ending my life": 1.0,
    "end it all": 1.0,
    "take my own life": 1.0,
    "suicide plan": 1.0,
    "going to die": 1.0,
    "final exit": 1.0,
    "ending it": 1.0,
    # Tier 2 — Active ideation (weight 0.7–0.9)
    "suicide": 0.7,
    "suicidal": 0.7,
    "want to die": 0.7,
    "wanting to die": 0.7,
    "better off dead": 0.7,
    "not worth living": 0.7,
    "no reason to live": 0.9,
    "overdose": 0.9,
    # Tier 3 — Self-harm (weight 0.6–0.9)
    "self-harm": 0.9,
    "self harm": 0.9,
    "cut myself": 0.9,
    "cutting myself": 0.9,
    "hurt myself": 0.9,
    "hurting myself": 0.9,
    "harm myself": 0.9,
    "harming myself": 0.9,
    # Tier 4 — Passive / ambiguous (weight 0.3–0.7)
    "can't go on": 0.7,
    "cannot go on": 0.7,
    "tired of living": 0.7,
    "don't want to be alive": 0.7,
    "hopeless": 0.3,
    "worthless": 0.3,
}
