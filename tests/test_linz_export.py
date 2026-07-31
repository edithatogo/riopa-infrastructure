from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import httpx
import pytest

from riopa_provenance.capture import CapturePolicy, CaptureResult
from riopa_provenance.hashing import sha256_json
from riopa_provenance.linz_export import (
    LinzExportArchiver,
    LinzExportError,
    _job_identity,
    _job_state,
    _require_object,
)


def _capture(
    tmp_path: Path,
    name: str,
    status: int = 200,
    *,
    location: str | None = None,
) -> CaptureResult:
    return CaptureResult(
        capture_id=f"capture-{name}",
        source_id="linz",
        endpoint_id=name,
        status_code=status,
        media_type="application/json",
        retrieved_at="2026-07-31T00:00:00Z",
        object_sha256=(name.encode().hex() + "0" * 64)[:64],
        size_bytes=len(name),
        object_path=tmp_path / f"{name}.object",
        metadata_path=tmp_path / f"{name}.metadata.json",
        request_fingerprint=f"request-{name}",
        response_location=location,
    )


class FakeCaptureClient:
    def __init__(
        self,
        tmp_path: Path,
        json_responses: list[tuple[CaptureResult, Any]] | None = None,
        downloads: list[CaptureResult] | None = None,
    ) -> None:
        self.client = httpx.Client()
        self.policy = CapturePolicy(
            allowed_hosts=frozenset({"data.linz.govt.nz", "objects.example"})
        )
        self.json_responses = list(json_responses or [])
        self.downloads = list(downloads or [])
        self.json_calls: list[tuple[str, str, Mapping[str, Any]]] = []
        self.download_calls: list[tuple[str, str, Mapping[str, Any]]] = []
        self.tmp_path = tmp_path

    def capture_json(self, method: str, url: str, **kwargs: Any) -> tuple[CaptureResult, Any]:
        self.json_calls.append((method, url, kwargs))
        return self.json_responses.pop(0)

    def capture(self, method: str, url: str, **kwargs: Any) -> CaptureResult:
        self.download_calls.append((method, url, kwargs))
        return self.downloads.pop(0)


def test_export_job_identity_and_state_normalise_supported_values() -> None:
    assert _job_identity({"id": 42, "url": "https://data.example/jobs/42"}) == (
        "42",
        "https://data.example/jobs/42",
    )
    assert _job_state({"state": "COMPLETE"}) == "complete"
    assert _job_state({"state": "processing"}) == "processing"
    assert _require_object({"ok": True}, context="test") == {"ok": True}
    with pytest.raises(LinzExportError, match="JSON object"):
        _require_object([], context="test")


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


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"item_urls": []}, "item_urls"),
        ({"formats": {}}, "formats"),
        ({"crs": ""}, "crs"),
        ({"poll_limit": 0}, "poll_limit"),
        ({"poll_interval_seconds": -1}, "poll_interval"),
        ({"item_urls": ["https://x/1", "https://x/1"]}, "unique"),
    ],
)
def test_archive_export_validates_arguments(
    tmp_path: Path, override: dict[str, object], message: str
) -> None:
    values: dict[str, Any] = {
        "source_id": "linz",
        "endpoint_id": "exports",
        "exports_url": "https://data.linz.govt.nz/services/api/v1.x/exports",
        "item_urls": ["https://data.linz.govt.nz/layer/1/"],
        "formats": {"1": "geopackage"},
        "crs": "EPSG:2193",
        "api_key": "secret",
        "output_dir": tmp_path,
    }
    values.update(override)
    with pytest.raises(ValueError, match=message):
        LinzExportArchiver(None).archive_export(**values)  # type: ignore[arg-type]


def test_download_follows_redirect_without_leaking_api_key(tmp_path: Path) -> None:
    client = FakeCaptureClient(
        tmp_path,
        downloads=[
            _capture(tmp_path, "redirect", 302, location="https://objects.example/file.zip"),
            _capture(tmp_path, "payload"),
        ],
    )
    captures, payload = LinzExportArchiver(client)._capture_download(  # type: ignore[arg-type]
        source_id="linz",
        endpoint_id="export",
        download_url="https://data.linz.govt.nz/download/1",
        api_key="secret",
        max_redirects=2,
    )
    assert len(captures) == 2
    assert payload.capture_id == "capture-payload"
    assert client.download_calls[0][2]["headers"]["Authorization"] == "key secret"
    assert client.download_calls[1][2]["headers"] == {"Accept": "application/octet-stream"}


