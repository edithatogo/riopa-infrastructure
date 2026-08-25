import json
from pathlib import Path


def test_accessibility_v1_freeze_is_bounded_and_non_promoting() -> None:
    root = Path(__file__).resolve().parents[1]
    packet = json.loads((root / "docs/accessibility-v1-contract-freeze-20260825.json").read_text())
    assert packet["status"] == "bounded-candidate-not-promoted"
    assert packet["scope"].startswith("bounded regional")
    assert packet["promotion_allowed"] is False
    assert {item["name"] for item in packet["supported_reference_operations"]} == {
        "straight_line_matrix",
        "reference_measures",
        "reference_matrix_comparison",
        "partition_and_incremental_recompute",
        "time_capacity_reference_projection",
    }
    assert set(packet["required_semantics"]["travel_statuses"]) == {
        "reachable",
        "unreachable",
        "missing",
        "censored",
    }
    assert any("national-scale" in gate for gate in packet["open_gates"])
    assert any("external operator" in gate for gate in packet["open_gates"])
    assert any("timetable" in item for item in packet["disabled_adapters_and_claims"])
