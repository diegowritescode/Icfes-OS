from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import (
    analytics,
    attempts,
    documents,
    health,
    practice,
    questions,
    recommendations,
    search,
    tutor,
)
from src.core.config import settings

app = FastAPI(
    title="ICFES OS API",
    version="0.1.0",
    description="Local-first adaptive study intelligence for Saber 11 preparation.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(questions.router)
app.include_router(practice.router)
app.include_router(attempts.router)
app.include_router(analytics.router)
app.include_router(recommendations.router)
app.include_router(tutor.router)
app.include_router(search.router)
