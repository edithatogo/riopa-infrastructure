import json
import shutil
from pathlib import Path

from riopa_provenance.hashing import sha256_json
from riopa_provenance.validation import validate_manifest_closure


def _copy_example(tmp_path: Path) -> Path:
    root = Path(__file__).resolve().parents[1]
    target = tmp_path / "minimal"
    shutil.copytree(root / "examples/minimal", target)
    return target


def test_tampered_event_breaks_integrity(tmp_path: Path) -> None:
    target = _copy_example(tmp_path)
    event_path = target / "provenance-event-transformation.json"
    event = json.loads(event_path.read_text(encoding="utf-8"))
    event["parameters"]["target_crs"] = "EPSG:4326"
    event_path.write_text(json.dumps(event, indent=2) + "\n", encoding="utf-8")

    result = validate_manifest_closure(target / "snapshot-manifest.json")
    assert not result.valid
    assert any("hash mismatch" in error for error in result.errors)


def test_missing_reference_breaks_closure(tmp_path: Path) -> None:
    target = _copy_example(tmp_path)
    (target / "rights-inventory.json").unlink()
    result = validate_manifest_closure(target / "snapshot-manifest.json")
    assert not result.valid
    assert any("missing referenced file" in error for error in result.errors)


def test_reference_escape_is_rejected_even_with_valid_manifest_hash(tmp_path: Path) -> None:
    target = _copy_example(tmp_path)
    manifest_path = target / "snapshot-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["domain_records"] = ["../outside.json"]
    manifest["manifest_sha256"] = sha256_json(manifest, omit_keys={"manifest_sha256"})
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    result = validate_manifest_closure(manifest_path)
    assert not result.valid
    assert any("escapes bundle root" in error for error in result.errors)
