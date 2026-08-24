import json
from pathlib import Path

PACKET = Path("docs/v1-release-candidate-packet-20260825.json")


def test_v1_release_candidate_packet_is_fail_closed() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    candidate = packet["candidate"]
    assert packet["status"] == "preparation-only"
    assert packet["release_ready"] is False
    assert packet["promotion_allowed"] is False
    assert len(candidate["revision"]) == 40
    assert candidate["signing_manifest_status"] == "unsigned-candidate"
    required = set(packet["required_external_or_elapsed_evidence"])
    assert any("30-day exact-RC soak" in item for item in required)
    assert any("accountable release-authority" in item for item in required)
    assert any("preservation" in item for item in required)


def test_v1_release_candidate_packet_has_non_claims() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    text = " ".join(packet["non_claims"])
    assert "not a signed release candidate" in text
    assert "cannot satisfy" in text
