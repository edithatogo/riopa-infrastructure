from __future__ import annotations

import json
from pathlib import Path

from riopa_provenance.hashing import sha256_json
from riopa_provenance.public_archive_spatial import WCC_PUBLIC_ARCHIVE_DESCRIPTOR

ROOT = Path(__file__).resolve().parents[1]


def test_wcc_public_archive_projection_evidence_is_bounded_and_content_pinned() -> None:
    evidence = json.loads(
        (ROOT / "docs/wcc-public-archive-spatial-projection-20260830.json").read_text()
    )
    assert evidence["dataset_repository"] == "edithatogo/riopa-public-data-archive"
    assert evidence["packet_revision"] == "001137c0df64e9f8a7b0539fd0286a7cd5819ce7"
    assert evidence["packet_manifest_sha256"] == (
        "d263e7c80f395f439ae4cf2e9a3ec6932b1eda3b21a0cfa19ac6cf426d15da52"
    )
    assert evidence["feature_count"] == 1
    assert evidence["rights"] == {
        "licence": "CC-BY-3.0-NZ",
        "attribution": "Wellington City Council",
        "publication_status": "public-rights-qualified",
    }
    feature = evidence["canonical_features"][0]
    assert feature["source_object_id"] == "1"
    assert feature["capture_ids"] == evidence["capture_inputs"]["page_capture_ids"]
    assert feature["valid_time"]["status"] == "unknown-not-imputed"
    assert evidence["geoparquet"]["profile"] == "GeoParquet 1.1.0"
    assert evidence["duckdb"]["reproducibility_class"] == "deterministic-semantics"
    assert "sha256" not in evidence["duckdb"]
    assert len(evidence["capture_inputs"]["rights_capture_ids"]) == 1
    assert any("does not satisfy four-council" in item for item in evidence["non_claims"])
    assert any("does not satisfy the three scheduled" in item for item in evidence["non_claims"])
    assert evidence["semantic_sha256"] == sha256_json(evidence, omit_keys={"semantic_sha256"})


def test_wcc_descriptor_reconciles_to_publication_receipt() -> None:
    receipt = json.loads(
        (ROOT / "docs/public-tier-a-archive-publication-20260829.json").read_text()
    )
    packet = next(
        item
        for item in receipt["packets"]
        if item["source_id"] == WCC_PUBLIC_ARCHIVE_DESCRIPTOR.source_id
    )
    assert receipt["repository"]["id"] == WCC_PUBLIC_ARCHIVE_DESCRIPTOR.dataset_repository
    assert receipt["repository"]["revision"] == WCC_PUBLIC_ARCHIVE_DESCRIPTOR.packet_revision
    assert packet == {
        "source_id": WCC_PUBLIC_ARCHIVE_DESCRIPTOR.source_id,
        "path": WCC_PUBLIC_ARCHIVE_DESCRIPTOR.packet_path,
        "manifest_sha256": WCC_PUBLIC_ARCHIVE_DESCRIPTOR.manifest_sha256,
        "capture_set_id": "urn:uuid:55c2ec4b-f977-4b6a-bce7-844b71c2d93b",
        "feature_count": 1,
        "licence": WCC_PUBLIC_ARCHIVE_DESCRIPTOR.licence,
        "attribution": WCC_PUBLIC_ARCHIVE_DESCRIPTOR.attribution,
    }
