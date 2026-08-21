import json
from math import isclose
from pathlib import Path

import pytest

from riopa_provenance.accessibility import (
    AccessibilityMatrix,
    TravelObservation,
    TravelStatus,
    cumulative_opportunity,
    gravity_accessibility,
    two_step_floating_catchment,
)
from riopa_provenance.validation import validate_instance


def _matrix() -> AccessibilityMatrix:
    return AccessibilityMatrix(
        "benchmark-1",
        "network-2026",
        "independent-table",
        "1",
        "walk",
        {
            ("a", "x"): TravelObservation(TravelStatus.REACHABLE, 5),
            ("a", "y"): TravelObservation(TravelStatus.REACHABLE, 15),
            ("b", "x"): TravelObservation(TravelStatus.REACHABLE, 10),
            ("b", "y"): TravelObservation(TravelStatus.UNREACHABLE),
        },
    )


def test_hand_calculated_accessibility_benchmark() -> None:
    matrix = _matrix()
    assert cumulative_opportunity(matrix, "a", {"x": 10, "y": 20}, threshold=10) == 10
    assert isclose(
        gravity_accessibility(matrix, "a", {"x": 10, "y": 20}, decay=0.1),
        10 * 0.6065306597 + 20 * 0.2231301601,
    )
    assert two_step_floating_catchment(
        matrix, {"a": 100, "b": 50}, {"x": 30, "y": 40}, threshold=10
    ) == {"a": 0.2, "b": 0.2}


def test_missing_unreachable_and_censored_remain_distinct() -> None:
    matrix = _matrix()
    assert matrix.observations[("b", "y")].status is TravelStatus.UNREACHABLE
    assert ("missing", "x") not in matrix.observations
    assert TravelObservation(TravelStatus.CENSORED).impedance is None
    with pytest.raises(ValueError, match="only reachable"):
        TravelObservation(TravelStatus.MISSING, 1)
    with pytest.raises(ValueError, match="finite non-negative"):
        TravelObservation(TravelStatus.REACHABLE, -1)


@pytest.mark.parametrize(
    "measure",
    [
        lambda matrix: cumulative_opportunity(matrix, "a", {"x": 1}, threshold=-1),
        lambda matrix: gravity_accessibility(matrix, "a", {"x": 1}, decay=-1),
        lambda matrix: two_step_floating_catchment(matrix, {"a": 1}, {"x": 1}, threshold=-1),
    ],
)
def test_measure_parameters_fail_closed(measure: object) -> None:
    with pytest.raises(ValueError):
        measure(_matrix())  # type: ignore[operator]


def test_empty_two_step_catchment_has_zero_ratio() -> None:
    assert two_step_floating_catchment(_matrix(), {"outside": 1}, {"x": 10}, threshold=2) == {
        "outside": 0.0
    }


def test_versioned_accessibility_contract_preserves_missing_semantics() -> None:
    root = Path(__file__).resolve().parents[1]
    matrix_schema = json.loads((root / "schemas/accessibility-matrix.schema.json").read_text())
    measure_schema = json.loads((root / "schemas/accessibility-measure.schema.json").read_text())
    matrix = {
        "schema_version": "1.0.0",
        "record_type": "accessibility_matrix",
        "matrix_id": "matrix:fixture",
        "network_version": "archive:fixture",
        "engine": "reference",
        "engine_version": "1",
        "mode": "straight-line",
        "observations": [
            {"origin": "o1", "destination": "d1", "status": "reachable", "impedance": 2.0},
            {"origin": "o1", "destination": "d2", "status": "missing", "impedance": None},
        ],
        "source_refs": ["fixture:archive"],
        "claim_classification": "reference-only",
    }
    assert validate_instance(matrix, matrix_schema) == ()
    invalid = json.loads(json.dumps(matrix))
    invalid["observations"][1]["impedance"] = 1.0
    assert validate_instance(invalid, matrix_schema)
    measure = {
        "schema_version": "1.0.0",
        "record_type": "accessibility_measure",
        "measure_id": "measure:fixture",
        "matrix_id": "matrix:fixture",
        "measure": "gravity",
        "missing_policy": "report-separately",
        "denominator_semantics": "none",
        "result": 1.5,
        "claim_classification": "reference-only",
    }
    assert validate_instance(measure, measure_schema) == ()
