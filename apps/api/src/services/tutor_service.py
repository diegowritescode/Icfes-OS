from __future__ import annotations

from sqlalchemy.orm import Session

from src.core.config import settings
from src.models.question import Question
from src.services.ai.anthropic_provider import AnthropicProvider
from src.services.ai.base import AIProvider
from src.services.ai.openai_provider import OpenAIProvider
from src.services.ai.prompts import TUTOR_PROMPT


class TutorService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _provider(self) -> AIProvider | None:
        providers: list[AIProvider]
        if settings.ai_provider == "anthropic":
            providers = [AnthropicProvider(), OpenAIProvider()]
        else:
            providers = [OpenAIProvider(), AnthropicProvider()]
        return next((provider for provider in providers if provider.available), None)

    def explain_error(
        self,
        *,
        question: Question,
        user_answer: str,
        error_type: str | None,
    ) -> dict[str, str | bool]:
        answer_text = {
            "A": question.option_a,
            "B": question.option_b,
            "C": question.option_c,
            "D": question.option_d,
        }
        prompt = (
            TUTOR_PROMPT.replace("{{question}}", question.statement)
            .replace("{{correct_answer}}", f"{question.correct_answer}. {answer_text[question.correct_answer]}")
            .replace("{{user_answer}}", f"{user_answer}. {answer_text.get(user_answer, '')}")
            .replace("{{error_type}}", error_type or "sin_tipo")
        )
        provider = self._provider()
        if provider:
            try:
                return {"used_ai": True, "explanation": provider.explain(prompt)}
            except Exception:
                pass

        fallback = (
            f"La respuesta correcta es {question.correct_answer} porque: "
            f"{question.explanation or 'la clave coincide con el concepto evaluado en el enunciado.'} "
            f"Tu respuesta fue {user_answer}. Revisa si el error fue de concepto, lectura del enunciado "
            "o descarte de distractores. Regla mental: antes de calcular o elegir, subraya qué pide exactamente "
            "la pregunta y elimina opciones que contradicen ese dato."
        )
        return {"used_ai": False, "explanation": fallback}
