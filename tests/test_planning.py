import pytest

from riopa_provenance.planning import PlanningLink, PlanVersion, ProvisionIdentity


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
