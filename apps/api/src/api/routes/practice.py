from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.repositories.attempts import AttemptRepository
from src.schemas.attempt import AttemptCreate, AttemptRead
from src.schemas.question import QuestionRead
from src.services.practice_service import PracticeService

router = APIRouter(prefix="/practice", tags=["practice"])


@router.get("/next", response_model=QuestionRead)
def next_question(
    mode: str = Query(default="adaptive"),
    area: str | None = None,
    topic: str | None = None,
    db: Session = Depends(get_db),
):
    question = PracticeService(db).next_question(mode=mode, area=area, topic=topic)
    if question is None:
        raise HTTPException(status_code=404, detail="No question available. Import questions first.")
    return question


@router.get("/review-due", response_model=list[QuestionRead])
def review_due(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    return AttemptRepository(db).due_questions(limit=limit)


@router.post("/attempt", response_model=AttemptRead)
def register_attempt(payload: AttemptCreate, db: Session = Depends(get_db)):
    try:
        return PracticeService(db).register_attempt(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
