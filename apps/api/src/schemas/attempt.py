from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

ERROR_TYPES = {
    "no_sabia_concepto",
    "formula_olvidada",
    "lectura_apresurada",
    "interprete_mal_grafica",
    "calculo_mal",
    "confundi_conceptos",
    "cai_en_distractor",
    "me_falto_contexto_colombia",
    "dude_entre_dos",
    "tiempo_excesivo",
    "otro",
}


class AttemptCreate(BaseModel):
    question_id: int
    selected_answer: str
    confidence: int = Field(ge=1, le=5)
    time_seconds: int | None = Field(default=None, ge=0)
    error_type: str | None = None
    notes: str | None = None

    @field_validator("selected_answer")
    @classmethod
    def validate_selected_answer(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in {"A", "B", "C", "D"}:
            raise ValueError("selected_answer must be one of A, B, C or D")
        return normalized

    @field_validator("error_type")
    @classmethod
    def validate_error_type(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if value not in ERROR_TYPES:
            raise ValueError(f"error_type must be one of {sorted(ERROR_TYPES)}")
        return value


class AttemptRead(BaseModel):
    id: int
    question_id: int
    selected_answer: str
    correct_answer: str
    is_correct: bool
    confidence: int
    time_seconds: int | None
    error_type: str | None
    notes: str | None
    attempted_at: datetime
    review_after: datetime | None

    model_config = ConfigDict(from_attributes=True)


class AttemptWithQuestion(AttemptRead):
    question_statement: str
    area: str
    topic: str | None = None
