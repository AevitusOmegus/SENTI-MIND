import pytest
from app.services.risk_engine import assess_risk


def test_low_risk_normal():
    emotions = [{"label": "joy", "score": 0.8}]
    clinical = {"category": "Normal", "confidence": 0.9, "top_categories": [{"category": "Suicidal", "confidence": 0.01}]}
    result = assess_risk("I had a great day!", emotions, clinical)
    assert result["level"] == "low"
    assert not result["safety_protocol"]


def test_high_risk_suicidal_conf():
    emotions = [{"label": "sadness", "score": 0.6}]
    clinical = {
        "category": "Suicidal",
        "confidence": 0.75,
        "top_categories": [{"category": "Suicidal", "confidence": 0.75}],
    }
    result = assess_risk("I don't narrow what to do anymore.", emotions, clinical)
    assert result["level"] == "critical"
    assert result["safety_protocol"] is True


def test_medium_risk_anxiety():
    emotions = [{"label": "fear", "score": 0.7}]
    clinical = {
        "category": "Anxiety",
        "confidence": 0.8,
        "top_categories": [{"category": "Anxiety", "confidence": 0.8}, {"category": "Suicidal", "confidence": 0.1}],
    }
    result = assess_risk("I am so stressed about exams.", emotions, clinical)
    assert result["level"] in ("medium", "high")


def test_keyword_risk_boost():
    emotions = [{"label": "neutral", "score": 0.9}]
    clinical = {"category": "Normal", "confidence": 0.5, "top_categories": [{"category": "Suicidal", "confidence": 0.05}]}
    result = assess_risk("I want to end my life.", emotions, clinical)
    assert "end my life" in result["triggers"]
    assert result["score"] >= 0.05
