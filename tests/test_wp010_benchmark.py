import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

from riopa_provenance.analysis import difference_in_differences, simulate_fcfs_queue
from riopa_provenance.registry import validate_registry

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "examples" / "wp010-synthetic-benchmark"


def test_independent_standard_library_benchmark_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(BENCHMARK / "verify.py")],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("PASS urn:riopa:benchmark:wp010")


def test_reference_implementation_matches_committed_benchmark() -> None:
    payload = json.loads((BENCHMARK / "benchmark.json").read_text(encoding="utf-8"))
    queue = payload["queue"]
    result = simulate_fcfs_queue(
        queue["arrival_times"],
        queue["service_times"],
        capacity=queue["capacity"],
        warm_up_customers=queue["warm_up_customers"],
    )
    assert {
        "waits": list(result.waits),
        "mean_wait": result.mean_wait,
        "maximum_wait": result.maximum_wait,
        "utilisation": result.utilisation,
        "observed_customers": result.observed_customers,
    } == queue["expected"]
    did = payload["difference_in_differences"]
    calculated = difference_in_differences(
        treated_pre=did["treated_pre"],
        treated_post=did["treated_post"],
        comparison_pre=did["comparison_pre"],
        comparison_post=did["comparison_post"],
    )
    assert calculated["estimate"] == did["expected"]["estimate"]
    assert calculated["group_means"] == did["expected"]["group_means"]


def test_reviewer_bundle_is_byte_deterministic(tmp_path: Path) -> None:
    from scripts.build_wp010_reviewer_bundle import build

    left = tmp_path / "left.zip"
    right = tmp_path / "right.zip"
    assert build(left) == build(right)
    assert hashlib.sha256(left.read_bytes()).digest() == hashlib.sha256(right.read_bytes()).digest()


def test_public_pilot_candidates_fail_closed() -> None:
    registry_path = ROOT / "config" / "source-registry" / "wp010-public-pilot-candidates.yaml"
    assert validate_registry(registry_path, ROOT / "schemas" / "source-registry.schema.json").valid
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    sources = {source["source_id"]: source for source in registry["sources"]}
    churton = sources["urn:riopa:source:wcc:churton-park-village-supermarket"]
    assert churton["status"] == "staged-rights-cleared"
    assert churton["rights"]["spdx_or_uri"] == "CC-BY-3.0-NZ"
    assert churton["rights"]["redistribution_status"] == "attribution-required"
    assert churton["endpoints"][0]["enabled"] is False
    enabled = {
        source["source_id"]
        for source in sources.values()
        if any(endpoint["enabled"] for endpoint in source["endpoints"])
    }
    assert enabled == {
        "urn:riopa:source:osm:nz-regional-pilot-pois",
        "urn:riopa:source:rangitikei:public-facilities",
    }
