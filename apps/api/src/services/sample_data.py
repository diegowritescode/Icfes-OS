from __future__ import annotations

from pathlib import Path

SAMPLE_FILENAME = "questions.sample.jsonl"


def sample_questions_candidates(explicit_path: Path | None = None) -> list[Path]:
    candidates: list[Path] = []
    if explicit_path is not None:
        candidates.append(explicit_path)

    candidates.extend(
        [
            Path("/app/data/samples") / SAMPLE_FILENAME,
            Path("/workspace/data/samples") / SAMPLE_FILENAME,
        ]
    )

    current = Path(__file__).resolve()
    for parent in current.parents:
        candidates.append(parent / "data/samples" / SAMPLE_FILENAME)

    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key not in seen:
            seen.add(key)
            unique.append(candidate)
    return unique


def resolve_sample_questions_path(explicit_path: Path | None = None) -> Path:
    candidates = sample_questions_candidates(explicit_path)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]
