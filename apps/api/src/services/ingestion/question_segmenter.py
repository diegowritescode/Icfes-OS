from __future__ import annotations

import re

QUESTION_START_RE = re.compile(
    r"(?im)^\s*(?:pregunta\s*)?(\d{1,3})[\).\-\s]+",
)
OPTION_RE = re.compile(
    r"(?ims)(?:^|\n)\s*([A-D])[\).\:\-]\s+(.*?)(?=(?:\n\s*[A-D][\).\:\-]\s+)|\Z)",
)


def _clean_text(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text.strip())


def _chunks_from_page(text: str) -> list[str]:
    matches = list(QUESTION_START_RE.finditer(text))
    if not matches:
        return [text]

    chunks: list[str] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        chunks.append(text[start:end])
    return chunks


def _parse_candidate(raw_text: str) -> dict[str, object]:
    cleaned = _clean_text(raw_text)
    options = {letter: value.strip() for letter, value in OPTION_RE.findall(cleaned)}
    first_option_position = None
    first_option_match = OPTION_RE.search(cleaned)
    if first_option_match:
        first_option_position = first_option_match.start()
    statement = cleaned[:first_option_position].strip() if first_option_position else cleaned[:1200]
    statement = QUESTION_START_RE.sub("", statement, count=1).strip()
    return {
        "raw_text": cleaned,
        "statement": statement or None,
        "option_a": options.get("A"),
        "option_b": options.get("B"),
        "option_c": options.get("C"),
        "option_d": options.get("D"),
        "correct_answer": None,
        "explanation": None,
        "status": "pending",
    }


def segment_questions_from_pages(pages: list[dict[str, object]]) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    for page in pages:
        page_number = int(page.get("page") or 0)
        text = str(page.get("text") or "")
        if not text.strip():
            continue
        for chunk in _chunks_from_page(text):
            parsed = _parse_candidate(chunk)
            if not parsed["raw_text"]:
                continue
            parsed["page"] = page_number
            candidates.append(parsed)
    return candidates


def build_review_items_from_text(pages: list[dict[str, str]]) -> list[dict[str, object]]:
    return segment_questions_from_pages([dict(page) for page in pages])
