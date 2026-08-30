"""Verify and materialise immutable RIOPA public ArcGIS archive packets."""

from __future__ import annotations

import json
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import duckdb
import pyarrow.parquet as pq

from .hashing import sha256_file, sha256_json
from .spatial import SpatialMaterialization, materialize_arcgis_capture_set

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_REVISION = re.compile(r"^[0-9a-f]{40}$")
_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_BASE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


class PublicArchivePacketError(ValueError):
    """Raised when a public archive packet is incomplete or inconsistent."""


def _safe_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or "." in path.parts or ".." in path.parts:
        raise PublicArchivePacketError(f"unsafe packet path: {value!r}")
    return path


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PublicArchivePacketError(f"{label} is not readable JSON") from exc
    if not isinstance(value, dict):
        raise PublicArchivePacketError(f"{label} must be an object")
    return value


@dataclass(frozen=True)
class PublicArchiveProjection:
    source_id: str
    packet_revision: str
    feature_count: int
    materialization: SpatialMaterialization
    evidence_path: Path


@dataclass(frozen=True)
class PublicArchiveDescriptor:
    dataset_repository: str
    packet_revision: str
    packet_path: str
    manifest_sha256: str
    source_id: str
    licence: str
    attribution: str
    rights_capture_id: str
    rights_object_sha256: str
    rights_licence_text: str

    def validate(self) -> None:
        if not _REPOSITORY.fullmatch(self.dataset_repository):
            raise PublicArchivePacketError("dataset repository must be an owner/name pair")
        if not _REVISION.fullmatch(self.packet_revision):
            raise PublicArchivePacketError("packet revision must be an immutable commit SHA")
        _safe_path(self.packet_path)
        if not _DIGEST.fullmatch(self.manifest_sha256):
            raise PublicArchivePacketError("manifest digest must be a SHA-256")
        if not self.source_id.startswith("urn:riopa:source:"):
            raise PublicArchivePacketError("source_id must be a RIOPA source URN")
        if not self.licence or not self.attribution:
            raise PublicArchivePacketError("rights binding requires licence and attribution")
        if not self.rights_capture_id.startswith("urn:uuid:"):
            raise PublicArchivePacketError("rights capture identity must be a UUID URN")
        if not _DIGEST.fullmatch(self.rights_object_sha256):
            raise PublicArchivePacketError("rights object digest must be a SHA-256")
        if not self.rights_licence_text:
            raise PublicArchivePacketError("rights licence text must be specified")


WCC_PUBLIC_ARCHIVE_DESCRIPTOR = PublicArchiveDescriptor(
    dataset_repository="edithatogo/riopa-public-data-archive",
    packet_revision="001137c0df64e9f8a7b0539fd0286a7cd5819ce7",
    packet_path="snapshots/wcc-churton-park-village-supermarket-20260829",
    manifest_sha256="d263e7c80f395f439ae4cf2e9a3ec6932b1eda3b21a0cfa19ac6cf426d15da52",
    source_id="urn:riopa:source:wcc:churton-park-village-supermarket",
    licence="CC-BY-3.0-NZ",
    attribution="Wellington City Council",
    rights_capture_id="urn:uuid:29b34e42-2c4d-4fd1-8c03-4c2faecfeca6",
    rights_object_sha256="92c3256907ad0d6453ace881f672a39978c2b06f023c128cafbe445a6518647b",
    rights_licence_text="Creative Commons 3.0 (NZ)",
)


