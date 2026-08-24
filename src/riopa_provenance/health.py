"""Deterministic source-health observations for connector evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from .hashing import sha256_json


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


@dataclass(frozen=True)
class CapabilityDrift:
    """Digest-bound field-level comparison of two capability snapshots."""

    previous_digest: str
    current_digest: str
    added: tuple[str, ...]
    removed: tuple[str, ...]
    changed: tuple[str, ...]

    @property
    def drifted(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def to_record(self) -> dict[str, object]:
        return {
            "schema_version": "1.0.0",
            "record_type": "capability_drift_observation",
            "previous_digest": self.previous_digest,
            "current_digest": self.current_digest,
            "added": list(self.added),
            "removed": list(self.removed),
            "changed": list(self.changed),
            "drifted": self.drifted,
        }


def detect_capability_drift(
    previous: Mapping[str, Any], current: Mapping[str, Any]
) -> CapabilityDrift:
    """Compare top-level capability fields without treating drift as failure."""

    previous_keys = set(previous)
    current_keys = set(current)
    added = tuple(sorted(current_keys - previous_keys))
    removed = tuple(sorted(previous_keys - current_keys))
    changed = tuple(
        sorted(key for key in previous_keys & current_keys if previous[key] != current[key])
    )
    return CapabilityDrift(
        previous_digest=sha256_json(dict(previous)),
        current_digest=sha256_json(dict(current)),
        added=added,
        removed=removed,
        changed=changed,
    )


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
