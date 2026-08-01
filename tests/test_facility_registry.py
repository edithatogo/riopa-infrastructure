import pytest

from riopa_provenance.facility_registry import (
    FacilityAssertion,
    apply_review,
    distance_m,
    name_similarity,
    reconcile,
    assertions_snapshot,
    assertions_snapshot_json,
)


def assertion(identifier: str, lat: float, lon: float, **changes: object) -> FacilityAssertion:
    values = {
        "assertion_id": identifier,
        "source_id": f"source:{identifier}",
        "facility_type": "ambulance-station",
        "name": "St. John Ambulance",
        "latitude": lat,
        "longitude": lon,
        "authority": "official-reference",
        "licence": "CC-BY-4.0",
    }
    values.update(changes)
    return FacilityAssertion(**values)  # type: ignore[arg-type]


def test_candidate_is_non_authoritative_and_review_is_explicit() -> None:
    left = assertion("council:43", -40.074234253256, 175.379189350458)
    right = assertion(
        "osm:way:636258913",
        -40.0742493,
        175.3791258,
        authority="community-reference",
        licence="ODbL-1.0",
        name="St John Ambulance",
    )
    result = reconcile((left,), (right,))
    assert result[0].disposition == "candidate-match"
    assert result[0].distance_m == pytest.approx(5.660, abs=0.001)
    assert result[0].reviewer is None
    reviewed = apply_review(
        result[0],
        reviewer="analyst-agent-1",
        same_facility=True,
        rationale="coordinates and names agree",
    )
    assert reviewed.disposition == "reviewed-match"
    assert reviewed.reviewer == "analyst-agent-1"


def test_type_distance_and_one_to_one_rules_preserve_unmatched_assertions() -> None:
    left = (assertion("left-a", 0, 0), assertion("left-b", 0, 0.0001))
    right = (
        assertion("wrong-type", 0, 0, facility_type="supermarket"),
        assertion("near", 0, 0.00005),
        assertion("far", 1, 1),
    )
    results = reconcile(left, right, maximum_distance_m=100)
    assert sum(item.disposition == "candidate-match" for item in results) == 1
    assert sum(item.disposition == "source-only" for item in results) == 3


def test_validation_similarity_and_determinism() -> None:
    assert name_similarity("The St. John Ambulance Ltd", "St John Ambulance") == 1
    with pytest.raises(ValueError, match="coordinates"):
        assertion("bad", 91, 0)
    with pytest.raises(ValueError, match="thresholds"):
        reconcile((), (), minimum_name_similarity=2)
    left = (assertion("b", 0, 0), assertion("a", 0, 0))
    right = (assertion("r", 0, 0),)
    assert reconcile(left, right) == reconcile(tuple(reversed(left)), right)
    assert distance_m(left[0], right[0]) == 0


def test_review_requires_accountability_and_candidate_state() -> None:
    candidate = reconcile((assertion("a", 0, 0),), (assertion("b", 0, 0),))[0]
    with pytest.raises(ValueError, match="reviewer"):
        apply_review(candidate, reviewer="", same_facility=False, rationale="uncertain")
    with pytest.raises(ValueError, match="candidate"):
        apply_review(
            reconcile((assertion("a", 0, 0),), ())[0],
            reviewer="analyst-agent-1",
            same_facility=False,
            rationale="no pair",
        )


def test_assertions_snapshot_is_sorted_and_non_authoritative() -> None:
    values = (assertion("b", 1, 1), assertion("a", 0, 0))
    snapshot = assertions_snapshot(values)
    assert snapshot["authoritative"] is False
    assert [row["assertion_id"] for row in snapshot["assertions"]] == ["a", "b"]
    assert assertions_snapshot_json(values).endswith("\n")
    with pytest.raises(ValueError, match="unique"):
        assertions_snapshot((assertion("a", 0, 0), assertion("a", 1, 1)))
