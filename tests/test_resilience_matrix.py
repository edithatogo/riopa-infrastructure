import importlib.util
import json
from pathlib import Path

import pytest

from scripts.run_bounded_resilience_rehearsal import run

ROOT = Path(__file__).resolve().parents[1]


def test_resilience_matrix_is_complete_and_fail_closed() -> None:
    matrix = json.loads(
        (ROOT / "examples/wp010-performance-benchmark/resilience-matrix.json").read_text(
            encoding="utf-8"
        )
    )
    spec = importlib.util.spec_from_file_location(
        "validate_resilience_matrix", ROOT / "scripts/validate_resilience_matrix.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.validate(matrix)
    assert matrix["completion"]["status"] == "not-run"


def test_resilience_matrix_validator_rejects_non_object_nested_sections() -> None:
    spec = importlib.util.spec_from_file_location(
        "validate_resilience_matrix", ROOT / "scripts/validate_resilience_matrix.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with pytest.raises(ValueError, match="must be an object"):
        module.validate([])
    matrix = {
        "classification": "repository-rehearsal-plan-not-operational-evidence",
        "required_cases": [
            "baseline",
            "stressed",
            "degraded",
            "concurrency",
            "retry-storm",
            "cancellation",
            "malformed-input",
        ],
        "safety": [],
    }
    with pytest.raises(ValueError, match="safety must be an object"):
        module.validate(matrix)


def test_bounded_rehearsal_executes_local_cases_without_operational_claim() -> None:
    report = run()
    assert report["classification"] == "repository-rehearsal-not-operational-evidence"
    assert set(report["cases"]) == {
        "baseline",
        "stressed",
        "degraded",
        "concurrency",
        "retry-storm",
        "cancellation",
        "malformed-input",
        "recovery",
    }
    assert all(case["status"] == "passed" for case in report["cases"].values())
    assert report["safety"]["live_endpoint_contacted"] is False
    assert report["cases"]["degraded"]["fallback"] == "bounded local checksum"
    assert report["cases"]["degraded"]["fallback_checksum"] > 0


def test_performance_plan_closes_bounded_tasks_without_closing_hosted_gates() -> None:
    plan = (
        ROOT / "conductor/tracks/performance_scalability_reliability_20260719/plan.md"
    ).read_text()
    assert "[x] 2.1 Run bounded local" in plan
    assert "[x] 2.2 Run bounded local" in plan
    assert "[x] 2.3 Record bounded deterministic" in plan
    assert "[x] 3.1 Add a deterministic noise-aware" in plan
    assert "[x] 3.2 Publish bounded synthetic" in plan
    assert "[x] 3.3 Resolve bottlenecks" in plan
    assert "hosted and national-scale measurement remain open" in plan
