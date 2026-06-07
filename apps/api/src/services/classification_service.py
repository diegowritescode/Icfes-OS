from __future__ import annotations

from sqlalchemy.orm import Session

from src.core.config import settings
from src.models.question import Question
from src.repositories.questions import QuestionRepository
from src.schemas.classification import ClassificationUpsert
from src.services.ai.anthropic_provider import AnthropicProvider
from src.services.ai.base import AIProvider
from src.services.ai.openai_provider import OpenAIProvider
from src.services.ai.prompts import CLASSIFICATION_PROMPT
from src.services.taxonomy import infer_topic


class ClassificationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = QuestionRepository(db)

    def _provider(self) -> AIProvider | None:
        providers: list[AIProvider]
        if settings.ai_provider == "anthropic":
            providers = [AnthropicProvider(), OpenAIProvider()]
        else:
            providers = [OpenAIProvider(), AnthropicProvider()]
        return next((provider for provider in providers if provider.available), None)

    def classify_question(self, question: Question) -> ClassificationUpsert:
        question_text = "\n".join(
            [
                question.statement,
                f"A. {question.option_a}",
                f"B. {question.option_b}",
                f"C. {question.option_c}",
                f"D. {question.option_d}",
            ]
        )
        provider = self._provider()
        if provider:
            try:
                raw = provider.classify(CLASSIFICATION_PROMPT, question_text)
                return ClassificationUpsert(
                    area=raw.get("area") or question.area,
                    subarea=raw.get("subarea"),
                    topic=raw.get("topic") or infer_topic(question.area, question_text),
                    subtopic=raw.get("subtopic"),
                    competence=raw.get("competence"),
                    skill=raw.get("skill"),
                    difficulty=int(raw.get("difficulty") or 3),
                    requires_formula=bool(raw.get("requires_formula") or False),
                    requires_graph=bool(raw.get("requires_graph") or False),
                    requires_colombia_context=bool(raw.get("requires_colombia_context") or False),
                    concepts=raw.get("concepts") or [],
                    keywords=raw.get("keywords") or [],
                    likely_error_types=raw.get("likely_error_types") or [],
                    confidence=float(raw.get("confidence") or 0.5),
                    classified_by=settings.ai_provider,
                )
            except Exception:
                pass
        return self.heuristic_classification(question, question_text)

    def heuristic_classification(self, question: Question, question_text: str | None = None) -> ClassificationUpsert:
        text = question_text or f"{question.statement} {question.explanation or ''}"
        topic = infer_topic(question.area, text)
        subarea = None
        if question.area == "ciencias_naturales":
            if topic in {"celula", "adn_genes_herencia", "ecosistemas", "fotosintesis_respiracion"}:
                subarea = "biologia"
            elif topic in {
                "atomos_y_moleculas",
                "tabla_periodica_basica",
                "enlaces_quimicos",
                "mezclas_y_soluciones",
                "cambios_fisicos_y_quimicos",
            }:
                subarea = "quimica"
            elif topic in {"fuerza_y_movimiento", "energia", "calor_temperatura", "electricidad_basica"}:
                subarea = "fisica"
            else:
                subarea = "indagacion"
        elif question.area == "matematicas":
            subarea = "razonamiento_cuantitativo"
        elif question.area == "sociales_ciudadanas":
            subarea = "ciudadania"
        elif question.area == "ingles":
            subarea = "comprension_lectora"
        elif question.area == "lectura_critica":
            subarea = "inferencia"

        return ClassificationUpsert(
            area=question.area,
            subarea=subarea,
            topic=topic,
            competence="clasificacion_inicial",
            skill="resolver_con_lectura_y_concepto_base",
            difficulty=3,
            requires_formula=question.area == "matematicas",
            requires_graph="grafica" in text.lower() or "tabla" in text.lower(),
            requires_colombia_context=question.area == "sociales_ciudadanas",
            concepts=[topic] if topic != "sin_clasificar" else [],
            keywords=[],
            likely_error_types=["no_sabia_concepto", "lectura_apresurada"],
            confidence=0.45,
            classified_by="heuristic_fallback",
        )

    def classify_and_save(self, question: Question):
        classification = self.classify_question(question)
        saved = self.repo.upsert_classification(question.id, classification)
        self.db.commit()
        self.db.refresh(saved)
        return saved
