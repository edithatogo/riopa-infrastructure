from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True)


def make_repo(path: Path, remote: str) -> None:
    path.mkdir(parents=True)
    git(path, "init", "-b", "main")
    git(path, "remote", "add", "origin", remote)


def test_discovery_matches_normalised_remotes_and_reports_duplicates(tmp_path: Path) -> None:
    project = tmp_path / "riopa-infrastructure"
    duplicate = tmp_path / "duplicate"
    related = tmp_path / "fyi-cli"
    dataset = tmp_path / "nz-hansard-corpus"
    make_repo(project, "https://github.com/edithatogo/riopa-infrastructure.git")
    make_repo(duplicate, "git@github.com:edithatogo/riopa-infrastructure.git")
    make_repo(related, "ssh://git@github.com/edithatogo/fyi-cli.git")
    make_repo(
        dataset,
        "git@hf.co:datasets/edithatogo/nz-hansard-corpus",
    )

    config_dir = project / "config" / "workspace"
    config_dir.mkdir(parents=True)
    (config_dir / "repositories.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "repositories": [
                    {
                        "full_name": "edithatogo/riopa-infrastructure",
                        "role": "primary",
                        "required": True,
                        "clone_if_missing": False,
                        "write_policy": "primary",
                    },
                    {
                        "full_name": "edithatogo/fyi-cli",
                        "role": "related",
                        "required": True,
                        "clone_if_missing": False,
                        "write_policy": "read-only",
                    },
                    {
                        "full_name": "edithatogo/nz-hansard-corpus",
                        "provider": "huggingface-dataset",
                        "canonical_remote": (
                            "huggingface.co/datasets/edithatogo/nz-hansard-corpus"
                        ),
                        "role": "dataset reference",
                        "required": False,
                        "clone_if_missing": False,
                        "write_policy": "read-only",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    script = Path(__file__).resolve().parents[1] / "scripts/discover_workspace_repositories.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo-root",
            str(project),
            "--search-root",
            str(tmp_path),
            "--max-depth",
            "2",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(
        (project / ".riopa-local/workspace-repositories.json").read_text(encoding="utf-8")
    )
    primary = payload["repositories"][0]
    assert primary["preferred"]["path"] == str(project.resolve())
    assert len(primary["clones"]) == 2
    assert payload["repositories"][1]["preferred"]["path"] == str(related.resolve())
    assert payload["repositories"][2]["preferred"]["path"] == str(dataset.resolve())
    assert (project / ".riopa-local/workspace-repositories.md").is_file()


def test_discovery_returns_two_when_required_repository_is_missing(tmp_path: Path) -> None:
    project = tmp_path / "riopa-infrastructure"
    make_repo(project, "https://github.com/edithatogo/riopa-infrastructure.git")
    config_dir = project / "config" / "workspace"
    config_dir.mkdir(parents=True)
    (config_dir / "repositories.json").write_text(
        json.dumps(
            {
                "repositories": [
                    {
                        "full_name": "edithatogo/riopa-infrastructure",
                        "role": "primary",
                        "required": True,
                        "clone_if_missing": False,
                    },
                    {
                        "full_name": "edithatogo/missing",
                        "role": "missing",
                        "required": True,
                        "clone_if_missing": False,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    script = Path(__file__).resolve().parents[1] / "scripts/discover_workspace_repositories.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo-root",
            str(project),
            "--search-root",
            str(tmp_path),
            "--max-depth",
            "2",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "edithatogo/missing" in result.stderr
