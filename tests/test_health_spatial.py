import pytest

from riopa_provenance.health_spatial import (
    HealthSpatialError,
    descriptive_mapping,
    moran_i,
    multilevel_ecological_summary,
)


def test_descriptive_mapping_is_deterministic_and_bounded() -> None:
    result = descriptive_mapping({"b": 1, "a": 2}, {"b": 4, "a": 5})
    assert [row["area"] for row in result["rows"]] == ["a", "b"]
    assert result["rows"][0]["rate"] == 0.4
    assert result["nonclaims"]


def test_moran_i_requires_closed_symmetric_graph() -> None:
    result = moran_i({"a": 1.0, "b": 1.0, "c": 3.0}, {"a": ["b"], "b": ["a", "c"], "c": ["b"]})
    assert result["area_count"] == 3
    assert result["edge_count"] == 4
    assert result["statistic"] < 0
    with pytest.raises(HealthSpatialError, match="symmetric"):
        moran_i({"a": 1.0, "b": 2.0}, {"a": ["b"], "b": []})


def test_ecological_summary_rejects_invalid_outcome() -> None:
    result = multilevel_ecological_summary(
        [{"region": "north", "value": 1}, {"region": "north", "value": 3}],
        group_field="region",
        value_field="value",
    )
    assert result["groups"] == [{"group": "north", "count": 2, "mean": 2.0}]
    with pytest.raises(HealthSpatialError, match="finite"):
        multilevel_ecological_summary(
            [{"region": "north", "value": float("nan")}], group_field="region", value_field="value"
        )
