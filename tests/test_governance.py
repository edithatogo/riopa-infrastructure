from __future__ import annotations

import pytest

from riopa_provenance.governance import GovernanceError, evaluate_decision, require_allowed


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
        },
        "evidence": ["urn:riopa:evidence:test"],
    }
    value.update(overrides)
    return value


def test_public_decision_allows_matching_scope() -> None:
    assert evaluate_decision(decision(), pathway="public", required_scope="publication").allowed


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
