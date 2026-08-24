import json
from pathlib import Path


def test_v1_upgrade_rehearsal_matrix_covers_all_required_scenarios() -> None:
    root = Path(__file__).resolve().parents[1]
    matrix = json.loads((root / "docs/v1-upgrade-rehearsal-matrix-20260825.json").read_text())
    assert matrix["status"] == "bounded-repository-rehearsal-complete-external-execution-pending"
    assert {item["scenario"] for item in matrix["scenarios"]} == {
        "upgrade",
        "migration",
        "rollback",
        "restore",
        "correction",
        "withdrawal",
    }
    assert all(item["evidence"] and item["open_gates"] for item in matrix["scenarios"])
    assert matrix["reset_conditions"]
    assert matrix["non_claims"]
