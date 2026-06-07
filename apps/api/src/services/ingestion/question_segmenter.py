from __future__ import annotations


def build_review_items_from_text(pages: list[dict[str, str]]) -> list[dict[str, object]]:
    """Create simple review items for imperfect PDF extraction.

    Phase 1 intentionally does not pretend that arbitrary PDFs can be segmented
    perfectly. It stores chunks that can later be reviewed and converted manually.
    """
    return [
        {"page": page.get("page"), "raw_text": page.get("text", ""), "status": "needs_review"}
        for page in pages
        if page.get("text", "").strip()
    ]
