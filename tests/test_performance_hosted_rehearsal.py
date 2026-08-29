import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_hosted_rehearsal_record_is_bounded_and_content_bound() -> None:
    record = json.loads((ROOT / "docs/performance-hosted-rehearsal-20260829.json").read_text())
    assert record["schema"] == "riopa.performance-hosted-rehearsal.v1"
    assert len(record["candidate_revision"]) == 40
    assert len(record["observations"]) == 2
    assert all(observation["status"] == "passed" for observation in record["observations"])
    assert record["qualification"]["promotion_allowed"] is False
    assert any("national-scale" in claim for claim in record["non_claims"])
