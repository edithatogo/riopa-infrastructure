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
        "agent-user-workflows",
        "performance-rehearsal",
        "recovery-rollback",
        "agent-clean-room",
        "scale-smoke",
        "operational-observation",
        "rc-soak-observation",
        "retrospective-replay",
    }


def test_performance_rehearsal_emits_benchmark_artifact(tmp_path: Path) -> None:
    receipt = run_lane("performance-rehearsal", tmp_path)
    assert receipt["status"] == "passed"
    report = json.loads((tmp_path / "benchmark.json").read_text())
    assert report["national"]["classification"] == "projection-not-measurement"


def test_agent_user_workflows_emit_two_bounded_reports(tmp_path: Path) -> None:
    receipt = run_lane("agent-user-workflows", tmp_path)
    assert receipt["status"] == "passed"
    report = json.loads((tmp_path / "user-workflows" / "agent-user-workflows.json").read_text())
    assert [item["status"] for item in report["workflows"]] == ["passed", "passed"]
    assert report["classification"].startswith("owner-authorized-agent")


def test_recorded_hosted_recovery_receipt_is_bound_to_successful_run() -> None:
    evidence = json.loads((ROOT / "docs/hosted-recovery-execution-20260802.json").read_text())
    receipt = evidence["receipt"]
    schema = json.loads((ROOT / "schemas/hosted-evidence.schema.json").read_text())
    Draft202012Validator(schema).validate(receipt)
    assert receipt["status"] == "passed"
    assert receipt["host"]["provider"] == "github-actions"
    assert evidence["gate_disposition"]["production_disaster_recovery"] == "pending"


def test_current_hosted_pipeline_observation_preserves_recovery_gate() -> None:
    evidence = json.loads(
        (ROOT / "docs/hosted-recovery-observation-20260829.json").read_text(encoding="utf-8")
    )
    assert evidence["status"] == "passed"
    assert evidence["lane"] == "publication-linz-pipeline"
    assert evidence["workflow_lane"] == "recovery-rollback"
    assert evidence["source_artifact"].endswith("recovery-rollback-33236847804")
    assert evidence["qualification"]["exit_code"] == 0
    assert evidence["qualification"]["recovery_rollback_execution"] is False
    assert evidence["qualification"]["production_disaster_recovery"] is False
    assert evidence["qualification"]["tests_executed"] == [
        "tests/test_publication.py",
        "tests/test_linz_pipeline.py",
    ]
    assert (
        evidence["qualification"]["preservation_targets"]["huggingface_dataset"]
        == "pending-credential"
    )
    assert evidence["qualification"]["preservation_targets"]["zenodo"] == "pending-credential"
    assert evidence["non_claims"]

    retained = ROOT / "docs/hosted-recovery-observation-20260829-artifact"
    receipt = retained / "recovery-rollback.receipt.json"
    log = retained / "recovery-rollback.log"
    assert evidence["retained_evidence"] == [
        "docs/hosted-recovery-observation-20260829-artifact/recovery-rollback.receipt.json",
        "docs/hosted-recovery-observation-20260829-artifact/recovery-rollback.log",
        "docs/hosted-recovery-observation-20260829-artifact/redundancy-manifest.json",
    ]
    assert receipt.is_file() and log.is_file()
    assert (
        hashlib.sha256(receipt.read_bytes()).hexdigest()
        == "970bfa9c3c2d948e2a1526db06d3ac86e4f3470401a061ee53cca0044c309b17"
    )
    assert hashlib.sha256(log.read_bytes()).hexdigest() == evidence["log_sha256"]


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
