from __future__ import annotations

from io import TextIOWrapper
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import get_db
from src.repositories.documents import DocumentRepository
from src.schemas.document import (
    DocumentDetail,
    DocumentPageRead,
    DocumentRead,
    ImportResult,
    QuestionCandidateRead,
    QuestionCandidateUpdate,
)
from src.schemas.question import QuestionRead
from src.services.candidate_service import CandidateApprovalError, CandidateService
from src.services.ingestion.csv_importer import import_csv_stream
from src.services.ingestion.jsonl_importer import import_jsonl_path, import_jsonl_stream
from src.services.ingestion.pdf_extractor import extract_pdf_text
from src.services.sample_data import resolve_sample_questions_path

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentRead])
def list_documents(db: Session = Depends(get_db)) -> list:
    return DocumentRepository(db).list()


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = DocumentRepository(db).get_detail(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    document.pages.sort(key=lambda item: item.page)
    document.candidates.sort(key=lambda item: (item.page or 0, item.id))
    return document


@router.get("/{document_id}/pages", response_model=list[DocumentPageRead])
def list_document_pages(document_id: int, db: Session = Depends(get_db)):
    document = DocumentRepository(db).get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentRepository(db).list_pages(document_id)


@router.get("/{document_id}/candidates", response_model=list[QuestionCandidateRead])
def list_document_candidates(
    document_id: int,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    document = DocumentRepository(db).get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentRepository(db).list_candidates(document_id, status=status)


@router.post("/import-jsonl", response_model=ImportResult)
def import_jsonl(file: UploadFile = File(...), db: Session = Depends(get_db)) -> ImportResult:
    stream = TextIOWrapper(file.file, encoding="utf-8")
    return import_jsonl_stream(db, stream, filename=file.filename or "uploaded.jsonl")


@router.post("/import-csv", response_model=ImportResult)
def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)) -> ImportResult:
    stream = TextIOWrapper(file.file, encoding="utf-8")
    return import_csv_stream(db, stream, filename=file.filename or "uploaded.csv")


@router.post("/import-sample", response_model=ImportResult)
def import_sample(db: Session = Depends(get_db)) -> ImportResult:
    path = resolve_sample_questions_path(settings.sample_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Sample questions file not found.")
    try:
        return import_jsonl_path(db, path)
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read sample questions from {path}: {exc}",
        ) from exc


@router.post("/extract-pdf")
def extract_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict[str, object]:
    suffix = Path(file.filename or "upload.pdf").suffix or ".pdf"
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
        tmp_path = Path(tmp.name)
    try:
        return extract_pdf_text(db, tmp_path, filename=file.filename or "uploaded.pdf")
    finally:
        tmp_path.unlink(missing_ok=True)


@router.patch("/candidates/{candidate_id}", response_model=QuestionCandidateRead)
def update_candidate(
    candidate_id: int,
    payload: QuestionCandidateUpdate,
    db: Session = Depends(get_db),
):
    service = CandidateService(db)
    candidate = service.get(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return service.update(candidate, payload)


@router.post("/candidates/{candidate_id}/approve", response_model=QuestionRead)
def approve_candidate(candidate_id: int, db: Session = Depends(get_db)):
    service = CandidateService(db)
    candidate = service.get(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    try:
        return service.approve(candidate)
    except CandidateApprovalError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/candidates/{candidate_id}/reject", response_model=QuestionCandidateRead)
def reject_candidate(candidate_id: int, db: Session = Depends(get_db)):
    service = CandidateService(db)
    candidate = service.get(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return service.reject(candidate)
