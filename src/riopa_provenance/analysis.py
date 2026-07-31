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
