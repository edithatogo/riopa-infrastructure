import json
from pathlib import Path


def test_module_coverage_inventory_is_python314_and_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    inventory = json.loads(
        (root / "docs/module-coverage-inventory-20260825.json").read_text(encoding="utf-8")
    )
    assert inventory["status"] == "measured-python314-full-suite"
    assert inventory["runtime"] == "Python 3.14 only"
    assert inventory["threshold"]["branch_aware_percent"] == 90.0
    assert inventory["threshold"]["stable_gate_unchanged"] is True
    expected = sorted(
        f"src.riopa_provenance.{path.stem}" for path in (root / "src/riopa_provenance").glob("*.py")
    )
    observed = sorted(item["module"] for item in inventory["files"])
    assert observed == expected
    assert inventory["non_claims"]
