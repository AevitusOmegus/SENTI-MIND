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


def test_anxiety_not_escalated_to_critical():
    # Fear/anxiety emotions alone should not push risk to critical.
    # With new weight scheme (emotion=0.15), stress about exams stays low/medium.
    emotions = [{"label": "fear", "score": 0.7}]
    clinical = {
        "category": "Anxiety",
        "confidence": 0.8,
        "top_categories": [{"category": "Anxiety", "confidence": 0.8}, {"category": "Suicidal", "confidence": 0.1}],
    }
    result = assess_risk("I am so stressed about exams.", emotions, clinical)
    assert result["level"] in ("low", "medium", "high")
    assert result["level"] != "critical"


def test_keyword_risk_boost():
    emotions = [{"label": "neutral", "score": 0.9}]
    clinical = {"category": "Normal", "confidence": 0.5, "top_categories": [{"category": "Suicidal", "confidence": 0.05}]}
    result = assess_risk("I want to end my life.", emotions, clinical)
    assert "end my life" in result["triggers"]
    assert result["safety_protocol"] is True


def test_negation_blocks_false_positive():
    emotions = [{"label": "neutral", "score": 0.6}]
    clinical = {"category": "Stress", "confidence": 0.8, "top_categories": [{"category": "Suicidal", "confidence": 0.05}]}
    result = assess_risk("I am not suicidal, just stressed out.", emotions, clinical)
    assert result["level"] == "low"
    assert not result["safety_protocol"]


def test_fictional_reference_no_modal():
    emotions = [{"label": "neutral", "score": 0.7}]
    clinical = {"category": "Normal", "confidence": 0.6, "top_categories": [{"category": "Suicidal", "confidence": 0.1}]}
    result = assess_risk("The movie had a suicidal character.", emotions, clinical)
    assert not result["safety_protocol"]


def test_confirmed_self_harm_escalates():
    emotions = [{"label": "sadness", "score": 0.7}]
    clinical = {"category": "Suicidal", "confidence": 0.5, "top_categories": [{"category": "Suicidal", "confidence": 0.5}]}
    result = assess_risk("I am not suicidal but I hurt myself today.", emotions, clinical)
    assert result["safety_protocol"] is True
    assert result["level"] == "critical"
