import json
from pathlib import Path

from riopa_provenance.transitions import select_temporal_records, validate_transition


def test_transition_fixture_covers_relationships_and_validates() -> None:
    records = json.loads(Path("fixtures/planning-transition-golden.json").read_text())
    assert {record["relationship"] for record in records} == {"rename", "merge", "split", "replacement", "partial_continuity"}
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
