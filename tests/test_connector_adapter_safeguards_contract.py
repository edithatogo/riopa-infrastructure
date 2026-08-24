from pathlib import Path


def test_connector_plan_closes_bounded_adapter_safeguards_only() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = (root / "conductor/tracks/connector_runtime_capture_20260719/plan.md").read_text()
    assert "[x] 2.1 Implement bounded ArcGIS REST" in plan
    assert "[x] 2.2 Implement bounded Koordinates/API" in plan
    assert "[x] 2.3 Implement bounded optional WARC/WACZ" in plan
    assert "live-source acceptance, rights/publication qualification" in plan
    assert "preservation and external qualification remain pending" in plan
