from __future__ import annotations

import json

from openai import OpenAI

from src.core.config import settings
from src.services.ai.base import AIProvider, ProviderUnavailable


class OpenAIProvider(AIProvider):
    @property
    def available(self) -> bool:
        return bool(settings.openai_api_key)

    def _client(self) -> OpenAI:
        if not settings.openai_api_key:
            raise ProviderUnavailable("OPENAI_API_KEY is not configured.")
        return OpenAI(api_key=settings.openai_api_key)

    def classify(self, prompt: str, question_text: str) -> dict:
        client = self._client()
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": question_text},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    def explain(self, prompt: str) -> str:
        client = self._client()
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    def embed(self, texts: list[str]) -> list[list[float]]:
        client = self._client()
        response = client.embeddings.create(model=settings.openai_embedding_model, input=texts)
        return [item.embedding for item in response.data]
