from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from riopa_provenance.capture import CaptureError, CaptureStore
from riopa_provenance.quarantine import quarantine_capture


def test_quarantine_record_is_digest_bound_and_idempotent(tmp_path: Path) -> None:
    store = CaptureStore(tmp_path, id_factory=lambda: "capture-1")
    object_sha256, _ = store.write_object(b"payload")
    store.write_capture({"capture_id": "urn:uuid:capture-1", "object": {"sha256": object_sha256}})
    now = datetime(2026, 8, 24, tzinfo=UTC)
    path = quarantine_capture(store, "urn:uuid:capture-1", reason="malformed", now=now)
    assert quarantine_capture(store, "urn:uuid:capture-1", reason="malformed", now=now) == path
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["object_sha256"] == object_sha256
    assert record["record_sha256"]
    assert store.object_path(object_sha256).read_bytes() == b"payload"


def test_quarantine_rejects_empty_reason_and_tampered_capture(tmp_path: Path) -> None:
    store = CaptureStore(tmp_path, id_factory=lambda: "capture-1")
    object_sha256, _ = store.write_object(b"payload")
    store.write_capture({"capture_id": "urn:uuid:capture-1", "object": {"sha256": object_sha256}})
    with pytest.raises(ValueError, match="reason"):
        quarantine_capture(
            store,
            "urn:uuid:capture-1",
            reason=" ",
            now=datetime(2026, 8, 24, tzinfo=UTC),
        )
    store.object_path(object_sha256).write_bytes(b"tampered")
    with pytest.raises(CaptureError, match="digest mismatch"):
        quarantine_capture(
            store,
            "urn:uuid:capture-1",
            reason="malformed",
            now=datetime(2026, 8, 24, tzinfo=UTC),
        )
