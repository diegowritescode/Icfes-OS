from __future__ import annotations

from pathlib import Path

import fitz
from sqlalchemy.orm import Session

from src.repositories.documents import DocumentRepository
from src.schemas.document import DocumentCreate
from src.services.ingestion.question_segmenter import segment_questions_from_pages


def extract_pdf_text(db: Session, path: Path, *, filename: str) -> dict[str, object]:
    doc = fitz.open(path)
    pages = [{"page": index + 1, "text": page.get_text("text")} for index, page in enumerate(doc)]
    documents = DocumentRepository(db)
    candidates = segment_questions_from_pages(pages)
    document = documents.create(
        DocumentCreate(
            filename=filename,
            source_type="pdf",
            metadata_json={
                "pages": len(pages),
                "candidate_count": len(candidates),
                "status": "text_extracted_review_required",
            },
        )
    )
    for page in pages:
        documents.add_page(
            document_id=document.id,
            page=int(page["page"]),
            text=str(page["text"]),
        )
    for candidate in candidates:
        documents.create_candidate(document_id=document.id, **candidate)
    db.commit()
    db.refresh(document)
    return {
        "document_id": document.id,
        "filename": filename,
        "pages": len(pages),
        "candidate_count": len(candidates),
        "review_required": True,
        "extracted_preview": pages[:3],
    }
