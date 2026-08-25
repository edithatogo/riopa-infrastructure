"""Validate the archived Meshblock materialization receipt and projection links."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import duckdb
import pyarrow.parquet as pq


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_path(artifact_root: Path, value: object, kind: str) -> Path:
    relative = Path(str(value))
    if relative.is_absolute() or relative.name != str(relative):
        raise ValueError(f"materialization receipt has unsafe {kind} path")
    path = artifact_root / relative
    if not path.is_file():
        raise ValueError(f"missing restored {kind} artifact: {relative}")
    return path


def _validate_artifacts(
    receipt: dict[str, Any], projection: dict[str, Any], artifact_root: Path
) -> dict[str, Any]:
    paths: dict[str, Path] = {}
    for kind in ("geoparquet", "duckdb", "quality_report"):
        contract = receipt[kind]
        path = _artifact_path(artifact_root, contract.get("path"), kind)
        if path.stat().st_size != contract["size_bytes"]:
            raise ValueError(f"restored {kind} size does not match receipt")
        if sha256(path) != contract["sha256"]:
            raise ValueError(f"restored {kind} digest does not match receipt")
        paths[kind] = path

    expected_features = projection["record"]["feature_count"]
    expected_nulls = projection["record"]["quality"]["null_geometry_count"]
    parquet = pq.read_table(paths["geoparquet"])
    required_columns = {
        "OBJECTID",
        "geometry",
        "_riopa_capture_ids",
        "_riopa_source_geometry_sha256",
    }
    missing = sorted(required_columns.difference(parquet.column_names))
    if missing:
        raise ValueError(f"restored GeoParquet is missing required columns: {missing}")
    if parquet.num_rows != expected_features:
        raise ValueError("restored GeoParquet feature count does not match projection")

    connection = duckdb.connect(str(paths["duckdb"]), read_only=True)
    try:
        tables = {row[0] for row in connection.execute("show tables").fetchall()}
        if not {"features", "riopa_metadata"}.issubset(tables):
            raise ValueError("restored DuckDB is missing required tables")
        counts = connection.execute(
            "select count(*), count(distinct OBJECTID), "
            "count(*) filter (where geometry is null) from features"
        ).fetchone()
        source_row = connection.execute(
            "select value from riopa_metadata where key = 'source_id'"
        ).fetchone()
        if counts is None or source_row is None:
            raise ValueError("restored DuckDB is missing required projection metadata")
        feature_count, distinct_ids, null_geometries = counts
        source_id = json.loads(source_row[0])
    finally:
        connection.close()
    if feature_count != expected_features or distinct_ids != expected_features:
        raise ValueError("restored DuckDB feature identity counts do not match projection")
    if null_geometries != expected_nulls:
        raise ValueError("restored DuckDB null geometry count does not match projection")
    if source_id != projection["record"]["source_id"]:
        raise ValueError("restored DuckDB source identity does not match projection")

    return {
        "status": "restored-artifacts-and-cross-tool-queries-validated",
        "feature_count": feature_count,
        "distinct_object_ids": distinct_ids,
        "null_geometry_count": null_geometries,
        "source_id": source_id,
        "required_columns": sorted(required_columns),
        "artifacts": {
            kind: {
                "path": receipt[kind]["path"],
                "sha256": receipt[kind]["sha256"],
                "size_bytes": receipt[kind]["size_bytes"],
            }
            for kind in paths
        },
    }


def build_report(root: Path, artifact_root: Path | None = None) -> dict[str, Any]:
    evidence = root / "evidence/stats-nz-meshblock-2026-projection"
    receipt_path = evidence / "materialization-receipt.json"
    records_manifest_path = evidence / "records-manifest.json"
    projection_path = evidence / "projection-records/sha256/64"
    projection_path /= "64a1cbce366794b2b802f04dbe2bf1dc5fbf813e5c5b159bcf0782af9adc511f.json"
    for path in (receipt_path, records_manifest_path, projection_path):
        if not path.is_file():
            raise ValueError(f"missing Meshblock evidence file: {path.relative_to(root)}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    manifest = json.loads(records_manifest_path.read_text(encoding="utf-8"))
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    if receipt.get("record_type") != "spatial_materialization_receipt":
        raise ValueError("unexpected materialization receipt type")
    if manifest.get("projection_id") != receipt.get("projection_id"):
        raise ValueError("records manifest and materialization receipt disagree on projection")
    if projection.get("projection_id") != receipt.get("projection_id"):
        raise ValueError("projection record and materialization receipt disagree on projection")
    if receipt.get("geoparquet", {}).get("profile") != "GeoParquet 1.1.0":
        raise ValueError("materialization receipt is missing the GeoParquet profile")
    for kind in ("geoparquet", "duckdb", "quality_report"):
        value = receipt.get(kind) if kind != "quality_report" else receipt.get("quality_report")
        if not isinstance(value, dict) or len(str(value.get("sha256", ""))) != 64:
            raise ValueError(f"materialization receipt has no digest for {kind}")
    artifact_validation = (
        _validate_artifacts(receipt, projection, artifact_root.resolve())
        if artifact_root is not None
        else None
    )
    return {
        "schema": "riopa.meshblock-materialization-receipt-validation.v1",
        "status": "receipt-and-projection-links-validated",
        "projection_id": receipt["projection_id"],
        "receipt": str(receipt_path.relative_to(root)),
        "records_manifest": str(records_manifest_path.relative_to(root)),
        "projection_record": str(projection_path.relative_to(root)),
        "receipt_sha256": sha256(receipt_path),
        "promotion_allowed": False,
        "artifact_validation": artifact_validation,
        "open_gates": [
            "independent target restoration and acceptance",
            "national authority and completeness evidence",
            "external reproduction and accountable release decision",
        ],
        "non_claims": [
            "Local artifact validation is repository-owned and is not independent acceptance.",
            "The projection is not population, national authority, or operational evidence.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--require-artifacts", action="store_true")
    args = parser.parse_args()
    if args.require_artifacts and args.artifact_root is None:
        parser.error("--require-artifacts requires --artifact-root")
    report = build_report(args.root.resolve(), args.artifact_root)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
