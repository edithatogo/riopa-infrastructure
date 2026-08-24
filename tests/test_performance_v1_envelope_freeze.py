import json
from pathlib import Path


def test_performance_envelope_freeze_is_bounded_and_non_promoting() -> None:
    root = Path(__file__).resolve().parents[1]
    packet = json.loads((root / "docs/performance-v1-envelope-freeze-20260825.json").read_text())
    assert packet["status"] == "bounded-candidate-not-promoted"
    assert packet["promotion_allowed"] is False
    assert {item["name"] for item in packet["envelopes"]} == {
        "measurement",
        "projection",
        "noise",
        "resource-cost",
    }
    assert any("national-scale" in gate for gate in packet["open_gates"])
    assert any("unknown" in action["condition"] for action in packet["operational_actions"])
