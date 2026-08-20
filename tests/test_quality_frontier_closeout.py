import json
from pathlib import Path


def test_quality_frontier_closeout_is_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    record = json.loads((root / "docs/quality-frontier-closeout-20260821.json").read_text())
    assert record["issue"] == 147
    assert all(item["status"] == "closed" for item in record["subissues"].values())
    assert "accountable release-authority decision" in record["remaining_boundaries"]
    assert "stable-v1" in record["release_claim"]
