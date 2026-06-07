from __future__ import annotations

import json

from src.schemas.question import QuestionCreate
from src.services.ingestion.jsonl_importer import _question_from_row


def test_question_from_jsonl_row_accepts_missing_topic() -> None:
    row = json.loads(
        """
        {
          "id": "x1",
          "year": 2024,
          "area": "matematicas",
          "statement": "Calcule el porcentaje de descuento.",
          "option_a": "10",
          "option_b": "20",
          "option_c": "30",
          "option_d": "40",
          "correct_answer": "A"
        }
        """
    )

    question = _question_from_row(row, document_id=1)

    assert isinstance(question, QuestionCreate)
    assert question.classification is not None
    assert question.classification.topic == "porcentajes"
