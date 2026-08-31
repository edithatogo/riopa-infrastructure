from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from huggingface_hub.errors import HfHubHTTPError, LocalEntryNotFoundError, OfflineModeIsEnabled

from riopa_provenance.hashing import sha256_bytes, sha256_json
from scripts import reconcile_publication_provider_metadata as adapter


class Hub:
    def __init__(self, body: bytes) -> None:
        self.body = body
        self.calls = 0
        self.downloads = 0
        self.failures: list[Exception] = []
        self.private = False
        self.missing = False
        self.size: Any = len(body)
        self.wrong_path = False
        self.wrong_revision = False
        self.escape = False
        self.symlink = False
        self.download_failures: list[Exception] = []
        self.directories: list[Path] = []

    def repo_info(self, repository: str, **kwargs: Any) -> SimpleNamespace:
        assert repository == "owner/repository"
        assert kwargs["token"] is False and kwargs["repo_type"] == "dataset"
        assert kwargs["revision"] == "a" * 40
        self.calls += 1
        if self.failures:
            raise self.failures.pop(0)
        return SimpleNamespace(
            private=self.private, sha="b" * 40 if self.wrong_revision else kwargs["revision"]
        )

    def get_paths_info(self, repository: str, paths: list[str], **kwargs: Any) -> list:
        assert repository == "owner/repository" and paths == ["release/metadata.json"]
        assert kwargs == {"repo_type": "dataset", "revision": "a" * 40, "token": False}
        return (
            []
            if self.missing
            else [SimpleNamespace(path="wrong" if self.wrong_path else paths[0], size=self.size)]
        )

    def download(self, **kwargs: Any) -> str:
        self.downloads += 1
        assert kwargs["endpoint"] == "https://huggingface.co"
        assert kwargs["repo_id"] == "owner/repository"
        assert kwargs["revision"] == "a" * 40 and kwargs["token"] is False
        assert kwargs["force_download"] is True and kwargs["local_files_only"] is False
        destination = kwargs["local_dir"]
        self.directories.append(destination)
        assert kwargs["cache_dir"].parent == destination.parent
        path = destination / kwargs["filename"]
        path.parent.mkdir(parents=True)
        path.write_bytes(self.body)
        if self.symlink:
            other = path.with_name("other.json")
            path.rename(other)
            path.symlink_to(other)
        if self.download_failures:
            raise self.download_failures.pop(0)
        return str(path.parent) if self.escape else str(path)


@pytest.fixture
def context(monkeypatch) -> tuple[dict, Hub]:
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    body = b'{"release":"v0.4.0","metadata":"bounded"}\n'
    request = {
        "schema_version": "1.0.0",
        "provider": "hugging-face",
        "repository": "owner/repository",
        "revision": "a" * 40,
        "path": "release/metadata.json",
        "sha256": sha256_bytes(body),
        "max_bytes": adapter.LIMIT,
    }
    return request, Hub(body)


def observe(context: tuple[dict, Hub]) -> dict:
    request, hub = context
    result = adapter.observe(request, api=hub, download=hub.download)
    assert result["request_sha256"] == sha256_json(request)
    assert result["report_sha256"] == sha256_json(result, omit_keys={"report_sha256"})
    assert result["remote_write_authorized"] is False
    assert result["publication_receipt_created"] is False
    assert result["attempts"] == len(result["attempt_history"])
    assert [item["ordinal"] for item in result["attempt_history"]] == list(
        range(1, result["attempts"] + 1)
    )
    assert all(not path.exists() for path in hub.directories)
    return result


def test_matching_anonymous_metadata_is_repeatable_and_cleaned(context: tuple) -> None:
    request, hub = context
    first = observe(context)
    assert first == observe(context)
    assert first["status"] == "matching-metadata-observed"
    assert first["binding"] == {
        key: request[key] for key in ("repository", "revision", "path", "sha256")
    }
    assert first["observed_bytes"] == len(hub.body)
    assert hub.calls == hub.downloads == 2
    assert "bounded" not in json.dumps(first)


@pytest.mark.parametrize(
    "key,value",
    [
        ("schema_version", "2"),
        ("provider", "other"),
        ("repository", "https://evil.test/x"),
        ("repository", "../private"),
        ("revision", "main"),
        ("revision", "A" * 40),
        ("sha256", "invalid"),
        ("path", "../private.json"),
        ("path", "/absolute.json"),
        ("path", "foo//bar.json"),
        ("path", "foo/./bar.json"),
        ("path", "foo\\bar.json"),
        ("path", "metadata.json?token=SECRET"),
        ("path", "features.parquet"),
        ("max_bytes", True),
        ("max_bytes", 0),
        ("max_bytes", adapter.LIMIT + 1),
    ],
)
def test_strict_request_rejected_before_transport(context: tuple, key: str, value: Any) -> None:
    request, hub = context
    request[key] = value
    with pytest.raises(ValueError):
        observe(context)
    assert hub.calls == hub.downloads == 0


