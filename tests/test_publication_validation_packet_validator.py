import json
from pathlib import Path

from scripts.validate_publication_validation_packet import validate_packet

ROOT = Path(__file__).resolve().parents[1]


def _packet() -> dict[str, object]:
    return json.loads((ROOT / "docs/publication-validation-packet-20260825.json").read_text())


def test_publication_packet_validator_passes() -> None:
    assert validate_packet(_packet(), root=ROOT) == ()


def test_publication_packet_validator_rejects_publication_ready() -> None:
    packet = _packet()
    packet["publication_ready"] = True
    assert any("publication_ready" in error for error in validate_packet(packet, root=ROOT))
