from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class DailyPlanRequest(BaseModel):
    available_minutes: int = Field(default=120, ge=30, le=480)
    area: str | None = None
    max_blocks: int = Field(default=3, ge=1, le=6)
    preference: Literal["teoria", "practica", "repaso", "mixto"] = "mixto"


class StudyBlock(BaseModel):
    block: int
    minutes: int
    area: str
    topic: str
    activity: str
    suggested_questions: int
    review_question_ids: list[int] = []
    reason: str


class DailyPlanRead(BaseModel):
    id: int | None = None
    plan_date: date
    available_minutes: int
    generated_at: datetime | None = None
    plan_json: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)
