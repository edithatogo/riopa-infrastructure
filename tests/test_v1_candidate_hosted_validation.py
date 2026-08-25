import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = "26bc0b49bcd84f409bf24b527e1049fd396c94a6"


def test_candidate_hosted_validation_is_exact_and_fail_closed() -> None:
    record = json.loads(
        (ROOT / "docs/v1-candidate-hosted-validation-20260825.json").read_text(encoding="utf-8")
    )
    assert record["candidate_revision"] == CANDIDATE
    rc = record["rc_campaign"]
    assert rc["status"] == "passed"
    assert rc["candidate_checkout_verified"] is True
    assert rc["receipt_schema_validated"] is True
    assert rc["source_revisions"] == [CANDIDATE]
    assert rc["observation_count"] == 1
    assert rc["duration_status"] == "pending-duration"
    assert rc["elapsed_seconds"] < rc["required_elapsed_days"] * 86_400
    assert len(rc["chain_head_sha256"]) == 64
    assert len(rc["receipt_sha256"]) == 64
    assert {item["lane"] for item in record["candidate_workflows"]} == {
        "agent-clean-room",
        "agent-user-workflows",
    }
    assert all(
        item["status"] == "passed" and item["source_revision"] == CANDIDATE
        for item in record["candidate_workflows"]
    )
    assert record["blockers"]
    assert any("not independent external" in item for item in record["non_claims"])


def test_campaign_status_points_to_the_fresh_candidate_segment() -> None:
    status = json.loads(
        (ROOT / "docs/evidence-campaign-status-20260821.json").read_text(encoding="utf-8")
    )
    assert status["source_revision"] == CANDIDATE
    gate = status["rc_gate"]
    assert gate["campaign_id"] == "operational-rc-20260825-26bc0b4"
    assert gate["qualification_epoch"] == "rc-epoch-20260825-26bc0b4"
    assert gate["candidate_revision"] == CANDIDATE
    assert gate["required_days"] == 30
    assert gate["status"] == "pending-duration"
    current = [
        item for item in status["observations"] if item.get("campaign_id") == gate["campaign_id"]
    ]
    assert len(current) == 1
    assert current[0]["run_id"] == "32856370956"
    assert current[0]["candidate_revision"] == CANDIDATE
