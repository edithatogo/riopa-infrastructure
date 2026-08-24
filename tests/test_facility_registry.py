import pytest

from riopa_provenance.facility_registry import (
    FacilityAssertion,
    FacilityHistoryEvent,
    Reconciliation,
    apply_review,
    assertions_snapshot,
    assertions_snapshot_json,
    build_snapshot_record,
    disagreement_coverage_report,
    distance_m,
    history_snapshot,
    name_similarity,
    public_release_snapshot,
    reconcile,
    validate_snapshot_record,
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


def test_disagreement_coverage_report_is_bounded_and_sorted() -> None:
    left = assertion("left", 0, 0, source_id="z-source")
    right = assertion("right", 0, 0.00001, source_id="a-source")
    report = disagreement_coverage_report((left, right), reconcile((left,), (right,)))
    assert report["authoritative"] is False
    assert report["source_counts"] == {"a-source": 1, "z-source": 1}
    assert report["candidate_match_count"] == 1
    assert report["scope"] == "supplied archived assertions only"


def test_disagreement_coverage_report_rejects_unknown_assertions() -> None:
    left = assertion("left", 0, 0)
    with pytest.raises(ValueError, match="unknown assertions"):
        disagreement_coverage_report(
            (left,),
            (Reconciliation("left", "missing", "candidate-match", 1.0, 1.0),),
        )


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
    assertion_rows = snapshot["assertions"]
    assert isinstance(assertion_rows, list)
    assert [row["assertion_id"] for row in assertion_rows] == ["a", "b"]
    assert assertions_snapshot_json(values).endswith("\n")
    with pytest.raises(ValueError, match="unique"):
        assertions_snapshot((assertion("a", 0, 0), assertion("a", 1, 1)))


def test_snapshot_record_is_content_addressed_and_correction_successor_only() -> None:
    record = build_snapshot_record((assertion("public", 0, 0),), revision="snapshot-1")
    assert validate_snapshot_record(record) == ()
    corrected = build_snapshot_record(
        (assertion("public", 0, 0.1),), revision="snapshot-2", supersedes=record["payload_sha256"]
    )
    assert validate_snapshot_record(corrected) == ()
    tampered = dict(record)
    payload = dict(record["payload"])  # type: ignore[arg-type]
    payload["assertions"] = []
    tampered["payload"] = payload
    assert any("does not match" in error for error in validate_snapshot_record(tampered))


def test_history_records_opening_closure_relocation_rebrand_and_disagreement() -> None:
    events = (
        FacilityHistoryEvent(
            "event:closure",
            "facility:one",
            "closure",
            "2024-01-01",
            "2024-01-03",
            ("source:one",),
            "source reported closure",
        ),
        FacilityHistoryEvent(
            "event:opening",
            "facility:one",
            "opening",
            "2020-01-01",
            "2020-01-02",
            ("source:one",),
            "source reported opening",
        ),
        FacilityHistoryEvent(
            "event:relocation",
            "facility:one",
            "relocation",
            "2022-06-01",
            "2022-06-02",
            ("source:one", "source:two"),
            "coordinates differ across source assertions",
        ),
        FacilityHistoryEvent(
            "event:rebrand",
            "facility:one",
            "rebrand",
            "2023-01-01",
            "2023-01-02",
            ("source:two",),
            "operator name changed",
        ),
        FacilityHistoryEvent(
            "event:disagreement",
            "facility:one",
            "source-disagreement",
            "2023-02-01",
            "2023-02-02",
            ("source:one", "source:two"),
            "sources disagree on current name",
        ),
    )
    snapshot = history_snapshot(events)
    assert snapshot["authoritative"] is False
    event_rows = snapshot["events"]
    assert isinstance(event_rows, list)
    assert [row["event_type"] for row in event_rows] == [
        "opening",
        "relocation",
        "rebrand",
        "source-disagreement",
        "closure",
    ]


def test_history_rejects_missing_evidence_reversed_window_and_retrospective_recording() -> None:
    with pytest.raises(ValueError, match="event type"):
        FacilityHistoryEvent(
            "event:bad-type",
            "facility:one",
            "unknown",  # type: ignore[arg-type]
            "2024-01-01",
            "2024-01-02",
            ("source:one",),
            "unsupported",
        )
    with pytest.raises(ValueError, match="source assertion"):
        FacilityHistoryEvent(
            "event:bad",
            "facility:one",
            "opening",
            "2024-01-01",
            "2024-01-02",
            (),
            "missing evidence",
        )
    with pytest.raises(ValueError, match="valid_to"):
        FacilityHistoryEvent(
            "event:bad-window",
            "facility:one",
            "closure",
            "2024-02-01",
            "2024-02-02",
            ("source:one",),
            "reversed",
            valid_to="2024-01-01",
        )
    with pytest.raises(ValueError, match="recorded_at"):
        FacilityHistoryEvent(
            "event:bad-recorded",
            "facility:one",
            "opening",
            "2024-02-01",
            "2024-01-01",
            ("source:one",),
            "recorded before event",
        )


def test_public_release_filter_excludes_non_public_assertions_and_records_ledger() -> None:
    public = assertion("public", 0, 0)
    restricted = assertion("restricted", 1, 1, release_classification="restricted")
    sensitive = assertion("sensitive", 2, 2, release_classification="sensitive")
    snapshot = public_release_snapshot((sensitive, public, restricted))
    rows = snapshot["assertions"]
    assert isinstance(rows, list)
    assert [row["assertion_id"] for row in rows] == ["public"]
    assert snapshot["excluded_assertion_ids"] == ["restricted", "sensitive"]
    assert snapshot["release_filter"] == "public-only"
    with pytest.raises(ValueError, match="classification"):
        assertion("bad-class", 0, 0, release_classification="unknown")
