from riopa_provenance.lineage import _identifier


def test_canonical_mapping_identity_is_supported() -> None:
    assert _identifier({"mapping_id": "urn:riopa:mapping:abc"}) == "urn:riopa:mapping:abc"


def test_canonical_version_identity_is_supported() -> None:
    assert _identifier({"version_id": "urn:riopa:entity:x:version:y"}) == (
        "urn:riopa:entity:x:version:y"
    )
