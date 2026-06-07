from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"))
    external_id: Mapped[str | None] = mapped_column(String(120), index=True)
    year: Mapped[int | None] = mapped_column(Integer, index=True)
    area: Mapped[str] = mapped_column(String(80), index=True)
    question_number: Mapped[int | None] = mapped_column(Integer)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    option_a: Mapped[str] = mapped_column(Text, nullable=False)
    option_b: Mapped[str] = mapped_column(Text, nullable=False)
    option_c: Mapped[str] = mapped_column(Text, nullable=False)
    option_d: Mapped[str] = mapped_column(Text, nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(1), nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text)
    source_file: Mapped[str | None] = mapped_column(String(255))
    page: Mapped[int | None] = mapped_column(Integer)
    raw_text: Mapped[str | None] = mapped_column(Text)
    is_invalid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_incomplete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    document = relationship("Document", back_populates="questions")
    classification = relationship(
        "Classification",
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan",
    )
    attempts = relationship("Attempt", back_populates="question", cascade="all, delete-orphan")
    embedding = relationship(
        "QuestionEmbedding",
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan",
    )
