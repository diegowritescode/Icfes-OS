from __future__ import annotations

from sqlalchemy.orm import Session

from src.core.config import settings
from src.models.vector import QuestionEmbedding
from src.services.ai.openai_provider import OpenAIProvider


class EmbeddingsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    @property
    def enabled(self) -> bool:
        return settings.enable_embeddings and bool(settings.openai_api_key)

    def embed_question(self, question_id: int, text: str) -> QuestionEmbedding | None:
        if not self.enabled:
            return None
        vector = OpenAIProvider().embed([text])[0]
        existing = self.db.query(QuestionEmbedding).filter_by(question_id=question_id).first()
        if existing:
            existing.embedding = vector
            existing.embedding_model = settings.openai_embedding_model
            return existing
        embedding = QuestionEmbedding(
            question_id=question_id,
            embedding=vector,
            embedding_model=settings.openai_embedding_model,
        )
        self.db.add(embedding)
        self.db.flush()
        return embedding
