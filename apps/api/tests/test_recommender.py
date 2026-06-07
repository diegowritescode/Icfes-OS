from __future__ import annotations

from src.schemas.study import DailyPlanRequest


def test_daily_plan_request_bounds() -> None:
    request = DailyPlanRequest(available_minutes=120, max_blocks=3, preference="mixto")

    assert request.available_minutes == 120
    assert request.max_blocks == 3
    assert request.preference == "mixto"
