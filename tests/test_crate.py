import json
import shutil
from pathlib import Path

import pytest

from riopa_provenance.crate import (
    _citation_cff,
    _datacite_metadata,
    _parse_checksums,
    build_research_object,
    build_ro_crate,
    validate_provenance_projections,
    verify_research_object,
)
from riopa_provenance.hashing import sha256_file


def test_ro_crate_projection(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    output = build_ro_crate(root / "examples/minimal/snapshot-manifest.json", tmp_path)
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["@context"] == "https://w3id.org/ro/crate/1.2/context"
    assert any(item.get("@id") == "./" for item in payload["@graph"])
    assert any(
        item.get("@id") == "urn:riopa:rights-inventory:nz-spatial-example:2026.07.18"
        for item in payload["@graph"]
    )
    root_entity = next(item for item in payload["@graph"] if item.get("@id") == "./")
    assert root_entity["conformsTo"] == {"@id": "https://w3id.org/ro/crate/1.2"}
    assert all("@id" in value and len(value) == 1 for value in root_entity["hasPart"])
    assert all(
        "@id" in value and len(value) == 1
        for item in payload["@graph"]
        for value in (
            item.get("additionalProperty", [])
            if isinstance(item.get("additionalProperty", []), list)
            else [item["additionalProperty"]]
        )
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


def test_provenance_projection_contract_is_bounded_and_fail_closed(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    output = build_research_object(root / "examples/minimal/snapshot-manifest.json", tmp_path)
    prov = json.loads((output / "prov.jsonld").read_text(encoding="utf-8"))
    lineage = json.loads((output / "openlineage-events.json").read_text(encoding="utf-8"))
    assert validate_provenance_projections(prov, lineage) == ()
    lineage["events"][0]["eventType"] = "INVALID"
    assert any("eventType" in error for error in validate_provenance_projections(prov, lineage))


def test_research_object_build_rejects_source_output_and_invalid_closure(
    tmp_path: Path,
) -> None:
    root = Path(__file__).resolve().parents[1]
    source = tmp_path / "source"
    shutil.copytree(root / "examples/minimal", source)
    manifest = source / "snapshot-manifest.json"
    with pytest.raises(ValueError, match="must differ"):
        build_research_object(manifest, source)

    (source / "rights-inventory.json").unlink()
    with pytest.raises(ValueError, match="manifest closure failed"):
        build_research_object(manifest, tmp_path / "output")


def test_citation_projections_cover_optional_and_single_name_fields() -> None:
    manifest = {
        "title": "Dataset",
        "snapshot_version": "1.2.3",
        "created_at": "2026-07-31T00:00:00Z",
        "description": "Evidence",
        "citation": {
            "creators": ["Prince", "Ada Lovelace"],
            "publisher": "RIOPA",
            "publication_year": 2026,
            "doi": "10.1234/example",
            "repository": "https://example.test/repo",
            "licence": "CC-BY-4.0",
        },
    }
    citation = _citation_cff(manifest)
    assert citation["authors"] == [
        {"name": "Prince"},
        {"given-names": "Ada", "family-names": "Lovelace"},
    ]
    assert citation["doi"] == "10.1234/example"
    assert citation["repository-code"] == "https://example.test/repo"
    assert citation["license"] == "CC-BY-4.0"
    attributes = _datacite_metadata(manifest)["data"]["attributes"]
    assert attributes["doi"] == "10.1234/example"
    assert attributes["url"] == "https://example.test/repo"


def test_checksum_parser_reports_all_malformed_input(tmp_path: Path) -> None:
    checksums = tmp_path / "checksums.sha256"
    digest = "a" * 64
    checksums.write_text(
        "\n".join(
            ["", "not-a-record", f"z{digest[1:]}  bad", f"{digest}  same", f"{digest}  same"]
        ),
        encoding="utf-8",
    )
    errors: list[str] = []
    assert _parse_checksums(checksums, errors) == {"same": digest}
    assert any("invalid checksum line" in error for error in errors)
    assert any("invalid SHA-256" in error for error in errors)
    assert any("duplicate checksum" in error for error in errors)

    directory = tmp_path / "directory"
    directory.mkdir()
    errors = []
    assert _parse_checksums(directory, errors) == {}
    assert any("could not read" in error for error in errors)


def _built_object(tmp_path: Path) -> Path:
    root = Path(__file__).resolve().parents[1]
    return build_research_object(
        root / "examples/minimal/snapshot-manifest.json", tmp_path / "research-object"
    )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("remove-required", "missing required research-object file"),
        ("bad-bundle-json", "could not validate bundle manifest"),
        ("bad-bundle-entry", "entry without a string path"),
        ("duplicate-bundle-entry", "duplicate bundle manifest path"),
        ("unsafe-bundle-entry", "bundle manifest: reference escapes"),
        ("missing-bundle-target", "bundle manifest references missing file"),
        ("bad-bundle-size", "bundle manifest size mismatch"),
        ("bad-bundle-hash", "bundle manifest hash mismatch"),
        ("bad-checksum", "checksum mismatch"),
        ("unsafe-checksum", "checksum inventory: reference escapes"),
        ("missing-checksum-target", "checksum inventory references missing file"),
        ("bad-crate-json", "could not validate RO-Crate metadata"),
        ("crate-no-root", "exactly one root dataset"),
        ("crate-missing-file", "RO-Crate graph omits package files"),
        ("crate-missing-part", "RO-Crate root omits package parts"),
    ],
)
def test_research_object_verifier_detects_tamper_classes(
    tmp_path: Path, mutation: str, message: str
) -> None:
    output = _built_object(tmp_path)
    bundle_path = output / "bundle-manifest.json"
    checksum_path = output / "checksums.sha256"
    crate_path = output / "ro-crate-metadata.json"

    if mutation == "remove-required":
        (output / "README.md").unlink()
    elif mutation == "bad-bundle-json":
        bundle_path.write_text("{", encoding="utf-8")
    elif mutation.startswith("bad-bundle") or mutation in {
        "duplicate-bundle-entry",
        "unsafe-bundle-entry",
        "missing-bundle-target",
    }:
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        entry = bundle["files"][0]
        if mutation == "bad-bundle-entry":
            entry["path"] = None
        elif mutation == "duplicate-bundle-entry":
            bundle["files"].append(dict(entry))
        elif mutation == "unsafe-bundle-entry":
            entry["path"] = "../escape"
        elif mutation == "missing-bundle-target":
            entry["path"] = "absent.json"
        elif mutation == "bad-bundle-size":
            entry["size_bytes"] = -1
        else:
            entry["sha256"] = "0" * 64
        bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    elif mutation == "bad-checksum":
        lines = checksum_path.read_text(encoding="utf-8").splitlines()
        lines[0] = f"{'0' * 64}  {lines[0].split('  ', 1)[1]}"
        checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    elif mutation == "unsafe-checksum":
        checksum_path.write_text(f"{'0' * 64}  ../escape\n", encoding="utf-8")
    elif mutation == "missing-checksum-target":
        checksum_path.write_text(f"{'0' * 64}  absent.json\n", encoding="utf-8")
    elif mutation == "bad-crate-json":
        crate_path.write_text("[", encoding="utf-8")
    else:
        crate = json.loads(crate_path.read_text(encoding="utf-8"))
        root_entity = next(item for item in crate["@graph"] if item.get("@id") == "./")
        if mutation == "crate-no-root":
            crate["@graph"].remove(root_entity)
        elif mutation == "crate-missing-file":
            crate["@graph"] = [item for item in crate["@graph"] if item.get("@id") != "README.md"]
        else:
            root_entity["hasPart"] = [
                item for item in root_entity["hasPart"] if item.get("@id") != "README.md"
            ]
        crate_path.write_text(json.dumps(crate), encoding="utf-8")

    result = verify_research_object(output)
    assert not result.valid
    assert any(message in error for error in result.errors)


def test_research_object_verifier_rejects_missing_directory(tmp_path: Path) -> None:
    result = verify_research_object(tmp_path / "absent")
    assert not result.valid
    assert result.errors == ("research object directory does not exist",)
