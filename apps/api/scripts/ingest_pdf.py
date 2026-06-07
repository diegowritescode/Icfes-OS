from __future__ import annotations

import argparse
from pathlib import Path

from src.core.database import SessionLocal
from src.services.ingestion.pdf_extractor import extract_pdf_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text from a PDF for review.")
    parser.add_argument("path", help="Path to PDF file.")
    args = parser.parse_args()
    path = Path(args.path)

    with SessionLocal() as db:
        result = extract_pdf_text(db, path, filename=path.name)
        print(result)


if __name__ == "__main__":
    main()
