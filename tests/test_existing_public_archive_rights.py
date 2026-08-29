import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text())


def test_existing_public_packets_are_revision_and_rights_bound() -> None:
    receipt = _load("docs/existing-public-archive-rights-qualification-20260829.json")
    packets = receipt["packets"]

    assert len(packets) == 4
    assert all(len(packet["packet_revision"]) == 40 for packet in packets)
    assert all(len(packet["manifest_sha256"]) == 64 for packet in packets)
    assert {packet["licence"] for packet in packets} == {"CC-BY-3.0-NZ", "CC-BY-4.0"}
    assert receipt["qualification"]["public_payloads"] == "permitted with attribution"


def test_archive_descriptors_match_the_qualification_receipt() -> None:
    receipt = _load("docs/existing-public-archive-rights-qualification-20260829.json")
    descriptors = {
        descriptor["source_id"]: descriptor
        for descriptor in (
            _load("config/archive-sources/hamilton-food-premise-register-2026.json"),
            _load("config/archive-sources/marlborough-food-premise-licences-2026.json"),
            _load("config/archive-sources/stats-nz-meshblock-2026.json"),
            _load("config/archive-sources/stats-nz-subnational-population-2025.json"),
        )
    }

    for packet in receipt["packets"]:
        descriptor = descriptors[packet["source_id"]]
        assert descriptor["packet_revision"] == packet["packet_revision"]
        assert descriptor["rights_status"] == "public-payload-qualified"
        assert descriptor["licence"] == packet["licence"]
        assert descriptor["rights_evidence_url"] == packet["rights_evidence_url"]


def test_qualification_retains_non_rights_boundaries() -> None:
    receipt = _load("docs/existing-public-archive-rights-qualification-20260829.json")
    non_claims = " ".join(receipt["non_claims"])

    assert "national completeness" in non_claims
    assert "bounded regional" in non_claims
    assert "provisional edition" in non_claims
    assert "third-party material" in non_claims
