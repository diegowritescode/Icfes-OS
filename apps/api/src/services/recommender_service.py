from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from src.models.study import DailyPlan
from src.repositories.attempts import AttemptRepository
from src.schemas.study import DailyPlanRequest, StudyBlock
from src.services.analytics_service import AnalyticsService


class RecommenderService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def generate_daily_plan(self, request: DailyPlanRequest) -> DailyPlan:
        priorities = AnalyticsService(self.db).priority_topics(limit=20)
        if request.area:
            priorities = [item for item in priorities if item.area == request.area]
        due_ids = AttemptRepository(self.db).due_question_ids(limit=20)

        block_count = max(1, min(request.max_blocks, max(1, request.available_minutes // 45)))
        minutes_remaining = request.available_minutes
        blocks: list[StudyBlock] = []

        for index in range(block_count):
            priority = priorities[index % len(priorities)] if priorities else None
            minutes = min(90, max(45, minutes_remaining // (block_count - index)))
            minutes_remaining -= minutes
            area = priority.area if priority else request.area or "ciencias_naturales"
            topic = priority.topic if priority else "sin_clasificar"
            suggested_questions = max(5, min(25, minutes // 4))

            if request.preference == "teoria":
                activity = f"mini teoria + {max(8, suggested_questions // 2)} preguntas"
            elif request.preference == "repaso":
                activity = f"repasar falladas + {suggested_questions} preguntas"
            elif request.preference == "practica":
                activity = f"{suggested_questions} preguntas cronometradas"
            else:
                activity = f"mini teoria + {suggested_questions} preguntas + correccion"

            reason = (
                f"{priority.interpretation}: prioridad {priority.priority_score:.2f}, "
                f"error {priority.error_rate:.0%}, peso estrategico {priority.strategic_area_weight:.2f}"
                if priority
                else "No hay suficientes datos; se usa prioridad estrategica inicial."
            )

            blocks.append(
                StudyBlock(
                    block=index + 1,
                    minutes=minutes,
                    area=area,
                    topic=topic,
                    activity=activity,
                    suggested_questions=suggested_questions,
                    review_question_ids=due_ids[: min(5, len(due_ids))] if index == 0 else [],
                    reason=reason,
                )
            )

        plan_json = {
            "blocks": [block.model_dump() for block in blocks],
            "due_review_question_ids": due_ids,
            "preference": request.preference,
            "phase": "fase_1_basica",
        }
        daily_plan = DailyPlan(
            plan_date=date.today(),
            available_minutes=request.available_minutes,
            plan_json=plan_json,
        )
        self.db.add(daily_plan)
        self.db.flush()
        return daily_plan
