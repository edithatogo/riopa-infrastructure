import json
from pathlib import Path


def test_v1_readiness_baseline_is_fail_closed() -> None:
    record = json.loads(Path("docs/v1-release-readiness-baseline-20260801.json").read_text())
    assert record["release"] == "1.0.0"
    assert record["status"] == "blocked"
    assert record["promotion_ready"] is False
    assert len(record["blocking_gates"]) >= 5
    assert record["limitations"]
