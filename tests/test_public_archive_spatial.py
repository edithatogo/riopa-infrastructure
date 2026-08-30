from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pytest
from pyarrow import parquet as pq

from riopa_provenance.hashing import sha256_bytes, sha256_file, sha256_json
from riopa_provenance.public_archive_spatial import (
    PublicArchiveDescriptor,
    PublicArchivePacketError,
    materialize_public_arcgis_packet,
    verify_public_archive_packet,
)

REVISION = "001137c0df64e9f8a7b0539fd0286a7cd5819ce7"


def descriptor(packet: Path, *, revision: str = REVISION) -> PublicArchiveDescriptor:
    rights_path = next((packet / "captures").glob("*000000000014.json"))
    rights_capture = json.loads(rights_path.read_text())
    return PublicArchiveDescriptor(
        dataset_repository="edithatogo/riopa-public-data-archive",
        packet_revision=revision,
        packet_path="snapshots/wcc-churton-park-village-supermarket-20260829",
        manifest_sha256=sha256_file(packet / "manifest.json"),
        source_id="urn:riopa:source:wcc:churton-park-village-supermarket",
        licence="CC-BY-3.0-NZ",
        attribution="Wellington City Council",
        rights_capture_id=rights_capture["capture_id"],
        rights_object_sha256=rights_capture["object"]["sha256"],
        rights_licence_text="CC-BY-3.0-NZ",
    )


@pytest.fixture
def packet(tmp_path: Path) -> Path:
    target = tmp_path / "packet"
    (target / "captures").mkdir(parents=True)
    (target / "objects/sha256").mkdir(parents=True)
    source_id = "urn:riopa:source:wcc:churton-park-village-supermarket"
    capture_set_id = "urn:uuid:00000000-0000-4000-8000-000000000001"
    payloads = {
        "metadata": {
            "objectIdField": "OBJECTID",
            "extent": {"spatialReference": {"wkid": 4326}},
        },
        "count-before": {"count": 1},
        "count-after": {"count": 1},
        "page": {
            "spatialReference": {"wkid": 4326},
            "features": [
                {
                    "attributes": {"OBJECTID": 1, "NAME": "Synthetic district-plan fixture"},
                    "geometry": {
                        "rings": [
                            [
                                [174.8, -41.2],
                                [174.81, -41.2],
                                [174.81, -41.19],
                                [174.8, -41.19],
                                [174.8, -41.2],
                            ]
                        ]
                    },
                }
            ],
        },
        "licence": {
            "licenseInfo": "CC-BY-3.0-NZ",
            "accessInformation": "Wellington City Council",
        },
    }
    capture_ids = {
        name: f"urn:uuid:00000000-0000-4000-8000-{index:012d}"
        for index, name in enumerate(payloads, start=10)
    }
    files: list[dict[str, object]] = []
    stored_objects: set[str] = set()
    for name, payload in payloads.items():
        body = json.dumps(payload, sort_keys=True).encode()
        digest = sha256_bytes(body)
        object_path = target / "objects/sha256" / digest
        object_path.write_bytes(body)
        if digest not in stored_objects:
            files.append(
                {
                    "path": f"objects/sha256/{digest}",
                    "sha256": digest,
                    "bytes": len(body),
                }
            )
            stored_objects.add(digest)
        capture_id = capture_ids[name]
        capture = {
            "schema_version": "1.0.0",
            "record_type": "http_capture",
            "capture_id": capture_id,
            "source_id": source_id,
            "endpoint_id": f"urn:riopa:endpoint:fixture:{name}",
            "retrieved_at": "2026-08-29T00:00:00Z",
            "request": {"method": "GET", "url": f"https://example.test/{name}"},
            "response": {"status_code": 200, "media_type": "application/json"},
            "object": {
                "sha256": digest,
                "size_bytes": len(body),
                "storage_path": f"objects/sha256/{digest[:2]}/{digest}",
            },
        }
        capture_path = target / "captures" / f"{capture_id.removeprefix('urn:uuid:')}.json"
        capture_path.write_text(json.dumps(capture, indent=2) + "\n")
        files.append(
            {
                "path": str(capture_path.relative_to(target)),
                "sha256": sha256_file(capture_path),
                "bytes": capture_path.stat().st_size,
            }
        )
    capture_set = {
        "schema_version": "1.1.0",
        "record_type": "arcgis_layer_capture_set",
        "capture_set_id": capture_set_id,
        "source_id": source_id,
        "service_url": "https://example.test/arcgis/MapServer",
        "layer_id": 152,
        "metadata_capture_id": capture_ids["metadata"],
        "count_capture_ids": [capture_ids["count-before"], capture_ids["count-after"]],
        "object_ids_capture_id": None,
        "page_capture_ids": [capture_ids["page"]],
        "feature_count": 1,
        "object_id_field": None,
        "page_size": 2000,
        "pagination_strategy": "offset",
        "query": {"where": "OBJECTID >= 0", "out_fields": "*"},
    }
    capture_set["manifest_sha256"] = sha256_json(capture_set)
    capture_set_path = target / "capture-set.json"
    capture_set_path.write_text(json.dumps(capture_set, indent=2) + "\n")
    files.append(
        {
            "path": "capture-set.json",
            "sha256": sha256_file(capture_set_path),
            "bytes": capture_set_path.stat().st_size,
        }
    )
    files.sort(key=lambda item: str(item["path"]))
    manifest = {
        "schema_version": "1.0.0",
        "record_type": "riopa_public_source_archive_packet",
        "source_id": source_id,
        "capture_set_id": capture_set_id,
        "captured_at": "2026-08-29",
        "licence": "CC-BY-3.0-NZ",
        "attribution": "Wellington City Council",
        "publication_status": "public-rights-qualified",
        "non_claims": [
            "No operative district-plan status is inferred.",
            "The feature does not establish current supermarket operation.",
        ],
        "files": files,
    }
    manifest_path = target / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    checksums = {str(item["path"]): str(item["sha256"]) for item in files}
    checksums["manifest.json"] = sha256_file(manifest_path)
    (target / "checksums.sha256").write_text(
        "".join(f"{digest}  {name}\n" for name, digest in sorted(checksums.items()))
    )
    return target


