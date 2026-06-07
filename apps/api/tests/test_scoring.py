from __future__ import annotations

from src.services.scoring_service import TopicInput, interpretation_for, score_topic_priorities


def test_priority_rewards_weak_strategic_area() -> None:
    scored = score_topic_priorities(
        [
            TopicInput(
                area="ciencias_naturales",
                topic="enlaces_quimicos",
                total_questions=10,
                recent_questions=8,
                attempts=5,
                correct_attempts=1,
                avg_confidence=2.0,
                avg_time_seconds=80,
            ),
            TopicInput(
                area="lectura_critica",
                topic="inferencia",
                total_questions=10,
                recent_questions=8,
                attempts=5,
                correct_attempts=5,
                avg_confidence=5.0,
                avg_time_seconds=40,
            ),
        ]
    )

    assert scored[0].topic == "enlaces_quimicos"
    assert scored[0].priority_score > scored[1].priority_score


def test_interpretation_thresholds() -> None:
    assert interpretation_for(0.80) == "estudiar hoy"
    assert interpretation_for(0.60) == "estudiar esta semana"
    assert interpretation_for(0.40) == "mantenimiento"
    assert interpretation_for(0.20) == "baja prioridad"
