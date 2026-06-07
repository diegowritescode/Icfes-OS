from __future__ import annotations

from fastapi import APIRouter

from src.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
        "ai_configured": settings.has_ai_key,
        "embeddings_enabled": settings.enable_embeddings and bool(settings.openai_api_key),
    }
