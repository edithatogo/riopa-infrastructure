import json
from pathlib import Path

from riopa_provenance.transitions import (
    audit_transition_history,
    build_continuity_crosswalk,
    classify_transition_evidence,
    select_temporal_records,
    validate_transition,
)


def test_transition_fixture_covers_relationships_and_validates() -> None:
    records = json.loads(Path("fixtures/planning-transition-golden.json").read_text())
    assert {record["relationship"] for record in records} == {
        "rename",
        "merge",
        "split",
        "replacement",
        "partial_continuity",
    }
    assert all(validate_transition(record) == () for record in records)


def test_temporal_perspective_is_explicit_and_fail_closed() -> None:
    records = json.loads(Path("fixtures/planning-transition-golden.json").read_text())
    assert len(select_temporal_records(records, perspective="valid_time", at="2021-06-01")) == 2
    assert len(select_temporal_records(records, perspective="recorded_time", at="2021-01-15")) == 1
    assert len(select_temporal_records(records, perspective="as_known_at", at="2020-01-15")) == 0


def test_partial_continuity_requires_scope_and_reversed_window_is_rejected() -> None:
    records = json.loads(Path("fixtures/planning-transition-golden.json").read_text())
    record = dict(records[-1], scope=None)
    assert "partial_continuity requires an explicit scope" in validate_transition(record)
    record = dict(records[0], valid_time={"from": "2025-01-01", "to": "2024-01-01"})
    assert "valid_time.to must not precede valid_time.from" in validate_transition(record)


def test_transition_evidence_and_crosswalk_preserve_discovery_and_scope() -> None:
    evidence = classify_transition_evidence(
        {"discovery_mode": "retrospective", "evidence": ["archive:1"]}
    )
    assert evidence["authority_status"] == "not-established"
    crosswalk = build_continuity_crosswalk(
        predecessor="plan-old",
        successor="plan-new",
        confidence="medium",
        scope="provisions 1-3 only",
        evidence=["archive:1"],
        valid_time={"from": "2020-01-01", "to": None},
        recorded_time={"from": "2022-01-01", "to": None},
    )
    assert crosswalk["relationship"] == "partial_continuity"
    assert crosswalk["scope"] == "provisions 1-3 only"
    assert crosswalk["promotion_allowed"] is False


def test_history_audit_reports_late_correction_supersession_and_gaps() -> None:
    base = {
        "relationship": "replacement",
        "predecessors": ["old"],
        "successors": ["new"],
        "state": "operative",
        "evidence": ["archive:1"],
        "history_group": "plan",
        "valid_time": {"from": "2020-01-01", "to": "2020-01-31"},
        "recorded_time": {"from": "2020-02-01", "to": None},
    }
    first = {**base, "transition_id": "urn:riopa:transition:first", "event_type": "correction"}
    second = {
        **base,
        "transition_id": "urn:riopa:transition:second",
        "state": "superseded",
        "valid_time": {"from": "2020-03-01", "to": None},
        "recorded_time": {"from": "2020-03-01", "to": None},
        "event_type": "supersession",
    }
    result = audit_transition_history([first, second])
    assert result["late_evidence"] == ["urn:riopa:transition:first"]
    assert result["corrections"] == ["urn:riopa:transition:first"]
    assert result["supersessions"] == ["urn:riopa:transition:second"]
    assert len(result["historical_gaps"]) == 1
    assert result["overlapping_windows"] == []
    assert result["promotion_allowed"] is False


def test_history_audit_reports_overlapping_declared_windows() -> None:
    base = {
        "relationship": "replacement",
        "predecessors": ["old"],
        "successors": ["new"],
        "state": "operative",
        "evidence": ["archive:1"],
        "history_group": "plan",
        "recorded_time": {"from": "2020-01-01", "to": None},
    }
    first = {
        **base,
        "transition_id": "urn:riopa:transition:overlap-first",
        "valid_time": {"from": "2020-01-01", "to": "2020-02-15"},
    }
    second = {
        **base,
        "transition_id": "urn:riopa:transition:overlap-second",
        "valid_time": {"from": "2020-02-01", "to": "2020-03-01"},
    }
    result = audit_transition_history([first, second])
    assert result["historical_gaps"] == []
    assert result["overlapping_windows"] == [
        {
            "history_group": "plan",
            "from": "2020-02-01",
            "to": "2020-02-15",
            "first": "urn:riopa:transition:overlap-first",
            "second": "urn:riopa:transition:overlap-second",
        }
    ]