def verify_public_archive_packet(
    packet_root: str | Path, *, descriptor: PublicArchiveDescriptor
) -> dict[str, Any]:
    """Verify packet closure, paths, byte sizes, digests and capture objects."""

    descriptor.validate()
    unresolved_root = Path(packet_root)
    if unresolved_root.is_symlink():
        raise PublicArchivePacketError("packet root must not be a symlink")
    root = unresolved_root.resolve()
    for control_name in ("manifest.json", "checksums.sha256"):
        if (root / control_name).is_symlink():
            raise PublicArchivePacketError(f"packet control file is a symlink: {control_name}")
    if sha256_file(root / "manifest.json") != descriptor.manifest_sha256:
        raise PublicArchivePacketError("packet manifest does not match trusted descriptor")
    manifest = _load_object(root / "manifest.json", "packet manifest")
    if (
        manifest.get("schema_version") != "1.0.0"
        or manifest.get("record_type") != "riopa_public_source_archive_packet"
    ):
        raise PublicArchivePacketError("unsupported public archive packet")
    if manifest.get("publication_status") != "public-rights-qualified":
        raise PublicArchivePacketError("packet is not public-rights-qualified")
    if manifest.get("source_id") != descriptor.source_id:
        raise PublicArchivePacketError("packet source does not match trusted descriptor")
    if manifest.get("licence") != descriptor.licence:
        raise PublicArchivePacketError("packet licence does not match trusted descriptor")
    if manifest.get("attribution") != descriptor.attribution:
        raise PublicArchivePacketError("packet attribution does not match trusted descriptor")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise PublicArchivePacketError("packet manifest has no files")
    seen: set[str] = set()
    by_path: dict[str, dict[str, Any]] = {}
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise PublicArchivePacketError("packet file record is malformed")
        relative = str(_safe_path(item["path"]))
        if relative in seen:
            raise PublicArchivePacketError(f"duplicate packet path: {relative}")
        seen.add(relative)
        digest = item.get("sha256")
        if not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
            raise PublicArchivePacketError(f"invalid packet digest: {relative}")
        candidate = root / relative
        if candidate.is_symlink():
            raise PublicArchivePacketError(f"packet file is a symlink: {relative}")
        path = candidate.resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise PublicArchivePacketError(f"packet file is missing: {relative}")
        if path.stat().st_size != item.get("bytes") or sha256_file(path) != digest:
            raise PublicArchivePacketError(f"packet file integrity mismatch: {relative}")
        by_path[relative] = item

    checksums: dict[str, str] = {}
    for line in (root / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        digest, separator, relative = line.partition("  ")
        safe = str(_safe_path(relative)) if separator else ""
        if not separator or not _DIGEST.fullmatch(digest) or safe in checksums:
            raise PublicArchivePacketError("checksums file is malformed")
        checksums[safe] = digest
    expected_checksums = {name: item["sha256"] for name, item in by_path.items()}
    expected_checksums["manifest.json"] = sha256_file(root / "manifest.json")
    if checksums != expected_checksums:
        raise PublicArchivePacketError("checksums do not exactly close the packet")
    expected_paths = {"manifest.json", "checksums.sha256", *by_path}
    observed_paths = {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    if observed_paths != expected_paths:
        raise PublicArchivePacketError("packet filesystem has missing or extra files")

    capture_set = _load_object(root / "capture-set.json", "capture set")
    if capture_set.get("source_id") != manifest.get("source_id"):
        raise PublicArchivePacketError("capture set source does not match manifest")
    if capture_set.get("capture_set_id") != manifest.get("capture_set_id"):
        raise PublicArchivePacketError("capture set identity does not match manifest")
    expected_set_digest = sha256_json(capture_set, omit_keys={"manifest_sha256"})
    if capture_set.get("manifest_sha256") != expected_set_digest:
        raise PublicArchivePacketError("capture set manifest digest mismatch")

    capture_ids: set[str] = set()
    object_items: dict[str, dict[str, Any]] = {}
    for name, item in by_path.items():
        if not name.startswith("objects/sha256/"):
            continue
        digest = name.rsplit("/", 1)[-1]
        if digest != item["sha256"]:
            raise PublicArchivePacketError(f"object filename/digest mismatch: {name}")
        object_items[digest] = item
    referenced_objects: set[str] = set()
    rights_capture_ids: set[str] = set()
    for relative in sorted(name for name in by_path if name.startswith("captures/")):
        capture = _load_object(root / relative, relative)
        capture_id = capture.get("capture_id")
        if capture.get("record_type") != "http_capture" or not isinstance(capture_id, str):
            raise PublicArchivePacketError(f"invalid capture record: {relative}")
        if capture_id in capture_ids:
            raise PublicArchivePacketError(f"duplicate capture identity: {capture_id}")
        expected_filename = f"captures/{capture_id.removeprefix('urn:uuid:')}.json"
        if relative != expected_filename:
            raise PublicArchivePacketError(f"capture filename does not match identity: {relative}")
        capture_ids.add(capture_id)
        if capture.get("source_id") != manifest.get("source_id"):
            raise PublicArchivePacketError(f"capture source mismatch: {relative}")
        object_record = capture.get("object")
        if not isinstance(object_record, dict):
            raise PublicArchivePacketError(f"capture object record is malformed: {relative}")
        digest = object_record.get("sha256")
        if digest not in object_items:
            raise PublicArchivePacketError(f"capture object is absent: {relative}")
        referenced_objects.add(digest)
        expected_storage = f"objects/sha256/{digest[:2]}/{digest}"
        if object_record.get("storage_path") != expected_storage:
            raise PublicArchivePacketError(f"capture storage path is not canonical: {relative}")
        if object_record.get("size_bytes") != object_items[digest]["bytes"]:
            raise PublicArchivePacketError(f"capture object size binding mismatch: {relative}")
        endpoint_id = capture.get("endpoint_id")
        if isinstance(endpoint_id, str) and ("licence" in endpoint_id or "license" in endpoint_id):
            rights_capture_ids.add(capture_id)
    referenced = {
        capture_set["metadata_capture_id"],
        *capture_set.get("count_capture_ids", []),
        *capture_set.get("page_capture_ids", []),
    }
    if capture_set.get("object_ids_capture_id"):
        referenced.add(capture_set["object_ids_capture_id"])
    if not referenced <= capture_ids:
        raise PublicArchivePacketError("capture set references an absent capture")
    if capture_ids != referenced | rights_capture_ids:
        raise PublicArchivePacketError("packet contains an unreferenced non-rights capture")
    if set(object_items) != referenced_objects:
        raise PublicArchivePacketError("packet contains an unreferenced object")
    if not rights_capture_ids:
        raise PublicArchivePacketError("packet has no explicit rights capture")
    if rights_capture_ids != {descriptor.rights_capture_id}:
        raise PublicArchivePacketError("rights capture does not match trusted descriptor")
    rights_relative = f"captures/{descriptor.rights_capture_id.removeprefix('urn:uuid:')}.json"
    rights_capture = _load_object(root / rights_relative, rights_relative)
    rights_object = rights_capture["object"]
    if rights_object["sha256"] != descriptor.rights_object_sha256:
        raise PublicArchivePacketError("rights object does not match trusted descriptor")
    rights_payload = _load_object(
        root / "objects" / "sha256" / descriptor.rights_object_sha256,
        "rights capture payload",
    )
    if descriptor.rights_licence_text not in str(rights_payload.get("licenseInfo", "")):
        raise PublicArchivePacketError("rights payload does not support declared licence")
    if descriptor.attribution not in str(rights_payload.get("accessInformation", "")):
        raise PublicArchivePacketError("rights payload does not support declared attribution")
    manifest["_verified_rights_capture_ids"] = sorted(rights_capture_ids)
    return manifest


def materialize_public_arcgis_packet(
    packet_root: str | Path,
    *,
    descriptor: PublicArchiveDescriptor,
    output_dir: str | Path,
    records_dir: str | Path,
    base_name: str = "features",
    policy_nonclaims: tuple[str, ...] = (),
) -> PublicArchiveProjection:
    """Build repair-free canonical, GeoParquet and DuckDB projections offline."""

    root = Path(packet_root).resolve()
    output = Path(output_dir).resolve()
    records = Path(records_dir).resolve()
    if output.is_relative_to(root) or records.is_relative_to(root):
        raise PublicArchivePacketError("materialization outputs must be outside the packet root")
    if not _BASE_NAME.fullmatch(base_name):
        raise PublicArchivePacketError("base_name must be a safe single filename component")
    manifest = verify_public_archive_packet(root, descriptor=descriptor)
    with tempfile.TemporaryDirectory(prefix="riopa-public-packet-") as temporary_name:
        store = Path(temporary_name).resolve()
        shutil.copy2(root / "capture-set.json", store / "capture-set.json")
        (store / "captures").mkdir()
        capture_paths = sorted(
            item["path"] for item in manifest["files"] if item["path"].startswith("captures/")
        )
        for relative in capture_paths:
            capture_path = store / relative
            capture_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / relative, capture_path)
            capture = _load_object(capture_path, relative)
            object_record = capture["object"]
            digest = object_record["sha256"]
            source = root / "objects" / "sha256" / digest
            safe_storage = _safe_path(object_record["storage_path"])
            target = (store / safe_storage).resolve()
            if not target.is_relative_to(store):
                raise PublicArchivePacketError(
                    f"capture object escapes materialization store: {relative}"
                )
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copy2(source, target)
        materialization = materialize_arcgis_capture_set(
            store / "capture-set.json",
            store_root=store,
            output_dir=output,
            base_name=base_name,
            repair_invalid=False,
        )

    table = pq.read_table(materialization.geoparquet_path)
    capture_set = _load_object(root / "capture-set.json", "capture set")
    records.mkdir(parents=True, exist_ok=True)
    rows = table.select(
        ["_riopa_feature_id", "_riopa_source_object_id", "_riopa_capture_ids", "geometry"]
    ).to_pylist()
    canonical = [
        {
            "feature_id": row["_riopa_feature_id"],
            "source_object_id": row["_riopa_source_object_id"],
            "capture_ids": json.loads(row["_riopa_capture_ids"]),
            "geometry_sha256": sha256_json(row["geometry"].hex() if row["geometry"] else None),
            "valid_time": {"from": None, "to": None, "status": "unknown-not-imputed"},
            "recorded_time": {"at": manifest["captured_at"], "basis": "archive-capture-date"},
        }
        for row in rows
    ]
    with duckdb.connect(str(materialization.duckdb_path), read_only=True) as connection:
        duckdb_rows = connection.execute(
            """
            select
                _riopa_feature_id,
                cast(_riopa_source_object_id as varchar),
                _riopa_capture_ids,
                hex(ST_AsWKB(geometry))
            from features
            order by _riopa_feature_id
            """
        ).fetchall()
    duckdb_semantic_sha256 = sha256_json([list(row) for row in duckdb_rows])
    evidence = {
        "schema_version": "1.0.0",
        "record_type": "public_archive_spatial_projection",
        "source_id": manifest["source_id"],
        "packet_revision": descriptor.packet_revision,
        "dataset_repository": descriptor.dataset_repository,
        "packet_path": descriptor.packet_path,
        "packet_manifest_sha256": descriptor.manifest_sha256,
        "capture_set_id": capture_set["capture_set_id"],
        "capture_inputs": {
            "metadata_capture_id": capture_set["metadata_capture_id"],
            "count_capture_ids": capture_set.get("count_capture_ids", []),
            "page_capture_ids": capture_set.get("page_capture_ids", []),
            "rights_capture_ids": manifest["_verified_rights_capture_ids"],
        },
        "rights": {
            "licence": manifest["licence"],
            "attribution": manifest["attribution"],
            "publication_status": manifest["publication_status"],
        },
        "feature_count": materialization.feature_count,
        "canonical_features": canonical,
        "geoparquet": {
            "profile": "GeoParquet 1.1.0",
            "sha256": materialization.geoparquet_sha256,
        },
        "duckdb": {
            "reproducibility_class": "deterministic-semantics",
            "semantic_sha256": duckdb_semantic_sha256,
        },
        "geometry_policy": "original translated geometry preserved; implicit repair disabled",
        "legal_status": "bounded-non-authoritative-planning-reference",
        "non_claims": [*manifest["non_claims"], *policy_nonclaims],
    }
    evidence["semantic_sha256"] = sha256_json(evidence)
    evidence_path = records / "public-archive-spatial-projection.json"
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    return PublicArchiveProjection(
        source_id=manifest["source_id"],
        packet_revision=descriptor.packet_revision,
        feature_count=materialization.feature_count,
        materialization=materialization,
        evidence_path=evidence_path,
    )