def test_request_exact_keys(context: tuple) -> None:
    request, hub = context
    request["unexpected"] = True
    with pytest.raises(ValueError):
        observe(context)
    del request["unexpected"]
    del request["sha256"]
    with pytest.raises(ValueError):
        observe(context)
    assert hub.calls == 0


@pytest.mark.parametrize(
    "fault", ["private", "missing", "size", "bool-size", "path", "revision", "digest", "escape"]
)
def test_permanent_conflicts_do_not_retry(context: tuple, fault: str) -> None:
    request, hub = context
    if fault == "private":
        hub.private = True
    elif fault == "missing":
        hub.missing = True
    elif fault == "size":
        hub.size = adapter.LIMIT + 1
    elif fault == "bool-size":
        hub.size = True
    elif fault == "path":
        hub.wrong_path = True
    elif fault == "revision":
        hub.wrong_revision = True
    elif fault == "digest":
        request["sha256"] = "0" * 64
    else:
        hub.escape = True
    result = observe(context)
    assert result["status"] == ("missing" if fault == "missing" else "conflict")
    assert hub.calls == 1
    assert hub.downloads == (1 if fault in {"digest", "escape"} else 0)


def http_error(status: int) -> HfHubHTTPError:
    return HfHubHTTPError(
        "SECRET-provider-message",
        response=httpx.Response(
            status, request=httpx.Request("GET", "https://huggingface.co/metadata")
        ),
    )


@pytest.mark.parametrize("status", [408, 429, 500, 502, 503, 504])
def test_transient_recovery_is_bounded(context: tuple, status: int) -> None:
    _, hub = context
    hub.failures = [http_error(status), http_error(status)]
    result = observe(context)
    assert result["status"] == "matching-metadata-observed" and result["attempts"] == 3
    assert hub.calls == 3 and hub.downloads == 1
    assert result["attempt_history"] == [
        {"ordinal": 1, "status": "transport", "http_status": status},
        {"ordinal": 2, "status": "transport", "http_status": status},
        {"ordinal": 3, "status": "matching-metadata-observed"},
    ]


@pytest.mark.parametrize(
    "failure", [http_error(503), httpx.ReadTimeout("SECRET"), ConnectionError("SECRET")]
)
def test_transient_exhaustion_redacts_error(context: tuple, failure: Exception) -> None:
    _, hub = context
    hub.failures = [failure] * 3
    result = observe(context)
    assert result["status"] == "transport" and result["attempts"] == 3
    assert "SECRET" not in json.dumps(result)
    assert hub.calls == 3 and hub.downloads == 0


@pytest.mark.parametrize(
    "status,classification",
    [(404, "missing"), (401, "conflict"), (403, "conflict"), (422, "conflict"), (501, "transport")],
)
def test_permanent_http_failure_is_not_retried(
    context: tuple, status: int, classification: str
) -> None:
    _, hub = context
    hub.failures = [http_error(status)]
    assert observe(context)["status"] == classification
    assert hub.calls == 1


@pytest.mark.parametrize("body", [b"[]", b'{"x":1,"x":2}', b'{"x":NaN}', b"not-json"])
def test_hash_matching_non_metadata_json_rejected(context: tuple, body: bytes) -> None:
    request, hub = context
    hub.body = body
    hub.size = len(body)
    request["sha256"] = sha256_bytes(body)
    assert observe(context)["status"] == "conflict"
    assert hub.calls == hub.downloads == 1


def test_actions_guard_no_network(context: tuple, monkeypatch) -> None:
    _, hub = context
    monkeypatch.delenv("GITHUB_ACTIONS")
    assert observe(context)["attempts"] == 0
    assert hub.calls == hub.downloads == 0


def test_download_transient_retry_cleans_partial_cache(context: tuple) -> None:
    _, hub = context
    hub.download_failures = [http_error(503)]
    result = observe(context)
    assert result["status"] == "matching-metadata-observed" and result["attempts"] == 2
    assert hub.calls == hub.downloads == 2
    assert hub.directories[0] != hub.directories[1]


def test_download_symlink_rejected_and_cleaned(context: tuple) -> None:
    _, hub = context
    hub.symlink = True
    result = observe(context)
    assert result["status"] == "conflict"
    assert hub.calls == hub.downloads == 1


