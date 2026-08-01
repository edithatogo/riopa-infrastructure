import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "examples/wp010-performance-benchmark"


def _runner():
    spec = importlib.util.spec_from_file_location("wp010_performance", BENCHMARK / "run.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_declares_projection_boundary() -> None:
    contract = json.loads((BENCHMARK / "contract.json").read_text())
    assert contract["status"] == "synthetic-non-operational"
    assert contract["projection"]["classification"] == "projection-not-measurement"
    assert "national-scale performance gate" in " ".join(contract["projection"]["limitations"])


def test_runner_has_reproducible_checksum_and_classifications() -> None:
    report = _runner().run()
    assert report["regional"]["classification"] == "measured-regional-synthetic"
    assert report["national"]["classification"] == "projection-not-measurement"
    assert report["regional"]["checksum"] == _runner().checksum(128, 200, 20260801)
    assert report["national"]["records"] == 250000
    assert report["national"]["estimated_elapsed_ns"] > report["regional"]["elapsed_ns"]
    assert {case["case_id"] for case in report["scenarios"]} == {"baseline", "stressed", "degraded"}
    for case in report["scenarios"]:
        assert case["latency"]["p95_ms"] >= case["latency"]["p50_ms"]
        assert "status" in case["resources"] and "status" in case["cost"]


def test_runner_writes_json(tmp_path: Path) -> None:
    output = tmp_path / "measurement.json"
    report = _runner().run(output)
    assert json.loads(output.read_text())["benchmark_id"] == report["benchmark_id"]
