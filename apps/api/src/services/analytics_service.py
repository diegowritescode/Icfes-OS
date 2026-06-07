from __future__ import annotations

from sqlalchemy.orm import Session

from src.core.config import settings
from src.repositories.analytics import AnalyticsRepository
from src.schemas.analytics import AreaAnalytics, ErrorAnalytics, OverviewAnalytics, TopicPriority
from src.services.scoring_service import TopicInput, score_topic_priorities


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AnalyticsRepository(db)

    def overview(self) -> OverviewAnalytics:
        totals = self.repo.totals()
        priorities = self.priority_topics(limit=1)
        recommendation = (
            f"Hoy prioriza {priorities[0].topic} en {priorities[0].area}."
            if priorities
            else "Importa preguntas sample para activar recomendaciones."
        )
        return OverviewAnalytics(
            **totals,
            ai_configured=settings.has_ai_key,
            embeddings_enabled=settings.enable_embeddings and bool(settings.openai_api_key),
            recommendation_today=recommendation,
        )

    def by_area(self) -> list[AreaAnalytics]:
        return [AreaAnalytics(**item) for item in self.repo.by_area()]

    def errors(self) -> list[ErrorAnalytics]:
        return [ErrorAnalytics(**item) for item in self.repo.error_counts()]

    def priority_topics(self, *, limit: int = 15) -> list[TopicPriority]:
        inputs = [
            TopicInput(
                area=str(row["area"]),
                topic=str(row["topic"] or "sin_clasificar"),
                total_questions=int(row["total_questions"] or 0),
                recent_questions=int(row["recent_questions"] or 0),
                attempts=int(row["attempts"] or 0),
                correct_attempts=int(row["correct_attempts"] or 0),
                avg_confidence=row["avg_confidence"],  # type: ignore[arg-type]
                avg_time_seconds=row["avg_time_seconds"],  # type: ignore[arg-type]
            )
            for row in self.repo.topic_inputs()
        ]
        return score_topic_priorities(inputs)[:limit]
