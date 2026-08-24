import json
import subprocess
from pathlib import Path

from scripts.build_v1_compatibility_diff import build_compatibility_diff


def test_v1_compatibility_diff_is_bound_to_frozen_predecessor() -> None:
    root = Path(__file__).resolve().parents[1]
    diff = json.loads((root / "docs/v1-compatibility-diff-20260825.json").read_text())
    assert diff["baseline_revision"] == "409cbc7"
    assert diff["current_revision"] == "b0357be"
    assert diff["status"] == "no-unintended-breaking-changes"
    assert diff["breaking_changes"] == []
    assert diff["non_claims"]


def test_v1_compatibility_diff_detects_removed_schema_fields(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    schema_dir = root / "schemas"
    schema_dir.mkdir(parents=True)
    (root / "src" / "riopa_provenance").mkdir(parents=True)
    (root / "docs" / "ontology").mkdir(parents=True)
    (root / "bindings" / "typescript").mkdir(parents=True)
    path = schema_dir / "artifact.schema.json"
    path.write_text(
        json.dumps(
            {
                "type": "object",
                "properties": {"artifact_id": {"type": "string"}},
                "required": ["artifact_id"],
            }
        ),
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Compatibility Test",
            "-c",
            "user.email=compatibility@example.invalid",
            "commit",
            "-qm",
            "baseline",
        ],
        cwd=root,
        check=True,
    )
    path.write_text(
        json.dumps(
            {
                "type": "object",
                "properties": {},
                "required": [],
            }
        ),
        encoding="utf-8",
    )
    diff = build_compatibility_diff(root, baseline_revision="HEAD", current_revision="test")
    assert diff["status"] == "review-required"
    assert any(item["kind"] == "field-removed" for item in diff["breaking_changes"])
