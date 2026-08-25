import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/nz-spatial-archive-operations-contract-20260825.json"


def test_operations_contract_binds_implemented_controls_and_negative_tests() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert contract["track_id"] == "nz_spatial_archive_operations_20260719"
    assert contract["promotion_allowed"] is False
    assert {control["control"] for control in contract["implemented_controls"]} == {
        "delta-and-drift-decision",
        "partial-release-assembly",
        "multidimensional-coverage-report",
    }
    assert "tampered decision digest" in contract["validation"]["negative_cases"]


def test_operations_contract_keeps_external_and_elapsed_gates_open() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    gates = " ".join(contract["remaining_gates"])
    assert "blocking dependency tracks" in gates
    assert "beta SLO evidence period" in gates
    assert "national-scale restore" in gates
    assert "accountable approval" in gates
    assert "target release readiness" in gates
    assert any("does not contact endpoints" in claim for claim in contract["nonclaims"])
