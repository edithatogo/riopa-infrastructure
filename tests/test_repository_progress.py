from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import scripts.report_repository_progress as progress
from riopa_provenance.hashing import sha256_bytes, sha256_file, sha256_json


def test_only_top_level_actual_tasks_are_counted() -> None:
    rows = progress.plan_tasks(
        "## Build\n- [x] done\n  - [ ] child\n```md\n- [x] example\n```\n"
        "- [~] current\n## Release\n- [ ] gate\n"
    )
    assert [r["state"] for r in rows] == ["x", "~", " "]
    assert rows[-1]["phase"] == "Release"


def test_empty_root_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="no Conductor tracks"):
        progress.track_progress(tmp_path)


def test_real_report_is_repeatable_and_non_mutating() -> None:
    root = Path(__file__).resolve().parents[1]
    state = root / ".riopa-local/codex/state.json"
    before = state.read_bytes() if state.exists() else None
    first = progress.report(root)
    assert first == progress.report(root)
    assert (state.read_bytes() if state.exists() else None) == before
    assert len(first["tracks"]) == 29
    assert first["task_totals"]["completed"] < first["task_totals"]["total"]
    mvp = next(t for t in first["tracks"] if t["track_id"] == "nz_spatial_archive_mvp_20260718")
    assert mvp["status"] == "active" and mvp["maturity"] == "M1"
    stable = first["release_readiness"]["releases"][-1]
    assert stable["version"] == "1.0.0" and stable["ready"] is False
    assert "hosted systems" in first["non_claims"][0]
    assert first["recorded_cycle_ledger"]["three_cycle_gate_qualified"] is False
    assert first["recorded_cycle_ledger"]["scheduled_automatic_source_runs"] == []
    assert "## Release qualification" in progress.markdown(first)


