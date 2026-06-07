from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import case, distinct, func, select
from sqlalchemy.orm import Session

from src.models.attempt import Attempt
from src.models.classification import Classification
from src.models.document import Document
from src.models.question import Question


class AnalyticsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def totals(self) -> dict[str, int | float]:
        total_questions = int(self.db.scalar(select(func.count(Question.id))) or 0)
        total_attempts = int(self.db.scalar(select(func.count(Attempt.id))) or 0)
        answered_questions = int(self.db.scalar(select(func.count(distinct(Attempt.question_id)))) or 0)
        correct_attempts = int(
            self.db.scalar(select(func.count(Attempt.id)).where(Attempt.is_correct.is_(True))) or 0
        )
        due_review = int(
            self.db.scalar(
                select(func.count(distinct(Attempt.question_id))).where(
                    Attempt.review_after.is_not(None),
                    Attempt.review_after <= datetime.now(timezone.utc),
                )
            )
            or 0
        )
        documents = int(self.db.scalar(select(func.count(Document.id))) or 0)
        accuracy = correct_attempts / total_attempts if total_attempts else 0.0
        return {
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "total_attempts": total_attempts,
            "global_accuracy": round(accuracy, 4),
            "due_review_count": due_review,
            "imported_documents": documents,
        }

    def by_area(self) -> list[dict[str, int | float | str]]:
        correct_case = case((Attempt.is_correct.is_(True), 1), else_=0)
        stmt = (
            select(
                Question.area,
                func.count(distinct(Question.id)).label("total_questions"),
                func.count(Attempt.id).label("attempts"),
                func.coalesce(func.sum(correct_case), 0).label("correct_attempts"),
            )
            .outerjoin(Attempt, Attempt.question_id == Question.id)
            .group_by(Question.area)
            .order_by(Question.area.asc())
        )
        rows = self.db.execute(stmt).all()
        return [
            {
                "area": row.area,
                "total_questions": int(row.total_questions or 0),
                "attempts": int(row.attempts or 0),
                "correct_attempts": int(row.correct_attempts or 0),
                "accuracy": round((row.correct_attempts or 0) / row.attempts, 4) if row.attempts else 0.0,
            }
            for row in rows
        ]

    def error_counts(self) -> list[dict[str, int | str]]:
        stmt = (
            select(Attempt.error_type, func.count(Attempt.id).label("count"))
            .where(Attempt.error_type.is_not(None))
            .group_by(Attempt.error_type)
            .order_by(func.count(Attempt.id).desc())
        )
        return [
            {"error_type": row.error_type or "sin_tipo", "count": int(row.count)}
            for row in self.db.execute(stmt).all()
        ]

    def topic_inputs(self) -> list[dict[str, int | float | str | None]]:
        correct_case = case((Attempt.is_correct.is_(True), 1), else_=0)
        recent_question_case = case((Question.year >= 2020, Question.id), else_=None)
        topic_expr = func.coalesce(Classification.topic, "sin_clasificar")
        stmt = (
            select(
                Question.area.label("area"),
                topic_expr.label("topic"),
                func.count(distinct(Question.id)).label("total_questions"),
                func.count(distinct(recent_question_case)).label("recent_questions"),
                func.count(Attempt.id).label("attempts"),
                func.coalesce(func.sum(correct_case), 0).label("correct_attempts"),
                func.avg(Attempt.confidence).label("avg_confidence"),
                func.avg(Attempt.time_seconds).label("avg_time_seconds"),
            )
            .outerjoin(Classification, Classification.question_id == Question.id)
            .outerjoin(Attempt, Attempt.question_id == Question.id)
            .group_by(Question.area, topic_expr)
        )
        rows = self.db.execute(stmt).all()
        return [
            {
                "area": row.area,
                "topic": row.topic,
                "total_questions": int(row.total_questions or 0),
                "recent_questions": int(row.recent_questions or 0),
                "attempts": int(row.attempts or 0),
                "correct_attempts": int(row.correct_attempts or 0),
                "avg_confidence": float(row.avg_confidence) if row.avg_confidence is not None else None,
                "avg_time_seconds": float(row.avg_time_seconds) if row.avg_time_seconds is not None else None,
            }
            for row in rows
        ]
