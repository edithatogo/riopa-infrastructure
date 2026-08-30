import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stable_v1_readiness_plan_is_revision_bound_and_fail_closed() -> None:
    record = json.loads((ROOT / "docs/stable-v1-readiness-plan-20260830.json").read_text())
    assert record["release"] == "1.0.0"
    assert re.fullmatch(r"[0-9a-f]{40}", record["source_revision"])
    assert record["promotion_allowed"] is False
    assert record["status"] == "preparation-only"
    assert len(record["stable_gate_families"]) == 14
    assert {gate["status"] for gate in record["stable_gate_families"]} == {"pending"}
    assert record["campaigns"]["beta"]["required_days"] == 90
    assert record["campaigns"]["beta"]["required_operational_cycles"] == 3
    assert record["campaigns"]["rc"]["required_days"] == 30
    assert record["campaigns"]["beta"]["campaign_id"] == "operational-beta-20260830-26bc0b4"
    assert record["campaigns"]["rc"]["campaign_id"] == "operational-rc-20260830-26bc0b4"
    assert record["non_substitutions"]
