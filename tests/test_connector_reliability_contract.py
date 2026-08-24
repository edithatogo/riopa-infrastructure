from pathlib import Path


def test_connector_plan_closes_bounded_reliability_controls_only() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = (root / "conductor/tracks/connector_runtime_capture_20260719/plan.md").read_text()
    assert "[x] 3.1 Add rate limiting" in plan
    assert "[x] 3.2 Add capability/schema drift" in plan
    assert "[x] 3.3 Add metrics, structured logs" in plan
    assert "hosted long-running operation and real-source qualification remain pending" in plan
    assert "source-specific live monitoring and hosted alert delivery remain pending" in plan
