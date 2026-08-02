import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.record_hosted_evidence import LANES, run_lane

ROOT = Path(__file__).resolve().parents[1]


def test_hosted_receipt_is_content_bound_and_fail_closed(tmp_path: Path) -> None:
    receipt = run_lane("operational-observation", tmp_path)
    schema = json.loads((ROOT / "schemas/hosted-evidence.schema.json").read_text())
    Draft202012Validator(schema).validate(receipt)
    log = (tmp_path / receipt["log"]["path"]).read_bytes()
    assert receipt["log"]["sha256"] == hashlib.sha256(log).hexdigest()
    assert receipt["classification"] == "hosted-technical-preview-drill"
    assert receipt["campaign_id"]
    assert receipt["qualification_epoch"]
    assert receipt["operational_cycle_id"]
    assert len(receipt["non_claims"]) >= 4


def test_hosted_lanes_are_fixed_not_arbitrary_commands() -> None:
    assert set(LANES) == {
        "recovery-rollback",
        "agent-clean-room",
        "scale-smoke",
        "operational-observation",
        "rc-soak-observation",
    }


def test_recorded_hosted_recovery_receipt_is_bound_to_successful_run() -> None:
    evidence = json.loads((ROOT / "docs/hosted-recovery-execution-20260802.json").read_text())
    receipt = evidence["receipt"]
    schema = json.loads((ROOT / "schemas/hosted-evidence.schema.json").read_text())
    Draft202012Validator(schema).validate(receipt)
    assert receipt["status"] == "passed"
    assert receipt["host"]["provider"] == "github-actions"
    assert evidence["gate_disposition"]["production_disaster_recovery"] == "pending"


def test_hosted_batch_records_all_bounded_lanes_without_overclaiming() -> None:
    batch = json.loads((ROOT / "docs/hosted-evidence-batch-20260802.json").read_text())
    observations = {item["lane"]: item for item in batch["observations"]}
    assert set(observations) == {
        "agent-clean-room",
        "scale-smoke",
        "operational-observation",
        "rc-soak-observation",
    }
    assert all(item["status"] == "passed" for item in observations.values())
    assert len({item["run_id"] for item in observations.values()}) == 4
    assert batch["disposition"]["rc_soak"] == "one-observation-duration-pending"
