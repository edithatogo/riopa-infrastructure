import json
from pathlib import Path


def test_evidence_acquisition_plan_is_complete_and_fail_closed() -> None:
    plan = json.loads(Path("docs/evidence-acquisition-plan-20260801.json").read_text())
    ids = {lane["id"] for lane in plan["lanes"]}
    assert {"matrix-reconciliation", "public-source-capture", "panel-qualification", "external-reproduction", "release-authority"} <= ids
    assert plan["status"] in {"in_progress", "approved_to_launch"}
    assert plan["non_claims"]
    assert all(lane["contingency"] for lane in plan["lanes"])
