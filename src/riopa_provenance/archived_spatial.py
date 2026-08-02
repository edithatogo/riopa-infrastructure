"""Offline construction of provenance records and spatial projections.

This module accepts only a content-pinned Hugging Face archive packet.  The
ArcGIS service URL in the archived manifest is evidence, never an acquisition
target.
"""

from __future__ import annotations

import gzip
import json
import re
import shutil
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote

import httpx
from shapely import to_wkb

from .hashing import sha256_bytes, sha256_file, sha256_json
from .spatial import SpatialMaterialization, arcgis_features_to_geojson, materialize_features

_REVISION = re.compile(r"^[0-9a-f]{40}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class ArchivedPacketError(ValueError):
    """Raised when immutable archive evidence is incomplete or inconsistent."""


def _safe_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ArchivedPacketError(f"unsafe archive path: {value!r}")
    return path


@dataclass(frozen=True)
class ArchivedPacketDescriptor:
    source_id: str
    dataset_repository: str
    packet_revision: str
    receipt_revision: str
    manifest_path: str
    manifest_sha256: str
    checksums_sha256: str
    receipt_path: str
    receipt_sha256: str
    expected_features: int
    expected_pages: int
    expected_null_geometries: int

    def validate(self) -> None:
        if not _REPOSITORY.fullmatch(self.dataset_repository):
            raise ArchivedPacketError("dataset repository must be an owner/name pair")
        for name in ("packet_revision", "receipt_revision"):
            if not _REVISION.fullmatch(getattr(self, name)):
                raise ArchivedPacketError(f"{name} must be a lower-case 40-character commit")
        for name in ("manifest_sha256", "checksums_sha256", "receipt_sha256"):
            if not _DIGEST.fullmatch(getattr(self, name)):
                raise ArchivedPacketError(f"{name} must be a lower-case SHA-256 digest")
        _safe_path(self.manifest_path)
        _safe_path(self.receipt_path)
        if not self.source_id.startswith("urn:riopa:source:"):
            raise ArchivedPacketError("source_id must be a RIOPA source URN")
        if min(
            self.expected_features,
            self.expected_pages,
            self.expected_null_geometries,
        ) < 0:
            raise ArchivedPacketError("expected counts must be non-negative")

    @classmethod
    def from_path(cls, path: str | Path) -> ArchivedPacketDescriptor:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        if value.pop("schema_version", None) != "1.0.0":
            raise ArchivedPacketError("descriptor schema_version must be 1.0.0")
        descriptor = cls(**value)
        descriptor.validate()
        return descriptor

    def as_record(self) -> dict[str, Any]:
        return {"schema_version": "1.0.0", **asdict(self)}


@dataclass(frozen=True)
class VerifiedArchivedPacket:
    root: Path
    manifest: dict[str, Any]
    receipt: dict[str, Any]
    files: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class ArchivedProjectionResult:
    feature_count: int
    capture_record_count: int
    source_record_path: Path
    capture_records_path: Path
    records_manifest_path: Path
    projection_record_path: Path
    projection_record: dict[str, Any]
    materialization: SpatialMaterialization


def immutable_hugging_face_url(
    descriptor: ArchivedPacketDescriptor,
    path: str,
    *,
    revision: str | None = None,
) -> str:
    """Build an immutable archive URL; branches and live endpoints are rejected."""

    descriptor.validate()
    selected = revision or descriptor.packet_revision
    if not _REVISION.fullmatch(selected):
        raise ArchivedPacketError("archive revision must be a lower-case 40-character commit")
    safe = _safe_path(path)
    encoded = "/".join(quote(part, safe="") for part in safe.parts)
    return (
        f"https://huggingface.co/datasets/{descriptor.dataset_repository}/"
        f"resolve/{selected}/{encoded}"
    )


def _default_fetch(url: str) -> bytes:
    response = httpx.get(url, follow_redirects=True, timeout=120.0)
    response.raise_for_status()
    return response.content


def _read_json_bytes(body: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ArchivedPacketError(f"{label} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise ArchivedPacketError(f"{label} must be a JSON object")
    return value


def _expect_digest(body: bytes, expected: str, label: str) -> None:
    actual = sha256_bytes(body)
    if actual != expected:
        raise ArchivedPacketError(
            f"{label} digest mismatch: expected {expected}, observed {actual}"
        )


def _verify_file_body(body: bytes, item: Mapping[str, Any]) -> None:
    relative = str(item["path"])
    _expect_digest(body, str(item["sha256"]), f"archive file {relative}")
    if item.get("bytes") != len(body):
        raise ArchivedPacketError(f"archive file size mismatch: {relative}")
    if item.get("content_encoding") == "gzip":
        try:
            uncompressed = gzip.decompress(body)
        except (OSError, EOFError) as exc:
            raise ArchivedPacketError(f"invalid gzip archive member: {relative}") from exc
        if item.get("uncompressed_bytes") != len(uncompressed):
            raise ArchivedPacketError(f"uncompressed file size mismatch: {relative}")
        expected = item.get("uncompressed_sha256")
        if not isinstance(expected, str) or sha256_bytes(uncompressed) != expected:
            raise ArchivedPacketError(f"uncompressed file digest mismatch: {relative}")


def _manifest_files(manifest: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    integrity = manifest.get("integrity")
    raw_files = integrity.get("files") if isinstance(integrity, Mapping) else None
    if not isinstance(raw_files, list) or not raw_files:
        raise ArchivedPacketError("manifest has no integrity.files records")
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in raw_files:
        if not isinstance(raw, dict) or not isinstance(raw.get("path"), str):
            raise ArchivedPacketError("manifest file record is malformed")
        path = str(_safe_path(raw["path"]))
        if path in seen:
            raise ArchivedPacketError(f"duplicate manifest file path: {path}")
        seen.add(path)
        if not _DIGEST.fullmatch(str(raw.get("sha256", ""))):
            raise ArchivedPacketError(f"manifest file has invalid digest: {path}")
        output.append(raw)
    return tuple(output)


def _verify_manifest_contract(
    descriptor: ArchivedPacketDescriptor, manifest: Mapping[str, Any]
) -> tuple[dict[str, Any], ...]:
    if manifest.get("schema") != "open-social-data.arcgis-archive.v1":
        raise ArchivedPacketError("unsupported archive manifest schema")
    scope = manifest.get("scope")
    integrity = manifest.get("integrity")
    if not isinstance(scope, Mapping) or not isinstance(integrity, Mapping):
        raise ArchivedPacketError("archive manifest scope or integrity is missing")
    expected = {
        "captured_features": descriptor.expected_features,
        "pages": descriptor.expected_pages,
        "null_geometries": descriptor.expected_null_geometries,
    }
    for key, count in expected.items():
        if scope.get(key) != count:
            raise ArchivedPacketError(
                f"manifest {key} mismatch: expected {count}, observed {scope.get(key)}"
            )
    if integrity.get("source_stable_during_capture") is not True:
        raise ArchivedPacketError("archive source was not stable during capture")
    files = _manifest_files(manifest)
    payload_identity = [
        {"path": item["path"], "sha256": item["sha256"]} for item in files
    ]
    if integrity.get("payload_set_sha256") != sha256_json(payload_identity):
        raise ArchivedPacketError("manifest payload-set digest mismatch")
    return files


def _verify_receipt(
    descriptor: ArchivedPacketDescriptor, receipt: Mapping[str, Any]
) -> None:
    if receipt.get("dataset") != descriptor.dataset_repository:
        raise ArchivedPacketError("receipt dataset does not bind the descriptor")
    if receipt.get("packet_revision") != descriptor.packet_revision:
        raise ArchivedPacketError("receipt packet revision does not bind the descriptor")
    if receipt.get("manifest_sha256") != descriptor.manifest_sha256:
        raise ArchivedPacketError("receipt manifest digest does not bind the descriptor")
    if receipt.get("credentials_recorded") is not False:
        raise ArchivedPacketError("receipt must state credentials_recorded=false")


def _parse_checksums(body: bytes) -> dict[str, str]:
    output: dict[str, str] = {}
    try:
        lines = body.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ArchivedPacketError("checksums file is not UTF-8") from exc
    for line in lines:
        if not line.strip():
            continue
        digest, separator, path = line.partition("  ")
        if not separator or not _DIGEST.fullmatch(digest):
            raise ArchivedPacketError("checksums file has a malformed line")
        safe = str(_safe_path(path))
        if safe in output:
            raise ArchivedPacketError(f"duplicate checksum path: {safe}")
        output[safe] = digest
    return output


def download_archived_packet(
    descriptor: ArchivedPacketDescriptor,
    destination: str | Path,
    *,
    fetch: Callable[[str], bytes] = _default_fetch,
) -> VerifiedArchivedPacket:
    """Download and verify a packet exclusively through immutable archive URLs."""

    descriptor.validate()
    manifest_body = fetch(immutable_hugging_face_url(descriptor, descriptor.manifest_path))
    _expect_digest(manifest_body, descriptor.manifest_sha256, "manifest")
    manifest = _read_json_bytes(manifest_body, "manifest")
    files = _verify_manifest_contract(descriptor, manifest)
    prefix = descriptor.manifest_path.rsplit("/", 1)[0]
    checksums_body = fetch(immutable_hugging_face_url(descriptor, f"{prefix}/checksums.sha256"))
    _expect_digest(checksums_body, descriptor.checksums_sha256, "checksums")
    checksums = _parse_checksums(checksums_body)
    receipt_body = fetch(
        immutable_hugging_face_url(
            descriptor, descriptor.receipt_path, revision=descriptor.receipt_revision
        )
    )
    _expect_digest(receipt_body, descriptor.receipt_sha256, "receipt")
    receipt = _read_json_bytes(receipt_body, "receipt")
    _verify_receipt(descriptor, receipt)

    target = Path(destination).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{target.name}-", dir=target.parent))
    try:
        (temporary / "manifest.json").write_bytes(manifest_body)
        (temporary / "checksums.sha256").write_bytes(checksums_body)
        (temporary / "receipt.json").write_bytes(receipt_body)
        for item in files:
            relative = str(_safe_path(item["path"]))
            body = fetch(immutable_hugging_face_url(descriptor, f"{prefix}/{relative}"))
            _verify_file_body(body, item)
            if checksums.get(relative) != item["sha256"]:
                raise ArchivedPacketError(f"checksums binding mismatch: {relative}")
            path = temporary / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
        if checksums.get("manifest.json") != descriptor.manifest_sha256:
            raise ArchivedPacketError("checksums do not bind manifest.json")
        if target.exists():
            shutil.rmtree(target)
        temporary.replace(target)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return verify_archived_packet(descriptor, target)


def verify_archived_packet(
    descriptor: ArchivedPacketDescriptor, packet_root: str | Path
) -> VerifiedArchivedPacket:
    """Verify an already-downloaded packet without any network access."""

    descriptor.validate()
    root = Path(packet_root).resolve()
    manifest_body = (root / "manifest.json").read_bytes()
    _expect_digest(manifest_body, descriptor.manifest_sha256, "manifest")
    checksums_body = (root / "checksums.sha256").read_bytes()
    _expect_digest(checksums_body, descriptor.checksums_sha256, "checksums")
    receipt_body = (root / "receipt.json").read_bytes()
    _expect_digest(receipt_body, descriptor.receipt_sha256, "receipt")
    manifest = _read_json_bytes(manifest_body, "manifest")
    receipt = _read_json_bytes(receipt_body, "receipt")
    files = _verify_manifest_contract(descriptor, manifest)
    _verify_receipt(descriptor, receipt)
    checksums = _parse_checksums(checksums_body)
    for item in files:
        path = root / str(_safe_path(item["path"]))
        if not path.is_file():
            raise ArchivedPacketError(f"packet file digest mismatch: {item['path']}")
        _verify_file_body(path.read_bytes(), item)
        if checksums.get(item["path"]) != item["sha256"]:
            raise ArchivedPacketError(f"checksums binding mismatch: {item['path']}")
    return VerifiedArchivedPacket(root, manifest, receipt, files)


def _read_gzip_json(packet: VerifiedArchivedPacket, relative: str) -> dict[str, Any]:
    try:
        return _read_json_bytes(gzip.decompress((packet.root / relative).read_bytes()), relative)
    except (OSError, EOFError) as exc:
        raise ArchivedPacketError(f"invalid gzip archive member: {relative}") from exc


def _envelope(kind: str, record: dict[str, Any]) -> dict[str, Any]:
    digest = sha256_json(record)
    id_field = {"source": "record_id", "capture": "capture_id"}.get(
        kind, f"{kind}_id"
    )
    return {
        id_field: f"urn:riopa:{kind.replace('_', '-')}:sha256:{digest}",
        "record_sha256": digest,
        "record": record,
    }


def _write_content_addressed(
    root: Path, kind: str, record: dict[str, Any]
) -> tuple[dict[str, Any], Path]:
    envelope = _envelope(kind, record)
    digest = envelope["record_sha256"]
    path = root / f"{kind.replace('_', '-')}-records" / "sha256" / digest[:2] / f"{digest}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return envelope, path


def _capture_record(
    descriptor: ArchivedPacketDescriptor,
    manifest: Mapping[str, Any],
    item: Mapping[str, Any],
) -> dict[str, Any]:
    receipt = next(
        (
            value
            for value in manifest.get("retrieval_receipts", [])
            if isinstance(value, Mapping) and value.get("artifact") == item["path"]
        ),
        None,
    )
    if receipt is None:
        raise ArchivedPacketError(f"archive artifact has no retrieval receipt: {item['path']}")
    return {
        "schema_version": "1.0.0",
        "record_type": "archived_http_capture",
        "source_id": descriptor.source_id,
        "archive": {
            "dataset_repository": descriptor.dataset_repository,
            "packet_revision": descriptor.packet_revision,
            "manifest_sha256": descriptor.manifest_sha256,
        },
        "artifact": dict(item),
        "original_retrieval_receipt": dict(receipt),
    }


def build_archived_arcgis_projection(
    descriptor: ArchivedPacketDescriptor,
    *,
    packet_root: str | Path,
    records_dir: str | Path,
    output_dir: str | Path,
    base_name: str = "features",
) -> ArchivedProjectionResult:
    """Build content-addressed records and a normalized, repair-free projection."""

    packet = verify_archived_packet(descriptor, packet_root)
    records = Path(records_dir).resolve()
    records.mkdir(parents=True, exist_ok=True)
    source = packet.manifest["source"]
    source_record = {
        "schema_version": "1.0.0",
        "source_id": descriptor.source_id,
        "name": source["dataset"],
        "publisher": {"name": source["authority"], "url": "https://www.stats.govt.nz/"},
        "jurisdiction": "New Zealand",
        "source_type": "web-service",
        "authoritativeness": "authoritative",
        "access": {
            "landing_page": "https://datafinder.stats.govt.nz/",
            "endpoint": None,
            "mechanism": "immutable archived packet",
            "authentication": "none",
            "terms_url": source.get("license_url"),
        },
        "rights": {
            "access_status": "public",
            "redistribution_status": "attribution-required",
            "licence_status": "declared",
            "spdx_or_uri": source.get("license_url") or source.get("license"),
            "attribution_text": source.get("authority"),
            "notes": "Rights assertion copied from the verified archive manifest.",
            "reviewed_at": packet.manifest["completed_at"],
        },
        "spatial_coverage": "New Zealand",
        "temporal_coverage": source.get("edition"),
        "update_pattern": None,
        "discovered_at": packet.manifest["started_at"],
        "metadata_snapshot_sha256": descriptor.manifest_sha256,
        "governance_triggers": [],
        "governance_decision_refs": [],
        "notes": "Constructed exclusively from a content-pinned archived packet.",
    }
    _, source_record_path = _write_content_addressed(records, "source", source_record)

    capture_envelopes: list[dict[str, Any]] = []
    capture_by_path: dict[str, str] = {}
    for item in packet.files:
        envelope, _ = _write_content_addressed(
            records, "capture", _capture_record(descriptor, packet.manifest, item)
        )
        capture_envelopes.append(envelope)
        capture_by_path[item["path"]] = envelope["capture_id"]
    capture_envelopes.sort(key=lambda value: value["record"]["artifact"]["path"])
    capture_records_path = records / "capture-records.jsonl"
    capture_records_path.write_text(
        "".join(json.dumps(value, sort_keys=True) + "\n" for value in capture_envelopes),
        encoding="utf-8",
    )

    layer = _read_gzip_json(packet, "raw/layer.json.gz")
    before = _read_gzip_json(packet, "raw/object-ids.json.gz")
    after = _read_gzip_json(packet, "raw/object-ids-post.json.gz")
    oid_field = before.get("objectIdFieldName") or layer.get("objectIdField")
    before_ids = before.get("objectIds")
    after_ids = after.get("objectIds")
    if not isinstance(oid_field, str) or not isinstance(before_ids, list):
        raise ArchivedPacketError("object ID inventory is malformed")
    if before_ids != after_ids or len(before_ids) != len(set(before_ids)):
        raise ArchivedPacketError("object ID inventories are unstable or non-unique")
    normalized_ids = sorted(before_ids)
    expected_object_digest = packet.manifest["integrity"].get("object_ids_sha256")
    if expected_object_digest != sha256_json(normalized_ids):
        raise ArchivedPacketError("object ID inventory digest mismatch")

    page_items = sorted(
        (item for item in packet.files if item["path"].startswith("raw/features/page-")),
        key=lambda item: item["path"],
    )
    if len(page_items) != descriptor.expected_pages:
        raise ArchivedPacketError("feature page count does not match descriptor")
    features: list[dict[str, Any]] = []
    observed_ids: list[Any] = []
    crs: str | None = None
    for item in page_items:
        payload = _read_gzip_json(packet, item["path"])
        page_features, page_crs = arcgis_features_to_geojson(
            [payload], object_id_field=oid_field, repair_invalid=False
        )
        page_capture_id = capture_by_path[item["path"]]
        for feature in page_features:
            observed_ids.append(feature["properties"].get(oid_field))
            feature["capture_ids"] = [page_capture_id]
            geometry = feature["geometry_object"]
            feature["source_geometry_sha256"] = (
                sha256_bytes(to_wkb(geometry)) if geometry is not None else None
            )
        features.extend(page_features)
        crs = crs or page_crs
    if observed_ids != normalized_ids or len(features) != descriptor.expected_features:
        raise ArchivedPacketError("feature pages do not exactly match the object ID inventory")
    null_count = sum(feature["geometry_object"] is None for feature in features)
    if null_count != descriptor.expected_null_geometries:
        raise ArchivedPacketError("null geometry count does not match descriptor")

    materialization = materialize_features(
        features,
        output_dir=output_dir,
        source_id=descriptor.source_id,
        layer_id=str(source.get("service_item_id") or source.get("arcgis_item_id")),
        capture_ids=[capture_by_path[item["path"]] for item in page_items],
        crs=crs,
        object_id_field=oid_field,
        base_name=base_name,
        repair_invalid=False,
    )
    projection_record = {
        "schema_version": "1.0.0",
        "record_type": "archived_spatial_projection",
        "source_id": descriptor.source_id,
        "archive_only": True,
        "live_endpoint_contacted": False,
        "dataset_repository": descriptor.dataset_repository,
        "packet_revision": descriptor.packet_revision,
        "manifest_sha256": descriptor.manifest_sha256,
        "source_record_sha256": sha256_json(source_record),
        "capture_record_ids": [value["capture_id"] for value in capture_envelopes],
        "feature_count": len(features),
        "object_id_field": oid_field,
        "object_ids_sha256": expected_object_digest,
        "crs": crs,
        "geometry_policy": "preserve translated source geometry; never repair implicitly",
        "normalized_semantic_sha256": sha256_json(
            [
                {
                    "id": str(feature["id"]),
                    "properties": feature["properties"],
                    "geometry_sha256": feature["source_geometry_sha256"],
                    "capture_ids": feature["capture_ids"],
                }
                for feature in sorted(features, key=lambda value: str(value["id"]))
            ]
        ),
        "materialization": {
            "geoparquet_sha256": materialization.geoparquet_sha256,
            "geoparquet_size_bytes": materialization.geoparquet_path.stat().st_size,
            "duckdb_sha256": materialization.duckdb_sha256,
            "duckdb_size_bytes": materialization.duckdb_path.stat().st_size,
            "quality_sha256": sha256_file(materialization.quality_report_path),
        },
    }
    projection_envelope, projection_record_path = _write_content_addressed(
        records, "projection", projection_record
    )
    records_manifest = {
        "schema_version": "1.0.0",
        "record_type": "archived_spatial_records_manifest",
        "source_record": str(source_record_path.relative_to(records)),
        "source_record_sha256": sha256_file(source_record_path),
        "capture_records": capture_records_path.name,
        "capture_records_sha256": sha256_file(capture_records_path),
        "projection_record": str(projection_record_path.relative_to(records)),
        "projection_record_sha256": sha256_file(projection_record_path),
        "projection_id": projection_envelope["projection_id"],
    }
    records_manifest["manifest_sha256"] = sha256_json(records_manifest)
    records_manifest_path = records / "records-manifest.json"
    records_manifest_path.write_text(
        json.dumps(records_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return ArchivedProjectionResult(
        feature_count=len(features),
        capture_record_count=len(capture_envelopes),
        source_record_path=source_record_path,
        capture_records_path=capture_records_path,
        records_manifest_path=records_manifest_path,
        projection_record_path=projection_record_path,
        projection_record=projection_record,
        materialization=materialization,
    )
