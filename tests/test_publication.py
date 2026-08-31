from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

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
    build_publication_resume_plan,
    initialise_publication_state,
    reconcile_publication_receipts,
    record_publication_receipt,
    stage_publication,
    validate_correction_package,
    validate_publication_state,
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


def test_publication_receipt_batch_rejects_duplicate_target_ids() -> None:
    plan = _ready_plan("github")
    state = initialise_publication_state(plan)
    receipt = {
        "target_id": "github",
        "operation_key": state["targets"]["github"]["operation_key"],
        "plan_sha256": plan["plan_sha256"],
        "identifier": "https://example.test/github",
        "revision": "a" * 64,
        "recorded_at": "2026-08-25T00:00:00Z",
    }
    with pytest.raises(PublicationError, match="target_id values must be unique"):
        reconcile_publication_receipts(state, [receipt, receipt])


def _journal_receipt(state: dict[str, Any], target: str) -> dict[str, Any]:
    return {
        "target_id": target,
        "operation_key": state["targets"][target]["operation_key"],
        "plan_sha256": state["plan_sha256"],
        "identifier": f"https://example.test/{target}",
        "revision": "provider-specific-opaque-revision",
        "recorded_at": "2026-08-31T10:00:00+10:00",
    }


def test_multi_target_journal_restore_and_recovery_is_deterministic() -> None:
    original = initialise_publication_state(_ready_plan("github", "hugging-face", "zenodo"))
    receipts = [_journal_receipt(original, target) for target in original["targets"]]
    checkpoint = record_publication_receipt(original, receipts[0])
    restored = json.loads(json.dumps(checkpoint))
    validate_publication_state(restored)
    assert reconcile_publication_receipts(restored, []) == checkpoint
    corrupted = {**restored, "state_sha256": "0" * 64}
    before = copy.deepcopy(corrupted)
    with pytest.raises(PublicationError, match="state hash"):
        reconcile_publication_receipts(corrupted, [])
    assert corrupted == before
    completed = reconcile_publication_receipts(restored, receipts)
    assert completed == reconcile_publication_receipts(original, list(reversed(receipts)))
    assert completed["status"] == "published"
    validate_publication_state(completed)
    assert record_publication_receipt(completed, receipts[0]) == completed
    assert original["status"] == "pending"
    assert restored == checkpoint


@pytest.mark.parametrize("provider", ["github", "hugging-face", "zenodo"])
def test_supplied_receipt_hash_checked_without_breaking_legacy(provider: str) -> None:
    state = initialise_publication_state(_ready_plan(provider))
    receipt = _journal_receipt(state, provider)
    expected = record_publication_receipt(state, receipt)
    hashed = {**receipt, "receipt_sha256": sha256_json(receipt)}
    assert record_publication_receipt(state, hashed) == expected
    assert record_publication_receipt(expected, receipt) == expected
    assert record_publication_receipt(expected, hashed) == expected
    for bad_hash in ("0" * 64, "", None, False, []):
        with pytest.raises(PublicationError, match="receipt hash"):
            record_publication_receipt(state, {**receipt, "receipt_sha256": bad_hash})


@pytest.mark.parametrize(
    "field,value",
    [
        ("identifier", " "),
        ("identifier", 42),
        ("revision", True),
        ("revision", []),
        ("recorded_at", "yesterday"),
        ("recorded_at", "2026-08-31T00:00:00"),
        ("recorded_at", "2026-99-31T00:00:00Z"),
        ("recorded_at", None),
        ("target_id", False),
        ("plan_sha256", "0" * 64),
        ("operation_key", "0" * 64),
    ],
)
def test_receipt_primitive_fields_and_timestamp_fail_closed(field: str, value: Any) -> None:
    state = initialise_publication_state(_ready_plan("github"))
    receipt = {**_journal_receipt(state, "github"), field: value}
    before = copy.deepcopy(state)
    with pytest.raises(PublicationError):
        record_publication_receipt(state, receipt)
    assert state == before


