import json
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_second_environment_lane_is_pinned_and_fail_closed() -> None:
    workflow = yaml.safe_load((ROOT / ".github/workflows/evidence-campaign.yml").read_text())
    job = workflow["jobs"]["performance-second-environment"]
    assert job["runs-on"] == "macos-latest"
    assert "inputs.lane == 'performance-rehearsal'" in job["if"]
    assert any("--frozen" in step.get("run", "") for step in job["steps"])
    assert any("hosted-evidence.schema.json" in step.get("run", "") for step in job["steps"])
    assert any("validate_performance_report.py" in step.get("run", "") for step in job["steps"])
    contract = json.loads(
        (ROOT / "docs/performance-second-environment-rehearsal-contract-20260825.json").read_text()
    )
    assert contract["environments"] == ["ubuntu-latest", "macos-latest"]
    assert contract["promotion_allowed"] is False
