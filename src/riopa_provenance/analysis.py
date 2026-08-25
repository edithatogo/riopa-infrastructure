"""Dependency-light analytical reference contracts and synthetic methods.

The functions in this module are deliberately small reference implementations. They
make assumptions inspectable and produce non-operational outputs; they are not
calibration, causal-identification, clinical, legal, or commercial decision systems.
"""

from __future__ import annotations

import hashlib
import heapq
import json
import math
import random
import statistics
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any, Literal, cast

ParameterSource = Literal["assumed", "fitted", "external"]
EventKind = Literal["arrival", "service_start", "service_end"]


class AnalysisProtocolError(ValueError):
    """Raised when an analysis protocol is incomplete or internally inconsistent."""


@dataclass(frozen=True)
class Estimand:
    """The quantity an analysis is designed to estimate."""

    name: str
    population: str
    exposure: str
    comparison: str
    outcome: str
    time_horizon: str
    identification_assumptions: tuple[str, ...]


@dataclass(frozen=True)
class ParameterEvidence:
    """A parameter value and the provenance class of that value."""

    name: str
    value: float
    unit: str
    source: ParameterSource
    evidence_reference: str | None = None


@dataclass(frozen=True)
class ReplicationDesign:
    """Statistical reproduction semantics for a stochastic analysis."""

    master_seed: int
    replications: int
    warm_up_customers: int = 0
    confidence_level: float = 0.95
    convergence_relative_half_width: float = 0.1


@dataclass(frozen=True)
class AnalysisProtocol:
    """Versioned, machine-readable assumptions for one bounded analysis."""

    protocol_id: str
    version: str
    scenario_id: str
    estimand: Estimand
    parameters: tuple[ParameterEvidence, ...]
    replication: ReplicationDesign
    limitations: tuple[str, ...]
    operational_status: Literal["synthetic-non-operational"] = "synthetic-non-operational"


@dataclass(frozen=True)
class SimulationEvent:
    """One event from a first-come, first-served capacity simulation."""

    customer: int
    kind: EventKind
    time: float
    resource: int | None


@dataclass(frozen=True)
class SimulationResult:
    """Result from one deterministic input sequence."""

    events: tuple[SimulationEvent, ...]
    waits: tuple[float, ...]
    mean_wait: float
    maximum_wait: float
    utilisation: float
    observed_customers: int


@dataclass(frozen=True)
class CoverageScenario:
    """Synthetic location/availability inputs for a bounded coverage check."""

    scenario_id: str
    demand_ids: tuple[str, ...]
    primary_locations: tuple[str, ...]
    backup_locations: tuple[str, ...]
    travel: Mapping[tuple[str, str], float]
    availability: Mapping[str, bool]
    threshold: float

    def __post_init__(self) -> None:
        if not self.scenario_id.strip() or not self.demand_ids:
            raise ValueError("scenario requires an id and demand IDs")
        if len(set(self.demand_ids)) != len(self.demand_ids):
            raise ValueError("demand IDs must be unique")
        locations = (*self.primary_locations, *self.backup_locations)
        if not locations or len(set(locations)) != len(locations):
            raise ValueError("scenario locations must be non-empty and unique")
        if not math.isfinite(self.threshold) or self.threshold < 0:
            raise ValueError("coverage threshold must be finite and non-negative")
        if any(not math.isfinite(value) or value < 0 for value in self.travel.values()):
            raise ValueError("travel values must be finite and non-negative")


@dataclass(frozen=True)
class DispatchRequest:
    """Synthetic demand event for the bounded dispatch adapter."""

    request_id: str
    demand_id: str
    arrival_time: float
    handover_minutes: float = 0.0
    service_minutes: float = 0.0

    def __post_init__(self) -> None:
        if not self.request_id.strip() or not self.demand_id.strip():
            raise ValueError("dispatch request IDs must be non-empty")
        if not math.isfinite(self.arrival_time) or self.arrival_time < 0:
            raise ValueError("arrival_time must be finite and non-negative")
        if not math.isfinite(self.handover_minutes) or self.handover_minutes < 0:
            raise ValueError("handover_minutes must be finite and non-negative")
        if not math.isfinite(self.service_minutes) or self.service_minutes < 0:
            raise ValueError("service_minutes must be finite and non-negative")


