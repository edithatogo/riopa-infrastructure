"""Dependency-free reference accessibility measures.

This module deliberately stops at measuring access.  Facility placement and policy
preferences belong in :mod:`riopa_provenance.facility_location`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from math import exp, isfinite
from typing import Any


class TravelStatus(StrEnum):
    """Semantically distinct states for one origin-destination observation."""

    REACHABLE = "reachable"
    UNREACHABLE = "unreachable"
    MISSING = "missing"
    CENSORED = "censored"


@dataclass(frozen=True)
class TravelObservation:
    status: TravelStatus
    impedance: float | None = None

    def __post_init__(self) -> None:
        if self.status is TravelStatus.REACHABLE:
            if self.impedance is None or not isfinite(self.impedance) or self.impedance < 0:
                raise ValueError("reachable observations require a finite non-negative impedance")
        elif self.impedance is not None:
            raise ValueError("only reachable observations may carry an impedance")


@dataclass(frozen=True)
class AccessibilityMatrix:
    """A versioned, mode-specific travel matrix."""

    matrix_id: str
    network_version: str
    engine: str
    engine_version: str
    mode: str
    observations: Mapping[tuple[str, str], TravelObservation]

    def reachable_impedance(self, origin: str, destination: str) -> float | None:
        observation = self.observations.get((origin, destination))
        if observation is None or observation.status is not TravelStatus.REACHABLE:
            return None
        return observation.impedance


def public_facility_opportunities(
    snapshot: Mapping[str, Any], *, facility_type: str | None = None
) -> dict[str, float]:
    """Project public facility assertions into unit opportunity weights.

    The projection is intentionally source-assertion based: one public
    assertion contributes one unit, while restricted rows are excluded and no
    authoritative facility identity or capacity is inferred.
    """

    if snapshot.get("record_type") != "facility_assertions":
        raise ValueError("snapshot must be a facility_assertions record")
    if snapshot.get("authoritative") is not False:
        raise ValueError("only non-authoritative snapshots may be projected")
    rows = snapshot.get("assertions")
    if not isinstance(rows, list):
        raise ValueError("snapshot assertions must be an array")
    opportunities: dict[str, float] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("snapshot assertions must contain objects")
        assertion_id = row.get("assertion_id")
        row_type = row.get("facility_type")
        if not isinstance(assertion_id, str) or not assertion_id.strip():
            raise ValueError("assertions require assertion_id")
        if not isinstance(row_type, str) or not row_type.strip():
            raise ValueError("assertions require facility_type")
        if facility_type is not None and row_type != facility_type:
            continue
        if row.get("release_classification", "public") != "public":
            continue
        if assertion_id in opportunities:
            raise ValueError("assertion IDs must be unique")
        opportunities[assertion_id] = 1.0
    return opportunities


def cumulative_opportunity(
    matrix: AccessibilityMatrix,
    origin: str,
    opportunities: Mapping[str, float],
    *,
    threshold: float,
) -> float:
    """Return opportunities reachable at or below an explicit impedance threshold."""

    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    return sum(
        amount
        for destination, amount in opportunities.items()
        if (impedance := matrix.reachable_impedance(origin, destination)) is not None
        and impedance <= threshold
    )


def gravity_accessibility(
    matrix: AccessibilityMatrix,
    origin: str,
    opportunities: Mapping[str, float],
    *,
    decay: float,
) -> float:
    """Return an exponential-decay gravity measure, excluding non-reachable pairs."""

    if decay < 0:
        raise ValueError("decay must be non-negative")
    return sum(
        amount * exp(-decay * impedance)
        for destination, amount in opportunities.items()
        if (impedance := matrix.reachable_impedance(origin, destination)) is not None
    )


def two_step_floating_catchment(
    matrix: AccessibilityMatrix,
    demand: Mapping[str, float],
    capacity: Mapping[str, float],
    *,
    threshold: float,
) -> dict[str, float]:
    """Calculate the unweighted two-step floating catchment area measure."""

    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    ratios: dict[str, float] = {}
    for facility, supply in capacity.items():
        catchment_demand = sum(
            amount
            for origin, amount in demand.items()
            if (impedance := matrix.reachable_impedance(origin, facility)) is not None
            and impedance <= threshold
        )
        ratios[facility] = supply / catchment_demand if catchment_demand > 0 else 0.0

    return {
        origin: sum(
            ratios[facility]
            for facility in capacity
            if (impedance := matrix.reachable_impedance(origin, facility)) is not None
            and impedance <= threshold
        )
        for origin in demand
    }
