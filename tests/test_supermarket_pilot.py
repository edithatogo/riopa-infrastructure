from copy import deepcopy

import pytest

from riopa_provenance.health_sensitivity import (
    maup_sensitivity,
    measurement_error_sensitivity,
    spatial_confounding_sensitivity,
)
from riopa_provenance.planning import build_planning_feasibility_record
from riopa_provenance.supermarket_pilot import (
    SupermarketPilotError,
    build_access_health_reference,
    build_planning_alternatives_reference,
)


def facility_snapshot() -> dict[str, object]:
    return {
        "record_type": "facility_assertions",
        "authoritative": False,
        "release_filter": "public-only",
        "registry_version": "fixture-v1",
        "assertions": [
            {
                "assertion_id": "source:market-a",
                "facility_type": "supermarket",
                "release_classification": "public",
            }
        ],
    }


def area_record(area_id: str = "area-a") -> dict[str, object]:
    return {
        "area_id": area_id,
        "access_measures": {
            "distance": 2.0,
            "network": 4.0,
            "multimodal": 5.0,
            "capacity": 20.0,
            "competition": 0.5,
        },
        "context": {
            "deprivation": "quintile-3",
            "demographic": "all-public-aggregate",
            "rurality": "urban",
        },
        "health": {
            "outcome_rate": 0.2,
            "denominator": 100.0,
            "source_ref": "fixture:aggregate-health-v1",
            "ecological": True,
            "small_cell_status": "not-small",
        },
    }


def sensitivities() -> list[dict[str, object]]:
    observations = [
        {"exposed": True, "outcome": 2.0, "stratum": "a"},
        {"exposed": False, "outcome": 1.0, "stratum": "a"},
    ]
    return [
        spatial_confounding_sensitivity(
            observations,
            exposure_field="exposed",
            outcome_field="outcome",
            confounder_field="stratum",
        ),
        maup_sensitivity({"small": 1.0, "large": 1.2}),
        measurement_error_sensitivity([1.0, 2.0], absolute_error=0.1),
    ]


def feasibility(candidate_id: str, status: str = "permitted") -> dict[str, object]:
    return build_planning_feasibility_record(
        [
            {
                "provision_id": f"provision:{candidate_id}",
                "status": status,
                "confidence": "medium",
                "evidence": [f"fixture:plan:{candidate_id}"],
                "caveats": ["authority review required"],
            }
        ],
        query_id=f"query:{candidate_id}",
        feature_ref=candidate_id,
        captured_at="2026-08-25T00:00:00Z",
    )


def alternative(candidate_id: str, cost: float) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "metrics": {
            "average_access": 5.0,
            "worst_case_access": 9.0,
            "subgroup_gap": 1.0,
            "capacity_served": 100.0,
            "competition_balance": 0.5,
            "cost": cost,
            "robustness_loss": 0.2,
        },
    }


def test_access_health_reference_binds_distinct_constructs_and_sensitivities() -> None:
    packet = build_access_health_reference(
        facility_snapshot(),
        [area_record("area-b"), area_record("area-a")],
        sensitivities(),
        packet_id="fixture-pilot",
        generated_at="2026-08-25T01:00:00Z",
    )
    assert [row["area_id"] for row in packet["areas"]] == ["area-a", "area-b"]
    assert packet["registry_version"] == "fixture-v1"
    assert "ecological-health-association" in packet["constructs_kept_distinct"]
    assert packet["claim_classification"] == "bounded-descriptive-reference"
    assert packet["promotion_allowed"] is False
    assert len(packet["packet_sha256"]) == 64


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"authoritative": True}, "public-only"),
        ({"registry_version": ""}, "registry_version"),
        ({"assertions": []}, "requires assertions"),
    ],
)
def test_access_health_reference_rejects_invalid_registry(
    change: dict[str, object], message: str
) -> None:
    snapshot = facility_snapshot()
    snapshot.update(change)
    with pytest.raises(SupermarketPilotError, match=message):
        build_access_health_reference(
            snapshot, [area_record()], sensitivities(), packet_id="p", generated_at="now"
        )


def test_access_health_reference_rejects_non_ecological_or_incomplete_area() -> None:
    row = area_record()
    health = dict(row["health"])  # type: ignore[arg-type]
    health["ecological"] = False
    row["health"] = health
    with pytest.raises(SupermarketPilotError, match="ecological"):
        build_access_health_reference(
            facility_snapshot(), [row], sensitivities(), packet_id="p", generated_at="now"
        )
    duplicate = area_record()
    with pytest.raises(SupermarketPilotError, match="unique"):
        build_access_health_reference(
            facility_snapshot(),
            [duplicate, duplicate],
            sensitivities(),
            packet_id="p",
            generated_at="now",
        )
    with pytest.raises(SupermarketPilotError, match="sensitivities"):
        build_access_health_reference(
            facility_snapshot(), [area_record()], [], packet_id="p", generated_at="now"
        )


def test_planning_alternatives_report_complete_pareto_tradeoffs() -> None:
    packet = build_planning_alternatives_reference(
        [feasibility("candidate-b", "discretionary"), feasibility("candidate-a")],
        [alternative("candidate-b", 12.0), alternative("candidate-a", 10.0)],
        packet_id="fixture-alternatives",
        generated_at="2026-08-25T01:00:00Z",
        non_modelled_constraints=("market", "land", "community", "consent"),
    )
    assert packet["pareto"]["dominated_candidate_ids"] == ["candidate-b"]
    assert packet["pareto"]["objectives"]["maximize"] == [
        "capacity_served",
        "competition_balance",
    ]
    assert packet["planning_dispositions"][1]["decision_status"] == "discretionary"
    assert packet["promotion_allowed"] is False


def test_planning_alternatives_excludes_unresolved_and_tampered_planning_evidence() -> None:
    with pytest.raises(SupermarketPilotError, match="only permitted or discretionary"):
        build_planning_alternatives_reference(
            [feasibility("candidate-a", "unresolved")],
            [alternative("candidate-a", 10.0)],
            packet_id="p",
            generated_at="now",
            non_modelled_constraints=("market", "land", "community", "consent"),
        )
    record = feasibility("candidate-a")
    tampered = deepcopy(record)
    tampered["rules"][0]["status"] = "prohibited"  # type: ignore[index]
    with pytest.raises(SupermarketPilotError, match="valid digest"):
        build_planning_alternatives_reference(
            [tampered],
            [alternative("candidate-a", 10.0)],
            packet_id="p",
            generated_at="now",
            non_modelled_constraints=("market", "land", "community", "consent"),
        )


def test_planning_alternatives_requires_complete_metrics_and_real_world_constraints() -> None:
    incomplete = alternative("candidate-a", 10.0)
    del incomplete["metrics"]["robustness_loss"]  # type: ignore[index]
    with pytest.raises(SupermarketPilotError, match="complete trade-off"):
        build_planning_alternatives_reference(
            [feasibility("candidate-a")],
            [incomplete],
            packet_id="p",
            generated_at="now",
            non_modelled_constraints=("market", "land", "community", "consent"),
        )
    with pytest.raises(SupermarketPilotError, match="constraints are required"):
        build_planning_alternatives_reference(
            [feasibility("candidate-a")],
            [alternative("candidate-a", 10.0)],
            packet_id="p",
            generated_at="now",
            non_modelled_constraints=("market",),
        )
