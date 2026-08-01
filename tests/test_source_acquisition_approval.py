from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


def test_acquisition_approval_requires_scope_rights_recipient_and_expiry() -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "schemas/source-acquisition-approval.schema.json").read_text())
    valid = {
        "decision_id": "urn:riopa:approval:test",
        "recipient": "named operator",
        "source_revision": "source-2026-08-01",
        "rights_reference": "https://example.test/terms",
        "scope": ["metadata-only"],
        "exclusions": ["raw payload"],
        "conditions": ["do not redistribute"],
        "expires_at": "2026-12-31T00:00:00Z",
        "approved_by": "programme owner",
    }
    assert not list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(valid))
    assert list(Draft202012Validator(schema).iter_errors({**valid, "recipient": ""}))
    assert list(Draft202012Validator(schema).iter_errors({**valid, "token": "secret"}))
