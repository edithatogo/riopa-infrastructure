"""Dependency-free reference accessibility measures.

This module deliberately stops at measuring access.  Facility placement and policy
preferences belong in :mod:`riopa_provenance.facility_location`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from math import exp, isfinite


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
