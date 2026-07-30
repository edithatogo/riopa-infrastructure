"""Deterministic source-health observations for connector evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True)
class SourceHealthObservation:
    """Classification of one source observation against a prior digest."""

    freshness: str
    changed: bool
    degraded: bool
    disappeared: bool
    age_seconds: float | None

    def to_record(self) -> dict[str, object]:
        """Return a versioned, JSON-compatible evidence record."""

        return {
            "schema_version": "1.0.0",
            "record_type": "source_health_observation",
            "freshness": self.freshness,
            "changed": self.changed,
            "degraded": self.degraded,
            "disappeared": self.disappeared,
            "age_seconds": self.age_seconds,
        }


def observe_source_health(
    *,
    retrieved_at: datetime | None,
    now: datetime,
    max_age: timedelta,
    current_digest: str | None,
    previous_digest: str | None,
    status_code: int | None = None,
    disappeared: bool = False,
) -> SourceHealthObservation:
    """Classify freshness and change without performing I/O."""

    if max_age.total_seconds() < 0:
        raise ValueError("max_age must not be negative")
    age: float | None = None
    if retrieved_at is None:
        freshness = "unknown"
    else:
        age = (now.astimezone(UTC) - retrieved_at.astimezone(UTC)).total_seconds()
        freshness = "fresh" if age <= max_age.total_seconds() else "stale"
    changed = (
        current_digest is not None
        and previous_digest is not None
        and current_digest != previous_digest
    )
    degraded = status_code is not None and not 200 <= status_code < 300
    return SourceHealthObservation(freshness, changed, degraded, disappeared, age)
