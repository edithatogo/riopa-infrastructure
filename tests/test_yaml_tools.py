from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

from riopa_provenance.yaml_tools import load_yaml


def test_yaml12_loader_isolated_and_json_compatible(tmp_path: Path) -> None:
    before_yes = yaml.safe_load("value: yes\n")
    before_date = yaml.safe_load("value: 2026-07-20\n")
    source = tmp_path / "registry.yaml"
    source.write_text(
        "enabled: true\nlegacy_yes: yes\ndate_value: 2026-07-20\n",
        encoding="utf-8",
    )

    loaded = load_yaml(source)

    assert loaded == {
        "enabled": True,
        "legacy_yes": "yes",
        "date_value": "2026-07-20",
    }
    assert yaml.safe_load("value: yes\n") == before_yes == {"value": True}
    assert yaml.safe_load("value: 2026-07-20\n") == before_date == {"value": date(2026, 7, 20)}
