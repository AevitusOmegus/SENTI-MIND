from pydantic import BaseModel
from typing import Optional


class AnalysisRequest(BaseModel):
    text: str


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


class AnalysisResponse(BaseModel):
    raw_text: str
    preprocessed_text: str
    emotions: list[EmotionResult]
    clinical: ClinicalResult
    entities: list[EntityResult]
    risk: RiskAssessment
    insight: Optional[str] = None
