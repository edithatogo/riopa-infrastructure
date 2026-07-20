"""Koordinates/LINZ asynchronous bulk-export archival.

The Koordinates export API is the capability-complete payload path for data
that cannot be archived efficiently through WFS.  This module preserves the
OPTIONS response, export creation request/response, every observed job state,
redirect responses, and the exact downloaded archive bytes.  It never follows
an unregistered host or silently treats a terminal job state as success.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .capture import CaptureError, CaptureResult, HttpCaptureClient, redact_url
from .hashing import sha256_json


class LinzExportError(CaptureError):
    """Raised when an export cannot be archived completely and safely."""


@dataclass(frozen=True)
class LinzExportArchive:
    """Content-bound result of one completed Koordinates export."""

    manifest_path: Path
    options_capture: CaptureResult
    create_capture: CaptureResult
    status_captures: tuple[CaptureResult, ...]
    download_captures: tuple[CaptureResult, ...]
    payload_capture: CaptureResult
    export_id: str
    job_url: str
    download_url: str
    state: str


def _capture_reference(capture: CaptureResult) -> dict[str, Any]:
    return {
        "capture_id": capture.capture_id,
        "object_sha256": capture.object_sha256,
        "size_bytes": capture.size_bytes,
        "status_code": capture.status_code,
        "retrieved_at": capture.retrieved_at,
        "metadata_path": capture.metadata_path.as_posix(),
        "object_path": capture.object_path.as_posix(),
    }


def _require_object(value: Any, *, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise LinzExportError(f"{context} response must be a JSON object")
    return value


def _job_identity(job: Mapping[str, Any]) -> tuple[str, str]:
    export_id = job.get("id")
    job_url = job.get("url")
    if isinstance(export_id, bool) or not isinstance(export_id, (int, str)):
        raise LinzExportError("export creation response has no valid id")
    if not isinstance(job_url, str) or not job_url:
        raise LinzExportError("export creation response has no job URL")
    return str(export_id), job_url


def _job_state(job: Mapping[str, Any]) -> str:
    state = job.get("state")
    if not isinstance(state, str) or not state:
        raise LinzExportError("export job response has no valid state")
    normalised = state.casefold()
    allowed = {"processing", "complete", "cancelled", "error", "gone"}
    if normalised not in allowed:
        raise LinzExportError(f"unsupported export job state: {state}")
    return normalised


class LinzExportArchiver:
    """Archive one Koordinates export job from request through download."""

    def __init__(
        self,
        capture_client: HttpCaptureClient,
        *,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.capture_client = capture_client
        self.sleeper = sleeper

    def _headers(self, api_key: str) -> dict[str, str]:
        if not api_key:
            raise ValueError("api_key must not be empty")
        return {"Authorization": f"key {api_key}", "Accept": "application/json"}

    def _capture_download(
        self,
        *,
        source_id: str,
        endpoint_id: str,
        download_url: str,
        api_key: str,
        max_redirects: int,
    ) -> tuple[tuple[CaptureResult, ...], CaptureResult]:
        if max_redirects < 0:
            raise ValueError("max_redirects must be non-negative")
        captures: list[CaptureResult] = []
        visited: set[str] = set()
        current = download_url
        for redirect_index in range(max_redirects + 1):
            if current in visited:
                raise LinzExportError(f"export download redirect loop detected: {current}")
            visited.add(current)
            # Credentials are sent only to the Koordinates host.  Signed object
            # storage URLs carry their own query credential and must not receive
            # the LINZ API key.
            host = self.capture_client.client.build_request("GET", current).url.host
            headers = (
                self._headers(api_key)
                if host and host.casefold() == "data.linz.govt.nz"
                else {"Accept": "application/octet-stream"}
            )
            capture = self.capture_client.capture(
                "GET",
                current,
                source_id=source_id,
                endpoint_id=f"{endpoint_id}:download:{redirect_index}",
                headers=headers,
                require_success=False,
                redact_values=(api_key,),
            )
            captures.append(capture)
            if capture.succeeded:
                return tuple(captures), capture
            if 300 <= capture.status_code < 400:
                location = capture.response_location
                if not location:
                    raise LinzExportError(
                        "export download redirect response has no Location header"
                    )
                # The capture client validates the next URL against the same
                # explicit host allowlist before issuing the request.
                current = str(
                    self.capture_client.client.build_request("GET", current).url.join(location)
                )
                continue
            raise LinzExportError(
                f"export download returned HTTP {capture.status_code}; capture={capture.capture_id}"
            )
        raise LinzExportError(f"export download exceeded {max_redirects} redirects")

    def archive_export(
        self,
        *,
        source_id: str,
        endpoint_id: str,
        exports_url: str,
        item_urls: Sequence[str],
        formats: Mapping[str, str],
        crs: str,
        api_key: str,
        output_dir: str | Path,
        name: str | None = None,
        extent: str | Mapping[str, Any] | None = None,
        options: Mapping[str, Any] | None = None,
        poll_limit: int = 120,
        poll_interval_seconds: float = 5.0,
        max_download_redirects: int = 3,
    ) -> LinzExportArchive:
        """Create, poll, download, and describe one complete export.

        The method is intentionally synchronous.  Operational schedulers can
        run many bounded jobs, while each individual manifest remains a simple,
        auditable state history.
        """

        if not item_urls:
            raise ValueError("item_urls must not be empty")
        if not formats:
            raise ValueError("formats must not be empty")
        if not crs:
            raise ValueError("crs must not be empty")
        if poll_limit < 1:
            raise ValueError("poll_limit must be positive")
        if poll_interval_seconds < 0:
            raise ValueError("poll_interval_seconds must be non-negative")
        if len(set(item_urls)) != len(item_urls):
            raise ValueError("item_urls must be unique")

        exports_url = exports_url.rstrip("/") + "/"
        headers = self._headers(api_key)
        options_capture, options_payload = self.capture_client.capture_json(
            "OPTIONS",
            exports_url,
            source_id=source_id,
            endpoint_id=f"{endpoint_id}:options",
            headers=headers,
            redact_values=(api_key,),
        )
        _require_object(options_payload, context="export OPTIONS")

        request_body: dict[str, Any] = {
            "crs": crs,
            "formats": dict(sorted(formats.items())),
            "items": [{"item": item_url} for item_url in sorted(item_urls)],
        }
        if name is not None:
            request_body["name"] = name
        if extent is not None:
            request_body["extent"] = extent
        if options is not None:
            request_body["options"] = dict(options)

        create_capture, create_payload = self.capture_client.capture_json(
            "POST",
            exports_url,
            source_id=source_id,
            endpoint_id=f"{endpoint_id}:create",
            headers=headers,
            json_body=request_body,
            redact_values=(api_key,),
        )
        job = _require_object(create_payload, context="export creation")
        export_id, job_url = _job_identity(job)
        state = _job_state(job)
        status_captures: list[CaptureResult] = []

        polls = 0
        while state == "processing":
            if polls >= poll_limit:
                raise LinzExportError(
                    f"export {export_id} remained processing after {poll_limit} polls"
                )
            if poll_interval_seconds:
                self.sleeper(poll_interval_seconds)
            status_capture, status_payload = self.capture_client.capture_json(
                "GET",
                job_url,
                source_id=source_id,
                endpoint_id=f"{endpoint_id}:status:{polls + 1}",
                headers=headers,
                redact_values=(api_key,),
            )
            status_captures.append(status_capture)
            job = _require_object(status_payload, context="export status")
            observed_id, observed_url = _job_identity(job)
            if observed_id != export_id or observed_url != job_url:
                raise LinzExportError("export job identity changed while polling")
            state = _job_state(job)
            polls += 1

        if state != "complete":
            raise LinzExportError(f"export {export_id} ended in terminal state {state}")
        download_url = job.get("download_url")
        if not isinstance(download_url, str) or not download_url:
            raise LinzExportError("completed export has no download_url")

        download_captures, payload_capture = self._capture_download(
            source_id=source_id,
            endpoint_id=endpoint_id,
            download_url=download_url,
            api_key=api_key,
            max_redirects=max_download_redirects,
        )

        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        manifest_seed = {
            "source_id": source_id,
            "endpoint_id": endpoint_id,
            "export_id": export_id,
            "request_body_sha256": sha256_json(request_body),
            "options_capture": options_capture.object_sha256,
            "create_capture": create_capture.object_sha256,
            "status_captures": [capture.object_sha256 for capture in status_captures],
            "download_captures": [capture.object_sha256 for capture in download_captures],
            "payload_sha256": payload_capture.object_sha256,
        }
        manifest: dict[str, Any] = {
            "schema_version": "1.0.0",
            "record_type": "linz_export_capture_set",
            "export_capture_set_id": (
                f"urn:riopa:linz-export-capture-set:{sha256_json(manifest_seed)}"
            ),
            "source_id": source_id,
            "endpoint_id": endpoint_id,
            "export_id": export_id,
            "job_url": redact_url(job_url, self.capture_client.policy, redact_values=(api_key,)),
            "state": state,
            "download_url": redact_url(
                download_url, self.capture_client.policy, redact_values=(api_key,)
            ),
            "request": request_body,
            "request_sha256": sha256_json(request_body),
            "options_capture": _capture_reference(options_capture),
            "create_capture": _capture_reference(create_capture),
            "status_captures": [_capture_reference(capture) for capture in status_captures],
            "download_captures": [_capture_reference(capture) for capture in download_captures],
            "payload": _capture_reference(payload_capture),
            "manifest_sha256": "",
        }
        manifest["manifest_sha256"] = sha256_json(manifest, omit_keys={"manifest_sha256"})
        manifest_path = output / f"export-{export_id}-capture-set.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return LinzExportArchive(
            manifest_path=manifest_path,
            options_capture=options_capture,
            create_capture=create_capture,
            status_captures=tuple(status_captures),
            download_captures=download_captures,
            payload_capture=payload_capture,
            export_id=export_id,
            job_url=job_url,
            download_url=download_url,
            state=state,
        )
