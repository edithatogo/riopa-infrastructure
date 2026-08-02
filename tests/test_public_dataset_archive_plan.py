import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _plan() -> dict:
    return json.loads(
        (ROOT / "docs/public-dataset-archive-incorporation-plan-20260802.json").read_text()
    )


def test_plan_is_public_only_and_archive_first() -> None:
    plan = _plan()
    assert plan["schema"] == "riopa.public-dataset-archive-plan.v1"
    assert plan["mode"] == "public-datasets-only"
    assert plan["archive_policy"]["raw_before_derived"] is True
    assert "content-addressed archived snapshot" in plan["archive_policy"]["incorporation_rule"]


def test_every_dataset_has_archive_action_targets_and_non_claim() -> None:
    for dataset in _plan()["datasets"]:
        assert dataset["archive_action"]
        assert dataset["incorporation"]
        assert dataset["status"]
        assert dataset["non_claim"]


def test_cross_repository_gaps_have_issue_routes() -> None:
    routes = {route["repository"]: route for route in _plan()["related_repository_routing"]}
    assert len(routes["edithatogo/open_social_data"]["issues"]) == 3
    assert routes["edithatogo/corpus-legislation-nz"]["issues"]
    assert routes["edithatogo/healthpoint-rs"]["issues"] == [
        "https://github.com/edithatogo/healthpoint-rs/issues/52"
    ]


def test_non_public_healthpoint_payloads_are_excluded() -> None:
    health = next(
        dataset
        for dataset in _plan()["datasets"]
        if dataset["id"] == "public-health-and-ambulance-facilities"
    )
    assert "Licensed Healthpoint payloads are excluded" in health["excluded_source"]


def test_stats_nz_meshblock_archive_is_revision_and_digest_bound() -> None:
    meshblocks = next(
        dataset
        for dataset in _plan()["datasets"]
        if dataset["id"] == "stats-nz-meshblock-2026-and-public-population"
    )
    evidence = meshblocks["archive_evidence"]
    assert meshblocks["status"] == "meshblock-and-population-archives-complete-workload-bound"
    assert evidence["captured_features"] == evidence["available_features"] == 57575
    assert evidence["pages"] == 231
    assert evidence["source_stable_during_capture"] is True
    assert evidence["readback_verified"] is True
    assert evidence["projection_features"] == 57575
    assert evidence["projection_capture_records"] == 236
    assert evidence["projection_live_endpoint_contacted"] is False
    assert evidence["projection_geometry_repairs"] == 0
    for field in (
        "workflow_revision",
        "packet_revision",
        "receipt_revision",
        "manifest_sha256",
        "payload_set_sha256",
    ):
        expected_length = 40 if "revision" in field else 64
        assert len(evidence[field]) == expected_length


def test_population_archive_is_revision_and_digest_bound() -> None:
    population = next(
        dataset
        for dataset in _plan()["datasets"]
        if dataset["id"] == "stats-nz-meshblock-2026-and-public-population"
    )
    evidence = population["archive_evidence"]
    assert evidence["population_packet_revision"] == ("4f94d300c0bea6b64972b4b67044990f7e591716")
    assert evidence["population_manifest_sha256"] == (
        "47540c8eb74fbc069b841308402961319aee57a0e85caad8b1de392595465617"
    )
    assert evidence["population_workbook_sha256"] == (
        "001e8a896cfb50f5ed17836dc815b235e3bcca55ee91c9869a2afaeb054b50a6"
    )


def test_food_service_packet_is_source_specific_and_claim_bounded() -> None:
    descriptor = json.loads(
        (ROOT / "config/archive-sources/osm-new-zealand-food-service-2026.json").read_text()
    )
    assert descriptor["packet_revision"] == "d834601efedada86be03dee2ff7a90d0fa37c0a2"
    assert descriptor["status"] == "archived-source-specific-assertions"
    assert "authoritative" in descriptor["non_claim"]
    assert "national-accessibility-claim" in descriptor["disabled_use"]


def test_marlborough_food_premise_packet_is_revision_bound() -> None:
    descriptor = json.loads(
        (ROOT / "config/archive-sources/marlborough-food-premise-licences-2026.json").read_text()
    )
    assert descriptor["packet_revision"] == "b31703eb0dbdaa6aa05b6a84df5fe46e57e37ee0"
    assert descriptor["status"] == "archived-source-specific-assertions"
    assert "national" in descriptor["non_claim"]


def test_hamilton_food_premise_packet_is_revision_bound() -> None:
    descriptor = json.loads(
        (ROOT / "config/archive-sources/hamilton-food-premise-register-2026.json").read_text()
    )
    assert descriptor["packet_revision"] == "3d3d0f4eb3065bcfb28e1c05cb8c7012a58df433"
    assert descriptor["status"] == "archived-source-specific-assertions"
    assert "national" in descriptor["non_claim"]


def test_facility_source_family_gate_is_bounded() -> None:
    evidence = json.loads(
        (ROOT / "docs/facility-source-family-qualification-20260803.json").read_text()
    )
    assert (
        evidence["qualification"]["independent_families"]
        >= evidence["qualification"]["required_minimum"]
    )
    assert evidence["qualification"]["reconciliation_gate"] == "open"
    assert evidence["qualification"]["national_completeness_claim"] is False


def test_materialized_food_source_summary_is_digest_bound_and_non_authoritative() -> None:
    evidence = json.loads((ROOT / "docs/facility-source-materialization-20260803.json").read_text())
    assert len(evidence["sources"]) == 3
    assert all(item["source_assertions_only"] for item in evidence["sources"])
    assert all(len(item["payload_sha256"]) == 64 for item in evidence["sources"])
    hamilton = next(
        item
        for item in evidence["sources"]
        if item["source_id"] == "hamilton-food-premise-register"
    )
    assert hamilton["null_geometry_count"] == hamilton["record_count"]
    assert hamilton["spatially_usable"] is False
    assert evidence["claims"]["authoritative_registry"] is False


def test_food_reconciliation_preserves_candidate_and_source_only_counts() -> None:
    evidence = json.loads((ROOT / "docs/facility-food-reconciliation-20260803.json").read_text())
    assert evidence["status"] == "candidate-matches-not-adjudicated"
    assert evidence["counts"]["candidate_matches"] == 39
    assert evidence["counts"]["source_only"] == 13951
    assert "Hamilton" in " ".join(evidence["limitations"])


def test_facility_panel_preserves_open_adjudication_gate() -> None:
    evidence = json.loads((ROOT / "docs/facility-panel-qualification-20260803.json").read_text())
    assert evidence["inputs"]["candidate_matches"] == 39
    assert evidence["decisions"]["reviewed_matches"] == 0
    assert evidence["decisions"]["authoritative_registry"] is False
    assert len(evidence["panel"]) == 3
