from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from riopa_provenance.capture import CaptureFailure, CaptureFailureCategory
from riopa_provenance.diagnostics import DiagnosticBundleError, write_diagnostic_bundle


def test_diagnostic_bundle_is_redacted_and_digest_bound(tmp_path: Path) -> None:
    output = tmp_path / "diagnostics" / "bundle.json"
    result = write_diagnostic_bundle(
        output,
        source_id="source",
        endpoint_id="endpoint",
        metrics={"attempts_total": 2, "failures_total": 1, "labels": {"token": "secret"}},
        failures=[
            CaptureFailure(
                CaptureFailureCategory.TRANSPORT,
                "https://data.example/?token=secret",
                retryable=True,
                status_code=503,
            )
        ],
        generated_at=datetime(2026, 8, 24, tzinfo=UTC),
        redact_values=("secret",),
    )
    record = json.loads(output.read_text(encoding="utf-8"))
    assert result.record_sha256
    assert record["record_type"] == "connector_diagnostic_bundle"
    assert "secret" not in output.read_text(encoding="utf-8")
    assert record["failures"][0]["retryable"] is True


def test_diagnostic_bundle_rejects_empty_identity_and_overwrite(tmp_path: Path) -> None:
    kwargs = {
        "source_id": "source",
        "endpoint_id": "endpoint",
        "metrics": {},
        "failures": [],
        "generated_at": datetime(2026, 8, 24, tzinfo=UTC),
    }
    with pytest.raises(DiagnosticBundleError, match="must not be empty"):
        write_diagnostic_bundle(
            tmp_path / "empty.json",
            source_id="",
            **{key: value for key, value in kwargs.items() if key != "source_id"},
        )
    output = tmp_path / "bundle.json"
    write_diagnostic_bundle(output, **kwargs)
    with pytest.raises(DiagnosticBundleError, match="already exists"):
        write_diagnostic_bundle(output, **kwargs)
