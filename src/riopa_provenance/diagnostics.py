"""Redacted, immutable diagnostic bundles for connector operations."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .capture import CaptureFailure, _atomic_write, redact_text
from .hashing import sha256_bytes, sha256_json


class DiagnosticBundleError(ValueError):
    """Raised when a diagnostic bundle cannot be safely persisted."""


@dataclass(frozen=True)
class DiagnosticBundle:
    """Digest-bound diagnostic artifact metadata."""

    path: Path
    record_sha256: str


def _redact_value(value: Any, secrets: Sequence[str]) -> Any:
    if isinstance(value, str):
        return redact_text(value, secrets)
    if isinstance(value, Mapping):
        return {str(key): _redact_value(item, secrets) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_value(item, secrets) for item in value]
    return value


def write_diagnostic_bundle(
    output_path: str | Path,
    *,
    source_id: str,
    endpoint_id: str,
    metrics: Mapping[str, object],
    failures: Sequence[CaptureFailure],
    generated_at: datetime,
    redact_values: Sequence[str] = (),
) -> DiagnosticBundle:
    """Persist redacted metrics and structured failures without overwriting."""

    if not source_id.strip() or not endpoint_id.strip():
        raise DiagnosticBundleError("source_id and endpoint_id must not be empty")
    failure_records = [
        {
            "category": failure.category.value,
            "message": redact_text(failure.message, redact_values),
            "retryable": failure.retryable,
            "status_code": failure.status_code,
        }
        for failure in failures
    ]
    record: dict[str, object] = {
        "schema_version": "1.0.0",
        "record_type": "connector_diagnostic_bundle",
        "source_id": source_id,
        "endpoint_id": endpoint_id,
        "generated_at": generated_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "metrics": _redact_value(dict(metrics), redact_values),
        "failures": failure_records,
    }
    record["record_sha256"] = sha256_json(record)
    payload = json.dumps(record, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    path = Path(output_path)
    if path.exists():
        raise DiagnosticBundleError(f"diagnostic bundle already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(path, payload)
    return DiagnosticBundle(path=path, record_sha256=sha256_bytes(payload))
