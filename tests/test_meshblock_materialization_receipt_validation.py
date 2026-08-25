import json
from pathlib import Path

import pytest

from scripts.validate_meshblock_materialization_receipt import build_report


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


def test_artifact_validation_rejects_unsafe_receipt_path(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    receipt_path = root / "evidence/stats-nz-meshblock-2026-projection/materialization-receipt.json"
    receipt = json.loads(receipt_path.read_text())
    receipt["geoparquet"]["path"] = "../escape.parquet"
    isolated = tmp_path / "repo"
    target = isolated / receipt_path.relative_to(root)
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps(receipt))
    for relative in (
        "evidence/stats-nz-meshblock-2026-projection/records-manifest.json",
        "evidence/stats-nz-meshblock-2026-projection/projection-records/sha256/64/64a1cbce366794b2b802f04dbe2bf1dc5fbf813e5c5b159bcf0782af9adc511f.json",
    ):
        destination = isolated / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((root / relative).read_bytes())
    with pytest.raises(ValueError, match="unsafe geoparquet path"):
        build_report(isolated, tmp_path)