@pytest.mark.parametrize(
    "fault",
    [
        "aggregate",
        "target_status",
        "operation",
        "stored_hash",
        "stored_binding",
        "missing_hash",
        "missing_receipt",
        "empty_targets",
        "target_object",
        "schema",
        "record_type",
        "publication_id",
        "plan_hash",
        "target_id",
        "receipt_object",
        "receipt_timestamp",
    ],
)
def test_resealed_journal_semantic_corruption_rejected(fault: str) -> None:
    original = initialise_publication_state(_ready_plan("github", "hugging-face", "zenodo"))
    receipt = _journal_receipt(original, "github")
    checkpoint = record_publication_receipt(original, receipt)
    state = copy.deepcopy(checkpoint)
    target = state["targets"]["github"]
    if fault == "aggregate":
        state["status"] = "pending"
    elif fault == "target_status":
        target["status"] = "pending"
    elif fault == "operation":
        target["operation_key"] = "0" * 64
    elif fault == "stored_hash":
        target["receipt"]["receipt_sha256"] = "0" * 64
    elif fault == "stored_binding":
        target["receipt"]["target_id"] = "zenodo"
    elif fault == "missing_hash":
        del target["receipt"]["receipt_sha256"]
    elif fault == "missing_receipt":
        del target["receipt"]
    elif fault == "empty_targets":
        state["targets"] = {}
    elif fault == "target_object":
        state["targets"]["github"] = []
    elif fault == "schema":
        state["schema_version"] = "2.0"
    elif fault == "record_type":
        state["record_type"] = "other"
    elif fault == "publication_id":
        state["publication_id"] = None
    elif fault == "plan_hash":
        state["plan_sha256"] = "not-a-digest"
    elif fault == "target_id":
        state["targets"][""] = state["targets"].pop("github")
    elif fault == "receipt_object":
        target["receipt"] = []
    else:
        target["receipt"]["recorded_at"] = "not-a-time"
        target["receipt"]["receipt_sha256"] = sha256_json(
            target["receipt"], omit_keys={"receipt_sha256"}
        )
    state["state_sha256"] = sha256_json(state, omit_keys={"state_sha256"})
    before = copy.deepcopy(state)
    with pytest.raises(PublicationError):
        validate_publication_state(state)
    with pytest.raises(PublicationError):
        reconcile_publication_receipts(state, [])
    with pytest.raises(PublicationError):
        record_publication_receipt(state, receipt)
    assert state == before
    assert record_publication_receipt(checkpoint, receipt) == checkpoint


def test_conflicting_late_batch_is_atomic_for_the_caller() -> None:
    initial = initialise_publication_state(_ready_plan("github", "hugging-face", "zenodo"))
    zenodo = _journal_receipt(initial, "zenodo")
    checkpoint = record_publication_receipt(initial, zenodo)
    before = copy.deepcopy(checkpoint)
    with pytest.raises(PublicationError, match="conflicting"):
        reconcile_publication_receipts(
            checkpoint, [_journal_receipt(initial, "github"), {**zenodo, "revision": "different"}]
        )
    assert checkpoint == before


@pytest.mark.parametrize(
    "targets", [[None], {"github": {}}, [{"target_id": False}], [{"target_id": ""}]]
)
def test_initial_journal_rejects_invalid_target_shapes(targets: Any) -> None:
    plan = {**_ready_plan("github"), "targets": targets}
    plan["plan_sha256"] = sha256_json(plan, omit_keys={"plan_sha256"})
    with pytest.raises(PublicationError):
        initialise_publication_state(plan)


def test_journal_entrypoints_reject_missing_fields_and_non_objects() -> None:
    state = initialise_publication_state(_ready_plan("github"))
    with pytest.raises(PublicationError, match="object"):
        validate_publication_state([])  # type: ignore[arg-type]
    with pytest.raises(PublicationError, match="object"):
        record_publication_receipt(state, [])  # type: ignore[arg-type]
    receipt = _journal_receipt(state, "github")
    del receipt["revision"]
    with pytest.raises(PublicationError, match="missing fields"):
        record_publication_receipt(state, receipt)
    with pytest.raises(PublicationError, match="unknown target"):
        record_publication_receipt(state, {**receipt, "target_id": "unknown"})
    with pytest.raises(PublicationError, match="at least one target"):
        initialise_publication_state(_ready_plan())


def test_resume_projection_is_plan_bound_sorted_and_non_authorising() -> None:
    plan = _ready_plan("zenodo", "hugging-face", "github")
    initial = initialise_publication_state(plan)
    first = _journal_receipt(initial, "github")
    state = record_publication_receipt(initial, first)
    receipt = _journal_receipt(initial, "hugging-face")
    before = copy.deepcopy((plan, state, receipt))
    result = build_publication_resume_plan(plan, state, [receipt])
    assert (plan, state, receipt) == before
    assert result["input_state_sha256"] == state["state_sha256"]
    assert result["plan_sha256"] == plan["plan_sha256"]
    assert result["publication_id"] == plan["publication_id"]
    assert result["reconciled_state_sha256"] == result["reconciled_state"]["state_sha256"]
    assert result["projection_sha256"] == sha256_json(result, omit_keys={"projection_sha256"})
    assert [target["target_id"] for target in result["targets"]] == [
        "github",
        "hugging-face",
        "zenodo",
    ]
    assert [target["disposition"] for target in result["targets"]] == [
        "receipt-recorded",
        "receipt-recorded",
        "provider-reconciliation-required",
    ]
    assert result["targets"][-1]["receipt_sha256"] is None
    assert all(target["remote_write_authorized"] is False for target in result["targets"])
    assert result["remote_write_authorized"] is False
    assert "not live provider acceptance" in result["non_claims"][0]
    assert result == build_publication_resume_plan(plan, state, [receipt])
    result["reconciled_state"]["targets"]["github"]["receipt"]["revision"] = "changed-output"
    assert (plan, state, receipt) == before


