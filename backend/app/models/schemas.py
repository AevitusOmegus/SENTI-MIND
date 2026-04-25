from pydantic import BaseModel, Field, field_validator
from typing import Optional


class AnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

    @field_validator("text")
    @classmethod
    def strip_text(cls, v: str) -> str:
        return v.strip()


class EmotionResult(BaseModel):
    label: str
    score: float


class ClinicalCategory(BaseModel):
    category: str
    confidence: float


class ClinicalResult(BaseModel):
    category: str
    confidence: float
    top_categories: list[ClinicalCategory]


class EntityResult(BaseModel):
    text: str
    label: str
    start: int
    end: int


class RiskAssessment(BaseModel):
    level: str
    score: float
    triggers: list[str]
    safety_protocol: bool


class ModelUsed(BaseModel):
    name: str
    type: str
    provider: str
    details: Optional[dict] = None

class AnalysisResponse(BaseModel):
    raw_text: str
    preprocessed_text: str
    emotions: list[EmotionResult]
    clinical: ClinicalResult
    entities: list[EntityResult]
    risk: RiskAssessment
    insight: Optional[str] = None
    models_used: list[ModelUsed] = []
