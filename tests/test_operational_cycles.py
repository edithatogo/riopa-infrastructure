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


def test_soak_can_report_synthetic_completion_without_claiming_deployment() -> None:
    evidence = record_soak("fixture", 3, 3, [])
    assert evidence.status == "qualified-synthetic"


def test_invalid_cycle_is_rejected() -> None:
    with pytest.raises(ValueError):
        record_soak("fixture", 1, 0, [Cycle(0, "", "", "failed")])
