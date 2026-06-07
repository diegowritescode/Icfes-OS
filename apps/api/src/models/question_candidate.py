from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class QuestionCandidate(Base):
    __tablename__ = "question_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    page: Mapped[int | None] = mapped_column(Integer)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    statement: Mapped[str | None] = mapped_column(Text)
    option_a: Mapped[str | None] = mapped_column(Text)
    option_b: Mapped[str | None] = mapped_column(Text)
    option_c: Mapped[str | None] = mapped_column(Text)
    option_d: Mapped[str | None] = mapped_column(Text)
    correct_answer: Mapped[str | None] = mapped_column(String(1))
    explanation: Mapped[str | None] = mapped_column(Text)
    year: Mapped[int | None] = mapped_column(Integer)
    area: Mapped[str | None] = mapped_column(String(80), index=True)
    subarea: Mapped[str | None] = mapped_column(String(120))
    topic: Mapped[str | None] = mapped_column(String(160), index=True)
    subtopic: Mapped[str | None] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    document = relationship("Document", back_populates="candidates")
