from __future__ import annotations

import argparse
from pathlib import Path

from src.core.database import SessionLocal
from src.services.ingestion.jsonl_importer import import_jsonl_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Import questions from JSONL.")
    parser.add_argument("path", help="Path to JSONL file.")
    args = parser.parse_args()

    with SessionLocal() as db:
        result = import_jsonl_path(db, Path(args.path))
        print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