def test_cli_failure_does_not_claim_success(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr("sys.argv", ["progress", "--root", str(tmp_path), "--format", "json"])
    assert progress.main() == 1
    assert json.loads(capsys.readouterr().out)["status"] == "invalid"


@pytest.mark.parametrize("tamper", ["hash", "escape", "duplicate", "missing", "unbound"])
def test_archive_evidence_validation_rejects_tampering(tamper: str) -> None:
    root = Path(__file__).resolve().parents[1]
    archive = json.loads((root / "docs/archive-current-status-20260831.json").read_bytes())
    if tamper == "hash":
        archive["evidence_refs"][0]["sha256"] = "0" * 64
    elif tamper == "escape":
        archive["evidence_refs"][0]["path"] = "../outside.json"
    elif tamper == "duplicate":
        archive["evidence_refs"].append(copy.deepcopy(archive["evidence_refs"][0]))
    elif tamper == "missing":
        archive["evidence_refs"][0]["path"] = "docs/nonexistent-progress-evidence.json"
    else:
        archive["dispositions"]["source_publication"]["evidence"] = "docs/unbound.json"
    with pytest.raises(ValueError):
        progress.validate_archive_evidence(root, archive)


def test_track_identity_and_symlink_fail_closed(tmp_path: Path) -> None:
    track = tmp_path / "conductor/tracks/sample"
    track.mkdir(parents=True)
    metadata = {"track_id": "wrong", "status": "active", "current_maturity": "M1"}
    (track / "metadata.json").write_text(json.dumps(metadata))
    (track / "plan.md").write_text("- [ ] pending\n")
    with pytest.raises(ValueError, match="identity"):
        progress.track_progress(tmp_path)
    (track / "plan.md").unlink()
    target = tmp_path / "plan-source.md"
    target.write_text("- [x] done\n")
    (track / "plan.md").symlink_to(target)
    with pytest.raises(ValueError, match="symlink"):
        progress.track_progress(tmp_path)


@pytest.mark.parametrize(
    "path,value",
    [
        (("schema_version",), "2"),
        (("record_type",), "complete_archive"),
        (("as_of",), "2027-01-01"),
        (("track",), "other_track"),
        (("basis",), "live-provider-health"),
        (("source_scope",), "all-councils"),
        (("public_repository",), "other/repo"),
        (("feature_count",), 3656),
        (("feature_count",), True),
        (("licence",), "CC0"),
        (("attribution",), "Other publisher"),
        (("dispositions", "source_publication", "status"), "pending"),
        (("dispositions", "derived_publication", "status"), "pending"),
        (("dispositions", "source_publication", "public_revision"), "0" * 40),
        (("dispositions", "derived_publication", "public_revision"), "0" * 40),
        (("dispositions", "run_attempt_binding", "status"), "accepted-scheduled"),
        (("dispositions", "fixed_baseline_comparison", "status"), "accepted-changes"),
        (("supersession", "scope"), "All preservation complete"),
        (("supersession", "historical_receipts_modified"), True),
        (("supersession", "source_only_receipt_reinterpreted_as_derived_publication"), True),
        (("remaining_qualification",), []),
        (("non_claims",), []),
        (("unexpected_claim",), "stable-ready"),
    ],
)
def test_every_projected_claim_is_receipt_bound(path: tuple, value: object) -> None:
    root = Path(__file__).resolve().parents[1]
    archive = json.loads((root / "docs/archive-current-status-20260831.json").read_bytes())
    target = archive
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    # All four evidence references and their hashes remain untouched.
    with pytest.raises(ValueError):
        progress.validate_archive_evidence(root, archive)


@pytest.mark.parametrize(
    "fault",
    [
        "source_status",
        "derived_status",
        "provenance_status",
        "comparison_status",
        "rights",
        "count",
        "manual",
        "differences",
        "change_hashes",
        "content_hash",
    ],
)
def test_resealed_receipt_semantic_drift_rejected(tmp_path: Path, fault: str) -> None:
    root = Path(__file__).resolve().parents[1]
    archive = json.loads((root / "docs/archive-current-status-20260831.json").read_bytes())
    documents = {path: json.loads((root / path).read_bytes()) for path in progress.ARCHIVE_RECEIPTS}
    source, derived, provenance, comparison = [
        documents[path] for path in progress.ARCHIVE_RECEIPTS[:4]
    ]
    if fault.endswith("_status"):
        docs = {
            "source": source,
            "derived": derived,
            "provenance": provenance,
            "comparison": comparison,
        }
        docs[fault.removesuffix("_status")]["status"] = "pending"
    elif fault == "rights":
        derived["publication_receipt"]["licence"] = "CC0"
    elif fault == "count":
        derived["publication_receipt"]["identity"]["feature_count"] = 3656
    elif fault == "manual":
        provenance["attempts"][0]["receipt"]["publication"]["event"] = "workflow_run"
    else:
        diff = comparison["comparison_receipt"]["comparison"]
        if fault == "differences":
            diff["added"] = ["99999"]
        elif fault == "change_hashes":
            diff["change_hashes"] = {"99999": {}}
        else:
            diff["before"]["comparison_content_sha256"] = "0" * 64
        diff["comparison_sha256"] = sha256_json(diff, omit_keys={"comparison_sha256"})

    # Re-seal file bindings and embedded byte hashes, forcing semantic validation.
    def body(value: dict) -> bytes:
        return (json.dumps(value, indent=2) + "\n").encode()

    for doc in (source, derived):
        doc["hosted_execution"]["identical_receipts_sha256"] = sha256_bytes(
            body(doc["publication_receipt"])
        )
    for attempt in provenance["attempts"]:
        attempt["receipt_sha256"] = sha256_bytes(body(attempt["receipt"]))
    comparison["hosted_execution"]["receipt_sha256"] = sha256_bytes(
        body(comparison["comparison_receipt"])
    )
    for reference in archive["evidence_refs"]:
        path = tmp_path / reference["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body(documents[reference["path"]]))
        reference["sha256"] = sha256_file(path)
    with pytest.raises(ValueError):
        progress.validate_archive_evidence(tmp_path, archive)


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", "accepted-three-cycles"),
        ("role", "historical-baseline"),
        ("source_run", "999"),
        ("publication_run", "999"),
        ("source_public_revision", "0" * 40),
        ("derived_public_revision", "0" * 40),
        ("ledger_public_revision", "0" * 40),
        ("scheduled_source_runs_observed", ["999"]),
        ("ledger_distinct_source_run_count", 3),
        ("comparison_basis", "adjacent-cycle"),
        ("difference_counts", {}),
        ("difference_cause", "authoritative-source-change"),
        ("three_cycle_gate_qualified", True),
    ],
)
def test_scheduled_summary_drift_rejected(field: str, value: object) -> None:
    root = Path(__file__).resolve().parents[1]
    archive = json.loads((root / "docs/archive-current-status-20260831.json").read_bytes())
    archive["dispositions"]["scheduled_capture_and_publication"][field] = value
    with pytest.raises(ValueError):
        progress.validate_archive_evidence(root, archive)


@pytest.mark.parametrize(
    "path,value",
    [
        (("status",), "pending"),
        (("publication_execution", "conclusion"), "failure"),
        (("source_execution", "event"), "workflow_dispatch"),
        (("qualification", "three_cycle_gate_qualified"), True),
        (("qualification", "scheduled_source_runs_observed"), ["999"]),
        (("comparison_summary", "diagnostic_status"), "source-change"),
        (("comparison_summary", "difference_counts", "attribute_changed"), 0),
        (("comparison_summary", "after", "canonical_sha256"), "0" * 64),
        (("receipts", "source", "sha256"), "0" * 64),
    ],
)
def test_scheduled_receipt_semantic_drift_rejected(path: tuple[str, ...], value: object) -> None:
    root = Path(__file__).resolve().parents[1]
    documents = {p: json.loads((root / p).read_bytes()) for p in progress.ARCHIVE_RECEIPTS}
    item = documents[progress.ARCHIVE_RECEIPTS[4]]
    for key in path[:-1]:
        item = item[key]
    item[path[-1]] = value
    with pytest.raises(ValueError):
        progress.archive_projection(documents)
