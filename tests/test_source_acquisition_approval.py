from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from riopa_provenance.governance import validate_source_acquisition_approval


def test_acquisition_approval_requires_scope_rights_recipient_and_expiry() -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "schemas/source-acquisition-approval.schema.json").read_text())
    valid = {
        "decision_id": "urn:riopa:approval:test",
        "recipient": "named operator",
        "source_revision": "source-2026-08-01",
        "rights_reference": "https://example.test/terms",
        "outcome": "allow-with-conditions",
        "scope": ["metadata-only"],
        "exclusions": ["raw payload"],
        "conditions": ["do not redistribute"],
        "expires_at": "2026-12-31T00:00:00Z",
        "approved_by": "programme owner",
    }
    assert not list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(valid))
    assert list(Draft202012Validator(schema).iter_errors({**valid, "recipient": ""}))
    assert list(Draft202012Validator(schema).iter_errors({**valid, "token": "secret"}))


def test_semantic_approval_validation_is_fail_closed() -> None:
    valid = {
        "decision_id": "urn:riopa:approval:test",
        "recipient": "named operator",
        "source_revision": "source-2026-08-01",
        "rights_reference": "https://example.test/terms",
        "outcome": "allow-with-conditions",
        "scope": ["metadata-only"],
        "exclusions": ["raw payload"],
        "conditions": ["do not redistribute"],
        "expires_at": "2026-12-31T00:00:00Z",
        "approved_by": "programme owner",
    }
    from datetime import UTC, datetime

    now = datetime(2026, 8, 1, tzinfo=UTC)
    assert validate_source_acquisition_approval(valid, now=now) == ()
    assert "recipient must be a non-empty string" in validate_source_acquisition_approval(
        {**valid, "recipient": "   "}, now=now
    )
    assert "approval has expired" in validate_source_acquisition_approval(
        {**valid, "expires_at": "2026-07-31T00:00:00Z"}, now=now
    )
    assert any(
        "credential-shaped" in error
        for error in validate_source_acquisition_approval(
            {**valid, "conditions": ["safe"], "notes": {"api_key": "never"}}, now=now
        )
    )
    assert "scope contains duplicate labels" in validate_source_acquisition_approval(
        {**valid, "scope": ["metadata-only", "metadata-only"]}, now=now
    )
    missing_outcome = {key: value for key, value in valid.items() if key != "outcome"}
    assert "outcome must be a non-empty string" in validate_source_acquisition_approval(
        missing_outcome, now=now
    )


def test_semantic_validation_reports_nested_or_unhashable_labels() -> None:
    valid = {
        "decision_id": "urn:riopa:approval:test",
        "recipient": "named operator",
        "source_revision": "source-2026-08-01",
        "rights_reference": "https://example.test/terms",
        "outcome": "allow-with-conditions",
        "scope": ["metadata-only"],
        "exclusions": [],
        "conditions": ["do not redistribute"],
        "expires_at": "2026-12-31T00:00:00Z",
        "approved_by": "programme owner",
    }
    errors = validate_source_acquisition_approval(
        {**valid, "scope": [["nested"]]}, now=datetime(2026, 8, 1, tzinfo=UTC)
    )
    assert "scope contains an empty label" in errors


def test_allow_outcome_rejects_placeholder_authority_fields() -> None:
    valid = {
        "decision_id": "urn:riopa:approval:test",
        "recipient": "named operator",
        "source_revision": "source-2026-08-01",
        "rights_reference": "https://example.test/terms",
        "outcome": "allow-with-conditions",
        "scope": ["metadata-only"],
        "exclusions": [],
        "conditions": ["do not redistribute"],
        "expires_at": "2026-12-31T00:00:00Z",
        "approved_by": "programme owner",
    }
    errors = validate_source_acquisition_approval(
        {**valid, "rights_reference": "TBD"},
        now=datetime(2026, 8, 1, tzinfo=UTC),
    )
    assert "rights_reference cannot be a placeholder for an allow outcome" in errors
    # Non-permission outcomes may deliberately record unresolved authority.
    assert (
        validate_source_acquisition_approval(
            {**valid, "outcome": "review-required", "rights_reference": "TBD"},
            now=datetime(2026, 8, 1, tzinfo=UTC),
        )
        == ()
    )
