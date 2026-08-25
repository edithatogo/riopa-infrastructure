from pathlib import Path

from scripts.validate_canonical_shacl import validate_fixture

ROOT = Path(__file__).parents[1]


def test_pinned_shacl_runtime_validates_the_digest_bound_golden_fixture() -> None:
    report = validate_fixture(
        ROOT / "fixtures/canonical-crosswalk-golden.json",
        ROOT / "docs/ontology/canonical-crosswalk.shacl.ttl",
    )
    assert report["conforms"] is True
    assert report["fixture_sha256"]
    assert report["shape_sha256"]
    assert report["promotion_allowed"] is False
