import json
from math import exp, isclose
from pathlib import Path
from typing import cast

from riopa_provenance.accessibility import (
    AccessibilityMatrix,
    TravelObservation,
    TravelStatus,
    gravity_accessibility,
)
from riopa_provenance.transitions import select_temporal_records


def _replacement_successor(*, perspective: str, at: str) -> str:
    records = json.loads(Path("fixtures/planning-transition-golden.json").read_text())
    selected = select_temporal_records(records, perspective=perspective, at=at)
    replacement = next(item for item in selected if item["relationship"] == "replacement")
    assert replacement["predecessors"] == ["urn:riopa:plan:old"]
    return cast(str, replacement["successors"][0])


def test_zoning_projection_uses_successor_plan_at_valid_time() -> None:
    successor = _replacement_successor(perspective="valid_time", at="2023-06-01")
    zoning_by_plan = {
        "urn:riopa:plan:old": {"allowed": False, "source": "fixture:historic"},
        "urn:riopa:plan:new": {"allowed": True, "source": "fixture:successor"},
    }
    assert zoning_by_plan[successor] == {"allowed": True, "source": "fixture:successor"}


def test_accessibility_reference_uses_transition_successor_without_operational_claim() -> None:
    successor = _replacement_successor(perspective="valid_time", at="2023-06-01")
    matrix = AccessibilityMatrix(
        "fixture-transition-matrix",
        "fixture-network-only",
        "reference-table",
        "1",
        "reference",
        {("origin", successor): TravelObservation(TravelStatus.REACHABLE, 10)},
    )
    value = gravity_accessibility(matrix, "origin", {successor: 5}, decay=0.1)
    assert isclose(value, 5 * exp(-1))
