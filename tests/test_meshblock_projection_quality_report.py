import json
from pathlib import Path


def test_meshblock_quality_report_is_bound_to_immutable_projection() -> None:
    root = Path(__file__).resolve().parents[1]
    report = json.loads((root / "docs/stats-nz-meshblock-projection-quality-report-20260825.json").read_text())
    manifest = json.loads(
        (root / "evidence/stats-nz-meshblock-2026-projection/records-manifest.json").read_text()
    )
    assert report["source_manifest_sha256"] == manifest["manifest_sha256"]
    assert report["projection_id"] == manifest["projection_id"]
    assert report["observations"]["feature_count"] == 57575
    assert report["observations"]["capture_record_count"] == 236
    assert report["observations"]["implicit_geometry_repairs"] == 0
    assert report["checks"]["geometry_and_topology"]["status"] == "pass"
    assert report["checks"]["lineage"]["status"] == "pass"
    assert report["promotion_allowed"] is False
