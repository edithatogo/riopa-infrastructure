import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from riopa_provenance.analysis import (
    AnalysisProtocol,
    AnalysisProtocolError,
    CoverageScenario,
    DispatchRequest,
    DispatchScenario,
    Estimand,
    ParameterEvidence,
    ReplicationDesign,
    calibrate_queue_parameters,
    compare_static_simulated_stress,
    difference_in_differences,
    evaluate_coverage_scenario,
    evaluate_dispatch_scenario,
    parameter_evidence_report,
    protocol_record,
    queue_parameter_sensitivity,
    run_seeded_replications,
    simulate_dispatch_scenario,
    simulate_fcfs_queue,
    synthetic_pilot_report,
    validate_analysis_protocol,
)


def test_coverage_scenario_preserves_primary_backup_and_availability() -> None:
    scenario = CoverageScenario(
        "synthetic-coverage",
        ("d1", "d2"),
        ("primary",),
        ("backup",),
        {("d1", "primary"): 2, ("d1", "backup"): 2, ("d2", "backup"): 2},
        {"primary": True, "backup": True},
        2,
    )
    result = evaluate_coverage_scenario(scenario)
    assert result["counts"] == {
        "demand": 2,
        "primary_covered": 1,
        "backup_covered": 2,
        "uncovered": 1,
    }
    assert result["promotion_allowed"] is False
    with pytest.raises(ValueError, match="threshold"):
        CoverageScenario("bad", ("d",), ("p",), ("b",), {}, {}, -1)


def test_dispatch_adapter_preserves_backup_relocation_and_handover_fields() -> None:
    scenario = DispatchScenario(
        "synthetic-dispatch",
        (DispatchRequest("r1", "d1", 0, handover_minutes=5),),
        ("a", "b", "c"),
        {("a", "d1"): 1, ("b", "d1"): 1, ("c", "d1"): 2},
        {"a": True, "b": True, "c": True},
        2,
    )
    result = evaluate_dispatch_scenario(scenario)
    assignment = result["assignments"][0]
    assert assignment["primary"] == "a"
    assert assignment["backup"] == "b"
    assert assignment["relocation_candidates"] == ["c"]
    assert assignment["handover_required"] is True
    assert result["promotion_allowed"] is False


def test_dispatch_queue_simulation_is_deterministic_and_bounded() -> None:
    scenario = DispatchScenario(
        "synthetic-queue",
        (
            DispatchRequest("r1", "d1", 0, service_minutes=10),
            DispatchRequest("r2", "d1", 1, service_minutes=1),
        ),
        ("a",),
        {("a", "d1"): 1},
        {"a": True},
        2,
    )
    result = simulate_dispatch_scenario(scenario)
    assert result["counts"] == {
        "requests": 2,
        "assigned": 1,
        "queued": 1,
        "handover_required": 0,
    }
    assert result["assignments"][1]["queue_wait"] == 9
    assert result["promotion_allowed"] is False


def test_static_and_simulated_stress_comparison_preserves_queue_delta() -> None:
    scenario = DispatchScenario(
        "synthetic-stress",
        (
            DispatchRequest("r1", "d1", 0, service_minutes=10),
            DispatchRequest("r2", "d1", 1, service_minutes=1),
        ),
        ("a",),
        {("a", "d1"): 1},
        {"a": True},
        2,
    )
    result = compare_static_simulated_stress(scenario, stress_profile="bounded-concurrency-fixture")
    assert result["comparison"] == {
        "primary_assignment_delta": -1,
        "queued_requests": 1,
        "maximum_queue_wait": 9.0,
        "primary_assignment_changes": ["r2"],
    }
    assert result["promotion_allowed"] is False
    with pytest.raises(ValueError, match="stress_profile"):
        compare_static_simulated_stress(scenario, stress_profile=" ")


