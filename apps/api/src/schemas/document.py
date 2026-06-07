from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


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


class ImportResult(BaseModel):
    document: DocumentRead
    imported_questions: int
    skipped_questions: int = 0
    errors: list[str] = []
