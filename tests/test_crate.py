import json
from pathlib import Path

from riopa_provenance.crate import build_research_object, build_ro_crate
from riopa_provenance.hashing import sha256_file


def test_ro_crate_projection(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    output = build_ro_crate(root / "examples/minimal/snapshot-manifest.json", tmp_path)
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["@context"] == "https://w3id.org/ro/crate/1.3/context"
    assert any(item.get("@id") == "./" for item in payload["@graph"])
    assert any(
        item.get("@id") == "urn:riopa:rights-inventory:nz-spatial-example:2026.07.18"
        for item in payload["@graph"]
    )


def test_research_object_is_complete_and_checksum_verified(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = root / "examples/minimal/snapshot-manifest.json"
    output = build_research_object(manifest, tmp_path / "research-object")

    expected = {
        "snapshot-manifest.json",
        "methods.md",
        "ro-crate-metadata.json",
        "rights-inventory.json",
        "quality-report.json",
        "bundle-manifest.json",
        "checksums.sha256",
    }
    assert expected <= {path.name for path in output.iterdir() if path.is_file()}

    for line in (output / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        assert sha256_file(output / relative) == digest


def test_research_object_build_is_content_deterministic(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = root / "examples/minimal/snapshot-manifest.json"
    left = build_research_object(manifest, tmp_path / "left")
    right = build_research_object(manifest, tmp_path / "right")
    assert (left / "checksums.sha256").read_bytes() == (right / "checksums.sha256").read_bytes()
