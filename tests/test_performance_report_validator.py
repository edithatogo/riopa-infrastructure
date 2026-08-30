from __future__ import annotations

from pathlib import Path

import pytest

from scripts.validate_performance_report import validate_report

ROOT = Path(__file__).resolve().parents[1]


def _report() -> dict[str, object]:
    run = __import__("runpy").run_path(str(ROOT / "examples/wp010-performance-benchmark/run.py"))
    return run["run"]()


def test_bounded_report_validates_and_preserves_projection_boundary() -> None:
    report = _report()
    assert validate_report(report) == ()


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("national", "classification"), "measured-national"),
        (("ingestion", "live_endpoint_contacted"), True),
        (("accessibility", "claim_supported"), True),
        (("scenarios", 0, "repetitions"), 2),
        (("scenarios", 0, "records_per_second"), 1),
    ],
)
def test_validator_rejects_promotion_or_contract_drift(
    path: tuple[object, ...], value: object
) -> None:
    report = _report()
    cursor: object = report
    for part in path[:-1]:
        cursor = cursor[part]  # type: ignore[index]
    cursor[path[-1]] = value  # type: ignore[index]
    assert validate_report(report)
