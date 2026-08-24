from __future__ import annotations

import json
from pathlib import Path


def test_repository_adoption_inventory_is_bounded_and_non_authoritative() -> None:
    root = Path(__file__).resolve().parents[1]
    inventory = json.loads((root / "docs/repository-adoption-inventory-20260825.json").read_text())
    repositories = inventory["repositories"]
    assert len(repositories) >= 8
    assert len({item["repository"] for item in repositories}) == len(repositories)
    assert all(item["repository"].startswith("edithatogo/") for item in repositories)
    assert "not claim" in inventory["nonclaims"][0]
    assert "native contract capture" in inventory["next_evidence"][0]
