from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.schemas.study import DailyPlanRead, DailyPlanRequest
from src.services.recommender_service import RecommenderService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/daily-plan", response_model=DailyPlanRead)
def daily_plan(payload: DailyPlanRequest, db: Session = Depends(get_db)):
    plan = RecommenderService(db).generate_daily_plan(payload)
    db.commit()
    db.refresh(plan)
    return plan
