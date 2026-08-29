import base64
import json

import pytest

from riopa_provenance.attestation import (
    DSSE_PAYLOAD_TYPE,
    AttestationError,
    build_dsse_envelope,
    build_in_toto_statement,
    decode_dsse_payload,
)


def test_build_and_decode_unsigned_dsse_intoto_envelope() -> None:
    statement = build_in_toto_statement(
        [{"name": "dist/package.whl", "digest": {"sha256": "a" * 64}}],
        predicate_type="https://riopa.example/predicate/build/v1",
        predicate={"builder": "github-actions", "signed": False},
    )
    envelope = build_dsse_envelope(statement)
    assert envelope["payloadType"] == "application/vnd.in-toto+json"
    assert envelope["signatures"] == []
    assert decode_dsse_payload(envelope) == statement


def test_dsse_builder_rejects_non_object_statement() -> None:
    with pytest.raises(AttestationError, match="Statement/v1 object"):
        build_dsse_envelope(None)  # type: ignore[arg-type]


def test_dsse_decoder_validates_statement_fields() -> None:
    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": 42,
        "predicateType": "https://riopa.example/predicate/build/v1",
        "predicate": {},
    }
    payload = base64.b64encode(json.dumps(statement).encode()).decode()
    with pytest.raises(AttestationError, match="statement fields are invalid"):
        decode_dsse_payload(
            {"payloadType": DSSE_PAYLOAD_TYPE, "payload": payload, "signatures": []}
        )


def test_dsse_decoder_rejects_malformed_signature_entries() -> None:
    statement = build_in_toto_statement(
        [{"name": "release.json", "digest": {"sha256": "b" * 64}}],
        predicate_type="https://riopa.example/predicate/release/v1",
        predicate={},
    )
    payload = base64.b64encode(json.dumps(statement).encode()).decode()
    with pytest.raises(AttestationError, match="keyid and sig"):
        decode_dsse_payload(
            {
                "payloadType": DSSE_PAYLOAD_TYPE,
                "payload": payload,
                "signatures": [{"sig": 1}],
            }
        )


def test_attestation_builder_rejects_missing_digest_and_invalid_payload() -> None:
    with pytest.raises(AttestationError, match="predicate type"):
        build_in_toto_statement(
            [{"name": "dist/package.whl", "digest": {"sha256": "a" * 64}}],
            predicate_type=None,  # type: ignore[arg-type]
            predicate={},
        )
    with pytest.raises(AttestationError, match="predicate must be an object"):
        build_in_toto_statement(
            [{"name": "dist/package.whl", "digest": {"sha256": "a" * 64}}],
            predicate_type="https://riopa.example/predicate/build/v1",
            predicate=None,  # type: ignore[arg-type]
        )
    with pytest.raises(AttestationError, match="each subject requires a name"):
        build_in_toto_statement(
            [{"name": [], "digest": {"sha256": "a" * 64}}],
            predicate_type="https://riopa.example/predicate/build/v1",
            predicate={},
        )
    with pytest.raises(AttestationError, match="sha256 digest"):
        build_in_toto_statement(
            [{"name": "dist/package.whl", "digest": {}}],
            predicate_type="https://riopa.example/predicate/build/v1",
            predicate={},
        )
    with pytest.raises(AttestationError, match="sha256 digest"):
        build_in_toto_statement(
            [{"name": "dist/package.whl", "digest": {"sha256": "not-a-digest"}}],
            predicate_type="https://riopa.example/predicate/build/v1",
            predicate={},
        )
    with pytest.raises(AttestationError, match="sha256 digest"):
        build_in_toto_statement(
            [{"name": "dist/package.whl", "digest": {"sha256": "A" * 64}}],
            predicate_type="https://riopa.example/predicate/build/v1",
            predicate={},
        )
    with pytest.raises(AttestationError, match="valid base64 JSON"):
        decode_dsse_payload(
            {"payloadType": "application/vnd.in-toto+json", "payload": "!", "signatures": []}
        )
    with pytest.raises(AttestationError, match="envelope must be an object"):
        decode_dsse_payload(None)  # type: ignore[arg-type]
    with pytest.raises(AttestationError, match="valid base64 JSON"):
        decode_dsse_payload({"payloadType": DSSE_PAYLOAD_TYPE, "payload": None, "signatures": []})


def test_unsigned_envelope_is_explicitly_not_a_signed_receipt() -> None:
    statement = build_in_toto_statement(
        [{"name": "release.json", "digest": {"sha256": "b" * 64}}],
        predicate_type="https://riopa.example/predicate/release/v1",
        predicate={},
    )
    assert build_dsse_envelope(statement)["signatures"] == []
