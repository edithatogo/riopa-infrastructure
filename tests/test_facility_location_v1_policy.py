import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_v1_registry_and_migration_policy_is_explicit_and_fail_closed() -> None:
    policy = (ROOT / "docs/facility-location-v1-api-migration-policy-20260825.md").read_text()
    contract = json.loads(
        (ROOT / "docs/facility-location-v1-api-migration-contract-20260825.json").read_text()
    )

    for model in ("set-cover", "maximal-cover", "p-median", "p-center"):
        assert model in policy
        assert model in contract["registry"]
    assert "breaking change" in policy
    assert "semantic loss" in policy
    assert contract["compatibility"]["semantic_or_unit_change"] == "breaking version required"
    for excluded in ("national-scale", "planning", "accessibility", "operational", "promotion"):
        assert excluded in policy
    assert contract["promotion_allowed"] is False
