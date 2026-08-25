from __future__ import annotations

import json
from pathlib import Path

import pytest

from riopa_provenance.crate import build_research_object
from riopa_provenance.hashing import sha256_json
from riopa_provenance.publication import (
    PublicationError,
    _artifact_rights_decision,
    _media_type,
    _most_restrictive,
    _narrow_decision,
    build_publication_plan,
    initialise_publication_state,
    reconcile_publication_receipts,
    record_publication_receipt,
    stage_publication,
    validate_correction_package,
)


def _ready_plan(*target_ids: str) -> dict[str, object]:
    plan: dict[str, object] = {
        "publication_id": "urn:riopa:publication:test",
        "status": "ready",
        "targets": [{"target_id": target_id} for target_id in target_ids],
        "plan_sha256": "",
    }
    plan["plan_sha256"] = sha256_json(plan, omit_keys={"plan_sha256"})
    return plan


def test_publication_decision_precedence_is_fail_closed() -> None:
    assert _most_restrictive([]) == "review-required"
    assert _most_restrictive(["publish", "metadata-only"]) == "metadata-only"
    assert _most_restrictive(["publish", "review-required"]) == "review-required"
    assert _most_restrictive(["withhold", "review-required"]) == "review-required"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("artifact.parquet", "application/vnd.apache.parquet"),
        ("artifact.duckdb", "application/vnd.duckdb"),
        ("metadata.json", "application/json"),
    ],
)
def test_publication_media_types_are_deterministic(name: str, expected: str) -> None:
    assert _media_type(Path(name)) == expected


def test_publication_error_is_value_error() -> None:
    assert issubclass(PublicationError, ValueError)


def test_correction_package_validator_accepts_bounded_example_and_rejects_reuse() -> None:
    package = json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "docs/publication-correction-package-20260803.json"
        ).read_text(encoding="utf-8")
    )
    assert validate_correction_package(package) == ()
    tampered = json.loads(json.dumps(package))
    tampered["bounded_example"]["successor"]["sha256"] = tampered["bounded_example"]["predecessor"][
        "sha256"
    ]
    assert any("successor digest" in error for error in validate_correction_package(tampered))


def test_publication_plan_closes_bounded_correction_validation_only() -> None:
    plan = Path("conductor/tracks/publication_validation_20260718/plan.md").read_text(
        encoding="utf-8"
    )
    assert "[x] 4.2 Exercise correction, supersession" in plan
    assert "production downstream notification remains open" in plan


def test_artifact_rights_override_precedes_source_and_global_fallback() -> None:
    records = {
        "source": {"redistribution_status": "open", "attribution": "Source"},
        "artifact-rights": {"redistribution_status": "metadata-only", "attribution": "Override"},
    }
    decision, basis, attribution = _artifact_rights_decision(
        {"rights_ref": "artifact-rights"}, ["source"], records, "allowed"
    )
    assert decision == "metadata-only"
    assert "artifact-rights" in " ".join(basis)
    assert attribution == ["Override"]
    decision, _, _ = _artifact_rights_decision(None, [], records, "allowed")
    assert decision == "publish"
    decision, _, _ = _artifact_rights_decision(
        {"rights_ref": "missing"}, ["source"], records, "allowed"
    )
    assert decision == "review-required"


def test_reviewed_decisions_can_narrow_but_not_widen_inherited_rights() -> None:
    assert _narrow_decision("publish", "metadata-only", context="test") == "metadata-only"
    with pytest.raises(PublicationError, match="would widen inherited rights"):
        _narrow_decision("withhold", "publish", context="test")


def test_publication_state_is_resumable_and_idempotent() -> None:
    plan = _ready_plan("github", "hugging-face", "zenodo")
    state = initialise_publication_state(plan)
    operation_key = state["targets"]["github"]["operation_key"]
    receipt = {
        "target_id": "github",
        "operation_key": operation_key,
        "plan_sha256": plan["plan_sha256"],
        "identifier": "https://github.com/example/releases/tag/v1",
        "revision": "0123456789abcdef",
        "recorded_at": "2026-07-31T08:00:00Z",
    }

    resumed = record_publication_receipt(state, receipt)
    assert resumed["status"] == "in-progress"
    assert resumed["targets"]["github"]["status"] == "published"
    assert record_publication_receipt(resumed, receipt) == resumed


