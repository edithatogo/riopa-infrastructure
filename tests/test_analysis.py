import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from riopa_provenance.analysis import (
    AnalysisProtocol,
    AnalysisProtocolError,
    Estimand,
    ParameterEvidence,
    ReplicationDesign,
    difference_in_differences,
    protocol_record,
    run_seeded_replications,
    simulate_fcfs_queue,
    synthetic_pilot_report,
    validate_analysis_protocol,
)


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
