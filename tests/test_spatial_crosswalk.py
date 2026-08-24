from __future__ import annotations

import pytest

from riopa_provenance.spatial_crosswalk import (
    CrosswalkError,
    interpolate_population,
    validate_boundary_crosswalk,
)


def _crosswalk() -> list[dict[str, object]]:
    return [
        {
            "source_id": "s1",
            "target_id": "t1",
            "weight": 0.25,
            "source_revision": "s-v1",
            "target_revision": "t-v1",
        },
        {
            "source_id": "s1",
            "target_id": "t2",
            "weight": 0.75,
            "source_revision": "s-v1",
            "target_revision": "t-v1",
        },
        {
            "source_id": "s2",
            "target_id": "t2",
            "weight": 1.0,
            "source_revision": "s-v1",
            "target_revision": "t-v1",
        },
    ]


def test_crosswalk_validates_and_interpolates_with_revision_binding() -> None:
    crosswalk = _crosswalk()
    assert validate_boundary_crosswalk(crosswalk) == ()
    result = interpolate_population({"s1": 100.0, "s2": 40.0}, crosswalk)
    assert result["values"] == {"t1": 25.0, "t2": 115.0}
    assert result["revision_pairs"] == ["s-v1->t-v1"]
    assert result["promotion_allowed"] is False


def test_crosswalk_rejects_unbalanced_weights_and_missing_sources() -> None:
    crosswalk = _crosswalk()
    crosswalk[0]["weight"] = 0.2
    assert any("sum to 1" in error for error in validate_boundary_crosswalk(crosswalk))
    with pytest.raises(CrosswalkError, match="no crosswalk rows"):
        interpolate_population({"s1": 1.0, "s2": 1.0, "s3": 1.0}, _crosswalk())
