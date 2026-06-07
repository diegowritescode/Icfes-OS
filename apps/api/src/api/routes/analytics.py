from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.schemas.analytics import AreaAnalytics, ErrorAnalytics, OverviewAnalytics, TopicPriority
from src.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=OverviewAnalytics)
def overview(db: Session = Depends(get_db)):
    return AnalyticsService(db).overview()


@router.get("/by-area", response_model=list[AreaAnalytics])
def by_area(db: Session = Depends(get_db)):
    return AnalyticsService(db).by_area()


@router.get("/by-topic", response_model=list[TopicPriority])
def by_topic(limit: int = Query(default=50, ge=1, le=200), db: Session = Depends(get_db)):
    return AnalyticsService(db).priority_topics(limit=limit)


@router.get("/errors", response_model=list[ErrorAnalytics])
def errors(db: Session = Depends(get_db)):
    return AnalyticsService(db).errors()


@router.get("/priority-topics", response_model=list[TopicPriority])
def priority_topics(limit: int = Query(default=15, ge=1, le=100), db: Session = Depends(get_db)):
    return AnalyticsService(db).priority_topics(limit=limit)
