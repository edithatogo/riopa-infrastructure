from __future__ import annotations

import json
from pathlib import Path

from scripts.tasman_cycle_ledger import validate


def test_preserved_manual_observation_is_not_scheduled_qualification() -> None:
    root = Path(__file__).resolve().parents[1]
    ledger = json.loads((root / "docs/tasman-cycle-ledger-baseline-20260831.json").read_bytes())
    events = validate(ledger)
    assert len(events) == ledger["unique_source_run_count"] == 1
    event = events[0]
    assert event["source_run"] == "33301038921"
    assert event["publication"]["run_id"] == "33345370638"
    assert event["predecessor_source_run"] is None
    assert ledger["scheduled_automatic_source_runs"] == []
    assert ledger["three_cycle_gate_qualified"] is False
    acceptance = json.loads(
        (root / "docs/tasman-feature-comparison-acceptance-20260831.json").read_bytes()
    )
    assert (
        event["evidence_sha256"]["comparison"] == acceptance["hosted_execution"]["receipt_sha256"]
    )
    for name in ("source", "derived"):
        assert (
            event["evidence_sha256"][name]
            == acceptance["comparison_receipt"][name + "_receipt_sha256"]
        )
