import pytest

from riopa_provenance.planning import (
    build_feature_provision_linkage,
    build_plan_source_intake,
    build_planning_concept_crosswalk,
    build_planning_feasibility_record,
    build_planning_linkage_error_report,
    build_rule_structure_record,
    validate_planning_linkage_error_report,
)


def _packets() -> dict[str, dict[str, object]]:
    return {
        "source_intake": build_plan_source_intake(
            [
                {
                    "plan_id": "plan:fixture",
                    "version_id": "plan:fixture:2026",
                    "source_ref": "archive:fixture:plan",
                    "locator": "archive:fixture:plan#root",
                    "document_sha256": "a" * 64,
                    "structure_sha256": "b" * 64,
                    "terms_status": "declared-public",
                    "rights_status": "unverified",
                }
            ],
            intake_id="intake:fixture",
            captured_at="2026-08-25T00:00:00Z",
        ),
        "structure": build_rule_structure_record(
            [{"provision_id": "provision:fixture"}],
            structure_id="structure:fixture",
            captured_at="2026-08-25T00:00:00Z",
        ),
        "linkage": build_feature_provision_linkage(
            [
                {
                    "feature_id": "fixture:zone",
                    "feature_kind": "zone",
                    "feature_source_ref": "archive:fixture:zone",
                    "provision_version_id": "plan:fixture:2026",
                    "evidence": ["archive:fixture:rule"],
                    "confidence": "unknown",
                }
            ],
            linkage_id="linkage:fixture",
            captured_at="2026-08-25T00:00:00Z",
        ),
        "crosswalk": build_planning_concept_crosswalk(
            [
                {
                    "source_id": "fixture:zone",
                    "source_label": "Declared zone",
                    "canonical_id": "urn:riopa:concept:planning:residential",
                    "method": "declared-reference",
                    "confidence": "unknown",
                    "reviewer": "agent-panel:unreviewed",
                    "valid_from": "2026-01-01",
                    "evidence": ["archive:fixture:zone"],
                }
            ],
            crosswalk_id="crosswalk:fixture",
            captured_at="2026-08-25T00:00:00Z",
        ),
        "feasibility": build_planning_feasibility_record(
            [
                {
                    "provision_id": "provision:fixture",
                    "status": "unresolved",
                    "confidence": "unknown",
                    "evidence": ["archive:fixture:rule"],
                    "caveats": ["synthetic fixture"],
                }
            ],
            query_id="query:fixture",
            feature_ref="fixture:zone",
            captured_at="2026-08-25T00:00:00Z",
        ),
    }


def test_linkage_error_report_is_deterministic_and_empty_for_consistent_packet() -> None:
    report = build_planning_linkage_error_report(**_packets())
    assert report["status"] == "no-unresolved-references"
    assert report["finding_counts"] == {
        "missing_link_targets": 0,
        "unlinked_crosswalk_sources": 0,
        "missing_feasibility_provisions": 0,
    }
    assert report["total_finding_count"] == 0
    assert len(report["report_sha256"]) == 64
    assert report["promotion_allowed"] is False


def test_linkage_error_report_quantifies_unresolved_identifiers() -> None:
    packets = _packets()
    packets["linkage"] = dict(packets["linkage"])
    packets["linkage"]["records"] = [
        {
            **packets["linkage"]["records"][0],
            "provision_version_id": "plan:missing:2026",
        }
    ]
    packets["crosswalk"] = dict(packets["crosswalk"])
    packets["crosswalk"]["records"] = [
        {
            **packets["crosswalk"]["records"][0],
            "source_assertion": {"source_id": "feature:missing", "label": "Missing"},
        }
    ]
    packets["feasibility"] = dict(packets["feasibility"])
    packets["feasibility"]["rules"] = [
        {**packets["feasibility"]["rules"][0], "provision_id": "provision:missing"}
    ]
    report = build_planning_linkage_error_report(**packets)
    assert report["status"] == "quantified-unresolved"
    assert report["finding_counts"] == {
        "missing_link_targets": 1,
        "unlinked_crosswalk_sources": 1,
        "missing_feasibility_provisions": 1,
    }
    assert report["total_finding_count"] == 3


def test_linkage_error_report_rejects_unexpected_packet_types() -> None:
    packets = _packets()
    packets["structure"] = {**packets["structure"], "record_type": "wrong"}
    with pytest.raises(ValueError, match="unexpected record_type"):
        build_planning_linkage_error_report(**packets)


def test_linkage_error_report_validator_binds_categories_and_digest() -> None:
    report = build_planning_linkage_error_report(**_packets())
    assert validate_planning_linkage_error_report(report) == ()
    tampered = dict(report)
    tampered["total_finding_count"] = 1
    assert any(
        "total_finding_count" in error for error in validate_planning_linkage_error_report(tampered)
    )


def test_linkage_error_report_validator_rejects_promotion() -> None:
    report = build_planning_linkage_error_report(**_packets())
    report["promotion_allowed"] = True
    assert (
        "linkage error reports must prohibit promotion"
        in validate_planning_linkage_error_report(report)
    )


def test_linkage_error_report_validator_rejects_non_numeric_counts() -> None:
    report = build_planning_linkage_error_report(**_packets())
    report["finding_counts"]["missing_link_targets"] = "bad"
    errors = validate_planning_linkage_error_report(report)
    assert "finding_counts must contain non-negative integers" in errors


def test_linkage_error_report_validator_rejects_non_string_findings_without_raising() -> None:
    report = build_planning_linkage_error_report(**_packets())
    report["findings"]["missing_link_targets"] = [object()]
    errors = validate_planning_linkage_error_report(report)
    assert "findings.missing_link_targets must be a list of strings" in errors