@dataclass(frozen=True)
class DispatchScenario:
    """Synthetic stations, requests and travel inputs for dispatch adapters."""

    scenario_id: str
    requests: tuple[DispatchRequest, ...]
    locations: tuple[str, ...]
    travel: Mapping[tuple[str, str], float]
    availability: Mapping[str, bool]
    threshold: float

    def __post_init__(self) -> None:
        if not self.scenario_id.strip() or not self.requests:
            raise ValueError("dispatch scenario requires an id and requests")
        if len({request.request_id for request in self.requests}) != len(self.requests):
            raise ValueError("dispatch request IDs must be unique")
        if not self.locations or len(set(self.locations)) != len(self.locations):
            raise ValueError("dispatch locations must be non-empty and unique")
        if not math.isfinite(self.threshold) or self.threshold < 0:
            raise ValueError("dispatch threshold must be finite and non-negative")
        if any(not math.isfinite(value) or value < 0 for value in self.travel.values()):
            raise ValueError("dispatch travel values must be finite and non-negative")


@dataclass(frozen=True)
class ServiceScenario:
    """Synthetic multi-service capacity, referral and workforce inputs."""

    scenario_id: str
    services: tuple[str, ...]
    demand: Mapping[tuple[str, str], float]
    capacity: Mapping[tuple[str, str], float]
    workforce: Mapping[str, float]
    referrals: Mapping[tuple[str, str], tuple[str, ...]]

    def __post_init__(self) -> None:
        if not self.scenario_id.strip() or not self.services:
            raise ValueError("service scenario requires an id and services")
        if len(set(self.services)) != len(self.services):
            raise ValueError("services must be unique")
        if any(not math.isfinite(value) or value < 0 for value in self.demand.values()):
            raise ValueError("demand values must be finite and non-negative")
        if any(not math.isfinite(value) or value < 0 for value in self.capacity.values()):
            raise ValueError("capacity values must be finite and non-negative")
        if any(not math.isfinite(value) or value < 0 for value in self.workforce.values()):
            raise ValueError("workforce values must be finite and non-negative")
        if any(
            service not in self.services or not zone or not facilities
            for (zone, service), facilities in self.referrals.items()
        ):
            raise ValueError("referrals must name a service and at least one facility")


def evaluate_service_scenario(scenario: ServiceScenario) -> dict[str, Any]:
    """Allocate synthetic service demand against declared capacity and workforce."""
    remaining_capacity = dict(scenario.capacity)
    remaining_workforce = dict(scenario.workforce)
    assignments: list[dict[str, Any]] = []
    for (zone, service), requested in sorted(scenario.demand.items()):
        eligible = sorted(
            facility
            for facility in scenario.referrals.get((zone, service), ())
            if remaining_capacity.get((facility, service), 0.0) > 0
            and remaining_workforce.get(facility, 0.0) > 0
        )
        facility = eligible[0] if eligible else None
        served = 0.0
        if facility is not None:
            served = min(
                requested,
                remaining_capacity[(facility, service)],
                remaining_workforce[facility],
            )
            remaining_capacity[(facility, service)] -= served
            remaining_workforce[facility] -= served
        assignments.append(
            {
                "zone": zone,
                "service": service,
                "facility": facility,
                "requested": requested,
                "served": served,
                "unmet": requested - served,
            }
        )
    return {
        "schema_version": "1.0.0",
        "record_type": "bounded_multi_service_scenario",
        "scenario_id": scenario.scenario_id,
        "assignments": assignments,
        "counts": {
            "service_demands": len(assignments),
            "requested": sum(item["requested"] for item in assignments),
            "served": sum(item["served"] for item in assignments),
            "unmet": sum(item["unmet"] for item in assignments),
        },
        "capacity_remaining": {
            f"{facility}|{service}": value
            for (facility, service), value in sorted(remaining_capacity.items())
        },
        "promotion_allowed": False,
        "nonclaims": [
            (
                "Synthetic service allocation only; no clinical, operational or referral "
                "guarantee is asserted."
            ),
            (
                "Capacity and workforce units are caller-supplied assumptions, not observed "
                "service data."
            ),
        ],
    }


