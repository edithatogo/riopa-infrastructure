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
