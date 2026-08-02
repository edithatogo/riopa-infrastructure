import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_local_qualification_packet_is_bounded_and_fail_closed() -> None:
    packet = json.loads(
        (ROOT / "docs/local-technical-preview-qualification-20260802.json").read_text()
    )
    assert packet["status"] == "local-qualification-passing"
    assert packet["recovery"]["status"] == "passing-local-synthetic"
    assert packet["performance"]["status"] == "passing-regional-synthetic"
    assert packet["promotion_ready"] is False
    assert "hosted or production recovery" in packet["not_established"]
