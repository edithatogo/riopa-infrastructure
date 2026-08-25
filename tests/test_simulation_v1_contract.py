import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_simulation_v1_contract_freezes_bounded_surfaces_and_open_gates() -> None:
    guidance = (ROOT / "docs/simulation-v1-reference-contract-20260825.md").read_text()
    contract = json.loads(
        (ROOT / "docs/simulation-v1-reference-contract-20260825.json").read_text()
    )
    for surface in ("FCFS queue", "seeded replication", "dispatch", "capacity-resilience"):
        assert surface in guidance
    assert "breaking contract change" in guidance
    assert "clinical calibration" in guidance
    assert "operational readiness" in guidance
    assert contract["promotion_allowed"] is False
    assert "master seed retention" in contract["required_controls"]
