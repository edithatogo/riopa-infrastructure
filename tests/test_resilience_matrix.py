import importlib.util
import json
from pathlib import Path

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
