from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.repositories.questions import QuestionRepository
from src.services.tutor_service import TutorService

router = APIRouter(prefix="/tutor", tags=["tutor"])


class ExplainErrorRequest(BaseModel):
    question_id: int
    user_answer: str
    error_type: str | None = None


@router.post("/explain-error")
def explain_error(payload: ExplainErrorRequest, db: Session = Depends(get_db)) -> dict[str, str | bool]:
    question = QuestionRepository(db).get(payload.question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found.")
    return TutorService(db).explain_error(
        question=question,
        user_answer=payload.user_answer.upper(),
        error_type=payload.error_type,
    )
