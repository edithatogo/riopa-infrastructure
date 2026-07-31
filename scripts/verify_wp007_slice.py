#!/usr/bin/env python3
"""Verify the bounded, preserved WP-007 real-source slice."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

import duckdb
import pyarrow.parquet as pq

from riopa_provenance.hashing import sha256_file, sha256_json
from riopa_provenance.registry import validate_registry
from riopa_provenance.spatial import materialize_arcgis_capture_set


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _verify_capture(root: Path, metadata_path: Path, source_id: str) -> Path:
    metadata = _load(metadata_path)
    if metadata.get("record_type") != "http_capture":
        raise ValueError(f"{metadata_path} is not an HTTP capture")
    if metadata.get("source_id") != source_id:
        raise ValueError(f"{metadata_path} has the wrong source identity")
    if metadata.get("response", {}).get("status_code") != 200:
        raise ValueError(f"{metadata_path} did not preserve an HTTP 200 response")
    record = metadata.get("object")
    if not isinstance(record, dict):
        raise ValueError(f"{metadata_path} has no object record")
    object_path = root / "store" / str(record["storage_path"])
    if object_path.stat().st_size != record["size_bytes"]:
        raise ValueError(f"{metadata_path} object size mismatch")
    if sha256_file(object_path) != record["sha256"]:
        raise ValueError(f"{metadata_path} object hash mismatch")
    return object_path


def verify(root: Path) -> None:
    manifest = _load(root / "manifest.json")
    expected_manifest_hash = sha256_json(manifest, omit_keys={"manifest_sha256"})
    if manifest.get("manifest_sha256") != expected_manifest_hash:
        raise ValueError("WP-007 evidence manifest hash mismatch")
    if manifest.get("publication_status") != "not-attempted":
        raise ValueError("WP-007 evidence must not claim or trigger publication")

    registry_path = (root / str(manifest["registry"])).resolve()
    registry_result = validate_registry(
        registry_path, registry_path.parents[2] / "schemas/source-registry.schema.json"
    )
    if not registry_result.valid:
        raise ValueError("source registry failed validation: " + "; ".join(registry_result.errors))

    captured: dict[str, Path] = {}
    for source in manifest["sources"]:
        metadata_reference = source.get("capture_metadata")
        if isinstance(metadata_reference, str):
            captured[str(source["role"])] = _verify_capture(
                root, root / metadata_reference, str(source["source_id"])
            )
        rights_reference = source.get("rights_capture_metadata")
        if isinstance(rights_reference, str):
            _verify_capture(root, root / rights_reference, str(source["source_id"]))

    if not captured["planning"].read_bytes().startswith(b"%PDF-"):
        raise ValueError("planning evidence is not a PDF")
    with captured["facility"].open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or not rows[0]:
        raise ValueError("facility evidence contains no tabular records")
    linz_metadata = _load(captured["linz"])
    if linz_metadata.get("id") != 50772:
        raise ValueError("LINZ metadata is not the bounded layer 50772 record")

    materialization = manifest["materialization"]
    quality_path = root / materialization["quality_report"]
    quality = _load(quality_path)
    parquet_path = root / materialization["geoparquet"]
    duckdb_path = root / materialization["duckdb"]
    if sha256_file(parquet_path) != quality["geoparquet"]["sha256"]:
        raise ValueError("GeoParquet hash does not match quality evidence")
    if sha256_file(duckdb_path) != quality["duckdb"]["sha256"]:
        raise ValueError("DuckDB hash does not match quality evidence")
    if pq.read_table(parquet_path).num_rows != quality["feature_count"]:
        raise ValueError("GeoParquet feature count does not match quality evidence")
    connection = duckdb.connect(str(duckdb_path), read_only=True)
    try:
        if connection.execute("SELECT count(*) FROM features").fetchone()[0] != 1:
            raise ValueError("DuckDB does not contain the bounded one-feature slice")
    finally:
        connection.close()

    capture_set = root / manifest["sources"][1]["capture_set"]
    with tempfile.TemporaryDirectory(prefix="riopa-wp007-") as temporary:
        rebuilt = materialize_arcgis_capture_set(
            capture_set,
            store_root=root / "store",
            output_dir=temporary,
            crs="EPSG:2193",
            base_name="rebuilt",
        )
        if rebuilt.geoparquet_sha256 != quality["geoparquet"]["sha256"]:
            raise ValueError("clean GeoParquet rebuild differs from preserved evidence")
        rebuilt_rows = pq.read_table(rebuilt.geoparquet_path).to_pylist()
        preserved_rows = pq.read_table(parquet_path).to_pylist()
        if rebuilt_rows != preserved_rows:
            raise ValueError("clean semantic rebuild differs from preserved evidence")


def main() -> int:
    repository = Path(__file__).resolve().parents[1]
    root = repository / "evidence/wp007-real-slice"
    try:
        verify(root)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL {exc}")
        return 1
    print("PASS bounded WP-007 real-source slice")
    return 0


if __name__ == "__main__":
    sys.exit(main())