def evaluate_service_constraints(
    scenario: ServiceScenario,
    *,
    minimum_volume: Mapping[str, float],
    resilience_fraction: float,
    transition_costs: Mapping[str, float],
    phase_investments: tuple[Mapping[tuple[str, str], float], ...],
) -> dict[str, Any]:
    """Check synthetic service constraints without selecting an operational plan."""
    if not math.isfinite(resilience_fraction) or not 0 <= resilience_fraction <= 1:
        raise ValueError("resilience_fraction must be finite and in [0, 1]")
    if any(not math.isfinite(value) or value < 0 for value in minimum_volume.values()):
        raise ValueError("minimum_volume values must be finite and non-negative")
    if any(not math.isfinite(value) or value < 0 for value in transition_costs.values()):
        raise ValueError("transition_costs values must be finite and non-negative")
    if any(
        not math.isfinite(value) or value < 0
        for phase in phase_investments
        for value in phase.values()
    ):
        raise ValueError("phase investments must be finite and non-negative")
    result = evaluate_service_scenario(scenario)
    served_by_service = {
        service: sum(item["served"] for item in result["assignments"] if item["service"] == service)
        for service in scenario.services
    }
    minimum_volume_met = {
        service: served_by_service.get(service, 0.0) >= required
        for service, required in sorted(minimum_volume.items())
    }
    reserve_met: dict[str, bool] = {}
    for (facility, service), initial in sorted(scenario.capacity.items()):
        remaining = float(result["capacity_remaining"].get(f"{facility}|{service}", 0.0))
        reserve_met[f"{facility}|{service}"] = (
            initial == 0 or remaining / initial >= resilience_fraction
        )
    phase_totals = [sum(investment.values()) for investment in phase_investments]
    return {
        "schema_version": "1.0.0",
        "record_type": "bounded_service_constraints",
        "scenario_id": scenario.scenario_id,
        "minimum_volume": {
            "required": dict(sorted(minimum_volume.items())),
            "served": served_by_service,
            "met": minimum_volume_met,
        },
        "resilience": {
            "reserve_fraction": resilience_fraction,
            "met": reserve_met,
        },
        "transition": {
            "costs": dict(sorted(transition_costs.items())),
            "total_cost": sum(transition_costs.values()),
        },
        "phased_investment": {
            "phase_totals": phase_totals,
            "phase_count": len(phase_totals),
        },
        "promotion_allowed": False,
        "nonclaims": [
            (
                "Synthetic constraint checks only; no operational plan or clinical "
                "recommendation is produced."
            ),
            (
                "Constraint satisfaction does not establish feasibility, safety, authority "
                "or external validity."
            ),
        ],
    }


def evaluate_dispatch_scenario(scenario: DispatchScenario) -> dict[str, Any]:
    """Return deterministic primary, backup, relocation and handover outputs.

    This adapter is a synthetic contract fixture.  It does not model live
    dispatch, clinical triage, fleet telemetry, response guarantees or service
    authority.
    """

    available = tuple(
        location for location in scenario.locations if scenario.availability.get(location, False)
    )
    assignments: list[dict[str, Any]] = []
    for request in sorted(scenario.requests, key=lambda item: (item.arrival_time, item.request_id)):
        eligible = sorted(
            (
                scenario.travel[(location, request.demand_id)],
                location,
            )
            for location in available
            if (location, request.demand_id) in scenario.travel
            and scenario.travel[(location, request.demand_id)] <= scenario.threshold
        )
        primary = eligible[0][1] if eligible else None
        backup = eligible[1][1] if len(eligible) > 1 else None
        relocation = [location for _, location in eligible[2:]]
        assignments.append(
            {
                "request_id": request.request_id,
                "primary": primary,
                "backup": backup,
                "relocation_candidates": relocation,
                "handover_required": request.handover_minutes > 0,
            }
        )
    return {
        "schema_version": "1.0.0",
        "record_type": "bounded_dispatch_scenario",
        "scenario_id": scenario.scenario_id,
        "assignments": assignments,
        "counts": {
            "requests": len(assignments),
            "primary_assigned": sum(item["primary"] is not None for item in assignments),
            "backup_available": sum(item["backup"] is not None for item in assignments),
            "handover_required": sum(item["handover_required"] for item in assignments),
        },
        "promotion_allowed": False,
        "nonclaims": [
            (
                "Synthetic/reference adapter only; no live dispatch, clinical or response "
                "guarantee is asserted."
            ),
            "Relocation and handover fields are contract outputs, not operational instructions.",
        ],
    }


def simulate_dispatch_scenario(scenario: DispatchScenario) -> dict[str, Any]:
    """Run a deterministic single-unit-per-location queue over the fixture.

    Queueing and relocation here are contract semantics only.  They do not
    represent a fleet, clinical triage, dispatch policy or service guarantee.
    """

    available = tuple(
        location for location in scenario.locations if scenario.availability.get(location, False)
    )
    busy_until = {location: 0.0 for location in available}
    assignments: list[dict[str, Any]] = []
    for request in sorted(scenario.requests, key=lambda item: (item.arrival_time, item.request_id)):
        eligible = sorted(
            (
                scenario.travel[(location, request.demand_id)],
                location,
            )
            for location in available
            if busy_until[location] <= request.arrival_time
            and (location, request.demand_id) in scenario.travel
            and scenario.travel[(location, request.demand_id)] <= scenario.threshold
        )
        if eligible:
            primary = eligible[0][1]
            backup = eligible[1][1] if len(eligible) > 1 else None
            wait = 0.0
            busy_until[primary] = request.arrival_time + request.service_minutes
        else:
            primary = None
            backup = None
            wait = min(
                (max(0.0, busy_until[location] - request.arrival_time) for location in available),
                default=0.0,
            )
        assignments.append(
            {
                "request_id": request.request_id,
                "primary": primary,
                "backup": backup,
                "queue_wait": wait,
                "handover_required": request.handover_minutes > 0,
            }
        )
    return {
        "schema_version": "1.0.0",
        "record_type": "bounded_dispatch_queue_simulation",
        "scenario_id": scenario.scenario_id,
        "assignments": assignments,
        "counts": {
            "requests": len(assignments),
            "assigned": sum(item["primary"] is not None for item in assignments),
            "queued": sum(item["primary"] is None for item in assignments),
            "handover_required": sum(item["handover_required"] for item in assignments),
        },
        "promotion_allowed": False,
        "nonclaims": [
            "Synthetic queue only; no live dispatch, clinical or response guarantee is asserted.",
            "Queue waits and relocation semantics are not operational instructions.",
        ],
    }


def compare_static_simulated_stress(
    scenario: DispatchScenario, *, stress_profile: str
) -> dict[str, Any]:
    """Compare static assignments with the bounded queue under a named stress profile.

    The comparison is descriptive evidence over caller-supplied synthetic inputs.  It does
    not extrapolate to a fleet, clinical response, live dispatch or national workload.
    """
    if not stress_profile.strip():
        raise ValueError("stress_profile must be non-empty")
    static = evaluate_dispatch_scenario(scenario)
    simulated = simulate_dispatch_scenario(scenario)
    static_assignments = {item["request_id"]: item["primary"] for item in static["assignments"]}
    simulated_assignments = {
        item["request_id"]: item["primary"] for item in simulated["assignments"]
    }
    changed = sorted(
        request_id
        for request_id in static_assignments
        if static_assignments[request_id] != simulated_assignments.get(request_id)
    )
    waits = [float(item["queue_wait"]) for item in simulated["assignments"]]
    return {
        "schema_version": "1.0.0",
        "record_type": "bounded_dispatch_stress_comparison",
        "scenario_id": scenario.scenario_id,
        "stress_profile": stress_profile,
        "static": static["counts"],
        "simulated": simulated["counts"],
        "comparison": {
            "primary_assignment_delta": (
                simulated["counts"]["assigned"] - static["counts"]["primary_assigned"]
            ),
            "queued_requests": simulated["counts"]["queued"],
            "maximum_queue_wait": max(waits, default=0.0),
            "primary_assignment_changes": changed,
        },
        "promotion_allowed": False,
        "nonclaims": [
            (
                "Synthetic stress comparison only; no live dispatch, clinical or response "
                "guarantee is asserted."
            ),
            "The result does not establish national-scale performance or operational safety.",
        ],
    }


def evaluate_coverage_scenario(scenario: CoverageScenario) -> dict[str, Any]:
    """Evaluate primary, backup and unavailable demand over supplied fixtures."""

    primary_available = tuple(
        location
        for location in scenario.primary_locations
        if scenario.availability.get(location, False)
    )
    backup_available = tuple(
        location
        for location in scenario.backup_locations
        if scenario.availability.get(location, False)
    )
    assignments: list[dict[str, Any]] = []
    for demand_id in scenario.demand_ids:
        primary = [
            location
            for location in primary_available
            if scenario.travel.get((demand_id, location), math.inf) <= scenario.threshold
        ]
        backups = [
            location
            for location in backup_available
            if scenario.travel.get((demand_id, location), math.inf) <= scenario.threshold
        ]
        assignments.append(
            {
                "demand_id": demand_id,
                "primary": primary[0] if primary else None,
                "backup": backups[0] if backups else None,
            }
        )
    covered = sum(item["primary"] is not None for item in assignments)
    backup_covered = sum(item["backup"] is not None for item in assignments)
    return {
        "schema_version": "1.0.0",
        "record_type": "bounded_coverage_scenario",
        "scenario_id": scenario.scenario_id,
        "locations": {
            "primary": list(scenario.primary_locations),
            "backup": list(scenario.backup_locations),
            "primary_available": list(primary_available),
            "backup_available": list(backup_available),
        },
        "assignments": assignments,
        "counts": {
            "demand": len(assignments),
            "primary_covered": covered,
            "backup_covered": backup_covered,
            "uncovered": len(assignments) - covered,
        },
        "promotion_allowed": False,
        "nonclaims": [
            (
                "Synthetic/reference calculation only; no dispatch, clinical or response "
                "guarantee is asserted."
            ),
            "The result does not establish national or authoritative service coverage.",
        ],
    }


def _required_text(value: str, field: str) -> None:
    if not value.strip():
        raise AnalysisProtocolError(f"{field} must be non-empty")


def validate_analysis_protocol(protocol: AnalysisProtocol) -> None:
    """Fail closed when assumptions or replication semantics are incomplete."""

    for value, field in (
        (protocol.protocol_id, "protocol_id"),
        (protocol.version, "version"),
        (protocol.scenario_id, "scenario_id"),
        (protocol.estimand.name, "estimand.name"),
        (protocol.estimand.population, "estimand.population"),
        (protocol.estimand.exposure, "estimand.exposure"),
        (protocol.estimand.comparison, "estimand.comparison"),
        (protocol.estimand.outcome, "estimand.outcome"),
        (protocol.estimand.time_horizon, "estimand.time_horizon"),
    ):
        _required_text(value, field)
    if not protocol.estimand.identification_assumptions:
        raise AnalysisProtocolError("at least one identification assumption is required")
    if not protocol.parameters:
        raise AnalysisProtocolError("at least one parameter is required")
    names = [parameter.name for parameter in protocol.parameters]
    if len(names) != len(set(names)):
        raise AnalysisProtocolError("parameter names must be unique")
    for parameter in protocol.parameters:
        _required_text(parameter.name, "parameter.name")
        _required_text(parameter.unit, f"parameter {parameter.name!r} unit")
        if not math.isfinite(parameter.value):
            raise AnalysisProtocolError(f"parameter {parameter.name!r} must be finite")
        if parameter.source in {"fitted", "external"} and not parameter.evidence_reference:
            raise AnalysisProtocolError(
                f"parameter {parameter.name!r} requires an evidence reference"
            )
    design = protocol.replication
    if design.replications < 1:
        raise AnalysisProtocolError("replications must be at least one")
    if design.warm_up_customers < 0:
        raise AnalysisProtocolError("warm_up_customers cannot be negative")
    if design.confidence_level != 0.95:
        raise AnalysisProtocolError("the reference implementation supports only 95% intervals")
    if design.convergence_relative_half_width <= 0:
        raise AnalysisProtocolError("convergence threshold must be positive")
    if not protocol.limitations:
        raise AnalysisProtocolError("at least one limitation is required")


def protocol_record(protocol: AnalysisProtocol) -> dict[str, Any]:
    """Return a stable JSON-compatible protocol record after validation."""

    validate_analysis_protocol(protocol)
    return cast(dict[str, Any], json.loads(json.dumps(asdict(protocol))))


def simulate_fcfs_queue(
    arrival_times: Sequence[float],
    service_times: Sequence[float],
    *,
    capacity: int,
    warm_up_customers: int = 0,
) -> SimulationResult:
    """Run a deterministic first-come, first-served multi-resource queue."""

    if capacity < 1:
        raise ValueError("capacity must be at least one")
    if len(arrival_times) != len(service_times):
        raise ValueError("arrival_times and service_times must have equal lengths")
    if warm_up_customers < 0 or warm_up_customers >= len(arrival_times):
        raise ValueError("warm_up_customers must leave at least one observed customer")
    previous = -math.inf
    for arrival, service in zip(arrival_times, service_times, strict=True):
        if not math.isfinite(arrival) or arrival < previous:
            raise ValueError("arrival_times must be finite and non-decreasing")
        if not math.isfinite(service) or service < 0:
            raise ValueError("service_times must be finite and non-negative")
        previous = arrival

    resources = [(0.0, resource) for resource in range(capacity)]
    heapq.heapify(resources)
    events: list[SimulationEvent] = []
    waits: list[float] = []
    busy_time = 0.0
    last_end = 0.0
    for customer, (arrival, duration) in enumerate(zip(arrival_times, service_times, strict=True)):
        available, resource = heapq.heappop(resources)
        start = max(arrival, available)
        end = start + duration
        heapq.heappush(resources, (end, resource))
        events.extend(
            (
                SimulationEvent(customer, "arrival", arrival, None),
                SimulationEvent(customer, "service_start", start, resource),
                SimulationEvent(customer, "service_end", end, resource),
            )
        )
        if customer >= warm_up_customers:
            waits.append(start - arrival)
            busy_time += duration
            last_end = max(last_end, end)

    event_order = {"arrival": 0, "service_start": 1, "service_end": 2}
    events.sort(key=lambda event: (event.time, event.customer, event_order[event.kind]))
    observed_start = arrival_times[warm_up_customers]
    observed_window = max(0.0, last_end - observed_start)
    utilisation = busy_time / (capacity * observed_window) if observed_window else 0.0
    return SimulationResult(
        events=tuple(events),
        waits=tuple(waits),
        mean_wait=statistics.fmean(waits),
        maximum_wait=max(waits),
        utilisation=utilisation,
        observed_customers=len(waits),
    )


def _replication_seed(master_seed: int, replication: int) -> int:
    material = f"riopa-simulation-v1:{master_seed}:{replication}".encode()
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def run_seeded_replications(
    protocol: AnalysisProtocol,
    *,
    customer_count: int,
    capacity: int,
    mean_interarrival: float,
    mean_service: float,
) -> dict[str, Any]:
    """Run seeded exponential queue replications with explicit uncertainty."""

    validate_analysis_protocol(protocol)
    if customer_count <= protocol.replication.warm_up_customers:
        raise ValueError("customer_count must exceed warm_up_customers")
    if mean_interarrival <= 0 or mean_service <= 0:
        raise ValueError("distribution means must be positive")

    means: list[float] = []
    seeds: list[int] = []
    for replication in range(protocol.replication.replications):
        seed = _replication_seed(protocol.replication.master_seed, replication)
        rng = random.Random(seed)  # nosec B311
        arrivals: list[float] = []
        clock = 0.0
        for _ in range(customer_count):
            clock += rng.expovariate(1.0 / mean_interarrival)
            arrivals.append(clock)
        services = [rng.expovariate(1.0 / mean_service) for _ in range(customer_count)]
        result = simulate_fcfs_queue(
            arrivals,
            services,
            capacity=capacity,
            warm_up_customers=protocol.replication.warm_up_customers,
        )
        seeds.append(seed)
        means.append(result.mean_wait)

    estimate = statistics.fmean(means)
    standard_error = statistics.stdev(means) / math.sqrt(len(means)) if len(means) > 1 else None
    half_width = 1.96 * standard_error if standard_error is not None else None
    relative_half_width = (
        half_width / abs(estimate) if half_width is not None and estimate != 0 else None
    )
    converged = (
        relative_half_width <= protocol.replication.convergence_relative_half_width
        if relative_half_width is not None
        else False
    )
    return {
        "scenario_id": protocol.scenario_id,
        "protocol_id": protocol.protocol_id,
        "protocol_version": protocol.version,
        "operational_status": protocol.operational_status,
        "replication_seeds": seeds,
        "replication_mean_waits": means,
        "estimate_mean_wait": estimate,
        "standard_error": standard_error,
        "confidence_interval_95": (
            [estimate - half_width, estimate + half_width] if half_width is not None else None
        ),
        "relative_half_width": relative_half_width,
        "converged": converged,
        "limitations": list(protocol.limitations),
    }


def parameter_evidence_report(protocol: AnalysisProtocol) -> dict[str, Any]:
    """Classify declared parameters without inferring missing evidence.

    The report is deliberately descriptive: ``fitted`` and ``external`` values
    remain invalid unless their references are present in the protocol, and a
    synthetic report never upgrades an assumed value into empirical evidence.
    """

    validate_analysis_protocol(protocol)
    parameters = [
        {
            "name": parameter.name,
            "value": parameter.value,
            "unit": parameter.unit,
            "source": parameter.source,
            "evidence_reference": parameter.evidence_reference,
        }
        for parameter in protocol.parameters
    ]
    counts = {
        source: sum(item["source"] == source for item in parameters)
        for source in (
            "assumed",
            "fitted",
            "external",
        )
    }
    return {
        "protocol_id": protocol.protocol_id,
        "parameters": parameters,
        "counts_by_source": counts,
        "evidence_status": {
            "assumed": "declared assumption only",
            "fitted": "reference required and recorded; fit quality is not established here",
            "external": "reference required and recorded; authority is not established here",
        },
        "operational_status": protocol.operational_status,
        "promotion_allowed": False,
    }


def calibrate_queue_parameters(
    protocol: AnalysisProtocol,
    *,
    observed_mean_wait: float,
    candidates: Sequence[tuple[float, float]],
    customer_count: int,
    capacity: int,
) -> dict[str, Any]:
    """Select the closest synthetic queue candidate against a declared target.

    This is a deterministic calibration *workflow* for contract testing.  The
    target is caller-supplied and no claim is made that it is an observed or
    authoritative real-world measurement.
    """

    if not math.isfinite(observed_mean_wait) or observed_mean_wait < 0:
        raise ValueError("observed_mean_wait must be finite and non-negative")
    if not candidates:
        raise ValueError("at least one calibration candidate is required")
    reports: list[dict[str, Any]] = []
    for mean_interarrival, mean_service in candidates:
        result = run_seeded_replications(
            protocol,
            customer_count=customer_count,
            capacity=capacity,
            mean_interarrival=mean_interarrival,
            mean_service=mean_service,
        )
        reports.append(
            {
                "mean_interarrival": mean_interarrival,
                "mean_service": mean_service,
                "estimate_mean_wait": result["estimate_mean_wait"],
                "absolute_error": abs(result["estimate_mean_wait"] - observed_mean_wait),
                "replication": result,
            }
        )
    selected = min(
        reports,
        key=lambda item: (
            item["absolute_error"],
            item["mean_interarrival"],
            item["mean_service"],
        ),
    )
    return {
        "protocol_id": protocol.protocol_id,
        "target_mean_wait": observed_mean_wait,
        "candidates": reports,
        "selected": {
            key: selected[key]
            for key in ("mean_interarrival", "mean_service", "estimate_mean_wait", "absolute_error")
        },
        "target_status": "caller-supplied synthetic calibration target",
        "operational_status": protocol.operational_status,
        "promotion_allowed": False,
    }


def queue_parameter_sensitivity(
    protocol: AnalysisProtocol,
    *,
    candidates: Sequence[tuple[float, float]],
    customer_count: int,
    capacity: int,
) -> dict[str, Any]:
    """Run a deterministic parameter grid and preserve all candidate outputs."""

    if not candidates:
        raise ValueError("at least one sensitivity candidate is required")
    reports = []
    for mean_interarrival, mean_service in candidates:
        result = run_seeded_replications(
            protocol,
            customer_count=customer_count,
            capacity=capacity,
            mean_interarrival=mean_interarrival,
            mean_service=mean_service,
        )
        reports.append(
            {
                "mean_interarrival": mean_interarrival,
                "mean_service": mean_service,
                "estimate_mean_wait": result["estimate_mean_wait"],
                "confidence_interval_95": result["confidence_interval_95"],
                "replication_seeds": result["replication_seeds"],
            }
        )
    return {
        "protocol_id": protocol.protocol_id,
        "candidates": reports,
        "ordering": "input order",
        "interpretation": (
            "Synthetic parameter sensitivity only; no empirical robustness is established."
        ),
        "operational_status": protocol.operational_status,
        "promotion_allowed": False,
    }


