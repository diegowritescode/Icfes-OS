from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from src.models.attempt import Attempt
from src.models.classification import Classification
from src.models.question import Question


class AttemptRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, attempt: Attempt) -> Attempt:
        self.db.add(attempt)
        self.db.flush()
        return attempt

    def list(self, *, limit: int = 100, offset: int = 0) -> list[Attempt]:
        stmt = select(Attempt).order_by(Attempt.attempted_at.desc()).limit(limit).offset(offset)
        return list(self.db.scalars(stmt).all())

    def answered_question_count(self) -> int:
        return int(self.db.scalar(select(func.count(distinct(Attempt.question_id)))) or 0)

    def due_question_ids(self, now: datetime | None = None, *, limit: int = 50) -> list[int]:
        current = now or datetime.now(timezone.utc)
        stmt = (
            select(Attempt.question_id)
            .where(Attempt.review_after.is_not(None), Attempt.review_after <= current)
            .group_by(Attempt.question_id)
            .order_by(func.max(Attempt.review_after).asc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def due_questions(self, now: datetime | None = None, *, limit: int = 20) -> list[Question]:
        ids = self.due_question_ids(now=now, limit=limit)
        if not ids:
            return []
        stmt = (
            select(Question)
            .outerjoin(Classification)
            .where(Question.id.in_(ids))
            .order_by(Question.id.asc())
        )
        return list(self.db.scalars(stmt).unique().all())
