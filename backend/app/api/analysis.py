from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    AnalysisRequest, AnalysisResponse,
    EmotionResult, ClinicalResult, ClinicalCategory,
    EntityResult, RiskAssessment,
)
from app.models.classifier import classifier
from app.models.emotions import detect_emotions
from app.models.llm import generate_insight
from app.services.ner import extract_entities
from app.services.risk_engine import assess_risk
from app.services.preprocessor import clean_text

router = APIRouter()


@router.post("/", response_model=AnalysisResponse)
async def analyze_text(payload: AnalysisRequest):
    raw_text = payload.text.strip()
    if not raw_text:
        raise HTTPException(status_code=422, detail="Text cannot be empty.")

    try:
        cleaned_text, emoji_tokens = clean_text(raw_text)

        raw_emotions = await detect_emotions(cleaned_text)
        emotions = [EmotionResult(label=e["label"], score=e["score"]) for e in raw_emotions]

        raw_clinical = classifier.predict(cleaned_text)
        clinical = ClinicalResult(
            category=raw_clinical["category"],
            confidence=raw_clinical["confidence"],
            top_categories=[
                ClinicalCategory(category=c["category"], confidence=c["confidence"])
                for c in raw_clinical.get("top_categories", [])
            ],
        )

        raw_entities = extract_entities(cleaned_text)
        entities = [
            EntityResult(text=e["text"], label=e["label"], start=e["start"], end=e["end"])
            for e in raw_entities
        ]

        raw_risk = assess_risk(cleaned_text, raw_emotions, raw_clinical)
        risk = RiskAssessment(
            level=raw_risk["level"],
            score=raw_risk["score"],
            triggers=raw_risk["triggers"],
            safety_protocol=raw_risk["safety_protocol"],
        )

        insight = await generate_insight(cleaned_text, raw_emotions, raw_clinical, raw_risk)

        return AnalysisResponse(
            raw_text=raw_text,
            preprocessed_text=cleaned_text,
            emotions=emotions,
            clinical=clinical,
            entities=entities,
            risk=risk,
            insight=insight,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
