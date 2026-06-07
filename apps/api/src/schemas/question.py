from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.classification import ClassificationRead, ClassificationUpsert

VALID_AREAS = {
    "lectura_critica",
    "matematicas",
    "sociales_ciudadanas",
    "ciencias_naturales",
    "ingles",
}


class QuestionBase(BaseModel):
    external_id: str | None = None
    year: int | None = None
    area: str
    question_number: int | None = None
    statement: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: str | None = None
    source_file: str | None = None
    page: int | None = None
    raw_text: str | None = None
    is_invalid: bool = False
    is_incomplete: bool = False

    @field_validator("correct_answer")
    @classmethod
    def validate_answer(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in {"A", "B", "C", "D"}:
            raise ValueError("correct_answer must be one of A, B, C or D")
        return normalized

    @field_validator("area")
    @classmethod
    def validate_area(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in VALID_AREAS:
            raise ValueError(f"area must be one of {sorted(VALID_AREAS)}")
        return normalized


class QuestionCreate(QuestionBase):
    document_id: int | None = None
    classification: ClassificationUpsert | None = None


class QuestionUpdate(BaseModel):
    external_id: str | None = None
    year: int | None = None
    area: str | None = None
    question_number: int | None = None
    statement: str | None = None
    option_a: str | None = None
    option_b: str | None = None
    option_c: str | None = None
    option_d: str | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    source_file: str | None = None
    page: int | None = None
    raw_text: str | None = None
    is_invalid: bool | None = None
    is_incomplete: bool | None = None
    classification: ClassificationUpsert | None = None

    @field_validator("correct_answer")
    @classmethod
    def validate_answer(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if normalized not in {"A", "B", "C", "D"}:
            raise ValueError("correct_answer must be one of A, B, C or D")
        return normalized


class QuestionRead(QuestionBase):
    id: int
    document_id: int | None
    created_at: datetime
    updated_at: datetime
    classification: ClassificationRead | None = None

    model_config = ConfigDict(from_attributes=True)


class SimilarQuestion(BaseModel):
    question: QuestionRead
    score: float = Field(ge=0.0, le=1.0)
    reason: str
