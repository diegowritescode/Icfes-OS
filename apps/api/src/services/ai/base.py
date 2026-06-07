from __future__ import annotations

from abc import ABC, abstractmethod


class ProviderUnavailable(RuntimeError):
    pass


class AIProvider(ABC):
    @property
    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def classify(self, prompt: str, question_text: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def explain(self, prompt: str) -> str:
        raise NotImplementedError

    def embed(self, texts: list[str]) -> list[list[float]]:
        raise ProviderUnavailable("Embeddings are not configured for this provider.")
