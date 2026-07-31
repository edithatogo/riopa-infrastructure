from __future__ import annotations

import pytest

from riopa_provenance.linz_export import (
    LinzExportArchiver,
    LinzExportError,
    _job_identity,
    _job_state,
)


def test_export_job_identity_and_state_normalise_supported_values() -> None:
    assert _job_identity({"id": 42, "url": "https://data.example/jobs/42"}) == (
        "42",
        "https://data.example/jobs/42",
    )
    assert _job_state({"state": "COMPLETE"}) == "complete"
    assert _job_state({"state": "processing"}) == "processing"


@pytest.mark.parametrize("job", [{}, {"id": True, "url": "/job"}, {"id": 1}])
def test_export_job_identity_fails_closed(job: dict[str, object]) -> None:
    with pytest.raises(LinzExportError):
        _job_identity(job)


@pytest.mark.parametrize("state", [None, "", "queued", 42])
def test_export_state_rejects_unknown_values(state: object) -> None:
    with pytest.raises(LinzExportError, match="state"):
        _job_state({"state": state})


def test_export_headers_redact_and_require_api_key() -> None:
    archiver = LinzExportArchiver(None)  # type: ignore[arg-type]
    assert archiver._headers("secret") == {
        "Authorization": "key secret",
        "Accept": "application/json",
    }
    with pytest.raises(ValueError, match="api_key must not be empty"):
        archiver._headers("")
