from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class DocumentCreate(BaseModel):
    filename: str
    source_type: str
    year: int | None = None
    area: str | None = None
    official_status: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class DocumentRead(BaseModel):
    id: int
    filename: str
    source_type: str
    year: int | None
    area: str | None
    official_status: str | None
    imported_at: datetime
    metadata_json: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class DocumentPageRead(BaseModel):
    id: int
    document_id: int
    page: int
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuestionCandidateBase(BaseModel):
    page: int | None = None
    raw_text: str
    statement: str | None = None
    option_a: str | None = None
    option_b: str | None = None
    option_c: str | None = None
    option_d: str | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    year: int | None = None
    area: str | None = None
    subarea: str | None = None
    topic: str | None = None
    subtopic: str | None = None

    @field_validator("correct_answer")
    @classmethod
    def validate_answer(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        normalized = value.strip().upper()
        if normalized not in {"A", "B", "C", "D"}:
            raise ValueError("correct_answer must be A, B, C or D")
        return normalized


class QuestionCandidateCreate(QuestionCandidateBase):
    document_id: int
    status: str = "pending"


class QuestionCandidateUpdate(BaseModel):
    page: int | None = None
    raw_text: str | None = None
    statement: str | None = None
    option_a: str | None = None
    option_b: str | None = None
    option_c: str | None = None
    option_d: str | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    year: int | None = None
    area: str | None = None
    subarea: str | None = None
    topic: str | None = None
    subtopic: str | None = None
    status: str | None = None

    @field_validator("correct_answer")
    @classmethod
    def validate_answer(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        normalized = value.strip().upper()
        if normalized not in {"A", "B", "C", "D"}:
            raise ValueError("correct_answer must be A, B, C or D")
        return normalized

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if value not in {"pending", "approved", "rejected"}:
            raise ValueError("status must be pending, approved or rejected")
        return value


class QuestionCandidateRead(QuestionCandidateBase):
    id: int
    document_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentDetail(DocumentRead):
    pages: list[DocumentPageRead] = Field(default_factory=list)
    candidates: list[QuestionCandidateRead] = Field(default_factory=list)


class ImportResult(BaseModel):
    document: DocumentRead
    imported_questions: int
    skipped_questions: int = 0
    errors: list[str] = []

    @computed_field
    @property
    def imported_count(self) -> int:
        return self.imported_questions

    @computed_field
    @property
    def skipped_count(self) -> int:
        return self.skipped_questions
