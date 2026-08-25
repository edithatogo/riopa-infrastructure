from riopa_provenance.planning import (
    build_feature_provision_linkage,
    build_plan_source_intake,
    build_planning_concept_crosswalk,
    build_planning_feasibility_record,
    build_rule_structure_record,
)


def _validate_declared_structure(prefix: str, structure_sha256: str) -> dict[str, object]:
    """Exercise the same bounded contracts for a structurally different fixture."""
    intake = build_plan_source_intake(
        [
            {
                "plan_id": f"plan:{prefix}",
                "version_id": f"plan:{prefix}:2024",
                "source_ref": f"archive:{prefix}:plan",
                "locator": f"archive:{prefix}:plan#root",
                "document_sha256": "a" * 64,
                "structure_sha256": structure_sha256,
                "terms_status": "declared-public",
                "rights_status": "unverified",
            }
        ],
        intake_id=f"intake:{prefix}",
        captured_at="2026-08-25T00:00:00Z",
    )
    structure = build_rule_structure_record(
        [
            {"provision_id": f"{prefix}:root"},
            {
                "provision_id": f"{prefix}:exception",
                "parent_provision_id": f"{prefix}:root",
                "exception_refs": [f"{prefix}:root"],
            },
        ],
        structure_id=f"structure:{prefix}",
        captured_at="2026-08-25T00:00:00Z",
    )
    linkage = build_feature_provision_linkage(
        [
            {
                "feature_id": f"{prefix}:zone",
                "feature_kind": "zone",
                "feature_source_ref": f"archive:{prefix}:zone",
                "provision_version_id": f"plan:{prefix}:2024",
                "evidence": [f"archive:{prefix}:rule"],
                "confidence": "unknown",
            }
        ],
        linkage_id=f"linkage:{prefix}",
        captured_at="2026-08-25T00:00:00Z",
    )
    crosswalk = build_planning_concept_crosswalk(
        [
            {
                "source_id": f"{prefix}:zone",
                "source_label": "Declared zone",
                "canonical_id": "urn:riopa:concept:planning:residential",
                "method": "declared-reference",
                "confidence": "unknown",
                "reviewer": "agent-panel:unreviewed",
                "valid_from": "2024-01-01",
                "evidence": [f"archive:{prefix}:zone"],
            }
        ],
        crosswalk_id=f"crosswalk:{prefix}",
        captured_at="2026-08-25T00:00:00Z",
    )
    feasibility = build_planning_feasibility_record(
        [
            {
                "provision_id": f"{prefix}:root",
                "status": "unresolved",
                "confidence": "unknown",
                "evidence": [f"archive:{prefix}:rule"],
                "caveats": ["synthetic fixture; operative status not verified"],
            }
        ],
        query_id=f"query:{prefix}",
        feature_ref=f"{prefix}:zone",
        captured_at="2026-08-25T00:00:00Z",
    )
    return {
        "intake": intake,
        "structure": structure,
        "linkage": linkage,
        "crosswalk": crosswalk,
        "feasibility": feasibility,
    }


def test_two_structurally_different_reference_council_fixtures_validate() -> None:
    district = _validate_declared_structure("district", "a" * 64)
    hybrid = _validate_declared_structure("hybrid", "b" * 64)
    assert (
        district["intake"]["records"][0]["structure_sha256"]
        != hybrid["intake"]["records"][0]["structure_sha256"]
    )
    for packet in (district, hybrid):
        assert packet["structure"]["promotion_allowed"] is False
        assert packet["linkage"]["promotion_allowed"] is False
        assert packet["crosswalk"]["status"] == "bounded-unreviewed"
        assert packet["feasibility"]["decision_status"] == "unresolved"
