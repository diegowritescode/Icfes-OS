from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.document import Document
from src.schemas.document import DocumentCreate


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[Document]:
        stmt = select(Document).order_by(Document.imported_at.desc())
        return list(self.db.scalars(stmt).all())

    def create(self, payload: DocumentCreate) -> Document:
        document = Document(**payload.model_dump())
        self.db.add(document)
        self.db.flush()
        return document

    def get(self, document_id: int) -> Document | None:
        return self.db.get(Document, document_id)
