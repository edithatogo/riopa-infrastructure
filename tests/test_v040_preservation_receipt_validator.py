import json
from pathlib import Path

from scripts.validate_v040_preservation_receipts import validate_reconciliation

ROOT = Path(__file__).resolve().parents[1]


def _record() -> dict[str, object]:
    return json.loads(
        (ROOT / "docs/v0.4.0-preservation-wp006-reconciliation-20260829.json").read_text()
    )


def test_v040_preservation_receipts_are_content_addressed() -> None:
    assert validate_reconciliation(_record(), root=ROOT) == ()


def test_v040_preservation_receipts_reject_tampered_digest() -> None:
    record = _record()
    receipts = record["verified_receipts"]
    assert isinstance(receipts, list)
    receipts[0]["sha256"] = "0" * 64
    errors = validate_reconciliation(record, root=ROOT)
    assert any("does not match" in error for error in errors)


def test_v040_preservation_receipts_retain_stable_boundary() -> None:
    record = _record()
    record["nonclaims"] = ["preview only"]
    assert any(
        "stable-v1 non-claim" in error for error in validate_reconciliation(record, root=ROOT)
    )


def test_v040_preservation_receipts_reject_duplicate_provider() -> None:
    record = _record()
    receipts = record["verified_receipts"]
    assert isinstance(receipts, list)
    receipts.append(dict(receipts[0]))
    assert any(
        "exactly one receipt per provider" in error
        for error in validate_reconciliation(record, root=ROOT)
    )


def test_v040_preservation_receipts_reject_non_object() -> None:
    assert validate_reconciliation([], root=ROOT) == ("preservation record must be a JSON object",)
