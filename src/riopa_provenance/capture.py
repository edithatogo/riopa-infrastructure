"""Safe, faithful, content-addressed HTTP capture primitives.

The runtime stores exact response bytes before interpretation.  It records a
redacted request, response metadata, stable content digest, and capture
identity.  Connectors compose this primitive rather than implementing their own
network and storage behaviour.
"""

from __future__ import annotations

import contextlib
import ipaddress
import json
import os
import tempfile
import uuid
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx
from httpx._transports.base import BaseTransport

from .hashing import sha256_bytes, sha256_json
from .retry import CircuitBreaker, RateLimiter, RetryDecision, RetryPolicy, decide_retry


class CaptureError(RuntimeError):
    """Raised when a request violates policy or cannot be archived safely."""


class CaptureFailureCategory(StrEnum):
    """Stable operational categories for capture failures."""

    POLICY = "policy"
    TRANSPORT = "transport"
    REDIRECT = "redirect"
    RESPONSE_SIZE = "response-size"
    MALFORMED_RESPONSE = "malformed-response"
    HTTP_STATUS = "http-status"
    CIRCUIT_OPEN = "circuit-open"


@dataclass(frozen=True)
class CaptureFailure:
    """Structured, persistence-safe failure observation."""

    category: CaptureFailureCategory
    message: str
    retryable: bool = False
    status_code: int | None = None


@dataclass
class CaptureMetrics:
    """Small dependency-free metric accumulator for adapters and tests."""

    attempts_total: int = 0
    successes_total: int = 0
    failures_total: int = 0
    bytes_archived_total: int = 0
    failures_by_category: dict[str, int] = field(default_factory=dict)

    def record_success(self, size_bytes: int) -> None:
        self.successes_total += 1
        self.bytes_archived_total += size_bytes

    def record_failure(self, category: CaptureFailureCategory) -> None:
        self.failures_total += 1
        key = category.value
        self.failures_by_category[key] = self.failures_by_category.get(key, 0) + 1

    def snapshot(self) -> dict[str, object]:
        return {
            "attempts_total": self.attempts_total,
            "successes_total": self.successes_total,
            "failures_total": self.failures_total,
            "bytes_archived_total": self.bytes_archived_total,
            "failures_by_category": dict(sorted(self.failures_by_category.items())),
        }


@dataclass(frozen=True)
class CapturePolicy:
    """Network and storage guardrails for one capture client."""

    allowed_hosts: frozenset[str]
    allowed_schemes: frozenset[str] = frozenset({"https"})
    max_response_bytes: int = 512 * 1024 * 1024
    reject_redirects: bool = True
    secret_query_keys: frozenset[str] = frozenset(
        {"key", "api_key", "apikey", "token", "access_token", "signature", "sig"}
    )
    secret_header_names: frozenset[str] = frozenset(
        {"authorization", "proxy-authorization", "cookie", "set-cookie", "x-api-key"}
    )
    resolve_addresses: Callable[[str], Iterable[str]] | None = None

    def __post_init__(self) -> None:
        if not self.allowed_hosts:
            raise ValueError("allowed_hosts must not be empty")
        if self.max_response_bytes < 1:
            raise ValueError("max_response_bytes must be positive")


@dataclass(frozen=True)
class CaptureResult:
    capture_id: str
    source_id: str
    endpoint_id: str
    status_code: int
    media_type: str | None
    retrieved_at: str
    object_sha256: str
    size_bytes: int
    object_path: Path
    metadata_path: Path
    request_fingerprint: str
    response_location: str | None = None
    retry_after: str | None = None

    @property
    def succeeded(self) -> bool:
        return 200 <= self.status_code < 300


