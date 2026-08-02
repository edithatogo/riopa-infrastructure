import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_release_packet_readiness_links_campaign_artifacts_and_fails_closed() -> None:
    packet = json.loads((ROOT / "docs/release-packet-readiness-20260802.json").read_text())
    assert packet["status"] == "preparation-only"
    assert packet["release_ready"] is False
    assert packet["release_authority"] == "pending"
    for artifact in packet["repository_owned_artifacts"]:
        assert (ROOT / artifact).exists()
    assert "hosted recovery execution" in packet["pending_gates"]
