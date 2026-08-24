import json
from pathlib import Path

PROFILE = Path("docs/spatial-quality-profile-contract-20260825.json")


def test_spatial_quality_profile_is_bounded_and_fail_closed() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    assert profile["status"] == "bounded-contract"
    assert profile["promotion_allowed"] is False
    metric_ids = {metric["id"] for metric in profile["metrics"]}
    assert {"geometry_validity", "stable_identity", "source_lineage"} <= metric_ids
    assert any("national-scale" in gate for gate in profile["open_gates"])
    assert any("rights uncertainty" in rule.lower() for rule in profile["waiver_rules"])


def test_spatial_quality_profile_requires_content_bound_evidence() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    assert {"quality report", "source or capture digest", "transformation revision"} <= set(
        profile["required_evidence"]
    )
    assert "not evidence of national completeness" in " ".join(profile["non_claims"])
