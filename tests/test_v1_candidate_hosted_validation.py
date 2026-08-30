import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = "26bc0b49bcd84f409bf24b527e1049fd396c94a6"


def test_candidate_hosted_validation_is_exact_and_fail_closed() -> None:
    record = json.loads(
        (ROOT / "docs/v1-candidate-hosted-validation-20260830.json").read_text(encoding="utf-8")
    )
    assert record["candidate_revision"] == CANDIDATE
    beta = record["beta_campaign"]
    assert beta["status"] == "passed"
    assert beta["receipt_schema_validated"] is True
    assert beta["source_revisions"] == [CANDIDATE]
    assert beta["observation_count"] == 1
    assert beta["operational_cycles"] == 1
    assert beta["duration_status"] == "pending-duration"
    assert beta["operational_cycles_status"] == "pending-cycles"
    assert beta["elapsed_seconds"] < beta["required_elapsed_days"] * 86_400
    assert beta["operational_cycles"] < beta["required_operational_cycles"]
    assert len(beta["chain_head_sha256"]) == 64
    assert len(beta["receipt_sha256s"]) == 1
    assert all(len(digest) == 64 for digest in beta["receipt_sha256s"])
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
    scheduled = record["scheduled_automation"]
    assert scheduled["candidate_revision"] == CANDIDATE
    assert scheduled["campaign_id"] == record["beta_campaign"]["campaign_id"]
    assert scheduled["qualification_epoch"] == record["beta_campaign"]["qualification_epoch"]
    assert scheduled["status"] == "default-pin-verified-manual-schedule-event-pending"
    assert scheduled["verification_run_id"] == "33289129127"
    assert record["blockers"]
    assert any("not independent external" in item for item in record["non_claims"])


def test_campaign_status_points_to_the_fresh_candidate_segment() -> None:
    status = json.loads(
        (ROOT / "docs/evidence-campaign-status-20260821.json").read_text(encoding="utf-8")
    )
    assert status["source_revision"] == CANDIDATE
    gate = status["rc_gate"]
    elapsed_gate = status["elapsed_gate"]
    assert elapsed_gate["campaign_id"] == "operational-beta-20260830-26bc0b4"
    assert elapsed_gate["qualification_epoch"] == "beta-epoch-20260830-26bc0b4"
    assert elapsed_gate["required_days"] == 90
    assert elapsed_gate["required_operational_cycles"] == 3
    beta = [
        item
        for item in status["observations"]
        if item.get("campaign_id") == elapsed_gate["campaign_id"]
    ]
    assert [item["run_id"] for item in beta] == ["33289129127"]
    assert all(item["revision"] == CANDIDATE for item in beta)
    assert beta[0]["classification"] == "qualifying-beta-observation"
    assert gate["campaign_id"] == "operational-rc-20260830-26bc0b4"
    assert gate["qualification_epoch"] == "rc-epoch-20260830-26bc0b4"
    assert gate["candidate_revision"] == CANDIDATE
    assert gate["required_days"] == 30
    assert gate["status"] == "pending-duration"
    current = [
        item for item in status["observations"] if item.get("campaign_id") == gate["campaign_id"]
    ]
    assert len(current) == 1
    assert current[0]["run_id"] == "33289130323"
    assert current[0]["candidate_revision"] == CANDIDATE
    assert current[0]["classification"] == "qualifying-rc-observation"
