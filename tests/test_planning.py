import pytest

from riopa_provenance.planning import (
    PlanningLink,
    PlanVersion,
    ProvisionIdentity,
    build_feature_provision_linkage,
    build_plan_source_intake,
    build_planning_concept_crosswalk,
    build_planning_feasibility_record,
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


def test_planning_concept_crosswalk_is_digest_bound_and_preserves_source_assertions() -> None:
    packet = build_planning_concept_crosswalk(
        [
            {
                "source_id": "council:zone:residential",
                "source_label": "Residential zone",
                "canonical_id": "urn:riopa:concept:planning:residential",
                "method": "declared-reference",
                "confidence": "unknown",
                "reviewer": "agent-panel:unreviewed",
                "valid_from": "2024-01-01",
                "evidence": ["archive:plan#zone-residential"],
            }
        ],
        crosswalk_id="crosswalk-1",
        captured_at="2026-08-25T00:00:00Z",
    )
    assert packet["records"][0]["source_assertion"]["label"] == "Residential zone"
    assert packet["status"] == "bounded-unreviewed"
    assert packet["promotion_allowed"] is False
    assert len(packet["records_sha256"]) == 64
    with pytest.raises(ValueError, match="invalid planning concept"):
        build_planning_concept_crosswalk(
            [
                {
                    "source_id": "source",
                    "source_label": "x",
                    "canonical_id": "not-canonical",
                    "method": "manual",
                    "confidence": "medium",
                    "reviewer": "agent",
                    "valid_from": "2024-01-01",
                }
            ],
            crosswalk_id="crosswalk-1",
            captured_at="now",
        )


def test_planning_feasibility_preserves_citations_and_fails_closed_on_conflict() -> None:
    record = build_planning_feasibility_record(
        [
            {
                "provision_id": "rule:permitted",
                "status": "permitted",
                "confidence": "medium",
                "evidence": ["archive:plan#rule-1"],
                "caveats": ["operative status not independently verified"],
            },
            {
                "provision_id": "rule:exception",
                "status": "prohibited",
                "confidence": "unknown",
                "evidence": ["archive:plan#rule-2"],
                "caveats": ["exception scope unresolved"],
            },
        ],
        query_id="query-1",
        feature_ref="zone:wcc:residential",
        captured_at="2026-08-25T00:00:00Z",
    )
    assert record["decision_status"] == "unresolved"
    assert record["authority_required"] is True
    assert record["promotion_allowed"] is False
    assert len(record["rules_sha256"]) == 64
    with pytest.raises(ValueError, match="evidence must not be empty"):
        build_planning_feasibility_record(
            [
                {
                    "provision_id": "rule:missing",
                    "status": "permitted",
                    "confidence": "unknown",
                    "evidence": [],
                    "caveats": [],
                }
            ],
            query_id="query-1",
            feature_ref="zone:wcc:residential",
            captured_at="now",
        )


def test_planning_feasibility_decision_statuses_are_deterministic() -> None:
    base = {
        "provision_id": "rule:one",
        "confidence": "high",
        "evidence": ["archive:rule"],
        "caveats": [],
    }
    for status, expected in (
        ("prohibited", "prohibited"),
        ("discretionary", "discretionary"),
        ("permitted", "permitted"),
        ("unresolved", "unresolved"),
    ):
        result = build_planning_feasibility_record(
            [{**base, "status": status}],
            query_id="query-status",
            feature_ref="feature:one",
            captured_at="now",
        )
        assert result["decision_status"] == expected


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (
            lambda: build_planning_feasibility_record(
                [], query_id="q", feature_ref="f", captured_at="now"
            ),
            "rules must be non-empty",
        ),
        (
            lambda: build_planning_feasibility_record(
                ["bad"], query_id="q", feature_ref="f", captured_at="now"
            ),
            "rules must be objects",
        ),
        (
            lambda: build_planning_feasibility_record(
                [{"provision_id": "p"}], query_id="q", feature_ref="f", captured_at="now"
            ),
            "missing fields",
        ),
        (
            lambda: build_planning_feasibility_record(
                [
                    {
                        "provision_id": "p",
                        "status": "bad",
                        "confidence": "high",
                        "evidence": ["e"],
                        "caveats": [],
                    }
                ],
                query_id="q",
                feature_ref="f",
                captured_at="now",
            ),
            "status is invalid",
        ),
        (
            lambda: build_planning_feasibility_record(
                [
                    {
                        "provision_id": "p",
                        "status": "permitted",
                        "confidence": "bad",
                        "evidence": ["e"],
                        "caveats": [],
                    }
                ],
                query_id="q",
                feature_ref="f",
                captured_at="now",
            ),
            "confidence is invalid",
        ),
        (
            lambda: build_planning_feasibility_record(
                [
                    {
                        "provision_id": "p",
                        "status": "permitted",
                        "confidence": "high",
                        "evidence": "e",
                        "caveats": [],
                    }
                ],
                query_id="q",
                feature_ref="f",
                captured_at="now",
            ),
            "evidence must be a list",
        ),
        (
            lambda: build_planning_feasibility_record(
                [
                    {
                        "provision_id": "p",
                        "status": "permitted",
                        "confidence": "high",
                        "evidence": ["e"],
                        "caveats": [1],
                    }
                ],
                query_id="q",
                feature_ref="f",
                captured_at="now",
            ),
            "caveats must be a list",
        ),
    ],
)
def test_planning_feasibility_rejects_malformed_records(factory: object, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        factory()  # type: ignore[operator]


def test_planning_feasibility_rejects_duplicate_and_empty_identity() -> None:
    rule = {
        "provision_id": "p",
        "status": "permitted",
        "confidence": "high",
        "evidence": ["e"],
        "caveats": [],
    }
    with pytest.raises(ValueError, match="unique"):
        build_planning_feasibility_record(
            [rule, rule], query_id="q", feature_ref="f", captured_at="now"
        )
    with pytest.raises(ValueError, match="query_id"):
        build_planning_feasibility_record([rule], query_id="", feature_ref="f", captured_at="now")


def test_planning_concept_crosswalk_rejects_empty_fields_and_evidence() -> None:
    base = {
        "source_id": "source",
        "source_label": "label",
        "canonical_id": "urn:riopa:concept:x",
        "method": "manual",
        "confidence": "medium",
        "reviewer": "agent",
        "valid_from": "2024-01-01",
        "evidence": ["archive:source"],
    }
    with pytest.raises(ValueError, match="crosswalk_id"):
        build_planning_concept_crosswalk([base], crosswalk_id="", captured_at="now")
    with pytest.raises(ValueError, match="concepts must be non-empty"):
        build_planning_concept_crosswalk([], crosswalk_id="id", captured_at="now")
    with pytest.raises(ValueError, match="non-empty string"):
        build_planning_concept_crosswalk(
            [{**base, "source_label": ""}], crosswalk_id="id", captured_at="now"
        )
    with pytest.raises(ValueError, match="evidence must be a list"):
        build_planning_concept_crosswalk(
            [{**base, "evidence": "archive:source"}], crosswalk_id="id", captured_at="now"
        )
    with pytest.raises(ValueError, match="objects"):
        build_planning_concept_crosswalk(["bad"], crosswalk_id="id", captured_at="now")  # type: ignore[list-item]
    with pytest.raises(ValueError, match="missing fields"):
        build_planning_concept_crosswalk(
            [{"source_id": "source"}], crosswalk_id="id", captured_at="now"
        )


def test_planning_identity_and_intake_negative_paths() -> None:
    with pytest.raises(ValueError, match="Invalid isoformat"):
        PlanVersion("p", "v", "title", "source", valid_from="not-a-date")
    with pytest.raises(ValueError, match="Invalid isoformat"):
        PlanVersion("p", "v", "title", "source", valid_to="not-a-date")
    with pytest.raises(ValueError, match="identity"):
        PlanningLink("", "s", "t", "contains", "low", ("e",), "uncertain")
    with pytest.raises(ValueError, match="evidence"):
        PlanningLink("l", "s", "t", "contains", "low", ("",), "uncertain")
    valid = {
        "plan_id": "p",
        "version_id": "v",
        "source_ref": "s",
        "locator": "l",
        "document_sha256": "a" * 64,
        "structure_sha256": "b" * 64,
        "terms_status": "candidate",
        "rights_status": "candidate",
    }
    with pytest.raises(ValueError, match="intake_id"):
        build_plan_source_intake([valid], intake_id="", captured_at="now")
    with pytest.raises(ValueError, match="intake_id"):
        build_plan_source_intake([valid], intake_id="id", captured_at="")
    with pytest.raises(ValueError, match="records must be non-empty"):
        build_plan_source_intake([], intake_id="id", captured_at="now")
    with pytest.raises(ValueError, match="objects"):
        build_plan_source_intake(["bad"], intake_id="id", captured_at="now")  # type: ignore[list-item]
    with pytest.raises(ValueError, match="missing fields"):
        build_plan_source_intake([{"version_id": "v"}], intake_id="id", captured_at="now")
    with pytest.raises(ValueError, match="unique"):
        build_plan_source_intake([valid, valid], intake_id="id", captured_at="now")
    with pytest.raises(ValueError, match="unique"):
        build_plan_source_intake([{**valid, "version_id": ""}], intake_id="id", captured_at="now")
    with pytest.raises(ValueError, match="document_sha256"):
        build_plan_source_intake(
            [{**valid, "document_sha256": "bad"}], intake_id="id", captured_at="now"
        )


def test_planning_extraction_and_linkage_negative_paths() -> None:
    with pytest.raises(ValueError, match="provision_id"):
        build_provision_extraction_record(
            provision_id="",
            source_ref="s",
            text_sha256="a" * 64,
            input_sha256="b" * 64,
            method="manual",
            extracted_fields={"x": 1},
            uncertainty="u",
        )
    with pytest.raises(ValueError, match="text_sha256"):
        build_provision_extraction_record(
            provision_id="p",
            source_ref="s",
            text_sha256="bad",
            input_sha256="b" * 64,
            method="manual",
            extracted_fields={"x": 1},
            uncertainty="u",
        )
    with pytest.raises(ValueError, match="extracted_fields"):
        build_provision_extraction_record(
            provision_id="p",
            source_ref="s",
            text_sha256="a" * 64,
            input_sha256="b" * 64,
            method="manual",
            extracted_fields={},
            uncertainty="u",
        )
    with pytest.raises(ValueError, match="tool_identity"):
        build_provision_extraction_record(
            provision_id="p",
            source_ref="s",
            text_sha256="a" * 64,
            input_sha256="b" * 64,
            method="ai-assisted",
            extracted_fields={"x": 1},
            uncertainty="u",
        )
    with pytest.raises(ValueError, match="linkage_id"):
        build_feature_provision_linkage([], linkage_id="", captured_at="now")
    with pytest.raises(ValueError, match="features must be non-empty"):
        build_feature_provision_linkage([], linkage_id="id", captured_at="now")
    with pytest.raises(ValueError, match="objects"):
        build_feature_provision_linkage(["bad"], linkage_id="id", captured_at="now")  # type: ignore[list-item]
    with pytest.raises(ValueError, match="missing fields"):
        build_feature_provision_linkage([{"feature_id": "f"}], linkage_id="id", captured_at="now")


def test_planning_linkage_and_structure_reject_invalid_references() -> None:
    feature = {
        "feature_id": "f",
        "feature_kind": "zone",
        "feature_source_ref": "source",
        "provision_version_id": "version",
        "evidence": ["e"],
        "confidence": "medium",
    }
    with pytest.raises(ValueError, match="unique"):
        build_feature_provision_linkage([feature, feature], linkage_id="id", captured_at="now")
    for key, value, message in (
        ("feature_id", "", "unique"),
        ("feature_kind", "bad", "feature_kind"),
        ("feature_source_ref", "", "feature_source_ref"),
        ("provision_version_id", "", "provision_version_id"),
        ("evidence", "e", "evidence"),
        ("confidence", "bad", "confidence"),
    ):
        with pytest.raises(ValueError, match=message):
            build_feature_provision_linkage(
                [{**feature, key: value}], linkage_id="id", captured_at="now"
            )
    with pytest.raises(ValueError, match="evidence entries"):
        build_feature_provision_linkage(
            [{**feature, "evidence": [""]}], linkage_id="id", captured_at="now"
        )
    with pytest.raises(ValueError, match="structure_id"):
        build_rule_structure_record([{"provision_id": "p"}], structure_id="", captured_at="now")
    with pytest.raises(ValueError, match="provisions must be non-empty"):
        build_rule_structure_record([], structure_id="id", captured_at="now")
    with pytest.raises(ValueError, match="objects"):
        build_rule_structure_record(["bad"], structure_id="id", captured_at="now")  # type: ignore[list-item]
    with pytest.raises(ValueError, match="unique"):
        build_rule_structure_record(
            [{"provision_id": "p"}, {"provision_id": "p"}], structure_id="id", captured_at="now"
        )
    with pytest.raises(ValueError, match="parent_provision_id"):
        build_rule_structure_record(
            [{"provision_id": "p", "parent_provision_id": 1}], structure_id="id", captured_at="now"
        )
    with pytest.raises(ValueError, match="exception_refs"):
        build_rule_structure_record(
            [{"provision_id": "p", "exception_refs": "bad"}], structure_id="id", captured_at="now"
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
