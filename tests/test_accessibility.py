import json
from math import isclose
from pathlib import Path

import pytest

from riopa_provenance.accessibility import (
    AccessibilityMatrix,
    AccessibilityResultCache,
    OpeningInterval,
    TravelObservation,
    TravelStatus,
    changed_origins,
    compare_reference_matrices,
    cumulative_opportunity,
    gravity_accessibility,
    incremental_cumulative_opportunity,
    partition_matrix,
    public_facility_opportunities,
    reachable_capacity_at_departure,
    straight_line_matrix,
    two_step_floating_catchment,
    validate_scenario_contract,
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


def test_partitioning_is_deterministic_and_preserves_rows() -> None:
    partitions = partition_matrix(_matrix(), origins_per_partition=1)
    assert [partition.partition_id for partition in partitions] == [
        "benchmark-1:partition:0000",
        "benchmark-1:partition:0001",
    ]
    assert [partition.origins for partition in partitions] == [("a",), ("b",)]
    assert sum(len(partition.observations) for partition in partitions) == 4
    with pytest.raises(ValueError, match="positive"):
        partition_matrix(_matrix(), origins_per_partition=0)


def test_reference_matrix_comparison_preserves_statuses_and_deltas() -> None:
    left = _matrix()
    right = AccessibilityMatrix(
        "benchmark-2",
        "network-2026",
        "independent-table",
        "2",
        "walk",
        {
            ("a", "x"): TravelObservation(TravelStatus.REACHABLE, 7),
            ("a", "y"): TravelObservation(TravelStatus.UNREACHABLE),
            ("b", "x"): TravelObservation(TravelStatus.REACHABLE, 10),
            ("c", "z"): TravelObservation(TravelStatus.MISSING),
        },
    )
    report = compare_reference_matrices(left, right)
    assert report["pair_count"] == 5
    assert report["comparable_pair_count"] == 2
    assert report["status_mismatch_count"] == 2
    assert report["max_abs_impedance_delta"] == 2
    assert report["metadata_compatible"] is True
    assert report["promotion_allowed"] is False
    incompatible = AccessibilityMatrix(
        "other", "network-other", "engine", "1", "cycle", left.observations
    )
    assert compare_reference_matrices(left, incompatible)["metadata_compatible"] is False


def test_cache_is_fingerprint_aware_and_incremental_recompute_changes_one_origin() -> None:
    matrix = _matrix()
    cache = AccessibilityResultCache()
    calls = 0

    def compute() -> float:
        nonlocal calls
        calls += 1
        return cumulative_opportunity(matrix, "a", {"x": 10}, threshold=10)

    assert (
        cache.get_or_compute(
            matrix,
            origin="a",
            measure="cumulative",
            parameters={"threshold": 10},
            compute=compute,
        )
        == 10
    )
    assert (
        cache.get_or_compute(
            matrix,
            origin="a",
            measure="cumulative",
            parameters={"threshold": 10},
            compute=compute,
        )
        == 10
    )
    assert calls == 1
    changed = AccessibilityMatrix(
        matrix.matrix_id,
        matrix.network_version,
        matrix.engine,
        matrix.engine_version,
        matrix.mode,
        {**matrix.observations, ("b", "x"): TravelObservation(TravelStatus.REACHABLE, 2)},
    )
    assert changed_origins(matrix, changed) == ("b",)
    assert incremental_cumulative_opportunity(
        matrix,
        changed,
        {"a": 10, "b": 0},
        {"x": 10, "y": 20},
        threshold=10,
    ) == {"a": 10, "b": 10}


def test_straight_line_matrix_is_deterministic_and_bounded() -> None:
    matrix = straight_line_matrix(
        "coordinates-1",
        {"origin": (0.0, 0.0), "destination": (0.0, 1.0)},
        ("origin",),
        ("destination",),
    )
    assert matrix.mode == "straight-line"
    assert matrix.network_version == "reference:coordinate-snapshot"
    assert matrix.reachable_impedance("origin", "destination") == pytest.approx(111.195, rel=1e-3)


def test_opening_hours_capacity_is_arrival_based_and_wraps_midnight() -> None:
    matrix = AccessibilityMatrix(
        "minutes-1",
        "archive:fixture",
        "reference",
        "1",
        "reference-minutes",
        {
            ("origin", "day"): TravelObservation(TravelStatus.REACHABLE, 30),
            ("origin", "night"): TravelObservation(TravelStatus.REACHABLE, 45),
        },
    )
    intervals = {
        "day": (OpeningInterval(480, 600),),
        "night": (OpeningInterval(1380, 60),),
    }
    assert (
        reachable_capacity_at_departure(
            matrix,
            "origin",
            {"day": 2.0, "night": 3.0},
            intervals,
            departure_minute=450,
            threshold_minutes=60,
        )
        == 2.0
    )
    assert (
        reachable_capacity_at_departure(
            matrix,
            "origin",
            {"day": 2.0, "night": 3.0},
            intervals,
            departure_minute=1380,
            threshold_minutes=60,
        )
        == 3.0
    )
    with pytest.raises(ValueError, match="equal endpoints"):
        OpeningInterval(60, 60)


@pytest.mark.parametrize(
    "coordinates",
    [
        {"origin": (91.0, 0.0), "destination": (0.0, 0.0)},
        {"origin": (0.0, 181.0), "destination": (0.0, 0.0)},
        {"origin": (0.0, 0.0)},
    ],
)
def test_straight_line_matrix_fails_closed_on_coordinate_errors(
    coordinates: dict[str, tuple[float, float]],
) -> None:
    with pytest.raises(ValueError):
        straight_line_matrix("coordinates-1", coordinates, ("origin",), ("destination",))


def test_public_facility_snapshot_becomes_unit_opportunities_only() -> None:
    snapshot = {
        "record_type": "facility_assertions",
        "authoritative": False,
        "assertions": [
            {
                "assertion_id": "public:one",
                "facility_type": "clinic",
                "release_classification": "public",
            },
            {
                "assertion_id": "restricted:two",
                "facility_type": "clinic",
                "release_classification": "restricted",
            },
            {
                "assertion_id": "public:three",
                "facility_type": "supermarket",
                "release_classification": "public",
            },
        ],
    }
    assert public_facility_opportunities(snapshot, facility_type="clinic") == {"public:one": 1.0}
    with pytest.raises(ValueError, match="non-authoritative"):
        public_facility_opportunities({**snapshot, "authoritative": True})


def test_scenario_contract_preserves_subgroups_and_uncertainty() -> None:
    contract = {
        "scenario_id": "bounded-reference",
        "claim_classification": "reference-only",
        "assumptions": ["archived matrix only"],
        "subgroup_dimensions": ["rurality", "deprivation_quintile"],
        "uncertainty": {
            "method": "scenario-range",
            "missing_policy": "report-separately",
            "reporting_unit": "minutes",
        },
    }
    assert validate_scenario_contract(contract) == ()
    contract["subgroup_dimensions"] = ["rurality", "rurality"]
    assert any("unique" in error for error in validate_scenario_contract(contract))


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


def test_accessibility_plan_closes_reference_scenario_contract_without_operational_claim() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = (root / "conductor/tracks/accessibility_network_engine_20260719/plan.md").read_text()
    assert "[x] 1.3 Define uncertainty, subgroup and scenario contracts" in plan
    assert "real-network and operational qualification remain pending" in plan
