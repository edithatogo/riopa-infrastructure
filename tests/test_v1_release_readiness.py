import json
from pathlib import Path

from scripts.validate_v1_feature_inventory import validate


def test_v1_readiness_baseline_is_fail_closed() -> None:
    record = json.loads(Path("docs/v1-release-readiness-baseline-20260801.json").read_text())
    assert record["release"] == "1.0.0"
    assert record["status"] == "blocked"
    assert record["promotion_ready"] is False
    assert len(record["blocking_gates"]) >= 5
    assert record["limitations"]


def test_v1_feature_freeze_inventory_matches_repository_without_overclaiming() -> None:
    root = Path(__file__).resolve().parents[1]
    inventory = json.loads((root / "docs/v1-feature-freeze-inventory-20260803.json").read_text())
    assert validate(inventory, root) == ()
    assert inventory["open_freeze_findings"]


def test_v1_normative_surface_inventory_is_complete_and_path_bound() -> None:
    root = Path(__file__).resolve().parents[1]
    inventory = json.loads((root / "docs/v1-normative-surface-inventory-20260825.json").read_text())
    assert inventory["status"] == "repository-inventory-complete-compatibility-diff-open"
    assert inventory["runtime"]["python"] == ">=3.14,<3.15"
    for relative in inventory["schemas"] + inventory["ontology_and_bindings"]:
        assert (root / relative).is_file(), relative
    for module in inventory["python_api"]["modules"]:
        assert (root / "src" / "riopa_provenance" / f"{module}.py").is_file(), module
    assert inventory["cli"]["command_groups"]
    assert inventory["file_formats"]
    assert inventory["open_findings"]
