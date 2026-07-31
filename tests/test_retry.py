from datetime import UTC, datetime, timedelta

import pytest

from riopa_provenance.retry import CircuitBreaker, RetryPolicy, decide_retry, parse_retry_after


def test_retry_is_bounded_and_idempotency_aware() -> None:
    policy = RetryPolicy(max_attempts=2, base_delay_seconds=2, max_delay_seconds=5)
    assert decide_retry(method="GET", attempt=1, status_code=503, policy=policy).delay_seconds == 2
    assert (
        decide_retry(method="GET", attempt=2, status_code=503, policy=policy).reason
        == "attempt-limit"
    )
    assert (
        decide_retry(method="POST", attempt=1, status_code=503, policy=policy).reason
        == "non-idempotent-method"
    )
    assert (
        decide_retry(method="GET", attempt=1, status_code=404, policy=policy).reason
        == "status-not-retryable"
    )


def test_retry_after_supports_seconds_and_http_dates() -> None:
    now = datetime(2026, 7, 30, 0, 0, tzinfo=UTC)
    assert parse_retry_after("3", now=now) == 3
    assert parse_retry_after("Thu, 30 Jul 2026 00:00:05 GMT", now=now) == 5
    assert parse_retry_after("-1", now=now) is None
    assert parse_retry_after("nonsense", now=now) is None


def test_retry_policy_rejects_unbounded_parameters() -> None:
    with pytest.raises(ValueError, match="max_attempts"):
        RetryPolicy(max_attempts=0)
    with pytest.raises(ValueError, match="finite"):
        RetryPolicy(base_delay_seconds=float("inf"))
    with pytest.raises(ValueError, match="less"):
        RetryPolicy(base_delay_seconds=2, max_delay_seconds=1)


def test_circuit_breaker_opens_and_allows_one_cooldown_probe() -> None:
    now = datetime(2026, 7, 30, 0, 0, tzinfo=UTC)
    breaker = CircuitBreaker(failure_threshold=2, cooldown=timedelta(seconds=10))
    assert breaker.allow(now=now)
    breaker.record_failure(now=now)
    assert breaker.state == "closed"
    breaker.record_failure(now=now)
    assert breaker.state == "open"
    assert not breaker.allow(now=now + timedelta(seconds=9))
    assert breaker.allow(now=now + timedelta(seconds=10))
    assert not breaker.allow(now=now + timedelta(seconds=11))
    breaker.record_success()
    assert breaker.state == "closed" and breaker.failures == 0
