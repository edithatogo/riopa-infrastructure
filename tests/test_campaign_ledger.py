import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from scripts.build_campaign_ledger import build_ledger


def _receipt(path: Path, **overrides: object) -> Path:
    value = {
        "campaign_id": "beta-test",
        "qualification_epoch": "beta-epoch-1",
        "operational_cycle_id": "cycle-1",
        "lane": "operational-observation",
        "classification": "qualifying-beta-observation",
        "campaign_activation": {
            "status": "activated",
            "campaign_id": "beta-test",
            "authority": "repository-owner",
            "activated_at": "2026-08-01T00:00:00Z",
        },
        "hosted_run_id": f"run-{path.stem}",
        "status": "passed",
        "source_revision": "a" * 40,
        "candidate_revision": None,
        "started_at": "2026-08-02T00:00:00Z",
        "ended_at": "2026-08-02T00:01:00Z",
    }
    value.update(overrides)
    path.write_text(json.dumps(value))
    return path


def test_ledger_does_not_invent_elapsed_duration(tmp_path: Path) -> None:
    ledger = build_ledger([_receipt(tmp_path / "one.json")])
    assert ledger["elapsed_gate_status"] == "pending"
    assert ledger["duration_status"] == "pending-duration"
    assert ledger["required_elapsed_days"] == 90
    assert ledger["active_segment"]["elapsed_seconds"] == 60
    assert len(ledger["chain_head_sha256"]) == 64


def test_beta_revision_change_does_not_reset_same_epoch(tmp_path: Path) -> None:
    first = _receipt(tmp_path / "one.json")
    second = _receipt(
        tmp_path / "two.json",
        source_revision="b" * 40,
        started_at="2026-08-03T00:00:00Z",
        ended_at="2026-08-03T00:01:00Z",
    )
    ledger = build_ledger([first, second], now=datetime(2026, 12, 1, tzinfo=UTC))
    assert len(ledger["segments"]) == 1


def test_beta_epoch_change_starts_a_new_segment(tmp_path: Path) -> None:
    first = _receipt(tmp_path / "one.json")
    second = _receipt(
        tmp_path / "two.json",
        qualification_epoch="beta-epoch-2",
        started_at="2026-08-03T00:00:00Z",
        ended_at="2026-08-03T00:01:00Z",
    )
    ledger = build_ledger([first, second])
    assert len(ledger["segments"]) == 2


def test_rc_receipt_requires_exact_candidate_binding(tmp_path: Path) -> None:
    receipt = _receipt(
        tmp_path / "rc.json",
        lane="rc-soak-observation",
        classification="qualifying-rc-observation",
        candidate_revision="b" * 40,
    )
    with pytest.raises(ValueError, match="not bound"):
        build_ledger([receipt])


def test_sparse_observations_cannot_pass_elapsed_gate(tmp_path: Path) -> None:
    first = _receipt(tmp_path / "one.json")
    second = _receipt(
        tmp_path / "two.json",
        operational_cycle_id="cycle-2",
        started_at="2026-11-01T00:00:00Z",
        ended_at="2026-11-01T00:01:00Z",
    )
    ledger = build_ledger([first, second], now=datetime(2026, 12, 1, tzinfo=UTC))
    assert ledger["duration_status"] == "passed"
    assert ledger["cadence_status"] == "failed-gap"
    assert ledger["operational_cycles_status"] == "pending-cycles"
    assert ledger["elapsed_gate_status"] == "pending"


def test_mixed_elapsed_lanes_are_rejected(tmp_path: Path) -> None:
    operational = _receipt(tmp_path / "operational.json")
    rc = _receipt(
        tmp_path / "rc.json",
        lane="rc-soak-observation",
        classification="qualifying-rc-observation",
        candidate_revision="a" * 40,
    )
    with pytest.raises(ValueError, match="exactly one"):
        build_ledger([operational, rc])


def test_daily_beta_with_three_cycles_can_pass(tmp_path: Path) -> None:
    start = datetime(2026, 8, 2, tzinfo=UTC)
    receipts = []
    for day in range(91):
        observed = start + timedelta(days=day)
        receipts.append(
            _receipt(
                tmp_path / f"{day:03}.json",
                source_revision=("a" if day < 45 else "b") * 40,
                operational_cycle_id=f"cycle-{day // 30 + 1}",
                started_at=observed.isoformat().replace("+00:00", "Z"),
                ended_at=(observed + timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
            )
        )
    ledger = build_ledger(receipts, now=datetime(2026, 12, 1, tzinfo=UTC))
    assert ledger["duration_status"] == "passed"
    assert ledger["cadence_status"] == "passed"
    assert ledger["operational_cycles_status"] == "passed"
    assert ledger["elapsed_gate_status"] == "passed"


def test_rc_revision_change_resets_segment(tmp_path: Path) -> None:
    first = _receipt(
        tmp_path / "one.json",
        lane="rc-soak-observation",
        classification="qualifying-rc-observation",
        candidate_revision="a" * 40,
    )
    second = _receipt(
        tmp_path / "two.json",
        lane="rc-soak-observation",
        classification="qualifying-rc-observation",
        source_revision="b" * 40,
        candidate_revision="b" * 40,
        started_at="2026-08-03T00:00:00Z",
        ended_at="2026-08-03T00:01:00Z",
    )
    ledger = build_ledger([first, second])
    assert len(ledger["segments"]) == 2


def test_identical_restored_receipts_count_once(tmp_path: Path) -> None:
    original = _receipt(
        tmp_path / "original.json",
        lane="rc-soak-observation",
        classification="qualifying-rc-observation",
        candidate_revision="a" * 40,
    )
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_bytes(original.read_bytes())
    ledger = build_ledger([original, duplicate])
    assert len(ledger["observations"]) == 1
    assert ledger["active_segment"]["observation_count"] == 1
    assert ledger["duplicate_receipt_count"] == 1


def test_preview_drill_cannot_qualify(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path / "preview.json", classification="hosted-technical-preview-drill")
    with pytest.raises(ValueError, match="classification"):
        build_ledger([receipt])


def test_duplicate_observation_day_cannot_qualify(tmp_path: Path) -> None:
    first = _receipt(tmp_path / "one.json")
    second = _receipt(
        tmp_path / "two.json",
        started_at="2026-08-02T12:00:00Z",
        ended_at="2026-08-02T12:01:00Z",
    )
    with pytest.raises(ValueError, match="distinct UTC"):
        build_ledger([first, second])
