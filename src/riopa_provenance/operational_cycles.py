"""Deterministic evidence records for synthetic operational cycles and soak."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Cycle:
    sequence: int
    started_at: str
    ended_at: str
    outcome: str
    failure: str | None = None
    recovery: str | None = None


@dataclass(frozen=True)
class SoakEvidence:
    scope: str
    required_days: int
    observed_days: int
    cycles: tuple[Cycle, ...]
    status: str

    def as_dict(self) -> dict[str, object]:
        return {
            "scope": self.scope,
            "required_days": self.required_days,
            "observed_days": self.observed_days,
            "cycles": [asdict(cycle) for cycle in self.cycles],
            "status": self.status,
        }


def record_soak(
    scope: str,
    required_days: int,
    observed_days: int,
    cycles: list[Cycle],
) -> SoakEvidence:
    """Build a fail-closed record; this function does not run deployments."""
    if not scope.strip():
        raise ValueError("scope must be non-empty")
    if required_days < 0 or observed_days < 0:
        raise ValueError("duration values must be non-negative")
    if [cycle.sequence for cycle in cycles] != list(range(1, len(cycles) + 1)):
        raise ValueError("cycle sequence numbers must be contiguous and ordered")
    for cycle in cycles:
        if not cycle.outcome.strip():
            raise ValueError("cycle outcomes must be non-empty")
        try:
            started = datetime.fromisoformat(cycle.started_at.replace("Z", "+00:00"))
            ended = datetime.fromisoformat(cycle.ended_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("cycle timestamps must be ISO 8601") from exc
        if started.tzinfo is None or ended.tzinfo is None or ended < started:
            raise ValueError("cycle timestamps must be timezone-aware and ordered")
        if (cycle.failure is None) != (cycle.recovery is None):
            raise ValueError("failure and recovery evidence must be recorded together")
    duration_met = observed_days >= required_days
    status = "synthetic-duration-met" if duration_met and cycles else "pending-duration"
    return SoakEvidence(scope, required_days, observed_days, tuple(cycles), status)


def write_soak_evidence(evidence: SoakEvidence, destination: Path) -> None:
    destination.write_text(
        json.dumps(evidence.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
