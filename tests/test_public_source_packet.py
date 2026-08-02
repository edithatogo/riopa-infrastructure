import json
from pathlib import Path

import pytest

from scripts.build_public_source_packet import build_packet


def test_metadata_only_source_emits_negative_receipt(tmp_path: Path) -> None:
    manifest = build_packet(
        tmp_path,
        [
            {
                "source_id": "urn:test:source",
                "landing_url": "https://example.test/source",
                "status": "metadata-only",
            }
        ],
    )
    assert manifest["payloads_acquired"] is False
    receipt = next(tmp_path.glob("negative-receipt-*.json"))
    data = json.loads(receipt.read_text())
    assert data["non_claim"] == "No source payload was acquired or approved."


def test_captured_source_requires_hash(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="payload_sha256"):
        build_packet(
            tmp_path,
            [
                {
                    "source_id": "urn:test:source",
                    "landing_url": "https://example.test",
                    "status": "captured",
                }
            ],
        )


def test_manifest_digest_is_deterministic_for_same_entries(tmp_path: Path) -> None:
    source = [
        {"source_id": "urn:test:source", "landing_url": "https://example.test", "status": "blocked"}
    ]
    left = build_packet(tmp_path / "a", source)
    right = build_packet(tmp_path / "b", source)
    assert left["manifest_sha256"] == right["manifest_sha256"]


def test_committed_campaign_packet_is_linked_and_fail_closed() -> None:
    root = Path(__file__).parents[1]
    campaign = json.loads((root / "docs/operational-evidence-campaign-20260802.json").read_text())
    lane = next(item for item in campaign["lanes"] if item["id"] == "public-source-packets")
    manifest_path = root / lane["artifact"]
    manifest = json.loads(manifest_path.read_text())
    assert manifest["payloads_acquired"] is False
    assert manifest["non_claims"]
    assert len(list(manifest_path.parent.glob("negative-receipt-*.json"))) == len(
        manifest["sources"]
    )
