import json
from pathlib import Path


def test_health_panel_remediation_is_bounded_and_complete() -> None:
    root = Path(__file__).resolve().parents[1]
    packet = json.loads((root / "docs/health-methods-panel-remediation-20260825.json").read_text())
    assert packet["status"] == "bounded-repository-remediation-complete"
    assert packet["promotion_allowed"] is False
    assert {finding["disposition"] for finding in packet["findings"]} == {"bounded"}
    assert packet["remaining_gates"]
    assert "cannot close external" in " ".join(packet["nonclaims"])
