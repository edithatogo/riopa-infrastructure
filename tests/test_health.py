from datetime import UTC, datetime, timedelta

import pytest

from riopa_provenance.health import observe_source_health


def test_source_health_classifies_fresh_change_and_degradation() -> None:
    now = datetime(2026, 7, 30, 0, 0, tzinfo=UTC)
    result = observe_source_health(
        retrieved_at=now - timedelta(minutes=5),
        now=now,
        max_age=timedelta(minutes=10),
        current_digest="new",
        previous_digest="old",
        status_code=503,
    )
    assert result.freshness == "fresh"
    assert result.changed and result.degraded and not result.disappeared
    assert result.to_record()["record_type"] == "source_health_observation"


def test_source_health_handles_unknown_stale_and_disappeared() -> None:
    now = datetime(2026, 7, 30, 0, 0, tzinfo=UTC)
    assert observe_source_health(
        retrieved_at=None,
        now=now,
        max_age=timedelta(hours=1),
        current_digest=None,
        previous_digest="old",
    ).freshness == "unknown"
    stale = observe_source_health(
        retrieved_at=now - timedelta(hours=2),
        now=now,
        max_age=timedelta(hours=1),
        current_digest="same",
        previous_digest="same",
        disappeared=True,
    )
    assert stale.freshness == "stale" and stale.disappeared and not stale.changed


def test_source_health_rejects_negative_age_window() -> None:
    with pytest.raises(ValueError, match="negative"):
        observe_source_health(
            retrieved_at=None,
            now=datetime.now(UTC),
            max_age=timedelta(seconds=-1),
            current_digest=None,
            previous_digest=None,
        )
