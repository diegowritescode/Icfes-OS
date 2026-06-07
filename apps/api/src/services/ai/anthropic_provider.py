from __future__ import annotations

import json

from anthropic import Anthropic

from src.core.config import settings
from src.services.ai.base import AIProvider, ProviderUnavailable


class AnthropicProvider(AIProvider):
    @property
    def available(self) -> bool:
        return bool(settings.anthropic_api_key)

    def _client(self) -> Anthropic:
        if not settings.anthropic_api_key:
            raise ProviderUnavailable("ANTHROPIC_API_KEY is not configured.")
        return Anthropic(api_key=settings.anthropic_api_key)

    def classify(self, prompt: str, question_text: str) -> dict:
        client = self._client()
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=700,
            temperature=0,
            system=prompt,
            messages=[{"role": "user", "content": question_text}],
        )
        text = "".join(block.text for block in response.content if hasattr(block, "text"))
        return json.loads(text)

    def explain(self, prompt: str) -> str:
        client = self._client()
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=900,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if hasattr(block, "text"))
