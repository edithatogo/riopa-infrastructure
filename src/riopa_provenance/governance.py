"""Fail-closed governance decision and public/controlled-path helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

ALLOW_OUTCOMES = frozenset({"allow", "allow-with-conditions"})
PUBLIC_CLASSES = frozenset({"public"})
CONTROLLED_CLASSES = frozenset({"restricted", "sensitive", "controlled"})
BLOCKING_OUTCOMES = frozenset({"withdraw", "superseded", "prohibited", "review-required"})
ACQUISITION_OUTCOMES = frozenset({"allow", "allow-with-conditions", "metadata-only", "review-required", "prohibited"})

# Scope labels are deliberately explicit rather than inferred from geography or
# population names.  This keeps cultural/community review a documented trigger
# (when required by scope, source terms or risk), not an automatic requirement.
SCOPE_REVIEW_TRIGGERS: dict[str, str] = {
    "health": "privacy-ethics",
    "unit-record": "privacy-ethics",
    "linkage": "privacy-ethics",
    "operational": "safety",
    "culturally-sensitive-geography": "cultural-community",
    "community-request": "cultural-community",
    "source-terms": "rights-licence",
    "statutory": "legal-authority",
}


class GovernanceError(ValueError):
    """Raised when a governance decision cannot safely permit an action."""


@dataclass(frozen=True)
class GovernanceResult:
    allowed: bool
    pathway: str
    reasons: tuple[str, ...]


def validate_source_acquisition_approval(
    record: Mapping[str, object] | None, *, now: datetime | None = None
) -> tuple[str, ...]:
    """Validate an acquisition approval beyond JSON Schema's structural checks.

    This helper is deliberately fail-closed and side-effect free.  It catches
    whitespace-only values, expired approvals, duplicate/empty scope labels and
    credential-shaped fields that a valid JSON Schema instance could otherwise
    contain.  It never fetches a source or resolves credentials.
    """

    if not isinstance(record, Mapping):
        return ("approval record is missing",)
    errors: list[str] = []
    for field in ("decision_id", "recipient", "source_revision", "rights_reference", "approved_by"):
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")
    outcome = record.get("outcome")
    if not isinstance(outcome, str) or not outcome.strip():
        errors.append("outcome must be a non-empty string")
    elif outcome not in ACQUISITION_OUTCOMES:
        errors.append("outcome is not an approved acquisition outcome")
    for field in ("scope", "conditions", "exclusions"):
        value = record.get(field)
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            errors.append(f"{field} must be an array")
            continue
        if field != "exclusions" and not value:
            errors.append(f"{field} must not be empty")
        if any(not isinstance(item, str) or not item.strip() for item in value):
            errors.append(f"{field} contains an empty label")
        # Do not call ``set`` until element types are known: malformed nested
        # arrays must produce validation errors, never a TypeError.
        string_values = [item for item in value if isinstance(item, str)]
        if len(set(string_values)) != len(string_values):
            errors.append(f"{field} contains duplicate labels")
    expiry = record.get("expires_at")
    if not isinstance(expiry, str) or not expiry.strip():
        errors.append("expires_at is required")
    else:
        try:
            parsed = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
            reference = now or datetime.now(UTC)
            if parsed.tzinfo is None:
                errors.append("expires_at must include a timezone")
            elif parsed <= reference:
                errors.append("approval has expired")
        except ValueError:
            errors.append("expires_at must be an ISO-8601 timestamp")
    forbidden = {"password", "token", "secret", "credential", "api_key", "access_token"}
    stack: list[object] = [record]
    while stack:
        current = stack.pop()
        if isinstance(current, Mapping):
            for key, value in current.items():
                if str(key).lower() in forbidden:
                    errors.append(f"credential-shaped field is prohibited: {key}")
                stack.append(value)
        elif isinstance(current, Sequence) and not isinstance(current, (str, bytes)):
            stack.extend(current)
    return tuple(dict.fromkeys(errors))


def scope_review_triggers(scope: Sequence[str]) -> tuple[str, ...]:
    """Return deterministic review domains activated by declared scope labels.

    Labels must be declared by the source/pilot owner; this helper never infers
    cultural or community obligations from place names or population attributes.
    Unknown labels are ignored so callers can evolve scope vocabularies without
    accidentally widening review requirements.
    """

    if isinstance(scope, (str, bytes)):
        raise GovernanceError("scope must be a sequence of labels")
    return tuple(
        sorted(
            {
                SCOPE_REVIEW_TRIGGERS[label]
                for label in scope
                if isinstance(label, str) and label in SCOPE_REVIEW_TRIGGERS
            }
        )
    )


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
        or not review.get("expires_at")
        or "conflict_of_interest" not in review
    ):
        reasons.append("review identity, date and expiry are required")
    elif review.get("conflict_of_interest") is True and not review.get("conflict_resolution"):
        reasons.append("conflict of interest requires documented resolution")
    else:
        try:
            reviewed_at = datetime.fromisoformat(str(review["reviewed_at"]).replace("Z", "+00:00"))
            expires_at = datetime.fromisoformat(str(review["expires_at"]).replace("Z", "+00:00"))
            if reviewed_at.tzinfo is None or expires_at.tzinfo is None:
                reasons.append("review dates must include a timezone")
            elif reviewed_at > datetime.now(UTC):
                reasons.append("review date is in the future")
            elif expires_at <= datetime.now(UTC):
                reasons.append("review has expired")
        except (TypeError, ValueError):
            reasons.append("review dates must be ISO-8601 timestamps")
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


def record_withdrawal(
    decision: Mapping[str, object], *, withdrawal_id: str, reason: str, scope: Sequence[str]
) -> dict[str, Any]:
    """Create an append-only withdrawal successor without rewriting provenance."""

    if not withdrawal_id or not reason or not scope:
        raise GovernanceError("withdrawal id, reason and scope are required")
    result = dict(decision)
    result.update(
        {
            "decision_id": withdrawal_id,
            "outcome": "withdraw",
            "scope": list(scope),
            "withdrawal_reference": str(decision.get("decision_id", "")),
            "rationale": reason,
            "recorded_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
    )
    return result


def record_supersession(
    decision: Mapping[str, object], *, successor_id: str, reason: str
) -> dict[str, Any]:
    """Create a supersession record while retaining the predecessor reference."""

    if not successor_id or not reason:
        raise GovernanceError("successor id and reason are required")
    result = dict(decision)
    result.update(
        {
            "decision_id": successor_id,
            "outcome": "superseded",
            "successor_id": successor_id,
            "supersedes_id": str(decision.get("decision_id", "")),
            "rationale": reason,
            "recorded_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
    )
    return result


def reconcile_withdrawal_targets(
    decision: Mapping[str, object], targets: Sequence[str]
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return allowed and withdrawn targets without mutating prior evidence."""

    if decision.get("outcome") != "withdraw":
        return tuple(targets), ()
    scope = decision.get("scope")
    withdrawn = (
        set(scope) if isinstance(scope, Sequence) and not isinstance(scope, (str, bytes)) else set()
    )
    return tuple(target for target in targets if target not in withdrawn), tuple(
        target for target in targets if target in withdrawn
    )