def _protocol(*, replications: int = 5) -> AnalysisProtocol:
    return AnalysisProtocol(
        protocol_id="synthetic-queue-v1",
        version="1.0.0",
        scenario_id="toy-capacity",
        estimand=Estimand(
            name="mean waiting time contrast",
            population="synthetic arrivals after warm-up",
            exposure="one synthetic service policy",
            comparison="reference synthetic service policy",
            outcome="waiting time",
            time_horizon="one bounded simulation run",
            identification_assumptions=(
                "generated arrivals follow the declared distribution",
                "no external validity is claimed",
            ),
        ),
        parameters=(
            ParameterEvidence("mean_interarrival", 2.0, "time units", "assumed"),
            ParameterEvidence("mean_service", 1.0, "time units", "assumed"),
        ),
        replication=ReplicationDesign(
            master_seed=8675309,
            replications=replications,
            warm_up_customers=2,
            convergence_relative_half_width=0.5,
        ),
        limitations=("Synthetic inputs do not establish real-world performance.",),
    )


def test_protocol_record_is_machine_readable_and_preserves_assumptions() -> None:
    record = protocol_record(_protocol())
    root = Path(__file__).resolve().parents[1]
    schema = json.loads(
        (root / "schemas/analysis-protocol.schema.json").read_text(encoding="utf-8")
    )

    assert json.loads(json.dumps(record))["estimand"]["outcome"] == "waiting time"
    assert {item["source"] for item in record["parameters"]} == {"assumed"}
    assert record["operational_status"] == "synthetic-non-operational"
    Draft202012Validator(schema).validate(record)


def test_parameter_evidence_report_preserves_source_classes() -> None:
    protocol = _protocol()
    report = parameter_evidence_report(protocol)
    assert report["counts_by_source"] == {"assumed": 2, "fitted": 0, "external": 0}
    assert report["parameters"][0]["evidence_reference"] is None
    assert report["promotion_allowed"] is False


def test_synthetic_calibration_and_sensitivity_are_reproducible() -> None:
    protocol = _protocol()
    candidates = ((2.0, 1.0), (3.0, 1.0))
    calibration = calibrate_queue_parameters(
        protocol,
        observed_mean_wait=0.0,
        candidates=candidates,
        customer_count=20,
        capacity=2,
    )
    assert calibration["selected"]["mean_interarrival"] in {2.0, 3.0}
    sensitivity = queue_parameter_sensitivity(
        protocol, candidates=candidates, customer_count=20, capacity=2
    )
    assert len(sensitivity["candidates"]) == 2
    assert sensitivity["promotion_allowed"] is False


def test_protocol_fails_closed_for_unreferenced_fitted_parameter() -> None:
    original = _protocol()
    invalid = AnalysisProtocol(
        **{
            **original.__dict__,
            "parameters": (ParameterEvidence("rate", 1.0, "per hour", "fitted"),),
        }
    )

    with pytest.raises(AnalysisProtocolError, match="evidence reference"):
        validate_analysis_protocol(invalid)


def test_deterministic_fcfs_queue_events_and_warm_up_metrics() -> None:
    result = simulate_fcfs_queue(
        [0.0, 0.0, 1.0],
        [2.0, 1.0, 1.0],
        capacity=1,
        warm_up_customers=1,
    )

    assert [event.time for event in result.events] == sorted(event.time for event in result.events)
    assert [event.kind for event in result.events].count("arrival") == 3
    assert [event.kind for event in result.events].count("service_start") == 3
    assert [event.kind for event in result.events].count("service_end") == 3
    assert result.waits == (2.0, 2.0)
    assert result.mean_wait == 2.0
    assert result.observed_customers == 2
    assert result.utilisation == pytest.approx(0.5)


