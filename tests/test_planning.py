import pytest

from riopa_provenance.planning import (
    PlanningLink,
    PlanVersion,
    ProvisionIdentity,
    build_feature_provision_linkage,
    build_plan_source_intake,
    build_provision_extraction_record,
    build_rule_structure_record,
)


def test_planning_identities_preserve_version_anchor_and_non_authority() -> None:
    plan = PlanVersion(
        plan_id="plan:wcc",
        version_id="plan:wcc:2024",
        title="Bounded district plan",
        source_ref="archive:plan-1",
        legal_status="operative",
        valid_from="2024-01-01",
    )
    provision = ProvisionIdentity(
        provision_id="provision:wcc:1",
        plan_version_id=plan.version_id,
        chapter="Chapter 1",
        citation="Rule 1.1",
        text_ref="archive:plan-1#rule-1-1",
    )
    link = PlanningLink(
        link_id="link:zone-rule-1",
        source_ref="zone:wcc:residential",
        target_ref=provision.provision_id,
        relation="implements",
        confidence="medium",
        evidence=("archive:plan-1#rule-1-1",),
        uncertainty="manual extraction; operative status not independently verified",
    )
    assert provision.plan_version_id == plan.version_id
    assert link.as_dict()["promotion_allowed"] is False


def test_plan_source_intake_is_digest_bound_and_preserves_rights_fields() -> None:
    records = [
        {
            "plan_id": "plan:wcc",
            "version_id": "plan:wcc:2024",
            "source_ref": "archive:wcc-plan",
            "locator": "https://example.test/wcc-plan",
            "document_sha256": "a" * 64,
            "structure_sha256": "b" * 64,
            "terms_status": "review-required",
            "rights_status": "public-candidate",
        }
    ]
    intake = build_plan_source_intake(
        records, intake_id="intake-1", captured_at="2026-08-25T00:00:00Z"
    )
    assert intake["status"] == "archived-declared-candidate"
    assert len(intake["records_sha256"]) == 64
    assert intake["records"][0]["rights_status"] == "public-candidate"
    assert intake["promotion_allowed"] is False
    with pytest.raises(ValueError, match="SHA-256"):
        build_plan_source_intake(
            [{**records[0], "document_sha256": "not-a-digest"}],
            intake_id="intake-1",
            captured_at="now",
        )


def test_provision_extraction_requires_hashes_and_ai_tool_identity() -> None:
    record = build_provision_extraction_record(
        provision_id="provision:wcc:1",
        source_ref="archive:plan#rule-1",
        text_sha256="a" * 64,
        input_sha256="b" * 64,
        method="ai-assisted",
        extracted_fields={"citation": "Rule 1"},
        uncertainty="text anchor preserved; legal status not assessed",
        tool_identity="agent-panel:extractor-v1",
    )
    assert record["method"] == "ai-assisted"
    assert record["review_status"] == "unreviewed"
    assert record["promotion_allowed"] is False
    with pytest.raises(ValueError, match="tool_identity"):
        build_provision_extraction_record(
            provision_id="provision:wcc:1",
            source_ref="archive:plan#rule-1",
            text_sha256="a" * 64,
            input_sha256="b" * 64,
            method="ai-assisted",
            extracted_fields={"citation": "Rule 1"},
            uncertainty="unreviewed",
        )


def test_feature_provision_linkage_is_sorted_digest_bound_and_non_authoritative() -> None:
    linkage = build_feature_provision_linkage(
        [
            {
                "feature_id": "zone:b",
                "feature_kind": "zone",
                "feature_source_ref": "archive:plan#zone-b",
                "provision_version_id": "plan:wcc:2024",
                "evidence": ["archive:plan#rule-2", "archive:plan#rule-2"],
                "confidence": "medium",
            },
            {
                "feature_id": "overlay:a",
                "feature_kind": "overlay",
                "feature_source_ref": "archive:plan#overlay-a",
                "provision_version_id": "plan:wcc:2024",
                "evidence": ["archive:plan#rule-1"],
                "confidence": "unknown",
            },
        ],
        linkage_id="linkage-1",
        captured_at="2026-08-25T00:00:00Z",
    )
    assert [row["feature_id"] for row in linkage["records"]] == ["overlay:a", "zone:b"]
    assert linkage["records"][1]["evidence"] == ["archive:plan#rule-2"]
    assert len(linkage["records_sha256"]) == 64
    assert linkage["promotion_allowed"] is False
    with pytest.raises(ValueError, match="feature_kind"):
        build_feature_provision_linkage(
            [
                {
                    "feature_id": "bad",
                    "feature_kind": "parcel",
                    "feature_source_ref": "archive:bad",
                    "provision_version_id": "plan:wcc:2024",
                    "evidence": ["archive:bad"],
                    "confidence": "low",
                }
            ],
            linkage_id="linkage-1",
            captured_at="now",
        )


def test_rule_structure_preserves_hierarchy_exceptions_and_unresolved_state() -> None:
    record = build_rule_structure_record(
        [
            {
                "provision_id": "rule:child",
                "parent_provision_id": "rule:root",
                "exception_refs": ["rule:exception"],
                "combined_with": ["rule:other"],
                "unresolved_reasons": ["operative status not captured"],
            },
            {"provision_id": "rule:root"},
        ],
        structure_id="structure-1",
        captured_at="2026-08-25T00:00:00Z",
    )
    assert [row["provision_id"] for row in record["records"]] == ["rule:child", "rule:root"]
    assert record["records"][0]["resolution_status"] == "unresolved"
    assert record["promotion_allowed"] is False
    assert len(record["records_sha256"]) == 64
    with pytest.raises(ValueError, match="own parent"):
        build_rule_structure_record(
            [{"provision_id": "rule:self", "parent_provision_id": "rule:self"}],
            structure_id="structure-1",
            captured_at="now",
        )


@pytest.mark.parametrize(
    "factory",
    [
        lambda: PlanVersion("", "v1", "title", "source"),
        lambda: PlanVersion(
            "p", "v1", "title", "source", valid_from="2025-01-01", valid_to="2024-01-01"
        ),
        lambda: ProvisionIdentity("p", "v", "", "citation", "ref"),
        lambda: PlanningLink("l", "s", "t", "crosswalk", "low", (), "unknown"),
    ],
)
def test_planning_contract_rejects_incomplete_or_reversed_records(factory: object) -> None:
    with pytest.raises((ValueError, TypeError)):
        factory()  # type: ignore[operator]
