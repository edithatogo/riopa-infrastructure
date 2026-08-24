import json
from pathlib import Path

from scripts.build_local_recovery_drill import build_report


def test_local_recovery_drill_is_digest_bound_and_fail_closed() -> None:
    report = build_report()
    assert report["status"] == "passing-local-synthetic"
    assert report["fail_closed"] is True
    assert report["tamper_rejection"] is True
    assert [item["operation"] for item in report["operations"]] == [
        "snapshot",
        "restore",
        "rollback",
    ]


def test_preserved_local_recovery_drill_keeps_provider_gate_open() -> None:
    root = Path(__file__).resolve().parents[1]
    report = json.loads((root / "docs/operations-local-recovery-drill-20260825.json").read_text())
    assert report["status"] == "passing-local-synthetic"
    assert any("not hosted" in claim for claim in report["non_claims"])