@dataclass
class CaptureStore:
    """Content-addressed object and immutable capture metadata store."""

    root: Path
    clock: Callable[[], datetime] = field(default=lambda: datetime.now(UTC))
    id_factory: Callable[[], str] = field(default=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        self.root = self.root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def object_path(self, digest: str) -> Path:
        return self.root / "objects" / "sha256" / digest[:2] / digest

    def capture_path(self, capture_id: str) -> Path:
        safe_id = capture_id.removeprefix("urn:uuid:")
        return self.root / "captures" / f"{safe_id}.json"

    def write_object(self, payload: bytes) -> tuple[str, Path]:
        digest = sha256_bytes(payload)
        path = self.object_path(digest)
        if path.is_file():
            if path.read_bytes() != payload:
                raise CaptureError(f"content-address collision at {path}")
            return digest, path
        _atomic_write(path, payload)
        return digest, path

    def write_capture(self, metadata: Mapping[str, Any]) -> Path:
        capture_id = metadata.get("capture_id")
        if not isinstance(capture_id, str) or not capture_id:
            raise ValueError("capture metadata requires capture_id")
        path = self.capture_path(capture_id)
        payload = json.dumps(metadata, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
        if path.exists():
            raise CaptureError(f"capture metadata already exists: {capture_id}")
        _atomic_write(path, payload)
        return path

    def verify_capture_integrity(self, capture_id: str) -> Mapping[str, Any]:
        """Verify an archived capture's metadata and content-addressed object.

        Verification is deliberately independent of the HTTP client so release
        and preservation checks can revalidate an old capture offline.
        """
        path = self.capture_path(capture_id)
        if not path.is_file():
            raise CaptureError(f"capture metadata is missing: {capture_id}")
        try:
            metadata = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CaptureError(f"capture metadata is unreadable: {capture_id}") from exc
        if not isinstance(metadata, Mapping):
            raise CaptureError(f"capture metadata must be an object: {capture_id}")
        obj = metadata.get("object")
        if not isinstance(obj, Mapping) or not isinstance(obj.get("sha256"), str):
            raise CaptureError(f"capture object digest is missing: {capture_id}")
        digest = obj["sha256"]
        object_path = self.object_path(digest)
        if not object_path.is_file() or sha256_bytes(object_path.read_bytes()) != digest:
            raise CaptureError(f"capture object digest mismatch: {capture_id}")
        return metadata


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporary)
        raise


def _normalise_host(host: str) -> str:
    return host.rstrip(".").lower()


def _validate_public_host(host: str) -> None:
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return
    if not address.is_global:
        raise CaptureError(f"non-public IP address is not allowed: {host}")


def validate_resolved_addresses(host: str, addresses: Iterable[str]) -> tuple[str, ...]:
    """Validate connection-time DNS results and return normalized addresses."""

    normalized: list[str] = []
    for value in addresses:
        try:
            address = ipaddress.ip_address(value)
        except ValueError as exc:
            raise CaptureError(f"resolver returned invalid address for {host}: {value}") from exc
        if not address.is_global:
            raise CaptureError(f"resolver returned non-public address for {host}: {value}")
        normalized.append(str(address))
    if not normalized:
        raise CaptureError(f"resolver returned no addresses for {host}")
    return tuple(dict.fromkeys(normalized))


def validate_capture_url(url: httpx.URL, policy: CapturePolicy) -> None:
    """Apply scheme, credential, host allowlist, and IP-address controls."""

    scheme = url.scheme.lower()
    if scheme not in policy.allowed_schemes:
        raise CaptureError(f"URL scheme is not allowed: {scheme}")
    if url.username or url.password:
        raise CaptureError("credentials in URL authority are not allowed")
    host = _normalise_host(url.host or "")
    if not host:
        raise CaptureError("URL has no host")
    allowed = {_normalise_host(item) for item in policy.allowed_hosts}
    if host not in allowed:
        raise CaptureError(f"host is not allowlisted: {host}")
    _validate_public_host(host)
    if policy.resolve_addresses is not None:
        validate_resolved_addresses(host, policy.resolve_addresses(host))


class PinnedResolverTransport(BaseTransport):
    """Connect to a validated DNS result while preserving HTTP Host and TLS SNI.

    The request URL is rewritten only at the transport boundary. This prevents
    the underlying network stack from resolving the hostname again after policy
    validation, while the original hostname remains available for HTTP routing
    and certificate verification.
    """

    def __init__(
        self,
        resolver: Callable[[str], Iterable[str]],
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.resolver = resolver
        self.transport = transport or httpx.HTTPTransport()

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        host = _normalise_host(request.url.host or "")
        addresses = validate_resolved_addresses(host, self.resolver(host))
        pinned_url = request.url.copy_with(host=addresses[0])
        headers = request.headers.copy()
        default_port = 443 if request.url.scheme == "https" else 80
        authority = (
            host if request.url.port in {None, default_port} else f"{host}:{request.url.port}"
        )
        headers["Host"] = authority
        extensions = dict(request.extensions)
        extensions["sni_hostname"] = host
        pinned_request = httpx.Request(
            request.method,
            pinned_url,
            headers=headers,
            stream=request.stream,
            extensions=extensions,
        )
        return self.transport.handle_request(pinned_request)

    def close(self) -> None:
        self.transport.close()


def _redacted_url(url: httpx.URL, secret_keys: frozenset[str]) -> str:
    parsed = urlsplit(str(url))
    query = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        query.append((key, "<redacted>" if key.lower() in secret_keys else value))
    return urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment)
    )


