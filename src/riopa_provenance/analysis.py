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
from dataclasses import asdict, dataclass, replace
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
    weight: float = 1.0
    subgroup: str = "all"
    rurality: str = "unspecified"

    def __post_init__(self) -> None:
        if not self.request_id.strip() or not self.demand_id.strip():
            raise ValueError("dispatch request IDs must be non-empty")
        if not math.isfinite(self.arrival_time) or self.arrival_time < 0:
            raise ValueError("arrival_time must be finite and non-negative")
        if not math.isfinite(self.handover_minutes) or self.handover_minutes < 0:
            raise ValueError("handover_minutes must be finite and non-negative")
        if not math.isfinite(self.service_minutes) or self.service_minutes < 0:
            raise ValueError("service_minutes must be finite and non-negative")
        if not math.isfinite(self.weight) or self.weight <= 0:
            raise ValueError("weight must be finite and positive")
        if not self.subgroup.strip() or not self.rurality.strip():
            raise ValueError("subgroup and rurality must be non-empty")


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
class StochasticDispatchDesign:
    """Seeded busy-availability design for bounded dispatch replications."""

    master_seed: int
    replications: int
    availability_probability: Mapping[str, float]

    def __post_init__(self) -> None:
        if self.replications < 2:
            raise ValueError("stochastic dispatch requires at least two replications")
        if any(
            not math.isfinite(probability) or not 0 <= probability <= 1
            for probability in self.availability_probability.values()
        ):
            raise ValueError("availability probabilities must be finite and in [0, 1]")


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
        residual = requested
        allocations: list[dict[str, Any]] = []
        for facility in scenario.referrals.get((zone, service), ()):
            capacity = remaining_capacity.get((facility, service), 0.0)
            workforce = remaining_workforce.get(facility, 0.0)
            allocated = min(residual, capacity, workforce)
            if allocated <= 0:
                continue
            remaining_capacity[(facility, service)] -= allocated
            remaining_workforce[facility] -= allocated
            residual -= allocated
            allocations.append({"facility": facility, "served": allocated})
            if residual == 0:
                break
        served = requested - residual
        assignments.append(
            {
                "zone": zone,
                "service": service,
                "facility": allocations[0]["facility"] if allocations else None,
                "allocations": allocations,
                "requested": requested,
                "served": served,
                "unmet": residual,
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
    served_by_facility_service: dict[str, float] = {}
    for assignment in result["assignments"]:
        service = str(assignment["service"])
        for allocation in assignment["allocations"]:
            key = f"{allocation['facility']}|{service}"
            served_by_facility_service[key] = (
                served_by_facility_service.get(key, 0.0) + allocation["served"]
            )
    observed_volume = {
        key: (
            served_by_facility_service.get(key, 0.0)
            if "|" in key
            else served_by_service.get(key, 0.0)
        )
        for key in minimum_volume
    }
    minimum_volume_met = {
        key: observed_volume[key] >= required for key, required in sorted(minimum_volume.items())
    }
    reserve_met: dict[str, bool] = {}
    for (facility, service), initial in sorted(scenario.capacity.items()):
        remaining = float(result["capacity_remaining"].get(f"{facility}|{service}", 0.0))
        reserve_met[f"{facility}|{service}"] = (
            initial == 0 or remaining / initial >= resilience_fraction
        )
    requested_total = float(result["counts"]["requested"])
    facility_failures: dict[str, dict[str, Any]] = {}
    for facility in sorted(scenario.workforce):
        failed_capacity = {
            key: (0.0 if key[0] == facility else value) for key, value in scenario.capacity.items()
        }
        failed_workforce = {
            key: (0.0 if key == facility else value) for key, value in scenario.workforce.items()
        }
        failed = evaluate_service_scenario(
            replace(scenario, capacity=failed_capacity, workforce=failed_workforce)
        )
        served_fraction = (
            float(failed["counts"]["served"]) / requested_total if requested_total else 1.0
        )
        facility_failures[facility] = {
            "served": failed["counts"]["served"],
            "unmet": failed["counts"]["unmet"],
            "served_fraction": served_fraction,
            "met": served_fraction >= resilience_fraction,
        }

    cumulative_capacity = dict(scenario.capacity)
    phase_results: list[dict[str, Any]] = []
    for phase_number, investment in enumerate(phase_investments, start=1):
        for capacity_key, value in investment.items():
            cumulative_capacity[capacity_key] = cumulative_capacity.get(capacity_key, 0.0) + value
        phase_result = evaluate_service_scenario(
            replace(scenario, capacity=dict(cumulative_capacity))
        )
        phase_results.append(
            {
                "phase": phase_number,
                "added_capacity": {
                    f"{facility}|{service}": value
                    for (facility, service), value in sorted(investment.items())
                },
                "cumulative_capacity": {
                    f"{facility}|{service}": value
                    for (facility, service), value in sorted(cumulative_capacity.items())
                },
                "counts": phase_result["counts"],
                "all_demand_met": phase_result["counts"]["unmet"] == 0,
            }
        )
    return {
        "schema_version": "1.0.0",
        "record_type": "bounded_service_constraints",
        "scenario_id": scenario.scenario_id,
        "minimum_volume": {
            "required": dict(sorted(minimum_volume.items())),
            "observed": observed_volume,
            "served_by_service": served_by_service,
            "served_by_facility_service": dict(sorted(served_by_facility_service.items())),
            "met": minimum_volume_met,
            "key_semantics": "facility|service keys are facility-specific; other keys are services",
        },
        "resilience": {
            "required_fraction": resilience_fraction,
            "capacity_reserve_met": reserve_met,
            "facility_failures": facility_failures,
        },
        "transition": {
            "costs": dict(sorted(transition_costs.items())),
            "total_cost": sum(transition_costs.values()),
        },
        "phased_investment": {
            "phase_totals": [sum(investment.values()) for investment in phase_investments],
            "phase_count": len(phase_results),
            "results": phase_results,
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


def build_service_pareto_report(
    alternatives: Sequence[Mapping[str, Any]],
    *,
    maximize: tuple[str, ...],
    minimize: tuple[str, ...],
    non_modelled_constraints: tuple[str, ...],
) -> dict[str, Any]:
    """Return a deterministic Pareto frontier over caller-supplied synthetic alternatives."""
    if not alternatives:
        raise ValueError("alternatives must be non-empty")
    if set(maximize) & set(minimize):
        raise ValueError("a metric cannot be both maximized and minimized")
    metrics = (*maximize, *minimize)
    if not metrics:
        raise ValueError("at least one metric is required")
    prepared: list[dict[str, Any]] = []
    seen: set[str] = set()
    for alternative in alternatives:
        candidate_id = str(alternative.get("candidate_id", ""))
        values = alternative.get("metrics")
        if not candidate_id or candidate_id in seen or not isinstance(values, Mapping):
            raise ValueError("alternatives require unique candidate_id and metrics")
        seen.add(candidate_id)
        if any(
            metric not in values
            or not isinstance(values[metric], (int, float))
            or isinstance(values[metric], bool)
            or not math.isfinite(float(values[metric]))
            for metric in metrics
        ):
            raise ValueError("all selected metrics must be finite numbers")
        prepared.append({"candidate_id": candidate_id, "metrics": dict(values)})

    def dominates(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
        left_metrics = left["metrics"]
        right_metrics = right["metrics"]
        no_worse = all(
            left_metrics[metric] >= right_metrics[metric] for metric in maximize
        ) and all(left_metrics[metric] <= right_metrics[metric] for metric in minimize)
        strictly_better = any(
            left_metrics[metric] > right_metrics[metric] for metric in maximize
        ) or any(left_metrics[metric] < right_metrics[metric] for metric in minimize)
        return no_worse and strictly_better

    frontier = [
        candidate
        for candidate in prepared
        if not any(
            other["candidate_id"] != candidate["candidate_id"] and dominates(other, candidate)
            for other in prepared
        )
    ]
    frontier.sort(key=lambda candidate: candidate["candidate_id"])
    frontier_ids = {candidate["candidate_id"] for candidate in frontier}
    return {
        "schema_version": "1.0.0",
        "record_type": "bounded_service_pareto_report",
        "alternatives": prepared,
        "frontier": frontier,
        "dominated_candidate_ids": sorted(
            candidate["candidate_id"]
            for candidate in prepared
            if candidate["candidate_id"] not in frontier_ids
        ),
        "objectives": {"maximize": list(maximize), "minimize": list(minimize)},
        "non_modelled_constraints": list(non_modelled_constraints),
        "promotion_allowed": False,
        "nonclaims": [
            (
                "Synthetic Pareto comparison only; it is not a clinical, operational or "
                "commercial recommendation."
            ),
            "Non-modelled constraints are recorded, not resolved or waived.",
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
    A unit is occupied from dispatch until the declared outbound travel,
    service and handover durations have elapsed.  Return-to-base travel is not
    modelled and remains a caller-visible limitation.
    """

    available = tuple(
        location for location in scenario.locations if scenario.availability.get(location, False)
    )
    busy_until = {location: 0.0 for location in available}
    assignments: list[dict[str, Any]] = []
    for request in sorted(scenario.requests, key=lambda item: (item.arrival_time, item.request_id)):
        eligible = sorted(
            (
                max(request.arrival_time, busy_until[location]),
                scenario.travel[(location, request.demand_id)],
                location,
            )
            for location in available
            if (location, request.demand_id) in scenario.travel
            and scenario.travel[(location, request.demand_id)] <= scenario.threshold
        )
        if eligible:
            dispatch_time, travel_minutes, primary = eligible[0]
            backup = eligible[1][2] if len(eligible) > 1 else None
            wait = dispatch_time - request.arrival_time
            arrival_at_demand = dispatch_time + travel_minutes
            completion_time = arrival_at_demand + request.service_minutes + request.handover_minutes
            busy_until[primary] = completion_time
        else:
            primary = None
            backup = None
            dispatch_time = None
            travel_minutes = None
            arrival_at_demand = None
            completion_time = None
            wait = None
        assignments.append(
            {
                "request_id": request.request_id,
                "demand_id": request.demand_id,
                "primary": primary,
                "backup": backup,
                "queue_wait": wait,
                "dispatch_time": dispatch_time,
                "travel_minutes": travel_minutes,
                "arrival_at_demand": arrival_at_demand,
                "completion_time": completion_time,
                "handover_required": request.handover_minutes > 0,
                "weight": request.weight,
                "subgroup": request.subgroup,
                "rurality": request.rurality,
                "response_time": (
                    arrival_at_demand - request.arrival_time
                    if arrival_at_demand is not None
                    else None
                ),
            }
        )
    metrics = _dispatch_outcome_metrics(assignments)
    return {
        "schema_version": "1.0.0",
        "record_type": "bounded_dispatch_queue_simulation",
        "scenario_id": scenario.scenario_id,
        "assignments": assignments,
        "counts": {
            "requests": len(assignments),
            "assigned": sum(item["primary"] is not None for item in assignments),
            "queued": sum(
                item["queue_wait"] is not None and item["queue_wait"] > 0 for item in assignments
            ),
            "unreachable": sum(item["primary"] is None for item in assignments),
            "handover_required": sum(item["handover_required"] for item in assignments),
        },
        "metrics": metrics,
        "promotion_allowed": False,
        "nonclaims": [
            "Synthetic queue only; no live dispatch, clinical or response guarantee is asserted.",
            (
                "Queue waits and relocation semantics are not operational instructions; "
                "return-to-base travel is not modelled."
            ),
        ],
    }


def _weighted_quantile(values: Sequence[tuple[float, float]], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    threshold = sum(weight for _, weight in ordered) * quantile
    cumulative = 0.0
    for value, weight in ordered:
        cumulative += weight
        if cumulative >= threshold:
            return value
    return ordered[-1][0]


def _dispatch_metric_slice(assignments: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    total_weight = sum(float(item["weight"]) for item in assignments)
    assigned = [item for item in assignments if item["response_time"] is not None]
    assigned_weight = sum(float(item["weight"]) for item in assigned)
    responses = [(float(item["response_time"]), float(item["weight"])) for item in assigned]
    waits = [
        (float(item["queue_wait"]), float(item["weight"]))
        for item in assigned
        if item["queue_wait"] is not None
    ]
    return {
        "demand_weight": total_weight,
        "assigned_weight": assigned_weight,
        "coverage_rate": assigned_weight / total_weight if total_weight else 0.0,
        "mean_response_time": (
            sum(value * weight for value, weight in responses) / assigned_weight
            if assigned_weight
            else None
        ),
        "p95_response_time": _weighted_quantile(responses, 0.95),
        "worst_response_time": max((value for value, _ in responses), default=None),
        "mean_queue_wait": (
            sum(value * weight for value, weight in waits) / assigned_weight
            if assigned_weight
            else None
        ),
    }


def _dispatch_outcome_metrics(assignments: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    subgroup_names = sorted({str(item["subgroup"]) for item in assignments})
    rurality_names = sorted({str(item["rurality"]) for item in assignments})
    return {
        "overall": _dispatch_metric_slice(assignments),
        "subgroups": {
            name: _dispatch_metric_slice([item for item in assignments if item["subgroup"] == name])
            for name in subgroup_names
        },
        "rurality": {
            name: _dispatch_metric_slice([item for item in assignments if item["rurality"] == name])
            for name in rurality_names
        },
        "limitations": [
            "Groups are caller-declared synthetic strata and are not protected-class evidence.",
            (
                "Small-cell suppression is not applied; controlled or person-level inputs "
                "are prohibited."
            ),
        ],
    }


def run_stochastic_dispatch_replications(
    scenario: DispatchScenario, design: StochasticDispatchDesign
) -> dict[str, Any]:
    """Run seeded busy-availability replications with explicit uncertainty.

    The only stochastic mechanism is caller-declared unit availability.  Demand,
    travel, service and handover values remain fixed synthetic inputs.
    """

    unknown = set(design.availability_probability) - set(scenario.locations)
    if unknown:
        raise ValueError("availability probabilities name unknown locations")
    replications: list[dict[str, Any]] = []
    coverage_rates: list[float] = []
    mean_responses: list[float] = []
    for replication in range(design.replications):
        seed = _replication_seed(design.master_seed, replication)
        rng = random.Random(seed)  # nosec B311
        availability = {
            location: scenario.availability.get(location, False)
            and rng.random() < design.availability_probability.get(location, 1.0)
            for location in scenario.locations
        }
        result = simulate_dispatch_scenario(replace(scenario, availability=availability))
        overall = result["metrics"]["overall"]
        coverage_rates.append(float(overall["coverage_rate"]))
        if overall["mean_response_time"] is not None:
            mean_responses.append(float(overall["mean_response_time"]))
        replications.append(
            {
                "replication": replication,
                "seed": seed,
                "availability": availability,
                "counts": result["counts"],
                "metrics": result["metrics"],
            }
        )

    def uncertainty(values: Sequence[float]) -> dict[str, Any]:
        estimate = statistics.fmean(values) if values else None
        standard_error = (
            statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else None
        )
        half_width = 1.96 * standard_error if standard_error is not None else None
        return {
            "estimate": estimate,
            "standard_error": standard_error,
            "confidence_interval_95": (
                [estimate - half_width, estimate + half_width]
                if estimate is not None and half_width is not None
                else None
            ),
        }

    return {
        "schema_version": "1.0.0",
        "record_type": "bounded_stochastic_dispatch_replications",
        "scenario_id": scenario.scenario_id,
        "master_seed": design.master_seed,
        "replications": replications,
        "uncertainty": {
            "coverage_rate": uncertainty(coverage_rates),
            "mean_response_time": uncertainty(mean_responses),
        },
        "promotion_allowed": False,
        "nonclaims": [
            "Seeded synthetic busy availability does not establish operational performance.",
            "Clinical calibration, external validation and dispatch authority remain absent.",
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
    waits = [
        float(item["queue_wait"])
        for item in simulated["assignments"]
        if item["queue_wait"] is not None
    ]
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


def compare_fcfs_reference_implementations(
    arrival_times: Sequence[float],
    service_times: Sequence[float],
    *,
    capacity: int,
    warm_up_customers: int = 0,
) -> dict[str, Any]:
    """Cross-check the queue core with a separate availability-list implementation.

    The alternate path deliberately uses no event heap or ``SimulationResult``
    internals.  It is a bounded repository cross-check, not an external or
    operational validation and cannot authorize promotion.
    """

    primary = simulate_fcfs_queue(
        arrival_times,
        service_times,
        capacity=capacity,
        warm_up_customers=warm_up_customers,
    )
    availability = [0.0] * capacity
    alternate_waits: list[float] = []
    alternate_busy = 0.0
    alternate_last_end = 0.0
    for customer, (arrival, duration) in enumerate(zip(arrival_times, service_times, strict=True)):
        resource = min(range(capacity), key=lambda item: (availability[item], item))
        start = max(arrival, availability[resource])
        end = start + duration
        availability[resource] = end
        if customer >= warm_up_customers:
            alternate_waits.append(start - arrival)
            alternate_busy += duration
            alternate_last_end = max(alternate_last_end, end)
    observed_start = arrival_times[warm_up_customers]
    observed_window = max(0.0, alternate_last_end - observed_start)
    alternate_utilisation = (
        alternate_busy / (capacity * observed_window) if observed_window else 0.0
    )
    alternate_mean = statistics.fmean(alternate_waits)
    wait_deltas = [left - right for left, right in zip(primary.waits, alternate_waits, strict=True)]
    deltas: dict[str, object] = {
        "waits": wait_deltas,
        "mean_wait": primary.mean_wait - alternate_mean,
        "maximum_wait": primary.maximum_wait - max(alternate_waits),
        "utilisation": primary.utilisation - alternate_utilisation,
    }
    float_parity = all(value == 0 for value in deltas.values() if isinstance(value, float))
    parity = all(value == 0 for value in wait_deltas) and float_parity
    return {
        "record_type": "simulation-reference-crosscheck",
        "capacity": capacity,
        "customer_count": len(arrival_times),
        "warm_up_customers": warm_up_customers,
        "primary": "simulate_fcfs_queue",
        "alternate": "availability-list-reference",
        "parity": parity,
        "deltas": deltas,
        "claim_classification": "bounded-reference-only",
        "promotion_allowed": False,
        "nonclaims": [
            "This is an internal deterministic cross-check, not external implementation evidence.",
            "It does not establish clinical, dispatch, national-scale or operational validity.",
        ],
    }


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
