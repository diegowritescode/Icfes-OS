from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer)
    area: Mapped[str | None] = mapped_column(String(80))
    official_status: Mapped[str | None] = mapped_column(String(80))
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    questions = relationship("Question", back_populates="document")
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    candidates = relationship(
        "QuestionCandidate",
        back_populates="document",
        cascade="all, delete-orphan",
    )
