from __future__ import annotations

import pytest

from riopa_provenance.governance import (
    GovernanceError,
    evaluate_decision,
    reconcile_withdrawal_targets,
    record_supersession,
    record_withdrawal,
    require_allowed,
    scope_review_triggers,
)


def decision(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "decision_id": "urn:riopa:governance-decision:test",
        "subject_id": "urn:riopa:source:test",
        "subject_kind": "source",
        "classification": "public",
        "outcome": "allow",
        "scope": ["publication"],
        "review": {
            "role": "governance analyst",
            "reviewed_at": "2026-07-29T00:00:00Z",
            "expires_at": "2026-12-31T00:00:00Z",
            "conflict_of_interest": False,
        },
        "evidence": ["urn:riopa:evidence:test"],
        "rationale": "reviewed source terms and governance triggers",
    }
    value.update(overrides)
    return value


def test_public_decision_allows_matching_scope() -> None:
    assert evaluate_decision(decision(), pathway="public", required_scope="publication").allowed


def test_scope_review_triggers_are_explicit_and_deterministic() -> None:
    assert scope_review_triggers(["health", "culturally-sensitive-geography", "health"]) == (
        "cultural-community",
        "privacy-ethics",
    )
    # A place or population label alone does not activate cultural review.
    assert scope_review_triggers(["new-zealand", "population- Māori"]) == ()


def test_scope_review_triggers_reject_scalar_scope() -> None:
    with pytest.raises(GovernanceError, match="sequence"):
        scope_review_triggers("health")


def test_scope_review_triggers_ignores_malformed_unknown_labels() -> None:
    assert scope_review_triggers([[], "unknown-label", "health"]) == ("privacy-ethics",)


def test_review_dates_without_timezone_fail_closed() -> None:
    result = evaluate_decision(
        decision(
            review={
                "role": "governance analyst",
                "reviewed_at": "2026-07-29T00:00:00",
                "expires_at": "2026-12-31T00:00:00",
                "conflict_of_interest": False,
            }
        ),
        pathway="public",
    )
    assert not result.allowed
    assert any("timezone" in reason for reason in result.reasons)


@pytest.mark.parametrize(
    "overrides",
    [
        {"outcome": "review-required"},
        {"classification": "sensitive"},
        {"scope": []},
        {"evidence": []},
        {"review": {"role": "", "reviewed_at": ""}},
    ],
)
def test_public_path_fails_closed(overrides: dict[str, object]) -> None:
    result = evaluate_decision(decision(**overrides), pathway="public")
    assert not result.allowed
    assert result.reasons


def test_controlled_path_accepts_controlled_classification() -> None:
    assert evaluate_decision(
        decision(classification="controlled"), pathway="controlled", required_scope="publication"
    ).allowed


def test_missing_decision_raises() -> None:
    with pytest.raises(GovernanceError, match="missing"):
        require_allowed(None, pathway="public")


@pytest.mark.parametrize(
    "overrides",
    [
        {"classification": "unknown-class"},
        {
            "review": {
                "role": "governance analyst",
                "reviewed_at": "2026-07-29T00:00:00Z",
                "expires_at": "2026-12-31T00:00:00Z",
                "conflict_of_interest": True,
            }
        },
    ],
)
def test_unknown_or_unresolved_rights_fail_closed(overrides: dict[str, object]) -> None:
    result = evaluate_decision(decision(**overrides), pathway="public")
    assert not result.allowed


def test_expired_review_fails_closed() -> None:
    result = evaluate_decision(
        decision(
            review={
                "role": "governance analyst",
                "reviewed_at": "2025-01-01T00:00:00Z",
                "expires_at": "2025-02-01T00:00:00Z",
                "conflict_of_interest": False,
            }
        ),
        pathway="public",
    )
    assert not result.allowed
    assert any("expired" in reason for reason in result.reasons)


def test_withdrawal_preserves_predecessor_reference() -> None:
    withdrawn = record_withdrawal(
        decision(),
        withdrawal_id="urn:riopa:governance-decision:withdrawn",
        reason="harm review",
        scope=["public"],
    )
    assert withdrawn["outcome"] == "withdraw"
    assert withdrawn["withdrawal_reference"] == decision()["decision_id"]
    assert not evaluate_decision(withdrawn, pathway="public").allowed


def test_supersession_is_append_only() -> None:
    superseded = record_supersession(
        decision(),
        successor_id="urn:riopa:governance-decision:successor",
        reason="corrected review",
    )
    assert superseded["outcome"] == "superseded"
    assert superseded["successor_id"] == "urn:riopa:governance-decision:successor"
    assert superseded["supersedes_id"] == decision()["decision_id"]


def test_withdrawal_reconciliation_removes_only_withdrawn_targets() -> None:
    withdrawn = record_withdrawal(
        decision(),
        withdrawal_id="urn:riopa:governance-decision:withdrawn-2",
        reason="takedown",
        scope=["zenodo"],
    )
    assert reconcile_withdrawal_targets(withdrawn, ["github", "zenodo"]) == (
        ("github",),
        ("zenodo",),
    )
