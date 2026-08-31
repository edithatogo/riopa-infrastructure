"""Verify bounded hosted field-diagnostic evidence without source downloads."""

import json
from datetime import datetime
from pathlib import Path

from riopa_provenance.hashing import sha256_bytes, sha256_file, sha256_json

ROOT = Path(__file__).resolve().parents[1]


def evidence() -> dict:
    return json.loads(
        (ROOT / "docs/tasman-attribute-diagnostics-acceptance-20260831.json").read_bytes()
    )


def test_diagnostic_receipt_exact_bytes_and_semantics() -> None:
    document = evidence()
    for key in ("diagnostics", "preservation", "provenance"):
        item = document[key]
        assert (
            sha256_bytes((json.dumps(item["receipt"], indent=2) + "\n").encode()) == item["sha256"]
        )
    diagnostic = document["diagnostics"]["receipt"]
    assert diagnostic["record_type"] == "tasman_attribute_change_diagnostics"
    assert diagnostic["diagnostics_sha256"] == sha256_json(
        diagnostic, omit_keys={"diagnostics_sha256"}
    )
    assert (
        diagnostic["comparison_sha256"]
        == document["reused_scheduled_observation"]["comparison_semantic_sha256"]
    )
    assert diagnostic["release_cycle_qualified"] is False


def test_field_counts_explain_projection_not_source_cause() -> None:
    document = evidence()
    diagnostic = document["diagnostics"]["receipt"]
    assert (
        diagnostic["shared_feature_count"] == diagnostic["attribute_changed_feature_count"] == 3655
    )
    assert diagnostic["added_feature_count"] == diagnostic["removed_feature_count"] == 0
    assert diagnostic["geometry_changed_feature_count"] == 0
    assert diagnostic["fields"] == [
        {
            "name": "UpdatedDate_UTC",
            "classification": "source-field",
            "changed_feature_count": 3655,
            "included_in_attribute_comparison": True,
        },
        {
            "name": "_riopa_capture_ids",
            "classification": "riopa-prefixed",
            "changed_feature_count": 3655,
            "included_in_attribute_comparison": False,
        },
    ]
    interpretation = document["interpretation"]
    assert interpretation["attribute_digest_difference_field"] == "UpdatedDate_UTC"
    assert interpretation["source_cause_established"] is False
    assert interpretation["three_cycle_gate_qualified"] is False
    assert "why the source timestamp changed" in " ".join(document["non_claims"])


def test_reused_source_and_derived_packet_bind_previous_scheduled_observation() -> None:
    document = evidence()
    reused = document["reused_scheduled_observation"]
    path = ROOT / reused["path"]
    assert sha256_file(path) == reused["sha256"]
    previous = json.loads(path.read_bytes())
    preservation = document["preservation"]["receipt"]
    provenance = document["provenance"]["receipt"]
    for key in ("source", "derived"):
        digest = previous["receipts"][key]["sha256"]
        assert reused[f"{key}_receipt_sha256"] == digest
        assert preservation["receipt_sha256"][key] == provenance[f"{key}_receipt_sha256"] == digest
    assert reused["comparison_receipt_sha256"] == previous["comparison_summary"]["receipt_sha256"]
    assert preservation["receipt_sha256"]["comparison"] == reused["comparison_receipt_sha256"]
    diagnostic = document["diagnostics"]["receipt"]
    assert (
        diagnostic["before_canonical_sha256"]
        == previous["comparison_summary"]["before"]["canonical_sha256"]
    )
    assert (
        diagnostic["after_canonical_sha256"]
        == previous["comparison_summary"]["after"]["canonical_sha256"]
    )
    assert reused["source_run"] == previous["source_execution"]["run_id"] == "33379733331"
    assert preservation["source_run"] == provenance["cycle_key"] == reused["source_run"]


def test_actual_manual_execution_does_not_add_scheduled_cycle() -> None:
    document = evidence()
    execution = document["execution"]
    p = document["provenance"]["receipt"]
    preserved = document["preservation"]["receipt"]
    assert execution["run_id"] == "33385367218" and execution["job_id"] == "99466675393"
    assert execution["conclusion"] == "success"
    assert execution["event"] == p["publication"]["event"] == "workflow_dispatch"
    assert p["publication"]["run_id"] == execution["run_id"]
    assert p["publication"]["attempt"] == str(execution["attempt"])
    assert p["publication"]["code_sha"] == document["producer_revision"]
    assert p["publication"]["status"] == "in_progress"
    assert p["publication"]["conclusion"] is None
    assert datetime.fromisoformat(p["publication"]["updated_at"]) <= datetime.fromisoformat(
        execution["job_completed_at"]
    )
    assert p["source_capture"]["event"] == "schedule"
    assert p["automatic_followup"] is False
    assert p["scheduled_source_trigger_observed"] is True
    assert p["publication_job_completion_claimed"] is False
    assert preserved["publication"] == p["publication"]
    assert preserved["receipt_sha256"]["provenance"] == document["provenance"]["sha256"]
    assert (
        preserved["source_run_count"]
        == document["interpretation"]["ledger_distinct_source_run_count"]
        == 2
    )
    assert document["interpretation"]["additional_scheduled_source_runs"] == 0
    assert preserved["three_cycle_gate_qualified"] is False


def test_artifact_and_ledger_preservation_boundaries_are_explicit() -> None:
    document = evidence()
    assert document["artifact"]["id"] == "9755917318"
    assert document["artifact"]["name"] == "tasman-publication-33385367218-1"
    assert document["artifact"]["archive_bytes"] == 460958
    assert "GitHub artifacts API" in document["artifact"]["archive_digest_basis"]
    preserved = document["preservation"]["receipt"]
    assert preserved["public_repository"] == "edithatogo/riopa-public-data-archive"
    assert preserved["public_revision"] == "268d1e87b38aafbda0c7d512d3ce3060cf389628"
    assert (
        preserved["ledger_path"]
        == "operational/tasman-cycle-ledger/v1/ledgers/" + preserved["ledger_sha256"] + ".json"
    )
    assert "diagnostics" not in preserved["receipt_sha256"]
    assert "does not itself claim to contain the diagnostics" in " ".join(document["non_claims"])
