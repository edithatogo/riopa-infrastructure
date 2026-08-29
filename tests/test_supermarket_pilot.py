import json
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest

from riopa_provenance.hashing import sha256_json
from riopa_provenance.health_sensitivity import (
    maup_sensitivity,
    measurement_error_sensitivity,
    spatial_confounding_sensitivity,
)
from riopa_provenance.planning import build_planning_feasibility_record
from riopa_provenance.supermarket_pilot import (
    SupermarketPilotError,
    build_access_health_reference,
    build_archived_supermarket_snapshot,
    build_planning_alternatives_reference,
)


def test_archived_supermarket_snapshot_filters_publisher_classification() -> None:
    snapshot = build_archived_supermarket_snapshot(
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "id": 2,
                    "properties": {"Premise_Type": "Dairy or Supermarket", "Status": "Active"},
                    "geometry": {"type": "Point", "coordinates": [175.27, -37.78]},
                },
                {"id": 3, "properties": {"Premise_Type": "Restaurant"}},
            ],
        },
        source_id="hamilton-food-premise-register",
        registry_version="hf:001137c0@hamilton",
        licence="CC-BY-4.0",
        observed_at="2026-08-02T15:30:08Z",
    )
    assert len(snapshot["assertions"]) == 1
    assertion = snapshot["assertions"][0]
    assert assertion["facility_type"] == "supermarket"
    assert assertion["source_status"] == "Active"
    assert snapshot["authoritative"] is False
    assert snapshot["promotion_allowed"] is False


def test_archived_supermarket_snapshot_rejects_invalid_payload() -> None:
    with pytest.raises(SupermarketPilotError, match="FeatureCollection"):
        build_archived_supermarket_snapshot(
            {"type": "Feature"},
            source_id="source",
            registry_version="v1",
            licence="CC-BY-4.0",
            observed_at="now",
        )


def test_archived_supermarket_snapshot_cli_reads_local_payload(tmp_path: Path) -> None:
    payload_path = tmp_path / "payload.json"
    output_path = tmp_path / "snapshot.json"
    payload_path.write_text(
        json.dumps({"type": "FeatureCollection", "features": []}), encoding="utf-8"
    )
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/build_archived_supermarket_snapshot.py",
            str(payload_path),
            "--output",
            str(output_path),
            "--source-id",
            "source",
            "--registry-version",
            "archive:v1",
            "--licence",
            "CC-BY-4.0",
            "--observed-at",
            "2026-08-29T00:00:00Z",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    snapshot = json.loads(output_path.read_text(encoding="utf-8"))
    assert snapshot["record_type"] == "facility_assertions"
    assert snapshot["assertions"] == []
    assert snapshot["promotion_allowed"] is False


