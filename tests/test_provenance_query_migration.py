from pathlib import Path


def test_provenance_query_migration_guidance_is_bounded_and_versioned() -> None:
    root = Path(__file__).resolve().parents[1]
    guidance = (root / "docs/provenance-query-migration-guidance-20260825.md").read_text(
        encoding="utf-8"
    )
    assert "LineageQuery` version `1.0.0" in guidance
    assert "new major contract version" in guidance
    assert "remote authorization" in guidance
    assert "release approval" in guidance
