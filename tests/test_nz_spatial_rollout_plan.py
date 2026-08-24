import json
from pathlib import Path


def test_rollout_plan_is_bounded_and_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = json.loads((root / "docs/nz-spatial-archive-rollout-plan-20260825.json").read_text())
    assert plan["status"] == "repository-owned-bounded-plan"
    assert plan["scope"] == "regional public-datasets-only technical preview"
    assert len(plan["waves"]) == 2
    endpoint_ids = [endpoint for wave in plan["waves"] for endpoint in wave["endpoints"]]
    assert len(endpoint_ids) == len(set(endpoint_ids))
    assert all(wave["rate_limit"]["maximum_concurrency"] == 1 for wave in plan["waves"])
    assert any("does not contact endpoints" in claim for claim in plan["nonclaims"])
    assert len(plan["exception_workflow"]) >= 4
    assert len(plan["retirement_workflow"]) >= 3
