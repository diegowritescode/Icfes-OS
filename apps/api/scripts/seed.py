from __future__ import annotations

import argparse
from pathlib import Path

from src.core.config import settings
from src.core.database import SessionLocal
from src.services.ingestion.jsonl_importer import import_jsonl_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed ICFES OS sample questions.")
    parser.add_argument(
        "path",
        nargs="?",
        default=str(settings.sample_path),
        help="Path to a questions JSONL file.",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        fallback = Path(__file__).resolve().parents[3] / "data/samples/questions.sample.jsonl"
        path = fallback if fallback.exists() else path
    if not path.exists():
        raise SystemExit(f"Seed file not found: {path}")

    with SessionLocal() as db:
        result = import_jsonl_path(db, path)
        print(
            f"Imported {result.imported_questions} questions from {path.name}; "
            f"skipped {result.skipped_questions}."
        )
        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"- {error}")


if __name__ == "__main__":
    main()
