import json
from pathlib import Path

from riopa_provenance.hashing import sha256_file


def test_current_disposition_evidence_references_are_content_bound() -> None:
    root = Path(__file__).resolve().parents[1]
    current = json.loads((root / "docs/archive-current-status-20260831.json").read_text())
    refs = {item["path"]: item["sha256"] for item in current["evidence_refs"]}
    assert set(refs) == {item["evidence"] for item in current["dispositions"].values()}
    for name, digest in refs.items():
        assert sha256_file(root / name) == digest


def test_current_disposition_is_bound_to_exact_accepted_packets() -> None:
    root = Path(__file__).resolve().parents[1]
    current = json.loads((root / "docs/archive-current-status-20260831.json").read_text())
    items = current["dispositions"]
    source = json.loads((root / items["source_publication"]["evidence"]).read_text())
    derived = json.loads((root / items["derived_publication"]["evidence"]).read_text())
    source_receipt, derived_receipt = source["publication_receipt"], derived["publication_receipt"]
    for key, receipt in (
        ("source_publication", source_receipt),
        ("derived_publication", derived_receipt),
    ):
        assert items[key]["status"] == "accepted"
        assert items[key]["role"] == "historical-baseline"
        assert items[key]["public_revision"] == receipt["public_revision"]
        assert receipt["state"] == "verified"
        assert receipt["licence"] == current["licence"]
        assert receipt["attribution"] == current["attribution"]
    assert source_receipt["anonymous_full_packet_verified"] is True
    assert source_receipt["public_dataset_repository"] == current["public_repository"]
    assert derived_receipt["public_repository"] == current["public_repository"]
    assert derived_receipt["identity"]["source_revision"] == source_receipt["public_revision"]
    assert source_receipt["reproduction"]["feature_count"] == current["feature_count"]
    assert derived_receipt["identity"]["feature_count"] == current["feature_count"]
    assert current["supersession"]["historical_receipts_modified"] is False
    assert (
        current["supersession"]["source_only_receipt_reinterpreted_as_derived_publication"] is False
    )
    assert (
        "broader-release-packet-preservation-and-publication" in current["remaining_qualification"]
    )


def test_current_disposition_does_not_turn_manual_replay_into_qualification() -> None:
    root = Path(__file__).resolve().parents[1]
    current = json.loads((root / "docs/archive-current-status-20260831.json").read_text())
    items = current["dispositions"]
    provenance = json.loads((root / items["run_attempt_binding"]["evidence"]).read_text())
    comparison = json.loads((root / items["fixed_baseline_comparison"]["evidence"]).read_text())
    for attempt in provenance["attempts"]:
        assert attempt["receipt"]["scheduled_source_trigger_observed"] is False
        assert attempt["receipt"]["release_cycle_qualified"] is False
    assert items["run_attempt_binding"]["role"] == "historical-baseline"
    assert items["fixed_baseline_comparison"]["role"] == "historical-baseline"
    observed = comparison["comparison_receipt"]["comparison"]
    for change in ("added", "removed", "attribute_changed", "geometry_changed"):
        assert observed[change] == []
    assert observed["after"]["feature_count"] == current["feature_count"]
    assert comparison["comparison_receipt"]["release_cycle_qualified"] is False
    assert (
        "three-scheduled-cycles-including-change-and-failure-recovery"
        in current["remaining_qualification"]
    )


def test_current_scheduled_disposition_binds_latest_without_rewriting_baseline() -> None:
    root = Path(__file__).resolve().parents[1]
    current = json.loads((root / "docs/archive-current-status-20260831.json").read_text())
    latest = current["dispositions"]["scheduled_capture_and_publication"]
    evidence = json.loads((root / latest["evidence"]).read_text())
    source = evidence["receipts"]["source"]["receipt"]
    derived = evidence["receipts"]["derived"]["receipt"]
    preserved = evidence["preservation"]["receipt"]
    assert latest["status"] == "accepted-first-scheduled-observation"
    assert latest["role"] == "latest-observed-scheduled-packet"
    assert latest["source_run"] == evidence["source_execution"]["run_id"] == "33379733331"
    assert latest["publication_run"] == evidence["publication_execution"]["run_id"]
    assert latest["source_public_revision"] == source["public_revision"]
    assert latest["derived_public_revision"] == derived["public_revision"]
    assert latest["ledger_public_revision"] == preserved["public_revision"]
    assert evidence["source_execution"]["event"] == "schedule"
    assert evidence["publication_execution"]["event"] == "workflow_run"
    assert latest["scheduled_source_runs_observed"] == [latest["source_run"]]
    assert latest["ledger_distinct_source_run_count"] == preserved["source_run_count"] == 2
    assert latest["three_cycle_gate_qualified"] is False
    assert latest["comparison_basis"] == evidence["comparison_summary"]["baseline_role"]
    assert latest["difference_counts"] == evidence["comparison_summary"]["difference_counts"]
    assert latest["difference_counts"]["attribute_changed"] == 3655
    assert latest["difference_cause"] == "unattributed"
    assert source["licence"] == derived["licence"] == current["licence"]
    assert source["reproduction"]["feature_count"] == current["feature_count"]
    assert (
        latest["source_public_revision"]
        != current["dispositions"]["source_publication"]["public_revision"]
    )
    assert "One scheduled source run" in " ".join(current["non_claims"])