def test_resume_projection_handles_complete_and_empty_replay_without_aliases() -> None:
    plan = _ready_plan("github", "hugging-face", "zenodo")
    state = initialise_publication_state(plan)
    receipts = [_journal_receipt(state, target) for target in state["targets"]]
    result = build_publication_resume_plan(plan, state, receipts)
    assert result == build_publication_resume_plan(plan, state, list(reversed(receipts)))
    complete = result["reconciled_state"]
    replay = build_publication_resume_plan(plan, complete, receipts)
    assert replay == build_publication_resume_plan(plan, complete, [])
    assert all(t["disposition"] == "receipt-recorded" for t in replay["targets"])
    assert replay["remote_write_authorized"] is False
    replay["reconciled_state"]["targets"]["github"]["receipt"]["revision"] = "changed"
    assert complete["targets"]["github"]["receipt"]["revision"] != "changed"


@pytest.mark.parametrize("fault", ["removed", "injected", "publication_id", "plan_sha256"])
def test_resume_rejects_internally_valid_but_wrong_plan_journal(fault: str) -> None:
    plan = _ready_plan("github", "hugging-face", "zenodo")
    state = initialise_publication_state(plan)
    if fault == "removed":
        del state["targets"]["zenodo"]
    elif fault == "injected":
        state["targets"]["extra"] = {
            "status": "pending",
            "receipt": None,
            "operation_key": sha256_json(
                {"plan_sha256": state["plan_sha256"], "target_id": "extra"}
            ),
        }
    elif fault == "publication_id":
        state["publication_id"] = "urn:other:publication"
    else:
        state["plan_sha256"] = "0" * 64
        for target_id, target in state["targets"].items():
            target["operation_key"] = sha256_json(
                {"plan_sha256": state["plan_sha256"], "target_id": target_id}
            )
    state["state_sha256"] = sha256_json(state, omit_keys={"state_sha256"})
    validate_publication_state(state)  # A self-consistent journal is insufficient.
    before = copy.deepcopy(state)
    with pytest.raises(PublicationError, match="expected plan"):
        build_publication_resume_plan(plan, state, [])
    assert state == before


@pytest.mark.parametrize(
    "fault", ["hash", "unready", "duplicate", "missing_id", "rights", "destination"]
)
def test_resume_rejects_invalid_or_changed_expected_plan(fault: str) -> None:
    plan = _ready_plan("github", "zenodo")
    state = initialise_publication_state(plan)
    changed = copy.deepcopy(plan)
    if fault == "hash":
        changed["plan_sha256"] = "0" * 64
    elif fault == "unready":
        changed["status"] = "review-required"
    elif fault == "duplicate":
        changed["targets"] = [{"target_id": "github"}, {"target_id": "github"}]
    elif fault == "missing_id":
        del changed["publication_id"]
    elif fault == "rights":
        changed["rights_decision"] = "withhold"
    else:
        changed["targets"] = [
            {"target_id": "github", "repository": "different/repo"},
            {"target_id": "zenodo"},
        ]
    if fault != "hash":
        changed["plan_sha256"] = sha256_json(changed, omit_keys={"plan_sha256"})
    before = copy.deepcopy((changed, state))
    with pytest.raises(PublicationError):
        build_publication_resume_plan(changed, state)
    assert (changed, state) == before


def test_resume_projection_rejects_receipt_conflict_and_recovers() -> None:
    plan = _ready_plan("github", "zenodo")
    initial = initialise_publication_state(plan)
    zenodo = _journal_receipt(initial, "zenodo")
    state = record_publication_receipt(initial, zenodo)
    github = _journal_receipt(initial, "github")
    before = copy.deepcopy(state)
    with pytest.raises(PublicationError, match="conflicting"):
        build_publication_resume_plan(plan, state, [github, {**zenodo, "revision": "other"}])
    assert state == before
    recovered = build_publication_resume_plan(plan, state, [github, zenodo])
    assert recovered["reconciled_state"]["status"] == "published"
    assert recovered["remote_write_authorized"] is False
    with pytest.raises(PublicationError, match="object"):
        build_publication_resume_plan([], state)  # type: ignore[arg-type]
    with pytest.raises(PublicationError, match="object"):
        build_publication_resume_plan(plan, [])  # type: ignore[arg-type]
    with pytest.raises(PublicationError, match="hash mismatch"):
        build_publication_resume_plan(plan, {**state, "state_sha256": "0" * 64}, [])


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