def redact_url(
    url: str | httpx.URL,
    policy: CapturePolicy,
    *,
    redact_values: Sequence[str] = (),
) -> str:
    """Return a persistence-safe URL with registered query keys and values redacted."""

    rendered = _redacted_url(httpx.URL(str(url)), policy.secret_query_keys)
    return redact_text(rendered, redact_values)


def redact_text(value: str, secrets: Sequence[str], *, replacement: str = "<redacted>") -> str:
    """Remove literal credential values from a string before persistence.

    The helper is deliberately literal rather than heuristic: callers know the
    credential material supplied at runtime, while attempting to infer secrets
    from arbitrary URLs risks both false negatives and destructive redaction.
    Longest values are replaced first so overlapping credentials cannot expose a
    suffix or prefix.
    """

    rendered = value
    for secret in sorted({item for item in secrets if item}, key=len, reverse=True):
        rendered = rendered.replace(secret, replacement)
    return rendered


def _redacted_headers(headers: httpx.Headers, secret_names: frozenset[str]) -> dict[str, str]:
    redacted: dict[str, str] = {}
    for name, value in sorted(headers.multi_items()):
        lower = name.lower()
        rendered = "<redacted>" if lower in secret_names else value
        if lower in redacted:
            redacted[lower] = f"{redacted[lower]}, {rendered}"
        else:
            redacted[lower] = rendered
    return redacted


