from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from riopa_provenance.capture import (
    CaptureError,
    CapturePolicy,
    CaptureStore,
    HttpCaptureClient,
    redact_text,
    redact_url,
    validate_resolved_addresses,
    validate_capture_url,
)
from riopa_provenance.retry import CircuitBreaker, RetryPolicy


def policy(**overrides: object) -> CapturePolicy:
    values: dict[str, object] = {"allowed_hosts": frozenset({"data.example.govt.nz"})}
    values.update(overrides)
    return CapturePolicy(**values)  # type: ignore[arg-type]


def test_capture_policy_and_url_controls() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        CapturePolicy(allowed_hosts=frozenset())
    with pytest.raises(ValueError, match="must be positive"):
        policy(max_response_bytes=0)

    validate_capture_url(httpx.URL("https://data.example.govt.nz/layer"), policy())
    with pytest.raises(CaptureError, match="scheme"):
        validate_capture_url(httpx.URL("http://data.example.govt.nz/layer"), policy())
    with pytest.raises(CaptureError, match="credentials"):
        validate_capture_url(httpx.URL("https://user:pass@data.example.govt.nz/layer"), policy())
    with pytest.raises(CaptureError, match="allowlisted"):
        validate_capture_url(httpx.URL("https://other.example/layer"), policy())
    with pytest.raises(CaptureError, match="non-public"):
        validate_capture_url(
            httpx.URL("https://127.0.0.1/layer"),
            CapturePolicy(allowed_hosts=frozenset({"127.0.0.1"})),
        )


def test_connection_time_resolution_rejects_private_or_invalid_addresses() -> None:
    assert validate_resolved_addresses("data.example.govt.nz", ["8.8.8.8"]) == ("8.8.8.8",)
    with pytest.raises(CaptureError, match="non-public"):
        validate_resolved_addresses("data.example.govt.nz", ["10.0.0.1"])
    with pytest.raises(CaptureError, match="invalid"):
        validate_resolved_addresses("data.example.govt.nz", ["not-an-ip"])
    with pytest.raises(CaptureError, match="no addresses"):
        validate_resolved_addresses("data.example.govt.nz", [])
    validate_capture_url(
        httpx.URL("https://data.example.govt.nz/layer"),
        policy(resolve_addresses=lambda host: ["8.8.8.8"]),
    )
    with pytest.raises(CaptureError, match="non-public"):
        validate_capture_url(
            httpx.URL("https://data.example.govt.nz/layer"),
            policy(resolve_addresses=lambda host: ["192.168.1.10"]),
        )


def test_redaction_helpers() -> None:
    configured = policy()
    assert (
        redact_url(
            "https://data.example.govt.nz/layer?key=secret&name=visible&token=abc",
            configured,
        )
        == "https://data.example.govt.nz/layer?key=%3Credacted%3E&name=visible&token=%3Credacted%3E"
    )
    assert redact_text("token-long token", ["token", "token-long"]) == "<redacted> <redacted>"


def test_capture_store_content_addressing_and_immutable_metadata(tmp_path: Path) -> None:
    store = CaptureStore(tmp_path, id_factory=lambda: "fixed")
    digest, object_path = store.write_object(b"payload")
    assert object_path.read_bytes() == b"payload"
    assert store.write_object(b"payload") == (digest, object_path)

    metadata = {"capture_id": "urn:uuid:fixed"}
    path = store.write_capture(metadata)
    assert json.loads(path.read_text(encoding="utf-8")) == metadata
    with pytest.raises(CaptureError, match="already exists"):
        store.write_capture(metadata)
    with pytest.raises(ValueError, match="requires capture_id"):
        store.write_capture({})


