import pytest

from riopa_provenance.supermarket import SupermarketReferenceError, build_density_reference


def test_density_reference_is_deterministic_and_preserves_missing_coverage() -> None:
    report = build_density_reference(
        {"area-b": 2, "area-a": 1},
        {"area-a": 500.0, "area-b": 1_000.0, "area-c": 250.0},
    )
    assert [row["area"] for row in report["rows"]] == ["area-a", "area-b", "area-c"]
    assert report["rows"][0]["density_per_population"] == 2.0
    assert report["rows"][1]["density_per_population"] == 2.0
    assert report["rows"][2]["status"] == "missing"
    assert report["rows"][2]["density_per_population"] is None
    assert report["observed_area_count"] == 2
    assert report["missing_area_count"] == 1
    assert report["promotion_allowed"] is False


@pytest.mark.parametrize(
    ("counts", "population"),
    [({"a": -1}, {"a": 10.0}), ({"a": 1}, {"a": 0.0})],
)
def test_density_reference_rejects_invalid_values(
    counts: dict[str, int], population: dict[str, float]
) -> None:
    with pytest.raises(SupermarketReferenceError):
        build_density_reference(counts, population)
