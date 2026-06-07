from __future__ import annotations

from sqlalchemy.orm import Session

from src.models.question import Question
from src.models.question_candidate import QuestionCandidate
from src.repositories.documents import DocumentRepository
from src.repositories.questions import QuestionRepository
from src.schemas.classification import ClassificationUpsert
from src.schemas.document import QuestionCandidateUpdate
from src.schemas.question import QuestionCreate


class CandidateApprovalError(ValueError):
    pass


class CandidateService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.documents = DocumentRepository(db)
        self.questions = QuestionRepository(db)

    def get(self, candidate_id: int) -> QuestionCandidate | None:
        return self.documents.get_candidate(candidate_id)

    def update(self, candidate: QuestionCandidate, payload: QuestionCandidateUpdate) -> QuestionCandidate:
        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(candidate, field, value)
        self.db.commit()
        self.db.refresh(candidate)
        return candidate

    def reject(self, candidate: QuestionCandidate) -> QuestionCandidate:
        candidate.status = "rejected"
        self.db.commit()
        self.db.refresh(candidate)
        return candidate

    def approve(self, candidate: QuestionCandidate) -> Question:
        required = {
            "area": candidate.area,
            "statement": candidate.statement,
            "option_a": candidate.option_a,
            "option_b": candidate.option_b,
            "option_c": candidate.option_c,
            "option_d": candidate.option_d,
            "correct_answer": candidate.correct_answer,
        }
        missing = [field for field, value in required.items() if not value]
        if missing:
            raise CandidateApprovalError(
                f"Candidate is missing required fields: {', '.join(missing)}"
            )
        document = self.documents.get(candidate.document_id)
        source_file = document.filename if document else None
        question = self.questions.create(
            QuestionCreate(
                document_id=candidate.document_id,
                external_id=f"candidate-{candidate.id}",
                year=candidate.year,
                area=str(candidate.area),
                question_number=None,
                statement=str(candidate.statement),
                option_a=str(candidate.option_a),
                option_b=str(candidate.option_b),
                option_c=str(candidate.option_c),
                option_d=str(candidate.option_d),
                correct_answer=str(candidate.correct_answer),
                explanation=candidate.explanation,
                source_file=source_file,
                page=candidate.page,
                raw_text=candidate.raw_text,
                classification=ClassificationUpsert(
                    area=str(candidate.area),
                    subarea=candidate.subarea,
                    topic=candidate.topic,
                    subtopic=candidate.subtopic,
                    competence="manual_review",
                    skill="manual_review",
                    difficulty=3,
                    confidence=0.9,
                    classified_by="manual_candidate_approval",
                ),
            )
        )
        candidate.status = "approved"
        self.db.commit()
        self.db.refresh(question)
        return question
