from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.repositories.analytics import AnalyticsRepository
from src.repositories.attempts import AttemptRepository
from src.schemas.attempt import AttemptRead

router = APIRouter(prefix="/attempts", tags=["attempts"])


@router.get("", response_model=list[AttemptRead])
def list_attempts(
    limit: int = Query(default=100, ge=1, le=300),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list:
    return AttemptRepository(db).list(limit=limit, offset=offset)


@router.get("/stats")
def attempt_stats(db: Session = Depends(get_db)) -> dict[str, object]:
    totals = AnalyticsRepository(db).totals()
    return {
        "answered_questions": totals["answered_questions"],
        "total_attempts": totals["total_attempts"],
        "global_accuracy": totals["global_accuracy"],
        "due_review_count": totals["due_review_count"],
    }
