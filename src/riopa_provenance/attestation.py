"""Deterministic DSSE/in-toto-compatible attestation envelopes.

The builder emits a content-bound, unsigned envelope for repository and CI
pipelines.  Signing is intentionally separate: an empty signature set is not
release evidence and must be rejected by release verification until a trusted
signer and protected environment provide a receipt.
"""

from __future__ import annotations

import base64
import json
from collections.abc import Mapping, Sequence
from typing import Any

DSSE_PAYLOAD_TYPE = "application/vnd.in-toto+json"
IN_TOTO_STATEMENT_TYPE = "https://in-toto.io/Statement/v1"


class AttestationError(ValueError):
    """Raised when an attestation cannot be constructed safely."""


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_in_toto_statement(
    subjects: Sequence[Mapping[str, Any]],
    *,
    predicate_type: str,
    predicate: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a minimal in-toto statement without signing or network access."""

    if not subjects:
        raise AttestationError("at least one attestation subject is required")
    if not isinstance(predicate_type, str) or not predicate_type.strip():
        raise AttestationError("predicate type is required")
    if not isinstance(predicate, Mapping):
        raise AttestationError("predicate must be an object")
    normalised: list[dict[str, Any]] = []
    for subject in subjects:
        if (
            not isinstance(subject, Mapping)
            or not isinstance(subject.get("name"), str)
            or not subject["name"].strip()
        ):
            raise AttestationError("each subject requires a name")
        digest = subject.get("digest")
        sha256 = digest.get("sha256") if isinstance(digest, Mapping) else None
        if (
            not isinstance(sha256, str)
            or len(sha256) != 64
            or any(character not in "0123456789abcdef" for character in sha256)
        ):
            raise AttestationError("each subject requires a sha256 digest")
        normalised.append({"name": str(subject["name"]), "digest": {"sha256": sha256}})
    return {
        "_type": IN_TOTO_STATEMENT_TYPE,
        "subject": normalised,
        "predicateType": predicate_type,
        "predicate": dict(predicate),
    }


def build_dsse_envelope(statement: Mapping[str, Any]) -> dict[str, Any]:
    """Encode one statement in a deterministic DSSE envelope.

    The returned ``signatures`` array is deliberately empty.  Callers must
    obtain a trusted signature in a protected release environment before
    treating the envelope as a release attestation.
    """

    if not isinstance(statement, Mapping) or statement.get("_type") != IN_TOTO_STATEMENT_TYPE:
        raise AttestationError("statement must be an in-toto Statement/v1 object")
    payload = base64.b64encode(_canonical_json(statement)).decode("ascii")
    return {"payloadType": DSSE_PAYLOAD_TYPE, "payload": payload, "signatures": []}


def decode_dsse_payload(envelope: Mapping[str, Any]) -> dict[str, Any]:
    """Decode and validate the in-toto payload without trusting signatures."""

    if not isinstance(envelope, Mapping):
        raise AttestationError("DSSE envelope must be an object")
    if envelope.get("payloadType") != DSSE_PAYLOAD_TYPE:
        raise AttestationError("unsupported DSSE payload type")
    signatures = envelope.get("signatures")
    if not isinstance(signatures, list):
        raise AttestationError("DSSE signatures must be an array")
    payload = envelope.get("payload")
    if not isinstance(payload, str) or not payload:
        raise AttestationError("DSSE payload is not valid base64 JSON")
    try:
        decoded = base64.b64decode(payload, validate=True)
        value = json.loads(decoded)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AttestationError("DSSE payload is not valid base64 JSON") from exc
    if not isinstance(value, dict) or value.get("_type") != IN_TOTO_STATEMENT_TYPE:
        raise AttestationError("DSSE payload is not an in-toto Statement/v1 object")
    return value
