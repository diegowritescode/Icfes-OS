from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.repositories.questions import QuestionRepository
from src.schemas.classification import ClassificationRead
from src.schemas.question import QuestionRead, QuestionUpdate, SimilarQuestion
from src.services.classification_service import ClassificationService
from src.services.search_service import SearchService

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", response_model=list[QuestionRead])
def list_questions(
    area: str | None = None,
    subarea: str | None = None,
    topic: str | None = None,
    year: int | None = None,
    difficulty: int | None = Query(default=None, ge=1, le=5),
    search: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list:
    return QuestionRepository(db).list(
        area=area,
        subarea=subarea,
        topic=topic,
        year=year,
        difficulty=difficulty,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get("/{question_id}", response_model=QuestionRead)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = QuestionRepository(db).get(question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found.")
    return question


@router.patch("/{question_id}", response_model=QuestionRead)
def update_question(question_id: int, payload: QuestionUpdate, db: Session = Depends(get_db)):
    repo = QuestionRepository(db)
    question = repo.get(question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found.")
    question = repo.update(question, payload)
    db.commit()
    db.refresh(question)
    return repo.get(question.id)


@router.post("/{question_id}/classify", response_model=ClassificationRead)
def classify_question(question_id: int, db: Session = Depends(get_db)):
    question = QuestionRepository(db).get(question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found.")
    return ClassificationService(db).classify_and_save(question)


@router.get("/{question_id}/similar", response_model=list[SimilarQuestion])
def similar_questions(question_id: int, limit: int = Query(default=5, ge=1, le=20), db: Session = Depends(get_db)):
    question = QuestionRepository(db).get(question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found.")
    return SearchService(db).similar_to_question(question, limit=limit)
