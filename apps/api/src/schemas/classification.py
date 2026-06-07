from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClassificationBase(BaseModel):
    area: str
    subarea: str | None = None
    topic: str | None = None
    subtopic: str | None = None
    competence: str | None = None
    skill: str | None = None
    difficulty: int = Field(default=3, ge=1, le=5)
    requires_formula: bool = False
    requires_graph: bool = False
    requires_colombia_context: bool = False
    concepts: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    likely_error_types: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    classified_by: str = "manual"

    @field_validator("area", "subarea", "topic", "subtopic", "competence", "skill", mode="before")
    @classmethod
    def normalize_slugish(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ClassificationUpsert(ClassificationBase):
    pass


class ClassificationRead(BaseModel):
    id: int
    question_id: int
    area: str
    subarea: str | None
    topic: str | None
    subtopic: str | None
    competence: str | None
    skill: str | None
    difficulty: int
    requires_formula: bool
    requires_graph: bool
    requires_colombia_context: bool
    concepts_json: list
    keywords_json: list
    likely_error_types_json: list
    confidence: float
    classified_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
