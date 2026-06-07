from __future__ import annotations

from sqlalchemy.orm import Session

from src.models.attempt import Attempt
from src.models.question import Question
from src.repositories.attempts import AttemptRepository
from src.repositories.questions import QuestionRepository
from src.schemas.attempt import AttemptCreate
from src.services.analytics_service import AnalyticsService
from src.services.spaced_repetition_service import calculate_review_after


class PracticeService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.questions = QuestionRepository(db)
        self.attempts = AttemptRepository(db)

    def next_question(
        self,
        *,
        mode: str = "adaptive",
        area: str | None = None,
        topic: str | None = None,
    ) -> Question | None:
        if mode == "review":
            due = self.attempts.due_questions(limit=1)
            if due:
                return due[0]
        if mode == "adaptive" and not topic:
            priorities = AnalyticsService(self.db).priority_topics(limit=5)
            if area:
                priorities = [item for item in priorities if item.area == area]
            if priorities:
                area = priorities[0].area
                topic = priorities[0].topic
        return self.questions.random_candidate(area=area, topic=topic, exclude_answered=False)

    def register_attempt(self, payload: AttemptCreate) -> Attempt:
        question = self.questions.get(payload.question_id)
        if question is None:
            raise ValueError("Question not found")
        selected = payload.selected_answer.upper()
        is_correct = selected == question.correct_answer.upper()
        attempt = Attempt(
            question_id=question.id,
            selected_answer=selected,
            correct_answer=question.correct_answer.upper(),
            is_correct=is_correct,
            confidence=payload.confidence,
            time_seconds=payload.time_seconds,
            error_type=None if is_correct else payload.error_type,
            notes=payload.notes,
            review_after=calculate_review_after(is_correct=is_correct, confidence=payload.confidence),
        )
        self.attempts.create(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt
