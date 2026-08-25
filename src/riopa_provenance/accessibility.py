"""Dependency-free reference accessibility measures.

This module deliberately stops at measuring access.  Facility placement and policy
preferences belong in :mod:`riopa_provenance.facility_location`.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from math import asin, cos, exp, isfinite, radians, sin, sqrt
from typing import Any, TypeVar

from .hashing import sha256_json


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
class OpeningInterval:
    """A recurring local-time opening interval in minutes after midnight."""

    opens_at: int
    closes_at: int

    def __post_init__(self) -> None:
        for value in (self.opens_at, self.closes_at):
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < 1440:
                raise ValueError("opening times must be integer minutes in [0, 1440)")
        if self.opens_at == self.closes_at:
            raise ValueError("opening intervals must not have equal endpoints")

    def contains(self, minute: float) -> bool:
        """Return whether a minute falls inside this interval.

        An interval with ``closes_at < opens_at`` crosses midnight.  The
        representation is intentionally recurrence-only and carries no
        timezone, holiday, or live-service assertion.
        """

        if not isfinite(minute):
            raise ValueError("minute must be finite")
        position = minute % 1440
        if self.opens_at < self.closes_at:
            return self.opens_at <= position < self.closes_at
        return position >= self.opens_at or position < self.closes_at


def reachable_capacity_at_departure(
    matrix: AccessibilityMatrix,
    origin: str,
    capacities: Mapping[str, float],
    opening_intervals: Mapping[str, tuple[OpeningInterval, ...]],
    *,
    departure_minute: float,
    threshold_minutes: float,
) -> float:
    """Sum reference capacity open on arrival for a minute-based matrix.

    The caller must provide an archived/reference matrix whose impedance is
    explicitly measured in minutes.  This function does not infer opening
    hours, capacity, timezone, routing, timetable service or operational
    availability from any source.
    """

    if not isfinite(departure_minute) or not 0 <= departure_minute < 1440:
        raise ValueError("departure_minute must be finite and in [0, 1440)")
    if not isfinite(threshold_minutes) or threshold_minutes < 0:
        raise ValueError("threshold_minutes must be finite and non-negative")
    total = 0.0
    for destination, capacity in capacities.items():
        if not isfinite(capacity) or capacity < 0:
            raise ValueError("capacities must be finite and non-negative")
        intervals = opening_intervals.get(destination)
        if not intervals:
            continue
        impedance = matrix.reachable_impedance(origin, destination)
        if impedance is None or impedance > threshold_minutes:
            continue
        if any(interval.contains(departure_minute + impedance) for interval in intervals):
            total += capacity
    return total


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


@dataclass(frozen=True)
class AccessibilityPartition:
    """Deterministic subset of a matrix, keyed by sorted origin identifiers."""

    partition_id: str
    matrix_id: str
    origins: tuple[str, ...]
    observations: Mapping[tuple[str, str], TravelObservation]


def partition_matrix(
    matrix: AccessibilityMatrix, *, origins_per_partition: int
) -> tuple[AccessibilityPartition, ...]:
    """Partition observations by sorted origins without changing missing semantics."""
    if origins_per_partition < 1:
        raise ValueError("origins_per_partition must be positive")
    origins = sorted({origin for origin, _ in matrix.observations})
    partitions: list[AccessibilityPartition] = []
    for index in range(0, len(origins), origins_per_partition):
        selected = tuple(origins[index : index + origins_per_partition])
        selected_set = set(selected)
        observations = {
            pair: observation
            for pair, observation in matrix.observations.items()
            if pair[0] in selected_set
        }
        partitions.append(
            AccessibilityPartition(
                partition_id=f"{matrix.matrix_id}:partition:{index // origins_per_partition:04d}",
                matrix_id=matrix.matrix_id,
                origins=selected,
                observations=observations,
            )
        )
    return tuple(partitions)


def changed_origins(previous: AccessibilityMatrix, current: AccessibilityMatrix) -> tuple[str, ...]:
    """Return changed origin rows; incompatible matrix metadata invalidates all rows."""
    all_origins = sorted(
        {origin for origin, _ in previous.observations}
        | {origin for origin, _ in current.observations}
    )
    if (
        previous.matrix_id != current.matrix_id
        or previous.network_version != current.network_version
        or previous.engine != current.engine
        or previous.engine_version != current.engine_version
        or previous.mode != current.mode
    ):
        return tuple(all_origins)
    return tuple(
        origin
        for origin in all_origins
        if {
            pair: observation
            for pair, observation in previous.observations.items()
            if pair[0] == origin
        }
        != {
            pair: observation
            for pair, observation in current.observations.items()
            if pair[0] == origin
        }
    )


_Result = TypeVar("_Result")


class AccessibilityResultCache:
    """Small deterministic cache keyed by matrix fingerprint and calculation inputs."""

    def __init__(self) -> None:
        self._values: dict[str, object] = {}

    def get_or_compute(
        self,
        matrix: AccessibilityMatrix,
        *,
        origin: str,
        measure: str,
        parameters: Mapping[str, float],
        compute: Callable[[], _Result],
    ) -> _Result:
        key = sha256_json(
            {
                "matrix": {
                    "matrix_id": matrix.matrix_id,
                    "network_version": matrix.network_version,
                    "engine": matrix.engine,
                    "engine_version": matrix.engine_version,
                    "mode": matrix.mode,
                    "observations": [
                        {
                            "origin": pair[0],
                            "destination": pair[1],
                            "status": observation.status.value,
                            "impedance": observation.impedance,
                        }
                        for pair, observation in sorted(matrix.observations.items())
                    ],
                },
                "origin": origin,
                "measure": measure,
                "parameters": dict(parameters),
            }
        )
        if key not in self._values:
            self._values[key] = compute()
        return self._values[key]  # type: ignore[return-value]

    def clear(self) -> None:
        """Drop cached values after an explicit caller-controlled invalidation."""
        self._values.clear()


def incremental_cumulative_opportunity(
    previous: AccessibilityMatrix | None,
    current: AccessibilityMatrix,
    previous_results: Mapping[str, float],
    opportunities: Mapping[str, float],
    *,
    threshold: float,
) -> dict[str, float]:
    """Recompute cumulative opportunity only for changed origins."""
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    all_origins = {origin for origin, _ in current.observations}
    changed = all_origins if previous is None else set(changed_origins(previous, current))
    result = {origin: value for origin, value in previous_results.items() if origin not in changed}
    for origin in sorted(changed):
        result[origin] = cumulative_opportunity(current, origin, opportunities, threshold=threshold)
    return result


def straight_line_matrix(
    matrix_id: str,
    coordinates: Mapping[str, tuple[float, float]],
    origins: tuple[str, ...],
    destinations: tuple[str, ...],
) -> AccessibilityMatrix:
    """Build a bounded Haversine reference matrix from ``(lat, lon)`` pairs.

    This pure adapter intentionally models geometric distance only. It does not
    infer roads, travel time, timetable service, accessibility, or operational
    coverage from coordinates.
    """

    if not matrix_id.strip():
        raise ValueError("matrix_id must be non-empty")
    if not origins or not destinations:
        raise ValueError("origins and destinations must be non-empty")
    for identifier in (*origins, *destinations):
        coordinate = coordinates.get(identifier)
        if coordinate is None or len(coordinate) != 2:
            raise ValueError(f"missing coordinate for {identifier}")
        latitude, longitude = coordinate
        if (
            not isfinite(latitude)
            or not isfinite(longitude)
            or latitude < -90
            or latitude > 90
            or longitude < -180
            or longitude > 180
        ):
            raise ValueError(f"invalid coordinate for {identifier}")

    observations: dict[tuple[str, str], TravelObservation] = {}
    radius_km = 6371.0088
    for origin in origins:
        origin_lat, origin_lon = coordinates[origin]
        origin_lat_radians = radians(origin_lat)
        for destination in destinations:
            destination_lat, destination_lon = coordinates[destination]
            delta_lat = radians(destination_lat - origin_lat)
            delta_lon = radians(destination_lon - origin_lon)
            haversine = (
                sin(delta_lat / 2) ** 2
                + cos(origin_lat_radians) * cos(radians(destination_lat)) * sin(delta_lon / 2) ** 2
            )
            distance = 2 * radius_km * asin(sqrt(haversine))
            observations[(origin, destination)] = TravelObservation(
                TravelStatus.REACHABLE, distance
            )
    return AccessibilityMatrix(
        matrix_id,
        "reference:coordinate-snapshot",
        "haversine-reference",
        "1",
        "straight-line",
        observations,
    )


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


def validate_scenario_contract(contract: Mapping[str, Any] | None) -> tuple[str, ...]:
    """Validate scenario semantics without treating them as operational claims."""

    if not isinstance(contract, Mapping):
        return ("scenario contract must be an object",)
    errors: list[str] = []
    for field in ("scenario_id", "claim_classification"):
        if not isinstance(contract.get(field), str) or not str(contract[field]).strip():
            errors.append(f"{field} is required")
    if contract.get("claim_classification") not in {"reference-only", "preview-only"}:
        errors.append("claim_classification must remain reference-only or preview-only")
    for field in ("assumptions", "subgroup_dimensions"):
        values = contract.get(field)
        if not isinstance(values, list) or any(
            not isinstance(item, str) or not item for item in values
        ):
            errors.append(f"{field} must be a string array")
    dimensions = contract.get("subgroup_dimensions")
    if isinstance(dimensions, list) and len(dimensions) != len(set(dimensions)):
        errors.append("subgroup_dimensions must be unique")
    uncertainty = contract.get("uncertainty")
    if not isinstance(uncertainty, Mapping):
        errors.append("uncertainty is required")
    else:
        if uncertainty.get("method") not in {
            "none-declared",
            "interval",
            "scenario-range",
            "censored",
        }:
            errors.append("uncertainty.method is unsupported")
        if uncertainty.get("missing_policy") not in {
            "report-separately",
            "exclude-from-denominator",
            "fail-closed",
        }:
            errors.append("uncertainty.missing_policy is unsupported")
        if uncertainty.get("reporting_unit") not in {"seconds", "minutes", "count", "proportion"}:
            errors.append("uncertainty.reporting_unit is unsupported")
    return tuple(dict.fromkeys(errors))


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
