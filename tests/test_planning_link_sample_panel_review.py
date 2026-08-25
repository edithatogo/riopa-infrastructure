import json
from pathlib import Path


def test_planning_link_sample_panel_review_is_bounded_and_promotion_disabled() -> None:
    root = Path(__file__).parents[1]
    packet = json.loads((root / "docs/planning-link-sample-panel-review-20260825.json").read_text())
    assert packet["status"] == "bounded-synthetic-agent-panel-qualified-open-gates"
    assert packet["sample"]["fixture_names"] == ["district", "hybrid"]
    assert packet["sample"]["expected_unresolved_feasibility_cases"] == 2
    assert packet["sample"]["negative_mutation_cases"] == 2
    assert len(packet["panel"]) == 4
    assert packet["decisions"]["synthetic_contracts_qualified"] is True
    assert packet["decisions"]["factual_council_link_review"] is False
    assert packet["decisions"]["promotion_allowed"] is False
    assert packet["open_gates"]