def test_wcc_packet_materializes_offline_without_geometry_repair(
    packet: Path, tmp_path: Path
) -> None:
    result = materialize_public_arcgis_packet(
        packet,
        descriptor=descriptor(packet),
        output_dir=tmp_path / "materialized",
        records_dir=tmp_path / "records",
        base_name="wcc",
    )
    assert result.feature_count == 1
    evidence = json.loads(result.evidence_path.read_text())
    assert evidence["rights"]["licence"] == "CC-BY-3.0-NZ"
    assert evidence["canonical_features"][0]["valid_time"]["status"] == "unknown-not-imputed"
    assert evidence["canonical_features"][0]["source_object_id"] == "1"
    assert (
        evidence["canonical_features"][0]["capture_ids"]
        == evidence["capture_inputs"]["page_capture_ids"]
    )
    assert "sha256" not in evidence["duckdb"]
    assert len(evidence["duckdb"]["semantic_sha256"]) == 64
    assert evidence["geometry_policy"].endswith("implicit repair disabled")
    assert pq.read_table(result.materialization.geoparquet_path).num_rows == 1
    with duckdb.connect(str(result.materialization.duckdb_path), read_only=True) as connection:
        assert connection.execute("select count(*) from features").fetchone() == (1,)


@pytest.mark.parametrize("mutation", ["digest", "missing", "unsafe", "capture-reference"])
def test_public_packet_verifier_fails_closed(packet: Path, mutation: str) -> None:
    manifest_path = packet / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if mutation == "digest":
        (packet / manifest["files"][0]["path"]).write_text("tampered")
    elif mutation == "missing":
        (packet / manifest["files"][-1]["path"]).unlink()
    elif mutation == "unsafe":
        manifest["files"][0]["path"] = "../capture-set.json"
        manifest_path.write_text(json.dumps(manifest))
    else:
        capture_set = json.loads((packet / "capture-set.json").read_text())
        capture_set["page_capture_ids"] = ["urn:uuid:absent"]
        capture_set["manifest_sha256"] = "0" * 64
        (packet / "capture-set.json").write_text(json.dumps(capture_set))
        for item in manifest["files"]:
            if item["path"] == "capture-set.json":
                item["sha256"] = sha256_file(packet / "capture-set.json")
                item["bytes"] = (packet / "capture-set.json").stat().st_size
        manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(PublicArchivePacketError):
        verify_public_archive_packet(packet, descriptor=descriptor(packet))