class HttpCaptureClient:
    """HTTP client that archives exact bytes and redacted exchange metadata."""

    def __init__(
        self,
        *,
        client: httpx.Client,
        store: CaptureStore,
        policy: CapturePolicy,
        user_agent: str = "riopa-provenance/0.2.1",
        metrics: CaptureMetrics | None = None,
        on_failure: Callable[[CaptureFailure], None] | None = None,
        rate_limiter: RateLimiter | None = None,
        sleep: Callable[[float], None] | None = None,
    ) -> None:
        self.client = client
        self.store = store
        self.policy = policy
        self.user_agent = user_agent
        self.metrics = metrics or CaptureMetrics()
        self.on_failure = on_failure
        self.rate_limiter = rate_limiter
        self.sleep = sleep or (lambda _seconds: None)

    def _record_failure(
        self,
        category: CaptureFailureCategory,
        message: str,
        *,
        retryable: bool = False,
        status_code: int | None = None,
    ) -> None:
        self.metrics.record_failure(category)
        if self.on_failure is not None:
            self.on_failure(
                CaptureFailure(
                    category=category,
                    message=message,
                    retryable=retryable,
                    status_code=status_code,
                )
            )

    def capture(
        self,
        method: str,
        url: str,
        *,
        source_id: str,
        endpoint_id: str,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        require_success: bool = True,
        redact_values: Sequence[str] = (),
    ) -> CaptureResult:
        request_headers = {"User-Agent": self.user_agent, "Accept-Encoding": "identity"}
        if headers:
            request_headers.update(headers)
        # httpx treats an empty params mapping as a request to replace the URL's
        # existing query string. Registry endpoints commonly carry static format
        # selectors such as ``?f=json``; preserve them when no additional query
        # parameters were supplied.
        request = self.client.build_request(
            method,
            url,
            params=params if params else None,
            headers=request_headers,
        )
        try:
            validate_capture_url(request.url, self.policy)
        except CaptureError as exc:
            self._record_failure(CaptureFailureCategory.POLICY, str(exc))
            raise
        self.metrics.attempts_total += 1
        started = self.store.clock().astimezone(UTC)
        if self.rate_limiter is not None:
            self.sleep(self.rate_limiter.acquire(now=started))

        try:
            with self.client.stream(
                request.method,
                request.url,
                headers=request.headers,
                follow_redirects=False,
            ) as response:
                if self.policy.reject_redirects and response.is_redirect:
                    message = (
                        f"redirect response rejected for {request.url}: {response.status_code}"
                    )
                    self._record_failure(CaptureFailureCategory.REDIRECT, message)
                    raise CaptureError(message)
                declared_size = response.headers.get("content-length")
                if declared_size:
                    try:
                        declared_size_value = int(declared_size)
                    except ValueError as exc:
                        message = f"invalid response Content-Length: {declared_size!r}"
                        self._record_failure(CaptureFailureCategory.MALFORMED_RESPONSE, message)
                        raise CaptureError(message) from exc
                    if declared_size_value > self.policy.max_response_bytes:
                        message = (
                            f"response Content-Length {declared_size} exceeds "
                            f"limit {self.policy.max_response_bytes}"
                        )
                        self._record_failure(CaptureFailureCategory.RESPONSE_SIZE, message)
                        raise CaptureError(message)
                chunks: list[bytes] = []
                total = 0
                # Preserve response-body bytes exactly as received. ``iter_bytes``
                # transparently decompresses content encodings and is unsuitable
                # for a faithful archive.
                raw_chunks = (
                    [response.content] if response.is_stream_consumed else response.iter_raw()
                )
                for chunk in raw_chunks:
                    total += len(chunk)
                    if total > self.policy.max_response_bytes:
                        message = f"response exceeded byte limit {self.policy.max_response_bytes}"
                        self._record_failure(CaptureFailureCategory.RESPONSE_SIZE, message)
                        raise CaptureError(message)
                    chunks.append(chunk)
                payload = b"".join(chunks)
                status_code = response.status_code
                response_headers = response.headers
        except httpx.TransportError as exc:
            message = f"transport failure for {request.url}: {exc}"
            self._record_failure(
                CaptureFailureCategory.TRANSPORT,
                message,
                retryable=True,
            )
            raise

        digest, object_path = self.store.write_object(payload)
        capture_id = f"urn:uuid:{self.store.id_factory()}"
        retrieved_at = started.isoformat().replace("+00:00", "Z")
        redacted_url = _redacted_url(request.url, self.policy.secret_query_keys)
        redacted_request_headers = _redacted_headers(
            request.headers, self.policy.secret_header_names
        )
        redacted_response_headers = _redacted_headers(
            response_headers, self.policy.secret_header_names
        )
        redacted_url = redact_text(redacted_url, redact_values)
        redacted_request_headers = {
            key: redact_text(value, redact_values)
            for key, value in redacted_request_headers.items()
        }
        redacted_response_headers = {
            key: redact_text(value, redact_values)
            for key, value in redacted_response_headers.items()
        }
        request_fingerprint = sha256_json(
            {
                "method": request.method,
                "url": redacted_url,
                "headers": redacted_request_headers,
            }
        )
        media_type = response_headers.get("content-type")
        metadata = {
            "schema_version": "1.0.0",
            "record_type": "http_capture",
            "capture_id": capture_id,
            "source_id": source_id,
            "endpoint_id": endpoint_id,
            "retrieved_at": retrieved_at,
            "request": {
                "method": request.method,
                "url": redacted_url,
                "headers": redacted_request_headers,
                "fingerprint_sha256": request_fingerprint,
            },
            "response": {
                "status_code": status_code,
                "headers": redacted_response_headers,
                "media_type": media_type,
            },
            "object": {
                "sha256": digest,
                "size_bytes": len(payload),
                "storage_path": object_path.relative_to(self.store.root).as_posix(),
            },
        }
        metadata_path = self.store.write_capture(metadata)
        result = CaptureResult(
            capture_id=capture_id,
            source_id=source_id,
            endpoint_id=endpoint_id,
            status_code=status_code,
            media_type=media_type,
            retrieved_at=retrieved_at,
            object_sha256=digest,
            size_bytes=len(payload),
            object_path=object_path,
            metadata_path=metadata_path,
            request_fingerprint=request_fingerprint,
            response_location=response_headers.get("location"),
            retry_after=response_headers.get("retry-after"),
        )
        if result.succeeded:
            self.metrics.record_success(result.size_bytes)
        else:
            self._record_failure(
                CaptureFailureCategory.HTTP_STATUS,
                f"captured HTTP {status_code} for {redacted_url}",
                retryable=status_code in {408, 425, 429, 500, 502, 503, 504},
                status_code=status_code,
            )
        if require_success and not result.succeeded:
            raise CaptureError(
                f"captured HTTP {status_code} for {redacted_url}; metadata={metadata_path}"
            )
        return result

    def capture_json(self, *args: Any, **kwargs: Any) -> tuple[CaptureResult, Any]:
        result = self.capture(*args, **kwargs)
        try:
            value = json.loads(result.object_path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._record_failure(
                CaptureFailureCategory.MALFORMED_RESPONSE,
                f"captured response is not valid UTF-8 JSON: {result.capture_id}",
            )
            raise CaptureError(
                f"captured response is not valid UTF-8 JSON: {result.capture_id}: {exc}"
            ) from exc
        return result, value

    def capture_with_retry(
        self,
        method: str,
        url: str,
        *,
        retry_policy: RetryPolicy | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        sleep: Callable[[float], None] | None = None,
        on_decision: Callable[[RetryDecision], None] | None = None,
        now: Callable[[], datetime] | None = None,
        **kwargs: Any,
    ) -> CaptureResult:
        """Capture with bounded status retries while preserving every attempt.

        Each attempt delegates to :meth:`capture` with ``require_success=False``;
        consequently a retryable response is already content-addressed and has
        immutable metadata before the next attempt begins.  Sleeping is injected
        so callers can use a scheduler and tests can assert delays without I/O.
        """

        policy = retry_policy or RetryPolicy()
        wait = sleep or (lambda _seconds: None)
        clock = now or (lambda: datetime.now(UTC))
        kwargs.pop("require_success", None)
        for attempt in range(1, policy.max_attempts + 1):
            if circuit_breaker is not None and not circuit_breaker.allow(now=clock()):
                self._record_failure(
                    CaptureFailureCategory.CIRCUIT_OPEN,
                    "circuit breaker is open",
                )
                raise CaptureError("circuit breaker is open")
            try:
                result = self.capture(method, url, require_success=False, **kwargs)
            except httpx.TransportError as exc:
                decision = decide_retry(
                    method=method,
                    attempt=attempt,
                    status_code=None,
                    policy=policy,
                )
                if on_decision is not None:
                    on_decision(decision)
                if decision.retry:
                    if circuit_breaker is not None:
                        circuit_breaker.record_failure(now=clock())
                    wait(decision.delay_seconds)
                    continue
                raise CaptureError(f"transport failure after {attempt} attempt(s): {exc}") from exc
            decision = decide_retry(
                method=method,
                attempt=attempt,
                status_code=result.status_code,
                retry_after=result.retry_after,
                policy=policy,
            )
            if on_decision is not None:
                on_decision(decision)
            if not decision.retry:
                if not result.succeeded:
                    if circuit_breaker is not None:
                        circuit_breaker.record_failure(now=clock())
                    raise CaptureError(
                        f"captured HTTP {result.status_code} after {attempt} attempt(s): "
                        f"{result.metadata_path}"
                    )
                if circuit_breaker is not None:
                    circuit_breaker.record_success()
                return result
            if circuit_breaker is not None:
                circuit_breaker.record_failure(now=clock())
            wait(decision.delay_seconds)
        raise AssertionError("retry loop must return on its final attempt")