def facility_snapshot() -> dict[str, object]:
    return {
        "record_type": "facility_assertions",
        "authoritative": False,
        "release_filter": "public-only",
        "registry_version": "fixture-v1",
        "assertions": [
            {
                "assertion_id": "source:market-a",
                "source_id": "source",
                "facility_type": "supermarket",
                "licence": "fixture-public",
                "observed_at": "2026-08-25T00:00:00Z",
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
            "small_cell_status": "eligible",
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


@pytest.mark.parametrize(
    ("assertions", "message"),
    [
        (["bad"], "must be objects"),
        ([{"assertion_id": "a", "facility_type": "clinic"}], "classified as supermarket"),
        (
            [
                {
                    "assertion_id": "a",
                    "facility_type": "supermarket",
                    "release_classification": "private",
                }
            ],
            "non-public",
        ),
    ],
)
def test_access_health_reference_rejects_malformed_assertions(
    assertions: list[object], message: str
) -> None:
    snapshot = facility_snapshot()
    snapshot["assertions"] = assertions
    with pytest.raises(SupermarketPilotError, match=message):
        build_access_health_reference(
            snapshot, [area_record()], sensitivities(), packet_id="p", generated_at="now"
        )


def test_access_health_reference_rejects_empty_packet_area_and_duplicate_assertion() -> None:
    with pytest.raises(SupermarketPilotError, match="packet_id"):
        build_access_health_reference(
            facility_snapshot(), [area_record()], sensitivities(), packet_id="", generated_at=""
        )
    with pytest.raises(SupermarketPilotError, match="area records"):
        build_access_health_reference(
            facility_snapshot(), [], sensitivities(), packet_id="p", generated_at="now"
        )
    snapshot = facility_snapshot()
    snapshot["assertions"] = snapshot["assertions"] * 2  # type: ignore[operator]
    with pytest.raises(SupermarketPilotError, match="identities must be unique"):
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


def test_access_health_reference_rejects_negative_measure_and_protects_small_cells() -> None:
    negative = area_record()
    negative["access_measures"] = {**negative["access_measures"], "distance": -1.0}  # type: ignore[dict-item]
    with pytest.raises(SupermarketPilotError, match="non-negative"):
        build_access_health_reference(
            facility_snapshot(), [negative], sensitivities(), packet_id="p", generated_at="now"
        )
    suppressed = area_record()
    suppressed["health"] = {
        **suppressed["health"],  # type: ignore[dict-item]
        "small_cell_status": "suppressed",
        "outcome_rate": None,
    }
    packet = build_access_health_reference(
        facility_snapshot(), [suppressed], sensitivities(), packet_id="p", generated_at="now"
    )
    assert packet["areas"][0]["health"]["outcome_rate"] is None
    exposed = deepcopy(suppressed)
    exposed["health"]["outcome_rate"] = 0.2  # type: ignore[index]
    with pytest.raises(SupermarketPilotError, match="must not expose"):
        build_access_health_reference(
            facility_snapshot(), [exposed], sensitivities(), packet_id="p", generated_at="now"
        )
    invalid_status = area_record()
    invalid_status["health"] = {
        **invalid_status["health"],  # type: ignore[dict-item]
        "small_cell_status": "unknown",
    }
    with pytest.raises(SupermarketPilotError, match="eligible or suppressed"):
        build_access_health_reference(
            facility_snapshot(),
            [invalid_status],
            sensitivities(),
            packet_id="p",
            generated_at="now",
        )
    no_nonclaims = sensitivities()
    no_nonclaims[0]["nonclaims"] = []
    with pytest.raises(SupermarketPilotError, match="retain nonclaims"):
        build_access_health_reference(
            facility_snapshot(), [area_record()], no_nonclaims, packet_id="p", generated_at="now"
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


def test_planning_alternatives_rederives_status_and_rejects_malformed_rows() -> None:
    inconsistent = feasibility("candidate-a")
    inconsistent["decision_status"] = "discretionary"
    with pytest.raises(SupermarketPilotError, match="does not match"):
        build_planning_alternatives_reference(
            [inconsistent],
            [alternative("candidate-a", 10.0)],
            packet_id="p",
            generated_at="now",
            non_modelled_constraints=("market", "land", "community", "consent"),
        )


def test_planning_alternatives_rejects_invalid_contract_and_cited_rule_status() -> None:
    constraints = ("market", "land", "community", "consent")
    with pytest.raises(SupermarketPilotError, match="packet_id"):
        build_planning_alternatives_reference(
            [], [], packet_id="", generated_at="", non_modelled_constraints=constraints
        )
    with pytest.raises(SupermarketPilotError, match="non-empty strings"):
        build_planning_alternatives_reference(
            [], [], packet_id="p", generated_at="now", non_modelled_constraints=(*constraints, "")
        )
    with pytest.raises(SupermarketPilotError, match="feasibility records"):
        build_planning_alternatives_reference(
            [],
            [alternative("candidate-a", 1.0)],
            packet_id="p",
            generated_at="now",
            non_modelled_constraints=constraints,
        )
    with pytest.raises(SupermarketPilotError, match="planning-feasibility-query"):
        build_planning_alternatives_reference(
            [{}],
            [alternative("candidate-a", 1.0)],
            packet_id="p",
            generated_at="now",
            non_modelled_constraints=constraints,
        )
    invalid = feasibility("candidate-a")
    invalid["rules"][0]["status"] = "invented"  # type: ignore[index]
    invalid["rules_sha256"] = sha256_json(invalid["rules"])
    with pytest.raises(SupermarketPilotError, match="cited planning rule status"):
        build_planning_alternatives_reference(
            [invalid],
            [alternative("candidate-a", 1.0)],
            packet_id="p",
            generated_at="now",
            non_modelled_constraints=constraints,
        )


def test_planning_alternatives_rejects_duplicate_candidate_and_promotion() -> None:
    constraints = ("market", "land", "community", "consent")
    record = feasibility("candidate-a")
    with pytest.raises(SupermarketPilotError, match="identities must be unique"):
        build_planning_alternatives_reference(
            [record, record],
            [alternative("candidate-a", 1.0)],
            packet_id="p",
            generated_at="now",
            non_modelled_constraints=constraints,
        )
    record["promotion_allowed"] = True
    with pytest.raises(SupermarketPilotError, match="prohibit promotion"):
        build_planning_alternatives_reference(
            [record],
            [alternative("candidate-a", 1.0)],
            packet_id="p",
            generated_at="now",
            non_modelled_constraints=constraints,
        )
    with pytest.raises(SupermarketPilotError, match="non-empty objects"):
        build_planning_alternatives_reference(
            [feasibility("candidate-a")],
            ["bad"],  # type: ignore[list-item]
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
    negative = alternative("candidate-a", -1.0)
    with pytest.raises(SupermarketPilotError, match="finite and non-negative"):
        build_planning_alternatives_reference(
            [feasibility("candidate-a")],
            [negative],
            packet_id="p",
            generated_at="now",
            non_modelled_constraints=("market", "land", "community", "consent"),
        )
