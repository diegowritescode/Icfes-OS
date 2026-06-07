from __future__ import annotations

from pathlib import Path

import fitz
from sqlalchemy.orm import Session

from src.repositories.documents import DocumentRepository
from src.schemas.document import DocumentCreate


def extract_pdf_text(db: Session, path: Path, *, filename: str) -> dict[str, object]:
    doc = fitz.open(path)
    pages = [{"page": index + 1, "text": page.get_text("text")} for index, page in enumerate(doc)]
    document = DocumentRepository(db).create(
        DocumentCreate(
            filename=filename,
            source_type="pdf",
            metadata_json={"pages": len(pages), "status": "text_extracted_review_required"},
        )
    )
    db.commit()
    db.refresh(document)
    return {
        "document_id": document.id,
        "filename": filename,
        "pages": len(pages),
        "review_required": True,
        "extracted_preview": pages[:3],
    }
