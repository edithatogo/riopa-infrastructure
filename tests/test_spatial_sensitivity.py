import pytest

from riopa_provenance.spatial_sensitivity import (
    SpatialSensitivityError,
    compare_revision_sensitivity,
)


def test_revision_sensitivity_retains_both_axes_and_range() -> None:
    result = compare_revision_sensitivity(
        [
            {
                "analysis_id": "a",
                "boundary_revision": "b1",
                "denominator_revision": "d1",
                "estimate": 10,
            },
            {
                "analysis_id": "a",
                "boundary_revision": "b2",
                "denominator_revision": "d1",
                "estimate": 12,
            },
            {
                "analysis_id": "a",
                "boundary_revision": "b1",
                "denominator_revision": "d2",
                "estimate": 11,
            },
        ]
    )
    assert result["status"] == "bounded-sensitive"
    assert result["minimum"] == 10.0
    assert result["maximum"] == 12.0
    assert result["range"] == 2.0
    assert result["promotion_allowed"] is False
    assert {item["denominator_revision"] for item in result["observations"]} == {"d1", "d2"}


@pytest.mark.parametrize(
    "observations",
    [
        [],
        [
            {
                "analysis_id": "a",
                "boundary_revision": "b",
                "denominator_revision": "d",
                "estimate": float("nan"),
            }
        ],
    ],
)
def test_revision_sensitivity_fails_closed(observations: object) -> None:
    with pytest.raises(SpatialSensitivityError):
        compare_revision_sensitivity(observations)  # type: ignore[arg-type]
