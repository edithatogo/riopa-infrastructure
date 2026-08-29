import json
from pathlib import Path

from scripts.validate_cyclonedx_sbom import validate_sbom


def test_strict_cyclonedx_validator_accepts_v16_document(tmp_path: Path) -> None:
    path = tmp_path / "sbom.json"
    path.write_text(
        json.dumps(
            {
                "bomFormat": "CycloneDX",
                "specVersion": "1.6",
                "version": 1,
                "components": [{"type": "library", "name": "example", "version": "1"}],
            }
        ),
        encoding="utf-8",
    )
    assert validate_sbom(path) == ()


def test_strict_cyclonedx_validator_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "sbom.json"
    path.write_text('{"bomFormat":"CycloneDX","specVersion":"9.9"}', encoding="utf-8")
    assert validate_sbom(path) == ("CycloneDX specVersion must be 1.6",)

    path.write_text("[]", encoding="utf-8")
    assert validate_sbom(path) == ("CycloneDX document must be a JSON object",)

    path.write_text("{", encoding="utf-8")
    assert validate_sbom(path)[0].startswith("could not read CycloneDX JSON:")


def test_strict_cyclonedx_validator_rejects_empty_and_invalid_components(
    tmp_path: Path,
) -> None:
    path = tmp_path / "sbom.json"
    path.write_text(
        json.dumps(
            {"bomFormat": "CycloneDX", "specVersion": "1.6", "version": 1, "components": []}
        ),
        encoding="utf-8",
    )
    assert validate_sbom(path) == ("CycloneDX components must be a non-empty array",)

    path.write_text(
        json.dumps(
            {
                "bomFormat": "CycloneDX",
                "specVersion": "1.6",
                "version": 1,
                "components": [{"type": "not-a-type", "name": "example"}],
            }
        ),
        encoding="utf-8",
    )
    assert any("not-a-type" in error for error in validate_sbom(path))
