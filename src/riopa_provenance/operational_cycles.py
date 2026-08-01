"""Deterministic evidence records for synthetic operational cycles and soak."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
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
    if required_days < 0 or observed_days < 0:
        raise ValueError("duration values must be non-negative")
    if any(cycle.sequence < 1 for cycle in cycles):
        raise ValueError("cycle sequence numbers must be positive")
    status = "qualified-synthetic" if observed_days >= required_days else "pending-duration"
    return SoakEvidence(scope, required_days, observed_days, tuple(cycles), status)


def write_soak_evidence(evidence: SoakEvidence, destination: Path) -> None:
    destination.write_text(
        json.dumps(evidence.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
