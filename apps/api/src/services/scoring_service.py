from __future__ import annotations

from dataclasses import dataclass

from src.schemas.analytics import TopicPriority
from src.services.taxonomy import STRATEGIC_AREA_WEIGHTS


@dataclass(frozen=True)
class TopicInput:
    area: str
    topic: str
    total_questions: int
    recent_questions: int
    attempts: int
    correct_attempts: int
    avg_confidence: float | None = None
    avg_time_seconds: float | None = None


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def interpretation_for(priority_score: float) -> str:
    if priority_score >= 0.75:
        return "estudiar hoy"
    if priority_score >= 0.55:
        return "estudiar esta semana"
    if priority_score >= 0.35:
        return "mantenimiento"
    return "baja prioridad"


def score_topic_priorities(inputs: list[TopicInput]) -> list[TopicPriority]:
    max_frequency = max((item.total_questions for item in inputs), default=1) or 1
    max_recent = max((item.recent_questions for item in inputs), default=1) or 1
    scored: list[TopicPriority] = []

    for item in inputs:
        frequency_score = item.total_questions / max_frequency
        recent_score = item.recent_questions / max_recent
        error_rate = 1 - (item.correct_attempts / item.attempts) if item.attempts else 0.5
        avg_confidence = item.avg_confidence
        confidence_normalized = ((avg_confidence - 1) / 4) if avg_confidence is not None else 0.5
        low_confidence_score = 1 - clamp(confidence_normalized)
        strategic_weight = STRATEGIC_AREA_WEIGHTS.get(item.area, 0.5)
        accuracy = item.correct_attempts / item.attempts if item.attempts else 0.0
        mastery_score = accuracy * clamp(confidence_normalized)

        priority_score = (
            0.25 * frequency_score
            + 0.25 * recent_score
            + 0.30 * error_rate
            + 0.10 * low_confidence_score
            + 0.10 * strategic_weight
            - 0.20 * mastery_score
        )
        priority_score = clamp(priority_score)

        scored.append(
            TopicPriority(
                area=item.area,
                topic=item.topic,
                total_questions=item.total_questions,
                recent_questions=item.recent_questions,
                attempts=item.attempts,
                correct_attempts=item.correct_attempts,
                error_rate=round(clamp(error_rate), 4),
                avg_confidence=round(avg_confidence, 2) if avg_confidence is not None else None,
                avg_time_seconds=round(item.avg_time_seconds, 2)
                if item.avg_time_seconds is not None
                else None,
                frequency_score=round(clamp(frequency_score), 4),
                recent_score=round(clamp(recent_score), 4),
                low_confidence_score=round(clamp(low_confidence_score), 4),
                strategic_area_weight=round(strategic_weight, 4),
                mastery_score=round(clamp(mastery_score), 4),
                priority_score=round(priority_score, 4),
                interpretation=interpretation_for(priority_score),
            )
        )

    return sorted(scored, key=lambda item: item.priority_score, reverse=True)
