from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Classification(Base):
    __tablename__ = "classifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    area: Mapped[str] = mapped_column(String(80), nullable=False)
    subarea: Mapped[str | None] = mapped_column(String(120), index=True)
    topic: Mapped[str | None] = mapped_column(String(160), index=True)
    subtopic: Mapped[str | None] = mapped_column(String(160))
    competence: Mapped[str | None] = mapped_column(String(160))
    skill: Mapped[str | None] = mapped_column(String(160))
    difficulty: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    requires_formula: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_graph: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_colombia_context: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    concepts_json: Mapped[list[Any]] = mapped_column(JSON, default=list, nullable=False)
    keywords_json: Mapped[list[Any]] = mapped_column(JSON, default=list, nullable=False)
    likely_error_types_json: Mapped[list[Any]] = mapped_column(JSON, default=list, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    classified_by: Mapped[str] = mapped_column(String(80), default="manual", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    question = relationship("Question", back_populates="classification")
