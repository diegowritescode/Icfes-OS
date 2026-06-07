from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, joinedload

from src.models.classification import Classification
from src.models.question import Question
from src.schemas.classification import ClassificationUpsert
from src.schemas.question import QuestionCreate, QuestionUpdate


class QuestionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _with_classification(self, stmt: Select[tuple[Question]]) -> Select[tuple[Question]]:
        return stmt.options(joinedload(Question.classification))

    def list(
        self,
        *,
        area: str | None = None,
        subarea: str | None = None,
        topic: str | None = None,
        year: int | None = None,
        difficulty: int | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Question]:
        stmt = select(Question).outerjoin(Classification)
        if area:
            stmt = stmt.where(Question.area == area)
        if subarea:
            stmt = stmt.where(Classification.subarea == subarea)
        if topic:
            stmt = stmt.where(Classification.topic == topic)
        if year:
            stmt = stmt.where(Question.year == year)
        if difficulty:
            stmt = stmt.where(Classification.difficulty == difficulty)
        if search:
            query = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Question.statement.ilike(query),
                    Question.option_a.ilike(query),
                    Question.option_b.ilike(query),
                    Question.option_c.ilike(query),
                    Question.option_d.ilike(query),
                    Question.explanation.ilike(query),
                )
            )
        stmt = stmt.order_by(Question.year.desc().nullslast(), Question.id.desc()).limit(limit).offset(offset)
        return list(self.db.scalars(self._with_classification(stmt)).unique().all())

    def count(self) -> int:
        return int(self.db.scalar(select(func.count(Question.id))) or 0)

    def get(self, question_id: int) -> Question | None:
        stmt = select(Question).where(Question.id == question_id)
        return self.db.scalars(self._with_classification(stmt)).unique().first()

    def get_by_external_id(self, external_id: str) -> Question | None:
        stmt = select(Question).where(Question.external_id == external_id)
        return self.db.scalars(stmt).first()

    def create(self, payload: QuestionCreate) -> Question:
        data = payload.model_dump(exclude={"classification"})
        question = Question(**data)
        self.db.add(question)
        self.db.flush()
        if payload.classification:
            self.upsert_classification(question.id, payload.classification)
        return question

    def update(self, question: Question, payload: QuestionUpdate) -> Question:
        data = payload.model_dump(exclude_unset=True, exclude={"classification"})
        for field, value in data.items():
            setattr(question, field, value)
        if payload.classification:
            self.upsert_classification(question.id, payload.classification)
        self.db.flush()
        return question

    def upsert_classification(
        self,
        question_id: int,
        payload: ClassificationUpsert,
    ) -> Classification:
        classification = self.db.scalars(
            select(Classification).where(Classification.question_id == question_id)
        ).first()
        data = payload.model_dump()
        mapped = {
            "area": data["area"],
            "subarea": data.get("subarea"),
            "topic": data.get("topic"),
            "subtopic": data.get("subtopic"),
            "competence": data.get("competence"),
            "skill": data.get("skill"),
            "difficulty": data.get("difficulty", 3),
            "requires_formula": data.get("requires_formula", False),
            "requires_graph": data.get("requires_graph", False),
            "requires_colombia_context": data.get("requires_colombia_context", False),
            "concepts_json": data.get("concepts", []),
            "keywords_json": data.get("keywords", []),
            "likely_error_types_json": data.get("likely_error_types", []),
            "confidence": data.get("confidence", 0.0),
            "classified_by": data.get("classified_by", "manual"),
        }
        if classification is None:
            classification = Classification(question_id=question_id, **mapped)
            self.db.add(classification)
        else:
            for field, value in mapped.items():
                setattr(classification, field, value)
        self.db.flush()
        return classification

    def random_candidate(
        self,
        *,
        area: str | None = None,
        topic: str | None = None,
        exclude_answered: bool = False,
    ) -> Question | None:
        from src.models.attempt import Attempt

        stmt = select(Question).outerjoin(Classification).where(
            Question.is_invalid.is_(False),
            Question.is_incomplete.is_(False),
        )
        if area:
            stmt = stmt.where(Question.area == area)
        if topic:
            stmt = stmt.where(Classification.topic == topic)
        if exclude_answered:
            answered_ids = select(Attempt.question_id)
            stmt = stmt.where(Question.id.not_in(answered_ids))
        stmt = stmt.order_by(func.random()).limit(1)
        return self.db.scalars(self._with_classification(stmt)).unique().first()
