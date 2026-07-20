#!/usr/bin/env python3
"""Discover local clones relevant to the RIOPA programme.

The script is intentionally read-only unless ``--clone-missing`` is supplied.
It records all matching clones, their remotes, branch and dirty state, and a
preferred path for each expected repository.  Machine-local paths are written
under ``.riopa-local/``, which is ignored by Git.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

PRUNE_NAMES = {
    ".cache",
    ".cargo",
    ".git",
    ".gradle",
    ".mypy_cache",
    ".npm",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "Library",
    "Applications",
    "System",
    "Volumes",
    "build",
    "dist",
    "node_modules",
    "target",
    "venv",
}


@dataclass(frozen=True)
class GitRepository:
    path: Path
    remotes: dict[str, list[str]]
    normalised_remotes: set[str]
    branch: str | None
    head: str | None
    dirty: bool
    upstream: str | None
    ahead: int | None
    behind: int | None


def run_git(path: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(path), *args],
        check=check,
        capture_output=True,
        text=True,
        timeout=20,
    )


def normalise_remote(url: str) -> str | None:
    """Normalise GitHub/Hugging Face URLs to ``host/owner/repository``."""

    value = url.strip()
    if not value:
        return None
    scp = re.match(r"^(?:[^@]+@)?([^:]+):(.+)$", value)
    if scp and "://" not in value:
        host, path = scp.groups()
    else:
        parsed = urlsplit(value)
        host = parsed.hostname or ""
        path = parsed.path
    host = host.casefold()
    path = path.strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    if host not in {
        "github.com",
        "www.github.com",
        "huggingface.co",
        "www.huggingface.co",
        "hf.co",
        "www.hf.co",
    }:
        return None
    host = host.removeprefix("www.")
    if host == "hf.co":
        host = "huggingface.co"
    parts = [part for part in path.split("/") if part]
    if host == "github.com" and len(parts) >= 2:
        return f"github.com/{parts[0].casefold()}/{parts[1].casefold()}"
    if host == "huggingface.co" and len(parts) >= 2:
        return f"huggingface.co/{'/'.join(part.casefold() for part in parts)}"
    return None


def inspect_repository(path: Path) -> GitRepository | None:
    probe = run_git(path, "rev-parse", "--show-toplevel")
    if probe.returncode != 0:
        return None
    root = Path(probe.stdout.strip()).resolve()
    remote_names = run_git(root, "remote").stdout.splitlines()
    remotes: dict[str, list[str]] = {}
    normalised: set[str] = set()
    for remote in remote_names:
        urls = run_git(root, "remote", "get-url", "--all", remote).stdout.splitlines()
        remotes[remote] = [url.strip() for url in urls if url.strip()]
        for url in remotes[remote]:
            candidate = normalise_remote(url)
            if candidate:
                normalised.add(candidate)
    branch_result = run_git(root, "branch", "--show-current")
    branch = branch_result.stdout.strip() or None
    head_result = run_git(root, "rev-parse", "HEAD")
    head = head_result.stdout.strip() if head_result.returncode == 0 else None
    dirty = bool(run_git(root, "status", "--porcelain=v1").stdout.strip())
    upstream_result = run_git(
        root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"
    )
    upstream = upstream_result.stdout.strip() if upstream_result.returncode == 0 else None
    ahead: int | None = None
    behind: int | None = None
    if upstream:
        divergence = run_git(root, "rev-list", "--left-right", "--count", f"{upstream}...HEAD")
        if divergence.returncode == 0:
            fields = divergence.stdout.split()
            if len(fields) == 2:
                behind, ahead = int(fields[0]), int(fields[1])
    return GitRepository(root, remotes, normalised, branch, head, dirty, upstream, ahead, behind)


def walk_git_roots(search_root: Path, max_depth: int) -> list[Path]:
    roots: list[Path] = []
    base_depth = len(search_root.resolve().parts)
    for current, directories, files in os.walk(search_root, followlinks=False):
        current_path = Path(current)
        depth = len(current_path.resolve().parts) - base_depth
        # Detect repositories before pruning ``.git`` from descent.  A Git
        # worktree may expose ``.git`` as a file rather than a directory.
        if ".git" in directories or ".git" in files:
            roots.append(current_path.resolve())
            directories[:] = []
            continue
        directories[:] = [
            item
            for item in directories
            if item not in PRUNE_NAMES and not item.startswith(".") and depth < max_depth
        ]
    return roots


def default_search_roots(repository_root: Path) -> list[Path]:
    home = Path.home()
    candidates = [
        repository_root,
        repository_root.parent,
        repository_root.parent.parent,
        home / "src",
        home / "code",
        home / "Code",
        home / "dev",
        home / "git",
        home / "projects",
        home / "Projects",
        home / "Documents" / "GitHub",
    ]
    result: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved.exists() and resolved.is_dir() and resolved not in seen:
            seen.add(resolved)
            result.append(resolved)
    return result


def expected_remote_identity(item: dict[str, Any]) -> str:
    """Return the canonical normalised remote identity for a configured repository."""

    configured = item.get("canonical_remote")
    if isinstance(configured, str) and configured.strip():
        return (
            configured.strip()
            .removeprefix("https://")
            .removeprefix("http://")
            .rstrip("/")
            .removesuffix(".git")
            .casefold()
        )
    full_name = str(item["full_name"]).casefold()
    provider = str(item.get("provider", "github")).casefold()
    if provider == "github":
        return f"github.com/{full_name}"
    if provider == "huggingface-dataset":
        return f"huggingface.co/datasets/{full_name}"
    raise ValueError(f"unsupported repository provider: {provider}")


def score_clone(
    repo: GitRepository, expected_identity: str, repository_root: Path
) -> tuple[int, int, int, str]:
    normalised = expected_identity.casefold()
    origin_urls = repo.remotes.get("origin", [])
    origin_exact = any(normalise_remote(url) == normalised for url in origin_urls)
    any_exact = normalised in repo.normalised_remotes
    is_primary_root = repo.path == repository_root.resolve()
    return (
        0 if is_primary_root else 1,
        0 if origin_exact else (1 if any_exact else 2),
        0 if not repo.dirty else 1,
        str(repo.path).casefold(),
    )


def clone_repository(item: dict[str, Any], destination: Path) -> tuple[bool, str]:
    full_name = str(item["full_name"])
    provider = str(item.get("provider", "github")).casefold()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return False, f"destination already exists: {destination}"
    if provider == "github" and shutil.which("gh"):
        command = ["gh", "repo", "clone", full_name, str(destination), "--", "--origin", "origin"]
    elif provider == "github":
        command = ["git", "clone", f"https://github.com/{full_name}.git", str(destination)]
    elif provider == "huggingface-dataset":
        command = [
            "git",
            "clone",
            f"https://huggingface.co/datasets/{full_name}",
            str(destination),
        ]
    else:
        return False, f"unsupported repository provider: {provider}"
    result = subprocess.run(command, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        return False, (result.stderr or result.stdout).strip()
    return True, "cloned"


def repository_payload(repo: GitRepository) -> dict[str, Any]:
    return {
        "path": str(repo.path),
        "remotes": repo.remotes,
        "normalised_remotes": sorted(repo.normalised_remotes),
        "branch": repo.branch,
        "head": repo.head,
        "dirty": repo.dirty,
        "upstream": repo.upstream,
        "ahead": repo.ahead,
        "behind": repo.behind,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# RIOPA local workspace map",
        "",
        f"Generated from `{payload['configuration']}`.",
        "",
        "Absolute paths are machine-local and this file is intentionally ignored by Git.",
        "",
        "| Repository | Preferred clone | State | Other clones | Role |",
        "|---|---|---|---:|---|",
    ]
    for entry in payload["repositories"]:
        preferred = entry.get("preferred")
        if preferred:
            state = "dirty" if preferred["dirty"] else "clean"
            if preferred.get("branch"):
                state += f"; `{preferred['branch']}`"
            path = f"`{preferred['path']}`"
        else:
            state = entry.get("status", "missing")
            path = "—"
        lines.append(
            f"| `{entry['full_name']}` | {path} | {state} | "
            f"{max(0, len(entry.get('clones', [])) - (1 if preferred else 0))} | {entry['role']} |"
        )
    extras = payload.get("unmatched_git_repositories", [])
    if extras:
        lines.extend(["", "## Other discovered Git repositories", ""])
        lines.extend(f"- `{item['path']}`" for item in extras)
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--config", default="config/workspace/repositories.json")
    parser.add_argument("--search-root", action="append", default=[])
    parser.add_argument("--max-depth", type=int, default=5)
    parser.add_argument("--clone-missing", action="store_true")
    parser.add_argument("--clone-root")
    parser.add_argument("--output", default=".riopa-local/workspace-repositories.json")
    args = parser.parse_args(argv)

    repository_root = Path(args.repo_root).resolve()
    configuration_path = (repository_root / args.config).resolve()
    configuration = json.loads(configuration_path.read_text(encoding="utf-8"))
    expected = configuration.get("repositories", [])
    if not isinstance(expected, list):
        raise ValueError("workspace repository configuration must contain a repositories array")

    roots = [Path(value).expanduser().resolve() for value in args.search_root]
    if not roots:
        roots = default_search_roots(repository_root)
    candidates: set[Path] = set()
    for root in roots:
        if root.exists() and root.is_dir():
            candidates.update(walk_git_roots(root, args.max_depth))
    if (repository_root / ".git").exists():
        candidates.add(repository_root)

    inspected: dict[Path, GitRepository] = {}
    for candidate in sorted(candidates):
        repository = inspect_repository(candidate)
        if repository is not None:
            inspected[repository.path] = repository

    clone_root = (
        Path(args.clone_root).expanduser().resolve()
        if args.clone_root
        else repository_root.parent / "riopa-related"
    )
    entries: list[dict[str, Any]] = []
    matched_paths: set[Path] = set()
    for item in expected:
        full_name = str(item["full_name"])
        normalised = expected_remote_identity(item)
        clones = [repo for repo in inspected.values() if normalised in repo.normalised_remotes]
        if (
            full_name.casefold() == "edithatogo/riopa-infrastructure"
            and repository_root in inspected
            and inspected[repository_root] not in clones
        ):
            clones.append(inspected[repository_root])
        clone_result: str | None = None
        if not clones and args.clone_missing and bool(item.get("clone_if_missing")):
            destination = clone_root / full_name.split("/", 1)[1]
            success, clone_result = clone_repository(item, destination)
            if success:
                discovered = inspect_repository(destination)
                if discovered is not None:
                    inspected[discovered.path] = discovered
                    clones.append(discovered)
        clones.sort(key=lambda repo: score_clone(repo, normalised, repository_root))
        for clone in clones:
            matched_paths.add(clone.path)
        entries.append(
            {
                **item,
                "status": "found" if clones else ("clone-failed" if clone_result else "missing"),
                "clone_result": clone_result,
                "preferred": repository_payload(clones[0]) if clones else None,
                "clones": [repository_payload(repo) for repo in clones],
            }
        )

    payload = {
        "schema_version": "1.0.0",
        "configuration": str(configuration_path),
        "repository_root": str(repository_root),
        "search_roots": [str(path) for path in roots],
        "clone_root": str(clone_root),
        "repositories": entries,
        "unmatched_git_repositories": [
            repository_payload(repo)
            for path, repo in sorted(inspected.items(), key=lambda item: str(item[0]))
            if path not in matched_paths
        ],
    }
    output = (repository_root / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = output.with_suffix(".md")
    markdown.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Workspace map: {output}")
    print(f"Workspace report: {markdown}")
    missing_required = [
        entry["full_name"]
        for entry in entries
        if entry.get("required") and entry.get("preferred") is None
    ]
    if missing_required:
        print("Required repositories not found: " + ", ".join(missing_required), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
