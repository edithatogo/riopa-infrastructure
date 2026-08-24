import json
from pathlib import Path

from scripts.check_template_drift import build_template_drift_report

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/repository-template-contract-20260822.json"


def test_template_drift_report_is_aligned_and_non_mutating() -> None:
    report = build_template_drift_report(ROOT, CONTRACT)
    assert report["status"] == "aligned"
    assert report["safe_upgrade"] is True
    assert report["missing_scaffolding"] == []
    assert report["mutations_performed"] == []
    assert "project/issues.yaml" in report["generated_boundaries_present"]


def test_template_drift_report_detects_missing_scaffolding(tmp_path: Path) -> None:
    contract = {
        "template_id": "urn:test:template:1",
        "required_scaffolding": ["AGENTS.md", "conductor/workflow.md"],
        "generated_boundaries": {"generated": ["dist"], "never_overwrite": [".git"]},
    }
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("agent", encoding="utf-8")
    report = build_template_drift_report(tmp_path, path)
    assert report["status"] == "drift"
    assert report["safe_upgrade"] is False
    assert report["missing_scaffolding"] == ["conductor/workflow.md"]


def test_template_drift_preserves_local_customisations_and_never_overwrite_files(
    tmp_path: Path,
) -> None:
    contract = {
        "template_id": "urn:test:template:customisation",
        "required_scaffolding": ["README.md"],
        "generated_boundaries": {
            "generated": ["project/issues.yaml"],
            "never_overwrite": ["README.md", "docs/local-policy.md"],
        },
    }
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")
    readme = tmp_path / "README.md"
    readme.write_text("local customisation\n", encoding="utf-8")
    policy = tmp_path / "docs/local-policy.md"
    policy.parent.mkdir()
    policy.write_text("local policy\n", encoding="utf-8")

    before = {
        item: (tmp_path / item).read_bytes() for item in ("README.md", "docs/local-policy.md")
    }
    report = build_template_drift_report(tmp_path, path)

    assert report["status"] == "aligned"
    assert report["safe_upgrade"] is True
    assert report["never_overwrite_present"] == ["README.md", "docs/local-policy.md"]
    assert report["mutations_performed"] == []
    assert {item: (tmp_path / item).read_bytes() for item in before} == before
