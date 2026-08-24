import pytest

from riopa_provenance.health_subgroups import HealthSubgroupError, equity_gap, subgroup_summary


def test_subgroup_summary_suppresses_small_cells() -> None:
    result = subgroup_summary(
        [{"group": "a", "value": 1}, {"group": "a", "value": 3}, {"group": "b", "value": 9}],
        group_field="group",
        value_field="value",
        minimum_cell_size=2,
    )
    assert result["rows"] == [
        {"group": "a", "count": 2, "suppressed": False, "mean": 2.0},
        {"group": "b", "count": 1, "suppressed": True, "mean": None},
    ]
    assert result["nonclaims"]


def test_equity_gap_is_descriptive() -> None:
    result = equity_gap({"rural": 0.2, "urban": 0.5})
    assert result["lowest_group"] == "rural"
    assert result["highest_group"] == "urban"
    assert result["gap"] == 0.3


def test_subgroup_controls_fail_closed() -> None:
    with pytest.raises(HealthSubgroupError, match="minimum cell size"):
        subgroup_summary(
            [{"group": "a", "value": 1}],
            group_field="group",
            value_field="value",
            minimum_cell_size=0,
        )
