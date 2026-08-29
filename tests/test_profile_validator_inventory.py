import json
from pathlib import Path

from scripts.validate_profile_validator_inventory import validate

ROOT = Path(__file__).parents[1]


def test_profile_validator_inventory_is_complete_and_fail_closed() -> None:
    path = ROOT / "docs/wp006-profile-validator-inventory-20260829.json"
    assert validate(path) == []
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["promotion_allowed"] is False


def test_profile_validator_inventory_rejects_missing_claimed_profile(tmp_path: Path) -> None:
    value = json.loads((ROOT / "docs/wp006-profile-validator-inventory-20260829.json").read_text())
    value["profiles"].pop()
    path = tmp_path / "inventory.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    assert any("each required claimed profile" in error for error in validate(path))


def test_profile_validator_inventory_rejects_external_overclaim(tmp_path: Path) -> None:
    value = json.loads((ROOT / "docs/wp006-profile-validator-inventory-20260829.json").read_text())
    value["profiles"][0]["status"] = "externally-certified"
    del value["open_gates"]
    del value["nonclaims"]
    path = tmp_path / "inventory.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    errors = validate(path)
    assert any("outside the bounded status vocabulary" in error for error in errors)
    assert "open_gates must be a non-empty list" in errors
    assert "nonclaims must be a non-empty list" in errors
