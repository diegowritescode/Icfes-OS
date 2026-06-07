from __future__ import annotations

from io import StringIO

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src import models  # noqa: F401
from src.core.database import Base
from src.repositories.documents import DocumentRepository
from src.schemas.document import DocumentCreate
from src.services.candidate_service import CandidateService
from src.services.ingestion.csv_importer import import_csv_stream
from src.services.ingestion.jsonl_importer import import_jsonl_stream


@pytest.fixture()
def db() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def test_jsonl_import_accepts_missing_optional_taxonomy(db: Session) -> None:
    stream = StringIO(
        """
{"id":"real-001","year":2024,"area":"matematicas","statement":"Cuanto es 2 + 2?","option_a":"3","option_b":"4","option_c":"5","option_d":"6","correct_answer":"B","explanation":"2 + 2 = 4"}
""".strip()
    )

    result = import_jsonl_stream(db, stream, filename="real.jsonl")

    assert result.imported_questions == 1
    assert result.skipped_questions == 0
    assert result.errors == []


def test_jsonl_import_reports_row_errors(db: Session) -> None:
    stream = StringIO(
        """
{"id":"bad-001","year":2024,"area":"matematicas","statement":"Incompleta","option_a":"A","correct_answer":"Z"}
""".strip()
    )

    result = import_jsonl_stream(db, stream, filename="bad.jsonl")

    assert result.imported_questions == 0
    assert result.skipped_questions == 1
    assert "missing required fields" in result.errors[0]


def test_csv_import_reports_row_errors_and_imports_valid_rows(db: Session) -> None:
    stream = StringIO(
        "\n".join(
            [
                "id,year,area,subarea,topic,subtopic,question_number,statement,option_a,option_b,option_c,option_d,correct_answer,explanation,source_file",
                "csv-001,2024,ciencias_naturales,quimica,enlaces_quimicos,,1,Que se forma al transferir electrones?,atomos neutros,iones,moleculas sin enlace,isotopos,B,Se forman iones,real.csv",
                "csv-002,2024,matematicas,,,,2,Pregunta incompleta,uno,dos,,,A,,real.csv",
            ]
        )
    )

    result = import_csv_stream(db, stream, filename="real.csv")

    assert result.imported_questions == 1
    assert result.skipped_questions == 1
    assert "missing required fields" in result.errors[0]


def test_candidate_approval_creates_question(db: Session) -> None:
    document = DocumentRepository(db).create(
        DocumentCreate(filename="paper.pdf", source_type="pdf", metadata_json={})
    )
    candidate = DocumentRepository(db).create_candidate(
        document_id=document.id,
        page=2,
        raw_text="1. Cuanto es 2 + 2?\nA. 3\nB. 4\nC. 5\nD. 6",
        statement="Cuanto es 2 + 2?",
        option_a="3",
        option_b="4",
        option_c="5",
        option_d="6",
        correct_answer="B",
        explanation="2 + 2 = 4",
        year=2024,
        area="matematicas",
        subarea="aritmetica",
        topic="aritmetica",
        subtopic="suma",
        status="pending",
    )
    db.commit()

    question = CandidateService(db).approve(candidate)

    assert question.id is not None
    assert question.statement == "Cuanto es 2 + 2?"
    assert question.correct_answer == "B"
    assert question.classification is not None
    assert question.classification.topic == "aritmetica"
    assert DocumentRepository(db).get_candidate(candidate.id).status == "approved"