@pytest.mark.parametrize(
    ("arrivals", "services", "message"),
    [
        ([1.0], [], "equal lengths"),
        ([1.0, 0.0], [1.0, 1.0], "non-decreasing"),
        ([0.0], [-1.0], "non-negative"),
    ],
)
def test_queue_rejects_invalid_inputs(
    arrivals: list[float], services: list[float], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        simulate_fcfs_queue(arrivals, services, capacity=1)


def test_seeded_replications_are_statistically_reproducible() -> None:
    protocol = _protocol()

    first = run_seeded_replications(
        protocol,
        customer_count=25,
        capacity=1,
        mean_interarrival=2.0,
        mean_service=1.0,
    )
    second = run_seeded_replications(
        protocol,
        customer_count=25,
        capacity=1,
        mean_interarrival=2.0,
        mean_service=1.0,
    )

    assert first == second
    assert len(set(first["replication_seeds"])) == 5
    assert first["confidence_interval_95"] is not None
    assert isinstance(first["converged"], bool)


def test_one_replication_reports_uncertainty_as_unavailable() -> None:
    result = run_seeded_replications(
        _protocol(replications=1),
        customer_count=5,
        capacity=1,
        mean_interarrival=2.0,
        mean_service=1.0,
    )

    assert result["standard_error"] is None
    assert result["confidence_interval_95"] is None
    assert result["converged"] is False


def test_did_reports_pretrend_and_negative_control_hooks_without_causal_claim() -> None:
    result = difference_in_differences(
        treated_pre=[10.0, 12.0],
        treated_post=[16.0, 18.0],
        comparison_pre=[9.0, 11.0],
        comparison_post=[10.0, 12.0],
        pretrend_treated=[8.0, 9.0, 10.0],
        pretrend_comparison=[7.0, 8.0, 9.0],
        negative_control={
            "treated_pre": [4.0],
            "treated_post": [4.0],
            "comparison_pre": [3.0],
            "comparison_post": [3.0],
        },
    )

    assert result["estimate"] == 5.0
    assert result["assumption_diagnostics"]["pretrend_contrast"] == 0.0
    assert result["assumption_diagnostics"]["negative_control_estimate"] == 0.0
    assert "cannot prove" in result["assumption_diagnostics"]["interpretation"]


def test_did_rejects_non_finite_diagnostic_inputs() -> None:
    with pytest.raises(ValueError, match="negative-control outcomes"):
        difference_in_differences(
            treated_pre=[1.0],
            treated_post=[2.0],
            comparison_pre=[1.0],
            comparison_post=[1.5],
            negative_control={
                "treated_pre": [float("nan")],
                "treated_post": [1.0],
                "comparison_pre": [1.0],
                "comparison_post": [1.0],
            },
        )


def test_pilot_report_is_explicitly_non_operational() -> None:
    protocol = _protocol()
    simulation = run_seeded_replications(
        protocol,
        customer_count=10,
        capacity=1,
        mean_interarrival=2.0,
        mean_service=1.0,
    )
    causal: dict[str, Any] = difference_in_differences(
        treated_pre=[1.0],
        treated_post=[2.0],
        comparison_pre=[1.0],
        comparison_post=[1.5],
    )

    report = synthetic_pilot_report(protocol, simulation, causal)

    assert set(report["suitability"].values()) == {False}
    assert report["operational_status"] == "synthetic-non-operational"
    assert "do not validate empirical assumptions" in report["interpretation_boundary"]


def test_pilot_report_rejects_mismatched_scenario() -> None:
    with pytest.raises(ValueError, match="does not match"):
        synthetic_pilot_report(
            _protocol(),
            {"scenario_id": "different"},
            {"design": "difference-in-differences-reference-v1"},
        )


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda protocol: replace(protocol, protocol_id=" "), "protocol_id"),
        (
            lambda protocol: replace(
                protocol,
                estimand=replace(protocol.estimand, identification_assumptions=()),
            ),
            "identification assumption",
        ),
        (lambda protocol: replace(protocol, parameters=()), "at least one parameter"),
        (
            lambda protocol: replace(
                protocol, parameters=(protocol.parameters[0], protocol.parameters[0])
            ),
            "names must be unique",
        ),
        (
            lambda protocol: replace(
                protocol,
                parameters=(ParameterEvidence("", 1.0, "unit", "assumed"),),
            ),
            "parameter.name",
        ),
        (
            lambda protocol: replace(
                protocol,
                parameters=(ParameterEvidence("rate", 1.0, "", "assumed"),),
            ),
            "unit",
        ),
        (
            lambda protocol: replace(
                protocol,
                parameters=(ParameterEvidence("rate", float("inf"), "unit", "assumed"),),
            ),
            "finite",
        ),
        (
            lambda protocol: replace(
                protocol,
                replication=replace(protocol.replication, replications=0),
            ),
            "replications",
        ),
        (
            lambda protocol: replace(
                protocol,
                replication=replace(protocol.replication, warm_up_customers=-1),
            ),
            "warm_up_customers",
        ),
        (
            lambda protocol: replace(
                protocol,
                replication=replace(protocol.replication, confidence_level=0.9),
            ),
            "only 95%",
        ),
        (
            lambda protocol: replace(
                protocol,
                replication=replace(protocol.replication, convergence_relative_half_width=0),
            ),
            "threshold",
        ),
        (lambda protocol: replace(protocol, limitations=()), "limitation"),
    ],
)
def test_protocol_validation_rejects_incomplete_contracts(mutate: Any, message: str) -> None:
    with pytest.raises(AnalysisProtocolError, match=message):
        validate_analysis_protocol(mutate(_protocol()))


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"capacity": 0}, "capacity"),
        ({"warm_up_customers": -1}, "warm_up_customers"),
        ({"warm_up_customers": 1}, "warm_up_customers"),
    ],
)
def test_queue_rejects_invalid_capacity_and_warm_up(kwargs: dict[str, int], message: str) -> None:
    arguments = {"capacity": 1, **kwargs}
    with pytest.raises(ValueError, match=message):
        simulate_fcfs_queue([0.0], [1.0], **arguments)


