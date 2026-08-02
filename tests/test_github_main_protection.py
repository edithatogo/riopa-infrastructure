import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_github_main_protection", ROOT / "scripts/verify_github_main_protection.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _payload(**overrides: object) -> dict[str, object]:
    rule = {
        "pattern": "main",
        "requiresApprovingReviews": False,
        "requiredApprovingReviewCount": None,
        "requiresStatusChecks": True,
        "requiresStrictStatusChecks": True,
        "requiredStatusCheckContexts": sorted(MODULE.EXPECTED_CHECKS),
        "requiresConversationResolution": True,
        "requiresLinearHistory": True,
        "allowsForcePushes": False,
        "allowsDeletions": False,
        "isAdminEnforced": True,
    }
    rule.update(overrides)
    return {
        "data": {
            "repository": {"branchProtectionRules": {"nodes": [rule]}},
        }
    }


def test_single_developer_protection_contract_passes() -> None:
    assert MODULE.validate(_payload()) == []


def test_approving_review_requirement_fails_closed() -> None:
    errors = MODULE.validate(
        _payload(requiresApprovingReviews=True, requiredApprovingReviewCount=1)
    )
    assert "requiresApprovingReviews must be false" in errors
    assert "requiredApprovingReviewCount must be null when reviews are disabled" in errors


def test_required_check_drift_is_detected() -> None:
    errors = MODULE.validate(_payload(requiredStatusCheckContexts=[]))
    assert any(error.startswith("required checks differ") for error in errors)
