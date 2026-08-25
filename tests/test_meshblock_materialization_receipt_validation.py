import json
from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from riopa_provenance.hashing import sha256_json
from scripts.validate_meshblock_materialization_receipt import build_report, sha256

PROJECTION_DIGEST = "64a1cbce366794b2b802f04dbe2bf1dc5fbf813e5c5b159bcf0782af9adc511f"


def _write_artifact_fixture(root: Path, artifacts: Path) -> None:
    evidence = root / "evidence/stats-nz-meshblock-2026-projection"
    projection_path = evidence / f"projection-records/sha256/64/{PROJECTION_DIGEST}.json"
    projection_path.parent.mkdir(parents=True)
    artifacts.mkdir(parents=True)
    parquet_path = artifacts / "meshblocks.parquet"
    duckdb_path = artifacts / "meshblocks.duckdb"
    quality_path = artifacts / "meshblocks.quality.json"
    table = pa.table(
        {
            "OBJECTID": [1, 2],
            "geometry": [b"geometry", None],
            "_riopa_capture_ids": ['["capture-1"]', '["capture-2"]'],
            "_riopa_source_geometry_sha256": ["a" * 64, None],
        }
    )
    pq.write_table(table, parquet_path)
    connection = duckdb.connect(str(duckdb_path))
    try:
        connection.execute(
            "create table features as select * from read_parquet(?)", [str(parquet_path)]
        )
        connection.execute("create table riopa_metadata (key varchar primary key, value json)")
        connection.execute(
            "insert into riopa_metadata values ('source_id', ?)",
            [json.dumps("urn:test:source")],
        )
    finally:
        connection.close()
    quality_path.write_text("{}\n")
    projection = {
        "projection_id": f"urn:riopa:projection:sha256:{PROJECTION_DIGEST}",
        "record": {
            "feature_count": 2,
            "source_id": "urn:test:source",
            "quality": {"null_geometry_count": 1},
        },
    }
    projection_path.write_text(json.dumps(projection, sort_keys=True) + "\n")
    receipt = {
        "schema_version": "1.0.0",
        "record_type": "spatial_materialization_receipt",
        "projection_id": projection["projection_id"],
        "geoparquet": {
            "path": parquet_path.name,
            "profile": "GeoParquet 1.1.0",
            "sha256": sha256(parquet_path),
            "size_bytes": parquet_path.stat().st_size,
        },
        "duckdb": {
            "path": duckdb_path.name,
            "reproducibility_class": "deterministic-semantics",
            "sha256": sha256(duckdb_path),
            "size_bytes": duckdb_path.stat().st_size,
        },
        "quality_report": {
            "path": quality_path.name,
            "sha256": sha256(quality_path),
            "size_bytes": quality_path.stat().st_size,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    receipt_path = evidence / "materialization-receipt.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n")
    manifest = {
        "projection_id": projection["projection_id"],
        "projection_record_sha256": sha256(projection_path),
        "materialization_receipt_sha256": sha256(receipt_path),
    }
    manifest["manifest_sha256"] = sha256_json(manifest)
    (evidence / "records-manifest.json").write_text(json.dumps(manifest, sort_keys=True) + "\n")


def test_meshblock_materialization_receipt_links_are_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    report = build_report(root)
    assert report["status"] == "receipt-and-projection-links-validated"
    assert report["promotion_allowed"] is False
    assert len(report["receipt_sha256"]) == 64
    assert report["artifact_validation"] is None
    assert any("independent target" in gate for gate in report["open_gates"])


def test_restored_artifacts_are_digest_bound_and_queryable() -> None:
    root = Path(__file__).resolve().parents[1]
    artifacts = root / ".riopa-local/spatial-projections/stats-nz-meshblock-2026"
    if not artifacts.is_dir():
        pytest.skip("bounded restored artifacts are not present")
    report = build_report(root, artifacts)
    validation = report["artifact_validation"]
    assert validation["status"] == "restored-artifacts-and-cross-tool-queries-validated"
    assert validation["feature_count"] == 57_575
    assert validation["distinct_object_ids"] == 57_575
    assert validation["null_geometry_count"] == 16


def test_artifact_validation_is_hermetic(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    artifacts = tmp_path / "artifacts"
    _write_artifact_fixture(root, artifacts)
    validation = build_report(root, artifacts)["artifact_validation"]
    assert validation["feature_count"] == 2
    assert validation["distinct_object_ids"] == 2
    assert validation["null_geometry_count"] == 1

    parquet = artifacts / "meshblocks.parquet"
    parquet.write_bytes(parquet.read_bytes() + b"tampered")
    with pytest.raises(ValueError, match="geoparquet size does not match"):
        build_report(root, artifacts)


def test_artifact_validation_rejects_unsafe_receipt_path(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    artifacts = tmp_path / "artifacts"
    _write_artifact_fixture(root, artifacts)
    evidence = root / "evidence/stats-nz-meshblock-2026-projection"
    receipt_path = evidence / "materialization-receipt.json"
    receipt = json.loads(receipt_path.read_text())
    receipt["geoparquet"]["path"] = "../escape.parquet"
    receipt.pop("receipt_sha256")
    receipt["receipt_sha256"] = sha256_json(receipt)
    receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n")
    manifest_path = evidence / "records-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["materialization_receipt_sha256"] = sha256(receipt_path)
    manifest.pop("manifest_sha256")
    manifest["manifest_sha256"] = sha256_json(manifest)
    manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="unsafe geoparquet path"):
        build_report(root, artifacts)
