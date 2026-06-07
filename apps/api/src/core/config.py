from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ICFES OS API"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://icfes:icfes@localhost:5432/icfes_os"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-haiku-latest"

    ai_provider: str = "openai"
    enable_embeddings: bool = False
    sample_questions_path: str = "/workspace/data/samples/questions.sample.jsonl"

    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def sample_path(self) -> Path:
        return Path(self.sample_questions_path)

    @property
    def has_ai_key(self) -> bool:
        return bool(self.openai_api_key or self.anthropic_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
