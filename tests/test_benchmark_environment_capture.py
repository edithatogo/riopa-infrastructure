import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _module():
    spec = importlib.util.spec_from_file_location(
        "capture_benchmark_environment", ROOT / "scripts/capture_benchmark_environment.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_benchmark_environment_capture_binds_inputs_and_revision(tmp_path: Path) -> None:
    output = tmp_path / "environment.json"
    captured = _module().capture()
    output.write_text(json.dumps(captured), encoding="utf-8")
    assert len(captured["repository_revision"]) == 40
    assert captured["network_contacted"] is False
    assert len(captured["workload_sha256"]) == 64
    assert len(captured["national_manifest_sha256"]) == 64
    assert json.loads(output.read_text())["classification"] == "environment-capture-only"
