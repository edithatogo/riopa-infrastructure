import json
from pathlib import Path

PACKET = Path("docs/publication-validation-packet-20260825.json")


def test_publication_packet_is_doi_ready_but_not_published() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    assert packet["status"] == "doi-ready-preparation-only"
    assert packet["publication_ready"] is False
    assert packet["software"]["runtime"] == "Python 3.14"
    assert "citation_identifier" in packet["citation_fields"]
    assert any("persistent identifier" in step for step in packet["preservation_sequence"])


def test_publication_packet_preserves_external_and_elapsed_gates() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    pending = " ".join(packet["pending_gates"])
    assert "external operator/user reproduction" in pending
    assert "elapsed beta/RC qualification" in pending
    assert "accountable release-authority decision" in pending
    assert "not a DOI" in " ".join(packet["non_claims"])
