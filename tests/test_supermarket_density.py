import pytest

from riopa_provenance.supermarket import (
    SupermarketReferenceError,
    build_density_reference,
    compare_declared_study_reference,
)


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


def test_declared_study_comparison_is_explicitly_not_reproduction() -> None:
    reference = {
        "record_type": "supermarket-density-reference",
        "comparison_fields": {
            "estimand": "count per area",
            "geography": "synthetic bounded region",
            "population_denominator": "synthetic population edition",
            "facility_definition": "public source assertion",
            "exclusions": ["missing geometry"],
            "missing_data_policy": "report missing, never zero",
        },
    }
    descriptor = {
        "record_type": "declared-motivating-study",
        "study_id": "study-not-supplied",
        "comparison_fields": dict(reference["comparison_fields"]),
    }

    report = compare_declared_study_reference(reference, descriptor)

    assert report["comparison_status"] == "descriptor-aligned-not-reproduced"
    assert report["matches"] == [
        "estimand",
        "geography",
        "population_denominator",
        "facility_definition",
        "exclusions",
        "missing_data_policy",
    ]
    assert report["promotion_allowed"] is False
    assert "does not reproduce" in report["nonclaims"][0]


def test_declared_study_comparison_preserves_mismatch_and_missing_fields() -> None:
    report = compare_declared_study_reference(
        {
            "record_type": "supermarket-density-reference",
            "comparison_fields": {"estimand": "reference count"},
        },
        {
            "record_type": "declared-motivating-study",
            "study_id": "declared-only",
            "comparison_fields": {"estimand": "study rate", "geography": "region"},
        },
    )

    assert report["comparison_status"] == "descriptor-mismatch-or-incomplete"
    assert report["mismatches"] == ["estimand"]
    assert report["missing_reference_fields"] == [
        "geography",
        "population_denominator",
        "facility_definition",
        "exclusions",
        "missing_data_policy",
    ]
    assert report["missing_descriptor_fields"] == [
        "population_denominator",
        "facility_definition",
        "exclusions",
        "missing_data_policy",
    ]


@pytest.mark.parametrize("record_type", ["wrong", None])
def test_declared_study_comparison_rejects_untyped_records(record_type: object) -> None:
    with pytest.raises(SupermarketReferenceError):
        compare_declared_study_reference(
            {"record_type": record_type},
            {"record_type": "declared-motivating-study"},
        )
