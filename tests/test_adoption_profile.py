from pathlib import Path

from scripts.build_adoption_profile import build_adoption_profile


def test_adoption_profile_is_additive_and_reports_research_object_surface() -> None:
    root = Path(__file__).resolve().parents[1]
    profile = build_adoption_profile(root)
    assert profile["record_type"] == "riopa_additive_adoption_profile"
    assert profile["promotion_allowed"] is False
    assert profile["waves"][0]["status"] == "available"
    assert profile["waves"][1]["status"] == "available"
    assert any("never overwrites" in item for item in profile["semantic_loss_boundaries"])


def test_adoption_profile_fails_closed_for_missing_root(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    try:
        build_adoption_profile(missing)
    except ValueError as error:
        assert "does not exist" in str(error)
    else:
        raise AssertionError("missing repository root should fail closed")
