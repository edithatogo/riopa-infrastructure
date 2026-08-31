#!/usr/bin/env python3
"""Actions-only anonymous, pinned Hugging Face metadata observation; never publish."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from collections.abc import Callable
from pathlib import Path, PurePosixPath
from typing import Any

import httpx
from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.errors import HfHubHTTPError

from riopa_provenance.hashing import sha256_bytes, sha256_json

ENDPOINT = "https://huggingface.co"
LIMIT = 2_097_152
KEYS = {"schema_version", "provider", "repository", "revision", "path", "sha256", "max_bytes"}
TRANSIENT = {408, 429, 500, 502, 503, 504}


class ObservationError(ValueError):
    def __init__(self, classification: str) -> None:
        self.classification = classification
        super().__init__(classification)


def check(condition: bool, classification: str = "conflict") -> None:
    if not condition:
        raise ObservationError(classification)


def parse(body: bytes) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            check(key not in result)
            result[key] = value
        return result

    def constant(_value: str) -> Any:
        raise ObservationError("conflict")

    value = json.loads(body, object_pairs_hook=unique, parse_constant=constant)
    check(isinstance(value, dict))
    sha256_json(value)  # Reject unsupported canonical JSON numbers as well.
    return dict(value)


def validate_request(request: dict[str, Any]) -> None:
    check(isinstance(request, dict) and set(request) == KEYS)
    check(request["schema_version"] == "1.0.0" and request["provider"] == "hugging-face")
    repository = request["repository"]
    check(isinstance(repository, str) and len(repository) <= 193)
    check(
        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}/[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", repository)
        is not None
    )
    for key, length in (("revision", 40), ("sha256", 64)):
        value = request[key]
        check(isinstance(value, str) and re.fullmatch(rf"[a-f0-9]{{{length}}}", value) is not None)
    name = request["path"]
    check(isinstance(name, str) and len(name) <= 1024)
    path = PurePosixPath(name)
    check(
        not path.is_absolute()
        and path.as_posix() == name
        and ".." not in path.parts
        and path.suffix == ".json"
        and re.fullmatch(r"[A-Za-z0-9_./-]+", name) is not None
    )
    check(type(request["max_bytes"]) is int and 0 < request["max_bytes"] <= LIMIT)


def report(
    request: dict[str, Any] | None, status: str, attempts: int, *, observed_bytes: int | None = None
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "publication_provider_metadata_observation",
        "provider": "hugging-face",
        "request_sha256": sha256_json(request) if request is not None else None,
        "status": status,
        "attempts": attempts,
        "remote_write_authorized": False,
        "publication_receipt_created": False,
        "non_claims": [
            "Metadata observation is not full asset verification or publication acceptance.",
            "Missing or unavailable metadata does not authorize another release or deposit.",
            "No new plan, rights decision, preservation qualification or release authority "
            "is established.",
        ],
    }
    if status == "matching-metadata-observed":
        if request is None:
            raise ObservationError("conflict")
        result["binding"] = {
            key: request[key] for key in ("repository", "revision", "path", "sha256")
        }
        result["observed_bytes"] = observed_bytes
    else:
        result["classification"] = status
    return {**result, "report_sha256": sha256_json(result)}


def _read_once(request: dict[str, Any], api: Any, download: Callable[..., Any]) -> int:
    repository, revision, name = (request[key] for key in ("repository", "revision", "path"))
    info = api.repo_info(
        repository, repo_type="dataset", revision=revision, token=False, timeout=20
    )
    check(info.private is False and info.sha == revision)
    infos = api.get_paths_info(
        repository, [name], repo_type="dataset", revision=revision, token=False
    )
    check(bool(infos), "missing")
    check(len(infos) == 1 and infos[0].path == name)
    size = getattr(infos[0], "size", None)
    if not isinstance(size, int) or isinstance(size, bool):
        raise ObservationError("conflict")
    check(0 < size <= request["max_bytes"])
    with tempfile.TemporaryDirectory(prefix="riopa-provider-metadata-") as temporary:
        root = Path(temporary).resolve()
        destination = root / "download"
        returned = Path(
            download(
                repo_id=repository,
                filename=name,
                repo_type="dataset",
                revision=revision,
                endpoint=ENDPOINT,
                token=False,
                force_download=True,
                local_files_only=False,
                local_dir=destination,
                cache_dir=root / "cache",
                etag_timeout=20,
            )
        )
        expected = destination / name
        check(returned == expected and returned.resolve().is_relative_to(root))
        check(not any(path.is_symlink() for path in (returned, *returned.parents)))
        check(returned.is_file() and returned.stat().st_size == size)
        with returned.open("rb") as stream:
            body = stream.read(request["max_bytes"] + 1)
        check(len(body) == size and sha256_bytes(body) == request["sha256"])
        parse(body)
    return size


def observe(request: dict[str, Any], *, api: Any, download: Callable[..., Any]) -> dict[str, Any]:
    """At most three adapter attempts; injected transports enable offline testing."""
    validate_request(request)
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return report(request, "conflict", 0)
    for attempt in range(1, 4):
        try:
            size = _read_once(request, api, download)
            return report(request, "matching-metadata-observed", attempt, observed_bytes=size)
        except ObservationError as error:
            return report(request, error.classification, attempt)
        except HfHubHTTPError as error:
            status = error.response.status_code
            if status in TRANSIENT and attempt < 3:
                continue
            classification = "missing" if status == 404 else "transport"
            if status in {400, 401, 403, 409, 422}:
                classification = "conflict"
            return report(request, classification, attempt)
        except httpx.TransportError, TimeoutError, ConnectionError:
            if attempt < 3:
                continue
            return report(request, "transport", attempt)
        except ValueError, TypeError, KeyError, AttributeError, RecursionError:
            return report(request, "conflict", attempt)
        except OSError:
            return report(request, "transport", attempt)
    raise RuntimeError("unreachable retry state")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    args = parser.parse_args()
    request = None
    try:
        check(os.environ.get("GITHUB_ACTIONS") == "true")
        check(args.request.is_file() and 0 < args.request.stat().st_size <= 16_384)
        with args.request.open("rb") as stream:
            body = stream.read(16_385)
        check(len(body) <= 16_384)
        candidate = parse(body)
        validate_request(candidate)
        request = candidate
        result = observe(
            request, api=HfApi(endpoint=ENDPOINT, token=False), download=hf_hub_download
        )
    except Exception:
        # No exception text, URLs, file contents or credential material in failure output.
        result = report(request, "conflict", 0)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if result["status"] == "matching-metadata-observed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
