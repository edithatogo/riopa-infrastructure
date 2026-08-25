from pathlib import Path


def test_template_support_policy_declares_safe_upgrade_and_external_boundaries() -> None:
    root = Path(__file__).resolve().parents[1]
    policy = (root / "docs/repository-template-support-policy-20260825.md").read_text(
        encoding="utf-8"
    )
    assert "scripts/check_template_drift.py" in policy
    assert "never overwrites" in policy
    assert "independent" in policy and "reproduction" in policy
    assert "release approval" in policy
