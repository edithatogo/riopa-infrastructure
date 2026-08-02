import json
from pathlib import Path

from scripts.reconcile_open_issue_matrix import reconcile


def test_reconciliation_produces_one_row_per_track_without_inference() -> None:
    issues = json.loads(Path("/tmp/riopa-open-issues.json").read_text()) if Path("/tmp/riopa-open-issues.json").exists() else []
    if not issues:
        issues = [{"number": 1, "title": "[accessibility_network_engine_20260719] issue", "labels": [], "body": "", "url": ""}]
    payload = reconcile(issues, observed="2026-08-02")
    assert payload["snapshot"]["track_count"] == 28
    assert len(payload["track_inventory"]) == 28
    assert all("classification_basis" in row for row in payload["track_inventory"])
