import json
from pathlib import Path

from scripts.validate_v1_release_candidate_packet import validate_packet

ROOT = Path(__file__).resolve().parents[1]


def _packet() -> dict[str, object]:
    return json.loads((ROOT / "docs/v1-release-candidate-packet-20260825.json").read_text())


def test_v1_candidate_packet_validator_passes() -> None:
    assert validate_packet(_packet()) == ()


def test_v1_candidate_packet_validator_rejects_promotion() -> None:
    packet = _packet()
    packet["promotion_allowed"] = True
    assert any("promotion_allowed" in error for error in validate_packet(packet))


def test_v1_candidate_packet_validator_rejects_missing_soak_gate() -> None:
    packet = _packet()
    packet["required_external_or_elapsed_evidence"] = ["preservation"]
    assert any("30-day exact-RC soak" in error for error in validate_packet(packet))
