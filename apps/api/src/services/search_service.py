from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from src.models.classification import Classification
from src.models.question import Question
from src.models.vector import QuestionEmbedding
from src.schemas.question import SimilarQuestion
from src.services.embeddings_service import EmbeddingsService


class SearchService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def text_search(self, query: str, *, area: str | None = None, limit: int = 20) -> list[Question]:
        pattern = f"%{query.strip()}%"
        stmt = select(Question).outerjoin(Classification).options(joinedload(Question.classification)).where(
            or_(
                Question.statement.ilike(pattern),
                Question.option_a.ilike(pattern),
                Question.option_b.ilike(pattern),
                Question.option_c.ilike(pattern),
                Question.option_d.ilike(pattern),
                Classification.topic.ilike(pattern),
                Classification.subarea.ilike(pattern),
            )
        )
        if area:
            stmt = stmt.where(Question.area == area)
        stmt = stmt.limit(limit)
        return list(self.db.scalars(stmt).unique().all())

    def similar_to_question(self, question: Question, *, limit: int = 5) -> list[SimilarQuestion]:
        embedding_service = EmbeddingsService(self.db)
        if embedding_service.enabled and question.embedding is not None:
            distance = QuestionEmbedding.embedding.cosine_distance(question.embedding.embedding)
            stmt = (
                select(Question, distance.label("distance"))
                .join(QuestionEmbedding, QuestionEmbedding.question_id == Question.id)
                .where(Question.id != question.id)
                .order_by(distance)
                .limit(limit)
            )
            rows = self.db.execute(stmt).all()
            return [
                SimilarQuestion(question=row.Question, score=max(0, 1 - float(row.distance)), reason="vector")
                for row in rows
            ]

        topic = question.classification.topic if question.classification else None
        stmt = (
            select(Question)
            .outerjoin(Classification)
            .options(joinedload(Question.classification))
            .where(Question.id != question.id)
            .limit(limit)
        )
        if topic:
            stmt = stmt.where(Classification.topic == topic)
            reason = "fallback por tema"
        else:
            stmt = stmt.where(Question.area == question.area)
            reason = "fallback por area"
        questions = list(self.db.scalars(stmt).unique().all())
        return [SimilarQuestion(question=item, score=0.55, reason=reason) for item in questions]
