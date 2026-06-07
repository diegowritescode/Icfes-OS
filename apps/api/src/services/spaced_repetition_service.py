from __future__ import annotations

from datetime import datetime, timedelta, timezone


def calculate_review_after(*, is_correct: bool, confidence: int, now: datetime | None = None) -> datetime:
    current = now or datetime.now(timezone.utc)
    if not is_correct:
        return current + timedelta(days=1)
    if confidence <= 3:
        return current + timedelta(days=2)
    return current + timedelta(days=7)
