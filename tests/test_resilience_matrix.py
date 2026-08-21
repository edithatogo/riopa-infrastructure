import importlib.util
import json
from pathlib import Path

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


def test_bounded_rehearsal_executes_local_cases_without_operational_claim() -> None:
    report = run()
    assert report["classification"] == "repository-rehearsal-not-operational-evidence"
    assert set(report["cases"]) == {
        "baseline",
        "stressed",
        "concurrency",
        "retry-storm",
        "cancellation",
        "malformed-input",
        "recovery",
    }
    assert all(case["status"] == "passed" for case in report["cases"].values())
    assert report["safety"]["live_endpoint_contacted"] is False
