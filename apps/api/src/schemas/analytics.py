from __future__ import annotations

from pydantic import BaseModel, Field


class OverviewAnalytics(BaseModel):
    total_questions: int
    answered_questions: int
    total_attempts: int
    global_accuracy: float
    due_review_count: int
    imported_documents: int
    ai_configured: bool
    embeddings_enabled: bool
    recommendation_today: str


class AreaAnalytics(BaseModel):
    area: str
    total_questions: int
    attempts: int
    correct_attempts: int
    accuracy: float


class TopicPriority(BaseModel):
    area: str
    topic: str
    total_questions: int
    recent_questions: int
    attempts: int
    correct_attempts: int
    error_rate: float
    avg_confidence: float | None
    avg_time_seconds: float | None
    frequency_score: float
    recent_score: float
    low_confidence_score: float
    strategic_area_weight: float
    mastery_score: float
    priority_score: float
    interpretation: str


class ErrorAnalytics(BaseModel):
    error_type: str
    count: int


class TextSearchResult(BaseModel):
    id: int
    area: str
    topic: str | None
    statement: str
    score: float = Field(ge=0.0, le=1.0)
