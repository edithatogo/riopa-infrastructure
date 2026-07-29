"""Fail-closed governance decision and public/controlled-path helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

ALLOW_OUTCOMES = frozenset({"allow", "allow-with-conditions"})
PUBLIC_CLASSES = frozenset({"public"})
CONTROLLED_CLASSES = frozenset({"restricted", "sensitive", "controlled"})
BLOCKING_OUTCOMES = frozenset({"withdraw", "superseded", "prohibited", "review-required"})


class GovernanceError(ValueError):
    """Raised when a governance decision cannot safely permit an action."""


@dataclass(frozen=True)
class GovernanceResult:
    allowed: bool
    pathway: str
    reasons: tuple[str, ...]


def evaluate_decision(
    decision: Mapping[str, object] | None,
    *,
    pathway: str,
    required_scope: str | None = None,
) -> GovernanceResult:
    """Evaluate one decision for a public or controlled action.

    Missing, expired, conflicting or scope-incomplete decisions fail closed.
    ``pathway`` must be ``public`` or ``controlled``.
    """

    if pathway not in {"public", "controlled"}:
        raise GovernanceError("pathway must be public or controlled")
    if not isinstance(decision, Mapping):
        return GovernanceResult(False, pathway, ("governance decision is missing",))
    outcome = decision.get("outcome")
    classification = decision.get("classification")
    scope = decision.get("scope")
    reasons: list[str] = []
    if not isinstance(outcome, str) or outcome in BLOCKING_OUTCOMES:
        reasons.append(f"decision outcome is {outcome or 'missing'}")
    if not isinstance(classification, str):
        reasons.append("classification is missing")
    elif pathway == "public" and classification not in PUBLIC_CLASSES:
        reasons.append(f"classification {classification} is not public")
    elif pathway == "controlled" and classification not in PUBLIC_CLASSES | CONTROLLED_CLASSES:
        reasons.append(f"classification {classification} cannot use controlled pathway")
    if not isinstance(scope, Sequence) or isinstance(scope, (str, bytes)) or not scope:
        reasons.append("decision scope is missing")
    elif required_scope and required_scope not in scope:
        reasons.append(f"required scope {required_scope} is absent")
    review = decision.get("review")
    evidence = decision.get("evidence")
    if (
        not isinstance(review, Mapping)
        or not review.get("role")
        or not review.get("reviewed_at")
        or "expires_at" not in review
    ):
        reasons.append("review identity, date and expiry are required")
    if not isinstance(evidence, Sequence) or isinstance(evidence, (str, bytes)) or not evidence:
        reasons.append("review evidence is required")
    if reasons:
        return GovernanceResult(False, pathway, tuple(reasons))
    return GovernanceResult(True, pathway, ())


def require_allowed(
    decision: Mapping[str, object] | None, *, pathway: str, required_scope: str | None = None
) -> None:
    """Raise instead of permitting an unresolved governance action."""

    result = evaluate_decision(decision, pathway=pathway, required_scope=required_scope)
    if not result.allowed:
        raise GovernanceError("; ".join(result.reasons))