def test_main_guard_precedes_client_construction(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setattr("sys.argv", ["observe", "--request", str(tmp_path / "SECRET.json")])

    calls = []

    def forbidden(**kwargs: Any) -> None:
        calls.append(kwargs)
        raise AssertionError("client must not be constructed")

    monkeypatch.setattr(adapter, "HfApi", forbidden)
    assert adapter.main() == 1
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result["status"] == "conflict" and result["attempts"] == 0
    assert result["attempt_history"] == []
    assert "SECRET" not in captured.out
    assert calls == []


def test_main_stdout_only_bound_report(context: tuple, tmp_path: Path, monkeypatch, capsys) -> None:
    request, hub = context
    path = tmp_path / "request.json"
    path.write_text(json.dumps(request))

    def api(**kwargs: Any) -> Hub:
        assert kwargs == {"endpoint": adapter.ENDPOINT, "token": False}
        return hub

    monkeypatch.setattr(adapter, "HfApi", api)
    monkeypatch.setattr(adapter, "hf_hub_download", hub.download)
    monkeypatch.setattr("sys.argv", ["observe", "--request", str(path)])
    assert adapter.main() == 0
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert captured.err == "" and result["status"] == "matching-metadata-observed"
    hub.failures = [http_error(403)]
    assert adapter.main() == 1
    assert "SECRET" not in capsys.readouterr().out
    path.write_text('{"SECRET":1,"SECRET":2}')
    calls = hub.calls
    assert adapter.main() == 1
    assert "SECRET" not in capsys.readouterr().out and hub.calls == calls


@pytest.mark.parametrize("local_entry", [False, True])
@pytest.mark.parametrize("exhaust", [False, True])
@pytest.mark.parametrize("cli", [False, True])
def test_response_less_hub_failure_history(
    context: tuple,
    tmp_path: Path,
    monkeypatch,
    capsys,
    local_entry: bool,
    exhaust: bool,
    cli: bool,
) -> None:
    request, hub = context
    failure: Exception
    if local_entry:
        failure = LocalEntryNotFoundError("SECRET https://private.example/token")
    else:
        # Simulate response-less errors from older SDKs or custom Hub transports.
        failure = http_error(503)
        monkeypatch.setattr(failure, "response", None)
    hub.download_failures = [failure] * (3 if exhaust else 1)
    if cli:
        path = tmp_path / "request.json"
        path.write_text(json.dumps(request))
        monkeypatch.setattr(adapter, "HfApi", lambda **_kwargs: hub)
        monkeypatch.setattr(adapter, "hf_hub_download", hub.download)
        monkeypatch.setattr("sys.argv", ["observe", "--request", str(path)])
        assert adapter.main() == (1 if exhaust else 0)
        captured = capsys.readouterr()
        assert captured.err == ""
        result = json.loads(captured.out)
    else:
        result = observe(context)
    statuses = ["transport"] * (3 if exhaust else 1)
    if not exhaust:
        statuses.append("matching-metadata-observed")
    assert result["attempt_history"] == [
        {"ordinal": index, "status": status} for index, status in enumerate(statuses, 1)
    ]
    assert result["attempts"] == hub.calls == hub.downloads == len(statuses)
    assert result["status"] == statuses[-1]
    assert result["report_sha256"] == sha256_json(result, omit_keys={"report_sha256"})
    assert "SECRET" not in json.dumps(result) and "private.example" not in json.dumps(result)


@pytest.mark.parametrize(
    "cause,retry,status",
    [
        (httpx.ReadTimeout("SECRET"), True, "transport"),
        (http_error(503), True, "transport"),
        (http_error(403), False, "conflict"),
        (http_error(404), False, "missing"),
        (OfflineModeIsEnabled("SECRET"), False, "conflict"),
    ],
)
def test_force_download_wrapped_failure(
    context: tuple, cause: Exception, retry: bool, status: str
) -> None:
    _, hub = context
    wrapper = ValueError("Force download failed SECRET")
    wrapper.__cause__ = cause
    hub.download_failures = [wrapper]
    result = observe(context)
    assert result["attempt_history"][0]["status"] == status
    assert result["attempts"] == (2 if retry else 1)
    assert result["status"] == ("matching-metadata-observed" if retry else status)
    assert "SECRET" not in json.dumps(result)


def test_cyclic_or_excessive_error_causes_fail_closed() -> None:
    cycle = ValueError("SECRET")
    cycle.__cause__ = cycle
    assert adapter.failure_kind(cycle) == ("conflict", False, None)
    error: Exception = httpx.ReadTimeout("SECRET")
    for _ in range(5):
        wrapper = ValueError("SECRET")
        wrapper.__cause__ = error
        error = wrapper
    assert adapter.failure_kind(error) == ("conflict", False, None)
