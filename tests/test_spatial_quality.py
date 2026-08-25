from riopa_provenance.spatial_quality import (
    build_quality_benchmark_report,
    evaluate_quality_waiver,
    evaluate_spatial_quality,
)


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


def test_quality_waiver_requires_owner_rationale_and_expiry() -> None:
    waiver = {
        "waiver_id": "waiver-1",
        "metric_id": "geometry_repair",
        "rationale": "bounded preview fixture",
        "owner": "repository-owner",
        "expires_on": "2026-12-31",
        "release_blocking": False,
    }
    result = evaluate_quality_waiver(waiver, as_of="2026-08-25")
    assert result["status"] == "active"
    assert result["promotion_allowed"] is False


def test_quality_waiver_rejects_expired_and_release_blocking_waivers() -> None:
    waiver = {
        "waiver_id": "waiver-2",
        "metric_id": "geometry_validity",
        "rationale": "not permitted",
        "owner": "repository-owner",
        "expires_on": "2026-01-01",
        "release_blocking": True,
    }
    result = evaluate_quality_waiver(waiver, as_of="2026-08-25")
    assert result["status"] == "invalid-or-expired"
    assert any("expired" in error for error in result["errors"])
    assert any("release-blocking" in error for error in result["errors"])


def test_quality_benchmark_report_is_deterministic_and_bounded() -> None:
    report, profile = _fixtures()
    packet = build_quality_benchmark_report(
        [
            {
                "observation_id": "b",
                "report": report,
                "transformation_revision": "rev-1",
                "rights_disposition": "public-preview",
            },
            {
                "observation_id": "a",
                "report": report,
                "transformation_revision": "rev-1",
                "rights_disposition": "public-preview",
            },
        ],
        profile,
        profile_id="preview-profile",
        revision="rev-1",
    )
    assert packet["observation_count"] == 2
    assert packet["passed_count"] == 2
    assert [item["observation_id"] for item in packet["observations"]] == ["a", "b"]
    assert packet["promotion_allowed"] is False
