import json
from pathlib import Path

PACKET = Path("docs/v1-agent-operated-journeys-20260825.json")


def test_v1_agent_journey_packet_has_two_distinct_bounded_workflows() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    journeys = packet["journeys"]
    assert packet["status"] == "repository-owned-agent-journey-rehearsal"
    assert packet["promotion_allowed"] is False
    assert len(journeys) == 2
    assert len({journey["journey_id"] for journey in journeys}) == 2
    assert all(journey["status"] == "passed-bounded-local" for journey in journeys)
    assert all(Path(journey["workflow"]).exists() for journey in journeys)
    assert all(Path(journey["evidence"]).exists() for journey in journeys)


def test_v1_agent_journey_packet_preserves_external_and_release_gates() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    text = " ".join(packet["nonclaims"])
    assert "not external participant evidence" in text
    assert "release approval" in text
    assert "factual external operator" in " ".join(packet["open_gates"])
