from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.models.document import Document
from src.models.document_page import DocumentPage
from src.models.question_candidate import QuestionCandidate
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

    def get_detail(self, document_id: int) -> Document | None:
        stmt = (
            select(Document)
            .where(Document.id == document_id)
            .options(
                selectinload(Document.pages),
                selectinload(Document.candidates),
            )
        )
        return self.db.scalars(stmt).first()

    def add_page(self, *, document_id: int, page: int, text: str) -> DocumentPage:
        document_page = DocumentPage(document_id=document_id, page=page, text=text)
        self.db.add(document_page)
        self.db.flush()
        return document_page

    def list_pages(self, document_id: int) -> list[DocumentPage]:
        stmt = (
            select(DocumentPage)
            .where(DocumentPage.document_id == document_id)
            .order_by(DocumentPage.page.asc())
        )
        return list(self.db.scalars(stmt).all())

    def create_candidate(self, **data: object) -> QuestionCandidate:
        candidate = QuestionCandidate(**data)
        self.db.add(candidate)
        self.db.flush()
        return candidate

    def get_candidate(self, candidate_id: int) -> QuestionCandidate | None:
        return self.db.get(QuestionCandidate, candidate_id)

    def list_candidates(
        self,
        document_id: int,
        *,
        status: str | None = None,
    ) -> list[QuestionCandidate]:
        stmt = (
            select(QuestionCandidate)
            .where(QuestionCandidate.document_id == document_id)
            .order_by(QuestionCandidate.page.asc().nullslast(), QuestionCandidate.id.asc())
        )
        if status:
            stmt = stmt.where(QuestionCandidate.status == status)
        return list(self.db.scalars(stmt).all())
