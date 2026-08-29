import json
from pathlib import Path

from scripts.validate_publication_validation_packet import validate_packet

ROOT = Path(__file__).resolve().parents[1]


def _packet() -> dict[str, object]:
    return json.loads((ROOT / "docs/publication-validation-packet-20260825.json").read_text())


def test_publication_packet_validator_passes() -> None:
    assert validate_packet(_packet(), root=ROOT) == ()


def test_publication_packet_validator_resolves_relative_root() -> None:
    assert validate_packet(_packet(), root=Path(".")) == ()


def test_publication_packet_validator_rejects_publication_ready() -> None:
    packet = _packet()
    packet["publication_ready"] = True
    assert any("publication_ready" in error for error in validate_packet(packet, root=ROOT))


def test_publication_packet_validator_rejects_scope_expansion() -> None:
    packet = _packet()
    packet["scope"] = "national-operational-release"
    errors = validate_packet(packet, root=ROOT)
    assert any("scope must remain" in error for error in errors)


def test_publication_packet_validator_rejects_unsafe_contract_path() -> None:
    packet = _packet()
    packet["metadata_contracts"] = ["../outside.json"]
    errors = validate_packet(packet, root=ROOT)
    assert any("escapes root" in error for error in errors)


def test_publication_packet_validator_rejects_non_string_gate_and_claim_values() -> None:
    packet = _packet()
    packet["pending_gates"] = [{"gate": "protected artifact attestations"}]
    packet["non_claims"] = [{"claim": "not a DOI"}]
    errors = validate_packet(packet, root=ROOT)
    assert "pending_gates omits protected artifact attestations" in errors
    assert "non_claims must retain unpublished/external-acceptance boundaries" in errors


def test_publication_packet_validator_requires_complete_citation_fields() -> None:
    packet = _packet()
    packet["citation_fields"] = ["title"]
    errors = validate_packet(packet, root=ROOT)
    assert any("citation_fields omit required fields" in error for error in errors)


def test_publication_packet_validator_rejects_malformed_citation_fields() -> None:
    packet = _packet()
    packet["citation_fields"] = ["title", None]
    errors = validate_packet(packet, root=ROOT)
    assert "citation_fields must be a non-empty list of strings" in errors
