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
    observed = comparison["comparison_receipt"]["comparison"]
    for change in ("added", "removed", "attribute_changed", "geometry_changed"):
        assert observed[change] == []
    assert observed["after"]["feature_count"] == current["feature_count"]
    assert comparison["comparison_receipt"]["release_cycle_qualified"] is False
    assert (
        "three-scheduled-cycles-including-change-and-failure-recovery"
        in current["remaining_qualification"]
    )