def test_http_capture_exact_bytes_and_redacted_metadata(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["accept-encoding"] == "identity"
        return httpx.Response(
            200,
            headers={"Content-Type": "application/json", "X-Trace": "ok"},
            content=b'{"ok":true}',
            request=request,
        )

    store = CaptureStore(
        tmp_path,
        clock=lambda: datetime(2026, 7, 20, tzinfo=UTC),
        id_factory=lambda: "capture-1",
    )
    client = HttpCaptureClient(
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        store=store,
        policy=policy(),
    )
    result, value = client.capture_json(
        "GET",
        "https://data.example.govt.nz/layer",
        params={"key": "super-secret", "visible": "yes"},
        headers={"Authorization": "Bearer super-secret"},
        source_id="urn:test:source",
        endpoint_id="urn:test:endpoint",
        redact_values=["super-secret"],
    )

    assert value == {"ok": True}
    assert result.succeeded
    assert result.object_path.read_bytes() == b'{"ok":true}'
    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    rendered = json.dumps(metadata)
    assert "super-secret" not in rendered
    assert "%3Credacted%3E" in metadata["request"]["url"]
    assert metadata["request"]["headers"]["authorization"] == "<redacted>"
    assert metadata["object"]["sha256"] == result.object_sha256


def test_http_capture_rejects_redirect_size_bad_length_and_non_json(tmp_path: Path) -> None:
    responses = iter(
        [
            httpx.Response(302, headers={"Location": "https://data.example.govt.nz/other"}),
            httpx.Response(200, headers={"Content-Length": "bad"}, content=b"x"),
            httpx.Response(200, headers={"Content-Length": "10"}, content=b"0123456789"),
            httpx.Response(200, content=b"not-json"),
        ]
    )

    def handler(request: httpx.Request) -> httpx.Response:
        response = next(responses)
        response.request = request
        return response

    client = HttpCaptureClient(
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        store=CaptureStore(tmp_path, id_factory=lambda: "unused"),
        policy=policy(max_response_bytes=5),
    )
    kwargs = {"source_id": "urn:test:source", "endpoint_id": "urn:test:endpoint"}
    with pytest.raises(CaptureError, match="redirect"):
        client.capture("GET", "https://data.example.govt.nz/one", **kwargs)
    with pytest.raises(CaptureError, match="invalid response Content-Length"):
        client.capture("GET", "https://data.example.govt.nz/two", **kwargs)
    with pytest.raises(CaptureError, match="exceeds limit"):
        client.capture("GET", "https://data.example.govt.nz/three", **kwargs)

    json_client = HttpCaptureClient(
        client=client.client,
        store=CaptureStore(tmp_path / "json", id_factory=lambda: "json"),
        policy=policy(),
    )
    with pytest.raises(CaptureError, match="not valid UTF-8 JSON"):
        json_client.capture_json("GET", "https://data.example.govt.nz/four", **kwargs)


def test_non_success_is_archived_before_error(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, content=b"unavailable", request=request)

    store = CaptureStore(tmp_path, id_factory=lambda: "failure")
    client = HttpCaptureClient(
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        store=store,
        policy=policy(),
    )
    with pytest.raises(CaptureError, match="captured HTTP 503"):
        client.capture(
            "GET",
            "https://data.example.govt.nz/failure",
            source_id="urn:test:source",
            endpoint_id="urn:test:endpoint",
        )
    assert (tmp_path / "captures" / "failure.json").is_file()


def test_capture_with_retry_preserves_each_retryable_attempt(tmp_path: Path) -> None:
    responses = iter([503, 200])

    def handler(request: httpx.Request) -> httpx.Response:
        status = next(responses)
        headers = {"Retry-After": "3"} if status == 503 else {}
        return httpx.Response(status, headers=headers, content=b"ok", request=request)

    store = CaptureStore(tmp_path, id_factory=iter(["first", "second"]).__next__)
    client = HttpCaptureClient(
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        store=store,
        policy=policy(),
    )
    delays: list[float] = []
    decisions = []
    result = client.capture_with_retry(
        "GET",
        "https://data.example.govt.nz/retry",
        source_id="urn:test:source",
        endpoint_id="urn:test:endpoint",
        retry_policy=RetryPolicy(max_attempts=2, base_delay_seconds=0.25),
        sleep=delays.append,
        on_decision=decisions.append,
    )
    assert result.status_code == 200
    assert delays == [3.0]
    assert [item.reason for item in decisions] == ["retryable-status", "status-not-retryable"]
    assert (tmp_path / "captures" / "first.json").is_file()
    assert (tmp_path / "captures" / "second.json").is_file()


def test_capture_with_retry_bounds_transport_failures(tmp_path: Path) -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ConnectError("temporary DNS failure", request=request)

    client = HttpCaptureClient(
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        store=CaptureStore(tmp_path),
        policy=policy(),
    )
    with pytest.raises(CaptureError, match="transport failure"):
        client.capture_with_retry(
            "GET",
            "https://data.example.govt.nz/failure",
            source_id="urn:test:source",
            endpoint_id="urn:test:endpoint",
            retry_policy=RetryPolicy(max_attempts=2, base_delay_seconds=0),
        )
    assert attempts == 2


def test_capture_with_retry_uses_circuit_breaker(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"ok", request=request)

    breaker = CircuitBreaker(failure_threshold=1)
    client = HttpCaptureClient(
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        store=CaptureStore(tmp_path, id_factory=lambda: "ok"),
        policy=policy(),
    )
    result = client.capture_with_retry(
        "GET",
        "https://data.example.govt.nz/ok",
        source_id="urn:test:source",
        endpoint_id="urn:test:endpoint",
        circuit_breaker=breaker,
    )
    assert result.succeeded and breaker.state == "closed"
