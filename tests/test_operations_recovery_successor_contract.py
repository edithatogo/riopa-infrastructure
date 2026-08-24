import json
from pathlib import Path

from riopa_provenance.governance import (
    reconcile_withdrawal_targets,
    record_supersession,
    record_withdrawal,
)
from riopa_provenance.publication import validate_correction_package

ROOT = Path(__file__).resolve().parents[1]


def test_contract_declares_append_only_recovery_successor_states() -> None:
    record = json.loads(
        (ROOT / "docs/operations-recovery-successor-contract-20260824.json").read_text()
    )
    machine = record["state_machine"]
    assert "verified" in machine["states"]
    assert {"superseded", "withdrawn", "quarantined"} <= set(machine["terminal_states"])
    assert any(
        transition["from"] == "replicated"
        and transition["to"] == "verified"
        and "restore_check" in transition["evidence"]
        for transition in machine["transitions"]
    )
    assert any("Never overwrite" in rule for rule in record["fail_closed_rules"])


def test_supersession_and_withdrawal_preserve_predecessor_and_reconcile_targets() -> None:
    predecessor = {
        "decision_id": "evidence-old",
        "outcome": "allow",
        "scope": ["github", "zenodo"],
    }
    superseded = record_supersession(
        predecessor, successor_id="evidence-new", reason="corrected digest"
    )
    assert superseded["supersedes_id"] == "evidence-old"
    assert superseded["decision_id"] == "evidence-new"

    withdrawn = record_withdrawal(
        predecessor,
        withdrawal_id="withdraw-old",
        reason="rights status changed",
        scope=["zenodo"],
    )
    assert withdrawn["withdrawal_reference"] == "evidence-old"
    assert reconcile_withdrawal_targets(withdrawn, ["github", "zenodo"]) == (
        ("github",),
        ("zenodo",),
    )


def test_correction_validator_rejects_in_place_mutation() -> None:
    package = {
        "evidence_id": "correction-1",
        "status": "candidate",
        "correction_policy": {
            "immutable_predecessors": True,
            "successor_required": True,
            "silent_mutation_forbidden": True,
            "notification_targets": ["github"],
        },
        "bounded_example": {
            "predecessor": {"doi": "10.5281/example.old", "sha256": "a" * 64},
            "successor": {"doi": "10.5281/example.new", "sha256": "b" * 64},
        },
        "required_correction_record_fields": ["predecessor", "successor", "reason"],
        "qualification": "repository-only",
    }
    assert validate_correction_package(package) == ()
    package["bounded_example"]["successor"]["sha256"] = "a" * 64
    assert any("successor digest" in error for error in validate_correction_package(package))


def test_operations_plan_closes_recovery_contracts_without_claiming_execution() -> None:
    plan = (ROOT / "conductor/tracks/operations_preservation_sre_20260719/plan.md").read_text()
    assert "[x] 3.2 Implement the repository recovery-successor" in plan
    assert "[x] 3.3 Define and validate restore/disaster-recovery" in plan
    assert "production-representative execution remains pending" in plan
