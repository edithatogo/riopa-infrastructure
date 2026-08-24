"""Deterministic, bounded retry decisions for archival network adapters.

The policy is deliberately side-effect free.  Callers use the returned decision
to perform a retry and persist the decision alongside their capture evidence.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime

RETRYABLE_STATUS_CODES = frozenset({408, 425, 429, 500, 502, 503, 504})
IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})


@dataclass(frozen=True)
class RetryPolicy:
    """Bounded retry parameters shared by network capture adapters."""

    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        if not math.isfinite(self.base_delay_seconds) or self.base_delay_seconds < 0:
            raise ValueError("base_delay_seconds must be finite and non-negative")
        if not math.isfinite(self.max_delay_seconds) or self.max_delay_seconds < 0:
            raise ValueError("max_delay_seconds must be finite and non-negative")
        if self.max_delay_seconds < self.base_delay_seconds:
            raise ValueError("max_delay_seconds must not be less than base_delay_seconds")


@dataclass(frozen=True)
class RetryDecision:
    """An auditable decision for one completed attempt."""

    attempt: int
    retry: bool
    delay_seconds: float
    reason: str


@dataclass(frozen=True)
class RateLimitPolicy:
    """Token-bucket limits for one source or service."""

    requests_per_second: float = 1.0
    burst: int = 1

    def __post_init__(self) -> None:
        if not math.isfinite(self.requests_per_second) or self.requests_per_second <= 0:
            raise ValueError("requests_per_second must be finite and positive")
        if self.burst < 1:
            raise ValueError("burst must be positive")


@dataclass
class RateLimiter:
    """Deterministic token bucket returning a required sleep duration."""

    policy: RateLimitPolicy = RateLimitPolicy()
    tokens: float | None = None
    last_at: datetime | None = None

    def acquire(self, *, now: datetime) -> float:
        current = now.astimezone(UTC)
        if self.last_at is None or self.tokens is None:
            self.tokens = float(self.policy.burst - 1)
            self.last_at = current
            return 0.0
        elapsed = max(0.0, (current - self.last_at).total_seconds())
        tokens = min(
            float(self.policy.burst),
            self.tokens + elapsed * self.policy.requests_per_second,
        )
        if tokens >= 1.0:
            self.tokens = tokens - 1.0
            self.last_at = current
            return 0.0
        delay = (1.0 - tokens) / self.policy.requests_per_second
        self.tokens = 0.0
        self.last_at = current
        return delay


@dataclass
class CircuitBreaker:
    """Small deterministic circuit breaker for one source/endpoint pair."""

    failure_threshold: int = 3
    cooldown: timedelta = timedelta(seconds=30)
    failures: int = 0
    opened_at: datetime | None = None
    probe_in_flight: bool = False

    def __post_init__(self) -> None:
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be positive")
        if self.cooldown.total_seconds() < 0:
            raise ValueError("cooldown must not be negative")

    @property
    def state(self) -> str:
        return "open" if self.opened_at is not None else "closed"

    def allow(self, *, now: datetime) -> bool:
        if self.opened_at is None:
            return True
        if now.astimezone(UTC) - self.opened_at.astimezone(UTC) < self.cooldown:
            return False
        if self.probe_in_flight:
            return False
        self.probe_in_flight = True
        return True  # one half-open probe is admitted

    def record_failure(self, *, now: datetime) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.opened_at = now.astimezone(UTC)
            self.probe_in_flight = False

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None
        self.probe_in_flight = False


def parse_retry_after(value: str | None, *, now: datetime) -> float | None:
    """Parse seconds or an HTTP date, rejecting malformed/negative values."""

    if not value:
        return None
    rendered = value.strip()
    try:
        seconds = float(rendered)
    except ValueError:
        try:
            target = parsedate_to_datetime(rendered).astimezone(UTC)
        except TypeError, ValueError, OverflowError:
            return None
        current = now.astimezone(UTC)
        seconds = (target - current).total_seconds()
    if not math.isfinite(seconds) or seconds < 0:
        return None
    return seconds


def decide_retry(
    *,
    method: str,
    attempt: int,
    status_code: int | None = None,
    retry_after: str | None = None,
    policy: RetryPolicy | None = None,
    now: datetime | None = None,
) -> RetryDecision:
    """Return a bounded retry decision without sleeping or performing I/O."""

    retry_policy = policy or RetryPolicy()
    if attempt < 1:
        raise ValueError("attempt must be positive")
    normalized_method = method.upper()
    if normalized_method not in IDEMPOTENT_METHODS:
        return RetryDecision(attempt, False, 0.0, "non-idempotent-method")
    if status_code is not None and status_code not in RETRYABLE_STATUS_CODES:
        return RetryDecision(attempt, False, 0.0, "status-not-retryable")
    if attempt >= retry_policy.max_attempts:
        return RetryDecision(attempt, False, 0.0, "attempt-limit")

    exponential = min(
        retry_policy.max_delay_seconds,
        retry_policy.base_delay_seconds * (2 ** (attempt - 1)),
    )
    retry_delay = parse_retry_after(retry_after, now=now or datetime.now(UTC))
    delay = (
        min(retry_policy.max_delay_seconds, retry_delay) if retry_delay is not None else exponential
    )
    return RetryDecision(
        attempt, True, delay, "retryable-status" if status_code else "transport-error"
    )
