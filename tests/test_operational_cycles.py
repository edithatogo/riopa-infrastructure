from pathlib import Path

import pytest

from riopa_provenance.operational_cycles import Cycle, record_soak, write_soak_evidence


def test_soak_record_remains_pending_until_duration_is_met(tmp_path: Path) -> None:
    evidence = record_soak(
        "wp010-preview",
        required_days=90,
        observed_days=2,
        cycles=[
            Cycle(
                1,
                "2026-08-01T00:00:00Z",
                "2026-08-01T00:01:00Z",
                "recovered",
                "source-timeout",
                "backfill",
            )
        ],
    )
    assert evidence.status == "pending-duration"
    output = tmp_path / "soak.json"
    write_soak_evidence(evidence, output)
    assert '"status": "pending-duration"' in output.read_text()


def test_soak_can_report_synthetic_duration_without_claiming_qualification() -> None:
    evidence = record_soak(
        "fixture",
        3,
        3,
        [Cycle(1, "2026-08-01T00:00:00Z", "2026-08-01T00:01:00Z", "completed")],
    )
    assert evidence.status == "synthetic-duration-met"


def test_empty_soak_cannot_manufacture_duration_evidence() -> None:
    evidence = record_soak("fixture", 3, 3, [])
    assert evidence.status == "pending-duration"


def test_invalid_cycle_is_rejected() -> None:
    with pytest.raises(ValueError, match="contiguous"):
        record_soak("fixture", 1, 0, [Cycle(0, "", "", "failed")])


def test_cycle_requires_ordered_timestamps_and_paired_recovery() -> None:
    with pytest.raises(ValueError, match="ordered"):
        record_soak(
            "fixture",
            1,
            1,
            [Cycle(1, "2026-08-02T00:00:00Z", "2026-08-01T00:00:00Z", "failed")],
        )


def test_soak_rejects_empty_scope_negative_duration_and_invalid_cycle_fields() -> None:
    with pytest.raises(ValueError, match="scope"):
        record_soak("", 1, 1, [])
    with pytest.raises(ValueError, match="non-negative"):
        record_soak("fixture", -1, 0, [])
    with pytest.raises(ValueError, match="outcomes"):
        record_soak(
            "fixture",
            1,
            1,
            [Cycle(1, "2026-08-01T00:00:00Z", "2026-08-01T00:01:00Z", "")],
        )
    with pytest.raises(ValueError, match="ISO 8601"):
        record_soak("fixture", 1, 1, [Cycle(1, "bad", "bad", "failed")])
    with pytest.raises(ValueError, match="timezone-aware"):
        record_soak(
            "fixture",
            1,
            1,
            [Cycle(1, "2026-08-01T00:00:00", "2026-08-01T00:01:00", "failed")],
        )
    with pytest.raises(ValueError, match="recorded together"):
        record_soak(
            "fixture",
            1,
            1,
            [
                Cycle(
                    1,
                    "2026-08-01T00:00:00Z",
                    "2026-08-01T00:01:00Z",
                    "recovered",
                    failure="timeout",
                )
            ],
        )
