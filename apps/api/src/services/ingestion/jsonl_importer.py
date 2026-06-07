from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TextIO

from sqlalchemy.orm import Session

from src.repositories.documents import DocumentRepository
from src.repositories.questions import QuestionRepository
from src.schemas.classification import ClassificationUpsert
from src.schemas.document import DocumentCreate, ImportResult
from src.schemas.question import QuestionCreate
from src.services.taxonomy import infer_topic

REQUIRED_QUESTION_FIELDS = (
    "area",
    "statement",
    "option_a",
    "option_b",
    "option_c",
    "option_d",
    "correct_answer",
)


def _clean_row(row: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in row.items():
        if value == "":
            cleaned[key] = None
        else:
            cleaned[key] = value
    return cleaned


def _validate_question_row(row: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_QUESTION_FIELDS if not row.get(field)]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")
    answer = str(row.get("correct_answer", "")).strip().upper()
    if answer not in {"A", "B", "C", "D"}:
        raise ValueError("correct_answer must be A, B, C or D")


def _classification_from_row(row: dict[str, Any]) -> ClassificationUpsert:
    area = str(row.get("area") or "ciencias_naturales")
    topic = row.get("topic") or infer_topic(area, " ".join(str(row.get(k, "")) for k in ("statement", "explanation")))
    return ClassificationUpsert(
        area=area,
        subarea=row.get("subarea"),
        topic=topic,
        subtopic=row.get("subtopic"),
        competence=row.get("competence"),
        skill=row.get("skill"),
        difficulty=int(row.get("difficulty") or 3),
        requires_formula=bool(row.get("requires_formula") or False),
        requires_graph=bool(row.get("requires_graph") or False),
        requires_colombia_context=bool(row.get("requires_colombia_context") or False),
        concepts=row.get("concepts") or [],
        keywords=row.get("keywords") or [],
        likely_error_types=row.get("likely_error_types") or [],
        confidence=float(row.get("classification_confidence") or row.get("confidence") or 0.75),
        classified_by=str(row.get("classified_by") or "import"),
    )


def _question_from_row(row: dict[str, Any], document_id: int) -> QuestionCreate:
    return QuestionCreate(
        document_id=document_id,
        external_id=row.get("id") or row.get("external_id"),
        year=row.get("year"),
        area=row.get("area") or "ciencias_naturales",
        question_number=row.get("question_number"),
        statement=row.get("statement") or "",
        option_a=row.get("option_a") or "",
        option_b=row.get("option_b") or "",
        option_c=row.get("option_c") or "",
        option_d=row.get("option_d") or "",
        correct_answer=row.get("correct_answer") or "A",
        explanation=row.get("explanation"),
        source_file=row.get("source_file"),
        page=row.get("page"),
        raw_text=row.get("raw_text"),
        classification=_classification_from_row(row),
    )


def import_jsonl_stream(
    db: Session,
    stream: TextIO,
    *,
    filename: str,
    source_type: str = "jsonl",
) -> ImportResult:
    document = DocumentRepository(db).create(
        DocumentCreate(filename=filename, source_type=source_type, metadata_json={"importer": "jsonl"})
    )
    questions = QuestionRepository(db)
    imported = 0
    skipped = 0
    errors: list[str] = []

    for line_number, line in enumerate(stream, start=1):
        if not line.strip():
            continue
        try:
            row = _clean_row(json.loads(line))
            _validate_question_row(row)
            external_id = row.get("id") or row.get("external_id")
            if external_id and questions.get_by_external_id(str(external_id)):
                skipped += 1
                continue
            questions.create(_question_from_row(row, document.id))
            imported += 1
        except Exception as exc:  # noqa: BLE001 - importer reports malformed rows and continues.
            skipped += 1
            errors.append(f"line {line_number}: {exc}")

    db.commit()
    db.refresh(document)
    return ImportResult(document=document, imported_questions=imported, skipped_questions=skipped, errors=errors)


def import_jsonl_path(db: Session, path: Path) -> ImportResult:
    with path.open("r", encoding="utf-8") as stream:
        return import_jsonl_stream(db, stream, filename=path.name)
