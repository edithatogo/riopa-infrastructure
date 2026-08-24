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


def _envelope_validator():
    spec = importlib.util.spec_from_file_location(
        "performance_envelope", ROOT / "scripts/validate_performance_envelope.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_declares_projection_boundary() -> None:
    contract = json.loads((BENCHMARK / "contract.json").read_text())
    assert contract["status"] == "manifest-bound-synthetic-non-operational"
    assert contract["national_workload_manifest"] == "docs/national-workload-manifest-20260803.json"
    assert contract["disabled_domains"] == ["network", "timetable", "facility"]
    assert contract["projection"]["classification"] == "projection-not-measurement"
    assert "national-scale performance gate" in " ".join(contract["projection"]["limitations"])


def test_runner_has_reproducible_checksum_and_classifications() -> None:
    report = _runner().run()
    assert report["regional"]["classification"] == "measured-regional-synthetic"
    assert report["national"]["classification"] == "projection-not-measurement"
    assert report["regional"]["checksum"] == _runner().checksum(128, 200, 20260801)
    assert report["national"]["records"] == 57575
    assert report["national"]["estimated_elapsed_ns"] > report["regional"]["elapsed_ns"]
    assert {case["case_id"] for case in report["scenarios"]} == {"baseline", "stressed", "degraded"}
    for case in report["scenarios"]:
        assert case["latency"]["p95_ms"] >= case["latency"]["p50_ms"]
        assert "status" in case["resources"] and "status" in case["cost"]
    assert report["ingestion"]["geography_features"] == 57575
    assert report["ingestion"]["live_endpoint_contacted"] is False
    assert report["workload"]["national_workload_manifest_path"] == (
        "docs/national-workload-manifest-20260803.json"
    )
    assert report["accessibility"]["network"] == "disabled-no-archive"
    assert report["accessibility"]["timetable"] == "disabled-no-archive"
    assert report["accessibility"]["facility"] == "disabled-no-archive"
    assert report["workload"]["national_workload_manifest_sha256"] == (
        "2576fb0f4711b57a1847ba5b0617d352ee80cbd7a6f0c3cafcf7f4abc672eb67"
    )


def test_runner_writes_json(tmp_path: Path) -> None:
    output = tmp_path / "measurement.json"
    report = _runner().run(output)
    assert json.loads(output.read_text())["benchmark_id"] == report["benchmark_id"]


def test_noise_aware_envelope_accepts_bounded_rehearsal() -> None:
    report = _runner().run()
    assert _envelope_validator().validate(report) == ()


def test_noise_aware_envelope_rejects_insufficient_repetitions() -> None:
    report = _runner().run()
    report["scenarios"][0]["repetitions"] = 2
    assert "at least three repetitions" in _envelope_validator().validate(report)[0]