@pytest.mark.parametrize(
    ("arrivals", "services", "message"),
    [
        ([float("inf")], [1.0], "arrival_times"),
        ([0.0], [float("nan")], "service_times"),
    ],
)
def test_queue_rejects_non_finite_inputs(
    arrivals: list[float], services: list[float], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        simulate_fcfs_queue(arrivals, services, capacity=1)


def test_zero_duration_queue_has_zero_utilisation() -> None:
    result = simulate_fcfs_queue([0.0], [0.0], capacity=1)
    assert result.utilisation == 0.0
    assert result.mean_wait == 0.0


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"customer_count": 2}, "customer_count"),
        ({"mean_interarrival": 0.0}, "distribution means"),
        ({"mean_service": -1.0}, "distribution means"),
    ],
)
def test_replication_rejects_invalid_run_parameters(
    kwargs: dict[str, float | int], message: str
) -> None:
    arguments: dict[str, float | int] = {
        "customer_count": 5,
        "capacity": 1,
        "mean_interarrival": 2.0,
        "mean_service": 1.0,
    }
    arguments.update(kwargs)
    with pytest.raises(ValueError, match=message):
        run_seeded_replications(_protocol(), **arguments)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"treated_pre": []}, "non-empty"),
        ({"treated_post": [float("inf")]}, "outcomes must be finite"),
        ({"pretrend_treated": [1.0]}, "matching lengths"),
        (
            {
                "pretrend_treated": [1.0, float("nan")],
                "pretrend_comparison": [1.0, 2.0],
            },
            "pretrend outcomes",
        ),
        (
            {
                "negative_control": {
                    "treated_pre": [1.0],
                    "treated_post": [1.0],
                    "comparison_pre": [1.0],
                }
            },
            "four DID groups",
        ),
        (
            {
                "negative_control": {
                    "treated_pre": [],
                    "treated_post": [1.0],
                    "comparison_pre": [1.0],
                    "comparison_post": [1.0],
                }
            },
            "groups must be non-empty",
        ),
    ],
)
def test_did_rejects_incomplete_or_invalid_diagnostics(
    kwargs: dict[str, Any], message: str
) -> None:
    arguments: dict[str, Any] = {
        "treated_pre": [1.0],
        "treated_post": [2.0],
        "comparison_pre": [1.0],
        "comparison_post": [1.5],
    }
    arguments.update(kwargs)
    with pytest.raises(ValueError, match=message):
        difference_in_differences(**arguments)
