from riopa_provenance.spatial_quality import evaluate_spatial_quality


def _fixtures() -> tuple[dict, dict]:
    report = {
        "invalid_geometry_count_before_repair": 0,
        "repaired_geometry_count": 0,
        "null_geometry_count": 0,
        "duplicate_feature_id_count": 0,
        "source_id": "synthetic-source",
        "capture_ids": ["synthetic-capture"],
    }
    profile = {
        "metrics": [
            {"id": "geometry_validity", "threshold": {"warning": 0, "release_block": True}},
            {"id": "geometry_repair", "threshold": {"warning": 0, "release_block": False}},
            {"id": "null_geometry", "threshold": {"warning": 0, "release_block": False}},
            {"id": "stable_identity", "threshold": {"warning": 0, "release_block": True}},
            {"id": "source_lineage", "threshold": {"minimum": 1.0, "release_block": True}},
        ]
    }
    return report, profile


def test_spatial_quality_passes_synthetic_report() -> None:
    report, profile = _fixtures()
    result = evaluate_spatial_quality(
        report,
        profile,
        transformation_revision="synthetic-rev-1",
        rights_disposition="public-preview",
    )
    assert result["status"] == "pass"
    assert result["promotion_allowed"] is False
    assert result["errors"] == []


def test_spatial_quality_fails_closed_on_integrity_and_lineage() -> None:
    report, profile = _fixtures()
    report.update(
        invalid_geometry_count_before_repair=1,
        source_id=None,
        capture_ids=[],
    )
    result = evaluate_spatial_quality(report, profile)
    assert result["status"] == "fail"
    assert "geometry_validity failed" in result["errors"]
    assert any("missing required evidence" in error for error in result["errors"])