def test_publication_state_rejects_duplicate_target_conflicts() -> None:
    plan = _ready_plan("zenodo")
    state = initialise_publication_state(plan)
    receipt = {
        "target_id": "zenodo",
        "operation_key": state["targets"]["zenodo"]["operation_key"],
        "plan_sha256": plan["plan_sha256"],
        "identifier": "https://doi.org/10.5281/zenodo.1",
        "revision": "1",
        "recorded_at": "2026-07-31T08:00:00Z",
    }
    published = record_publication_receipt(state, receipt)
    assert published["status"] == "published"

    conflicting = {**receipt, "identifier": "https://doi.org/10.5281/zenodo.2"}
    with pytest.raises(PublicationError, match="conflicting publication receipt"):
        record_publication_receipt(published, conflicting)


def test_publication_receipt_batch_reconciles_in_target_order_and_replays() -> None:
    plan = _ready_plan("zenodo", "github")
    state = initialise_publication_state(plan)
    receipts = [
        {
            "target_id": target_id,
            "operation_key": state["targets"][target_id]["operation_key"],
            "plan_sha256": plan["plan_sha256"],
            "identifier": f"https://example.test/{target_id}",
            "revision": "a" * 64,
            "recorded_at": "2026-08-25T00:00:00Z",
        }
        for target_id in ("zenodo", "github")
    ]
    reconciled = reconcile_publication_receipts(state, list(reversed(receipts)))
    assert reconciled["status"] == "published"
    assert all(item["status"] == "published" for item in reconciled["targets"].values())
    assert reconcile_publication_receipts(reconciled, receipts) == reconciled


def test_publication_receipt_batch_rejects_non_object_receipts() -> None:
    state = initialise_publication_state(_ready_plan("github"))
    with pytest.raises(PublicationError, match="contain objects"):
        reconcile_publication_receipts(state, ["not-a-receipt"])  # type: ignore[list-item]


def test_publication_state_rejects_unready_or_unbound_work() -> None:
    with pytest.raises(PublicationError, match="ready plan"):
        initialise_publication_state(
            {
                "publication_id": "urn:riopa:publication:test",
                "plan_sha256": "c" * 64,
                "status": "review-required",
                "targets": [{"target_id": "github"}],
            }
        )
    unbound = _ready_plan("github")
    unbound["publication_id"] = "urn:riopa:publication:changed"
    with pytest.raises(PublicationError, match="content-bound plan"):
        initialise_publication_state(unbound)
    with pytest.raises(PublicationError, match="targets must be unique"):
        initialise_publication_state(_ready_plan("github", "github"))


def test_target_rights_decision_is_inherited_and_staged_separately(
    tmp_path: Path,
) -> None:
    root = Path(__file__).resolve().parents[1]
    research_object = build_research_object(
        root / "examples/minimal/snapshot-manifest.json",
        tmp_path / "research-object",
    )
    plan_path = tmp_path / "publication-plan.json"
    target_path = "artifact-raw.json"
    build_publication_plan(
        research_object,
        plan_path,
        target_overrides={"zenodo": {target_path: "metadata-only"}},
    )
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    asset = next(item for item in plan["assets"] if item["path"] == target_path)

    assert asset["rights_decision"] == "publish"
    assert asset["target_decisions"]["github"] == "publish"
    assert asset["target_decisions"]["zenodo"] == "metadata-only"
    staged = stage_publication(plan_path, research_object, tmp_path / "staged")
    assert (staged / "github" / target_path).is_file()
    assert (staged / "zenodo" / f"withheld/{target_path}.metadata.json").is_file()

    with pytest.raises(PublicationError, match="would widen inherited rights"):
        build_publication_plan(
            research_object,
            tmp_path / "unsafe-plan.json",
            overrides={target_path: "withhold"},
            target_overrides={"zenodo": {target_path: "publish"}},
        )
    with pytest.raises(PublicationError, match="unknown asset paths"):
        build_publication_plan(
            research_object,
            tmp_path / "unknown-path-plan.json",
            target_overrides={"zenodo": {"missing.bin": "withhold"}},
        )
