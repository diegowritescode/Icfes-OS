from __future__ import annotations

from io import TextIOWrapper
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import get_db
from src.repositories.documents import DocumentRepository
from src.schemas.document import DocumentRead, ImportResult
from src.services.ingestion.csv_importer import import_csv_stream
from src.services.ingestion.jsonl_importer import import_jsonl_path, import_jsonl_stream
from src.services.ingestion.pdf_extractor import extract_pdf_text

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentRead])
def list_documents(db: Session = Depends(get_db)) -> list:
    return DocumentRepository(db).list()


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
    path = settings.sample_path
    if not path.exists():
        fallback = Path(__file__).resolve().parents[5] / "data/samples/questions.sample.jsonl"
        path = fallback if fallback.exists() else path
    if not path.exists():
        raise HTTPException(status_code=404, detail="Sample questions file not found.")
    return import_jsonl_path(db, path)


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
