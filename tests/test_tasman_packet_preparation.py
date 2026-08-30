from __future__ import annotations

import json
import runpy
from pathlib import Path

import pytest
import yaml

from riopa_provenance.hashing import sha256_file, sha256_json

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/prepare_tasman_public_packet.py"


@pytest.mark.parametrize("failure", ["missing", "ambiguous", "incomplete", "escape", "digest"])
def test_prepare_rejects_unbound_receipt(tmp_path: Path, failure: str) -> None:
    prepare = runpy.run_path(str(SCRIPT))["prepare"]
    store = tmp_path / "store"
    store.mkdir()
    capture_set = store / "capture-set.json"
    capture_set.write_text("{}")
    receipt = {
        "status": "incomplete" if failure == "incomplete" else "captured",
        "zones": {
            "manifest_path": "../escape.json" if failure == "escape" else "capture-set.json",
            "manifest_sha256": "0" * 64 if failure == "digest" else sha256_file(capture_set),
        },
    }
    receipt["semantic_sha256"] = sha256_json(receipt)
    if failure != "missing":
        (store / f"tasman-receipt-{receipt['semantic_sha256']}.json").write_text(
            json.dumps(receipt)
        )
    if failure == "ambiguous":
        (store / "tasman-receipt-other.json").write_text(json.dumps(receipt))
    with pytest.raises(ValueError):
        prepare(tmp_path)
    assert not (tmp_path / "public").exists()


def test_workflow_prepares_without_publication_credential_after_preservation() -> None:
    workflow = yaml.safe_load((ROOT / ".github/workflows/council-archive.yml").read_text())
    steps = workflow["jobs"]["capture"]["steps"]
    preparation = next(s for s in steps if s["name"].startswith("Prepare isolated"))
    preservation = next(s for s in steps if s["name"].startswith("Preserve and"))
    assert steps.index(preparation) > steps.index(preservation)
    assert (
        preparation["if"] == "matrix.source == 'tasman' && steps.resume.outputs.resumed != 'true'"
    )
    assert "env" not in preparation
    assert "prepare_tasman_public_packet.py" in preparation["run"]
