from __future__ import annotations

from pathlib import Path
from typing import TextIO

import pandas as pd
from sqlalchemy.orm import Session

from src.repositories.documents import DocumentRepository
from src.repositories.questions import QuestionRepository
from src.schemas.document import DocumentCreate, ImportResult
from src.services.ingestion.jsonl_importer import _question_from_row


def import_csv_stream(db: Session, stream: TextIO, *, filename: str) -> ImportResult:
    document = DocumentRepository(db).create(
        DocumentCreate(filename=filename, source_type="csv", metadata_json={"importer": "csv"})
    )
    frame = pd.read_csv(stream)
    questions = QuestionRepository(db)
    imported = 0
    skipped = 0
    errors: list[str] = []

    for index, raw in frame.fillna("").iterrows():
        row = dict(raw)
        try:
            external_id = row.get("id") or row.get("external_id")
            if external_id and questions.get_by_external_id(str(external_id)):
                skipped += 1
                continue
            questions.create(_question_from_row(row, document.id))
            imported += 1
        except Exception as exc:  # noqa: BLE001
            skipped += 1
            errors.append(f"row {index + 1}: {exc}")

    db.commit()
    db.refresh(document)
    return ImportResult(document=document, imported_questions=imported, skipped_questions=skipped, errors=errors)


def import_csv_path(db: Session, path: Path) -> ImportResult:
    with path.open("r", encoding="utf-8") as stream:
        return import_csv_stream(db, stream, filename=path.name)
