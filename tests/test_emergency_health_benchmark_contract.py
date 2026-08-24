import json
from pathlib import Path


def test_emergency_health_contract_is_reference_only_and_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    contract = json.loads((root / "docs/emergency-health-pilot-benchmark-contract-20260825.json").read_text())
    assert contract["status"] == "bounded-reference-only"
    assert contract["scope"] == "regional public-datasets-only technical preview"
    assert len(contract["scenarios"]) == 3
    assert len(contract["metrics"]) == 6
    assert any("clinical" in claim for claim in contract["disabled_claims"])
    assert any("dispatch" in claim for claim in contract["disabled_claims"])
    assert any("not a deployment" in claim for claim in contract["nonclaims"])
