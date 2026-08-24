"""Immutable quarantine records for failed or suspect captures."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .capture import CaptureError, CaptureStore, _atomic_write
from .hashing import sha256_file, sha256_json


def quarantine_capture(
    store: CaptureStore,
    capture_id: str,
    *,
    reason: str,
    now: datetime,
) -> Path:
    """Write a digest-bound quarantine decision without changing raw evidence."""

    rendered_reason = reason.strip()
    if not rendered_reason:
        raise ValueError("reason must not be empty")
    metadata = store.verify_capture_integrity(capture_id)
    object_info = metadata.get("object")
    object_sha256 = object_info.get("sha256") if isinstance(object_info, dict) else None
    if not isinstance(object_sha256, str) or len(object_sha256) != 64:
        raise CaptureError("capture metadata has no valid object digest")
    safe_id = capture_id.removeprefix("urn:uuid:").replace("/", "_")
    record: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "capture_quarantine",
        "capture_id": capture_id,
        "reason": rendered_reason,
        "created_at": now.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "capture_metadata_sha256": sha256_file(store.capture_path(capture_id)),
        "object_sha256": object_sha256,
    }
    record["record_sha256"] = sha256_json(record)
    path = store.root / "quarantine" / f"{safe_id}-{record['record_sha256'][:16]}.json"
    payload = json.dumps(record, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    if path.exists():
        if path.read_bytes() != payload:
            raise CaptureError(f"quarantine record collision at {path}")
        return path
    _atomic_write(path, payload)
    return path