def test_public_packet_rejects_mutable_revision(packet: Path) -> None:
    with pytest.raises(PublicArchivePacketError, match="immutable"):
        verify_public_archive_packet(packet, descriptor=descriptor(packet, revision="main"))


def test_public_packet_rejects_unbound_manifest(packet: Path) -> None:
    bound = descriptor(packet)
    object.__setattr__(bound, "manifest_sha256", "0" * 64)
    with pytest.raises(PublicArchivePacketError, match="trusted descriptor"):
        verify_public_archive_packet(packet, descriptor=bound)


def test_public_packet_rejects_extra_file(packet: Path) -> None:
    bound = descriptor(packet)
    (packet / "unexpected.txt").write_text("not in manifest")
    with pytest.raises(PublicArchivePacketError, match="missing or extra"):
        verify_public_archive_packet(packet, descriptor=bound)


@pytest.mark.parametrize("unsafe", ["../escape", "nested/name"])
def test_materializer_rejects_unsafe_base_name(packet: Path, tmp_path: Path, unsafe: str) -> None:
    with pytest.raises(PublicArchivePacketError, match="base_name"):
        materialize_public_arcgis_packet(
            packet,
            descriptor=descriptor(packet),
            output_dir=tmp_path / "materialized",
            records_dir=tmp_path / "records",
            base_name=unsafe,
        )


@pytest.mark.parametrize("location", ["output", "records"])
def test_materializer_cannot_write_into_verified_packet(packet: Path, location: str) -> None:
    kwargs = {
        "output_dir": packet / "generated" if location == "output" else packet.parent / "out",
        "records_dir": packet / "records" if location == "records" else packet.parent / "records",
    }
    with pytest.raises(PublicArchivePacketError, match="outside"):
        materialize_public_arcgis_packet(packet, descriptor=descriptor(packet), **kwargs)


@pytest.mark.parametrize("control", ["manifest.json", "checksums.sha256"])
def test_public_packet_rejects_symlinked_control_file(
    packet: Path, tmp_path: Path, control: str
) -> None:
    original = packet / control
    external = tmp_path / f"external-{control}"
    external.write_bytes(original.read_bytes())
    original.unlink()
    original.symlink_to(external)
    with pytest.raises(PublicArchivePacketError, match="symlink"):
        verify_public_archive_packet(packet, descriptor=descriptor(packet))


def test_public_packet_rejects_symlinked_manifest_member(packet: Path, tmp_path: Path) -> None:
    bound = descriptor(packet)
    manifest = json.loads((packet / "manifest.json").read_text())
    member = packet / manifest["files"][0]["path"]
    external = tmp_path / "external-member"
    external.write_bytes(member.read_bytes())
    member.unlink()
    member.symlink_to(external)
    with pytest.raises(PublicArchivePacketError, match="symlink"):
        verify_public_archive_packet(packet, descriptor=bound)


def test_two_rebuilds_have_stable_bytes_or_semantics(packet: Path, tmp_path: Path) -> None:
    results = [
        materialize_public_arcgis_packet(
            packet,
            descriptor=descriptor(packet),
            output_dir=tmp_path / f"materialized-{index}",
            records_dir=tmp_path / f"records-{index}",
            base_name="wcc",
        )
        for index in range(2)
    ]
    evidence = [json.loads(result.evidence_path.read_text()) for result in results]
    assert (
        results[0].materialization.geoparquet_sha256 == results[1].materialization.geoparquet_sha256
    )
    assert evidence[0]["duckdb"]["semantic_sha256"] == evidence[1]["duckdb"]["semantic_sha256"]
    assert evidence[0]["semantic_sha256"] == evidence[1]["semantic_sha256"]
