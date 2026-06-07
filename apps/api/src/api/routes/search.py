from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.repositories.questions import QuestionRepository
from src.schemas.analytics import TextSearchResult
from src.schemas.question import SimilarQuestion
from src.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


class SemanticSearchRequest(BaseModel):
    query: str
    area: str | None = None
    limit: int = 10


@router.get("/text", response_model=list[TextSearchResult])
def text_search(
    q: str = Query(min_length=1),
    area: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    questions = SearchService(db).text_search(q, area=area, limit=limit)
    return [
        TextSearchResult(
            id=item.id,
            area=item.area,
            topic=item.classification.topic if item.classification else None,
            statement=item.statement,
            score=0.5,
        )
        for item in questions
    ]


@router.post("/semantic", response_model=list[SimilarQuestion])
def semantic_search(payload: SemanticSearchRequest, db: Session = Depends(get_db)):
    seed = SearchService(db).text_search(payload.query, area=payload.area, limit=1)
    if not seed:
        raise HTTPException(status_code=404, detail="No matching question for semantic fallback.")
    question = QuestionRepository(db).get(seed[0].id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found.")
    return SearchService(db).similar_to_question(question, limit=payload.limit)