def difference_in_differences(
    *,
    treated_pre: Sequence[float],
    treated_post: Sequence[float],
    comparison_pre: Sequence[float],
    comparison_post: Sequence[float],
    pretrend_treated: Sequence[float] | None = None,
    pretrend_comparison: Sequence[float] | None = None,
    negative_control: Mapping[str, Sequence[float]] | None = None,
) -> dict[str, Any]:
    """Calculate a synthetic DID contrast and surface assumption diagnostics.

    Diagnostics are warning hooks, not tests that establish causal identification.
    """

    groups = {
        "treated_pre": treated_pre,
        "treated_post": treated_post,
        "comparison_pre": comparison_pre,
        "comparison_post": comparison_post,
    }
    if any(not values for values in groups.values()):
        raise ValueError("all difference-in-differences groups must be non-empty")
    if any(not math.isfinite(value) for values in groups.values() for value in values):
        raise ValueError("difference-in-differences outcomes must be finite")
    means = {name: statistics.fmean(values) for name, values in groups.items()}
    estimate = (means["treated_post"] - means["treated_pre"]) - (
        means["comparison_post"] - means["comparison_pre"]
    )

    pretrend_difference: float | None = None
    if pretrend_treated is not None or pretrend_comparison is not None:
        if (
            pretrend_treated is None
            or pretrend_comparison is None
            or len(pretrend_treated) < 2
            or len(pretrend_treated) != len(pretrend_comparison)
        ):
            raise ValueError("pretrend series must have matching lengths of at least two")
        if any(not math.isfinite(value) for value in (*pretrend_treated, *pretrend_comparison)):
            raise ValueError("pretrend outcomes must be finite")
        pretrend_difference = (pretrend_treated[-1] - pretrend_treated[0]) - (
            pretrend_comparison[-1] - pretrend_comparison[0]
        )

    negative_control_estimate: float | None = None
    if negative_control is not None:
        required = {"treated_pre", "treated_post", "comparison_pre", "comparison_post"}
        if set(negative_control) != required:
            raise ValueError("negative_control must contain the four DID groups")
        if any(not values for values in negative_control.values()):
            raise ValueError("negative-control groups must be non-empty")
        if any(
            not math.isfinite(value) for values in negative_control.values() for value in values
        ):
            raise ValueError("negative-control outcomes must be finite")
        control_means = {
            name: statistics.fmean(values) for name, values in negative_control.items()
        }
        negative_control_estimate = (
            control_means["treated_post"] - control_means["treated_pre"]
        ) - (control_means["comparison_post"] - control_means["comparison_pre"])

    return {
        "design": "difference-in-differences-reference-v1",
        "estimate": estimate,
        "group_means": means,
        "assumption_diagnostics": {
            "pretrend_contrast": pretrend_difference,
            "negative_control_estimate": negative_control_estimate,
            "interpretation": (
                "Diagnostics can reveal concerns but cannot prove parallel trends, absence of "
                "interference, or causal identification."
            ),
        },
        "operational_status": "synthetic-non-operational",
    }


def synthetic_pilot_report(
    protocol: AnalysisProtocol,
    simulation: Mapping[str, Any],
    causal_reference: Mapping[str, Any],
) -> dict[str, Any]:
    """Bundle transparent synthetic outputs without elevating their maturity."""

    validate_analysis_protocol(protocol)
    if simulation.get("scenario_id") != protocol.scenario_id:
        raise ValueError("simulation scenario does not match the protocol")
    return {
        "title": "Synthetic methods pilot",
        "operational_status": "synthetic-non-operational",
        "suitability": {
            "clinical": False,
            "legal": False,
            "commercial": False,
            "live_operations": False,
        },
        "protocol": protocol_record(protocol),
        "simulation": dict(simulation),
        "causal_reference": dict(causal_reference),
        "interpretation_boundary": (
            "Outputs demonstrate contracts and deterministic computation only. They do not "
            "validate empirical assumptions or support real-world decisions."
        ),
    }
