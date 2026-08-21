import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_observability_contract_covers_required_signal_families() -> None:
    record = json.loads((ROOT / "docs/operations-observability-contract-20260822.json").read_text())
    names = {signal["name"] for signal in record["signals"]}
    assert names == {"source_health", "freshness", "quality", "storage", "cost", "release_status"}
    assert record["measurement_policy"]["missing_source_health"] == "unknown-not-healthy"
    assert record["measurement_policy"]["unmeasured_status"] == "candidate-not-measured"


def test_observability_contract_is_fail_closed() -> None:
    record = json.loads((ROOT / "docs/operations-observability-contract-20260822.json").read_text())
    claims = " ".join(record["non_claims"])
    assert "not evidence" in claims or "not production" in claims
    assert "missing or unmeasured" in claims