@pytest.mark.parametrize(
    ("downloads", "max_redirects", "message"),
    [
        ([_capture(Path("/tmp"), "missing-location", 302)], 1, "no Location"),
        ([_capture(Path("/tmp"), "server-error", 503)], 1, "HTTP 503"),
        (
            [_capture(Path("/tmp"), "redirect", 302, location="/download/1")],
            1,
            "redirect loop",
        ),
        (
            [_capture(Path("/tmp"), "redirect", 302, location="/other")],
            0,
            "exceeded 0 redirects",
        ),
    ],
)
def test_download_fails_closed(
    tmp_path: Path,
    downloads: list[CaptureResult],
    max_redirects: int,
    message: str,
) -> None:
    client = FakeCaptureClient(tmp_path, downloads=downloads)
    with pytest.raises(LinzExportError, match=message):
        LinzExportArchiver(client)._capture_download(  # type: ignore[arg-type]
            source_id="linz",
            endpoint_id="export",
            download_url="https://data.linz.govt.nz/download/1",
            api_key="secret",
            max_redirects=max_redirects,
        )
    with pytest.raises(ValueError, match="max_redirects"):
        LinzExportArchiver(client)._capture_download(  # type: ignore[arg-type]
            source_id="linz",
            endpoint_id="export",
            download_url="https://data.linz.govt.nz/download/1",
            api_key="secret",
            max_redirects=-1,
        )


def test_archive_export_polls_downloads_and_writes_bound_manifest(tmp_path: Path) -> None:
    job_url = "https://data.linz.govt.nz/services/api/v1.x/exports/7/"
    download_url = "https://objects.example/export.zip?signature=private"
    client = FakeCaptureClient(
        tmp_path,
        json_responses=[
            (_capture(tmp_path, "options"), {"formats": ["gpkg"]}),
            (
                _capture(tmp_path, "create"),
                {"id": 7, "url": job_url, "state": "processing"},
            ),
            (
                _capture(tmp_path, "status"),
                {
                    "id": "7",
                    "url": job_url,
                    "state": "complete",
                    "download_url": download_url,
                },
            ),
        ],
        downloads=[_capture(tmp_path, "payload")],
    )
    slept: list[float] = []
    result = LinzExportArchiver(client, sleeper=slept.append).archive_export(  # type: ignore[arg-type]
        source_id="linz",
        endpoint_id="exports",
        exports_url="https://data.linz.govt.nz/services/api/v1.x/exports",
        item_urls=[
            "https://data.linz.govt.nz/layer/2/",
            "https://data.linz.govt.nz/layer/1/",
        ],
        formats={"2": "csv", "1": "geopackage"},
        crs="EPSG:2193",
        api_key="private",
        output_dir=tmp_path / "out",
        name="bounded export",
        extent={"bbox": [1, 2, 3, 4]},
        options={"simplify": False},
        poll_interval_seconds=0.25,
    )
    assert slept == [0.25]
    assert result.export_id == "7"
    assert len(result.status_captures) == 1
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["request"]["items"] == [
        {"item": "https://data.linz.govt.nz/layer/1/"},
        {"item": "https://data.linz.govt.nz/layer/2/"},
    ]
    assert list(manifest["request"]["formats"]) == ["1", "2"]
    assert "signature=private" not in manifest["download_url"]
    assert manifest["manifest_sha256"] == sha256_json(manifest, omit_keys={"manifest_sha256"})


@pytest.mark.parametrize(
    ("responses", "poll_limit", "message"),
    [
        (
            [
                {"ok": True},
                {"id": 1, "url": "https://data.linz.govt.nz/jobs/1", "state": "error"},
            ],
            1,
            "terminal state error",
        ),
        (
            [
                {"ok": True},
                {"id": 1, "url": "https://data.linz.govt.nz/jobs/1", "state": "complete"},
            ],
            1,
            "no download_url",
        ),
        (
            [
                {"ok": True},
                {"id": 1, "url": "https://data.linz.govt.nz/jobs/1", "state": "processing"},
                {"id": 2, "url": "https://data.linz.govt.nz/jobs/1", "state": "complete"},
            ],
            1,
            "identity changed",
        ),
        (
            [
                {"ok": True},
                {"id": 1, "url": "https://data.linz.govt.nz/jobs/1", "state": "processing"},
                {"id": 1, "url": "https://data.linz.govt.nz/jobs/1", "state": "processing"},
            ],
            1,
            "remained processing",
        ),
    ],
)
def test_archive_export_rejects_incomplete_jobs(
    tmp_path: Path,
    responses: list[dict[str, Any]],
    poll_limit: int,
    message: str,
) -> None:
    client = FakeCaptureClient(
        tmp_path,
        json_responses=[
            (_capture(tmp_path, f"response-{index}"), response)
            for index, response in enumerate(responses)
        ],
    )
    with pytest.raises(LinzExportError, match=message):
        LinzExportArchiver(client).archive_export(  # type: ignore[arg-type]
            source_id="linz",
            endpoint_id="exports",
            exports_url="https://data.linz.govt.nz/exports/",
            item_urls=["https://data.linz.govt.nz/layer/1/"],
            formats={"1": "gpkg"},
            crs="EPSG:2193",
            api_key="secret",
            output_dir=tmp_path,
            poll_limit=poll_limit,
            poll_interval_seconds=0,
        )
