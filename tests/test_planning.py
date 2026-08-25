import pytest

from riopa_provenance.planning import (
    PlanningLink,
    PlanVersion,
    ProvisionIdentity,
    build_plan_source_intake,
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
