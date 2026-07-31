from __future__ import annotations

from pathlib import Path

import pytest

from riopa_provenance.publication import (
    PublicationError,
    _artifact_rights_decision,
    _media_type,
    _most_restrictive,
)


def test_publication_decision_precedence_is_fail_closed() -> None:
    assert _most_restrictive([]) == "review-required"
    assert _most_restrictive(["publish", "metadata-only"]) == "metadata-only"
    assert _most_restrictive(["publish", "review-required"]) == "review-required"
    assert _most_restrictive(["withhold", "review-required"]) == "review-required"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("artifact.parquet", "application/vnd.apache.parquet"),
        ("artifact.duckdb", "application/vnd.duckdb"),
        ("metadata.json", "application/json"),
    ],
)
def test_publication_media_types_are_deterministic(name: str, expected: str) -> None:
    assert _media_type(Path(name)) == expected


def test_publication_error_is_value_error() -> None:
    assert issubclass(PublicationError, ValueError)


def test_artifact_rights_override_precedes_source_and_global_fallback() -> None:
    records = {
        "source": {"redistribution_status": "open", "attribution": "Source"},
        "artifact-rights": {"redistribution_status": "metadata-only", "attribution": "Override"},
    }
    decision, basis, attribution = _artifact_rights_decision(
        {"rights_ref": "artifact-rights"}, ["source"], records, "allowed"
    )
    assert decision == "metadata-only"
    assert "artifact-rights" in " ".join(basis)
    assert attribution == ["Override"]
    decision, _, _ = _artifact_rights_decision(None, [], records, "allowed")
    assert decision == "publish"
    decision, _, _ = _artifact_rights_decision({"rights_ref": "missing"}, ["source"], records, "allowed")
    assert decision == "review-required"
