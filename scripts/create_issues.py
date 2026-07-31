#!/usr/bin/env python3
"""Idempotently create RIOPA labels, issues, sub-issues and project metadata with ``gh``.

The issue configuration files are JSON-compatible YAML.  The script deliberately keeps
human-authored GitHub issue bodies intact unless ``--update-existing`` is supplied.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MARKER_RE = re.compile(r"<!-- riopa-issue-key:\s*([^\s]+)\s*-->")


@dataclass
class IssueResult:
    key: str
    repository: str
    url: str | None
    number: int | None
    action: str
    mirror_to_umbrella: bool = False
    project: bool = False
    phase: str | None = None
    track_id: str | None = None
    target_release: str | None = None
    current_maturity: str | None = None
    maturity_target: str | None = None
    risk: str | None = None
    stability_class: str | None = None
    v1_critical: bool = False
    priority: str | None = None
    owner_repository: str | None = None
    owner_role: str | None = None
    blocking_defects: int = 0
    error: str | None = None


def load(path: Path) -> Any:
    """Load a JSON-compatible YAML file."""

    return json.loads(path.read_text(encoding="utf-8"))


def gh(args: list[str], *, check: bool = True) -> str:
    process = subprocess.run(
        ["gh", *args],
        check=False,
        text=True,
        capture_output=True,
    )
    if check and process.returncode != 0:
        raise RuntimeError(
            f"gh {' '.join(args)} failed ({process.returncode}): "
            f"{process.stderr.strip() or process.stdout.strip()}"
        )
    return process.stdout.strip()


def collection(payload: Any, *keys: str) -> list[dict[str, Any]]:
    """Return a collection from either a raw list or a gh JSON envelope."""

    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def list_existing(
    repo: str,
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, set[str]],
]:
    payload = json.loads(
        gh(
            [
                "issue",
                "list",
                "--repo",
                repo,
                "--state",
                "all",
                "--limit",
                "1000",
                "--json",
                "number,title,body,url,blockedBy",
            ]
        )
        or "[]"
    )
    by_key: dict[str, dict[str, Any]] = {}
    by_title: dict[str, dict[str, Any]] = {}
    blocked_by_url: dict[str, set[str]] = {}
    for issue in collection(payload, "issues"):
        by_title[issue["title"]] = issue
        blocked_by_url[issue["url"]] = {
            item["url"]
            for item in collection(issue.get("blockedBy"), "nodes", "items")
            if item.get("url")
        }
        match = MARKER_RE.search(issue.get("body") or "")
        if match:
            by_key[match.group(1)] = issue
    return by_key, by_title, blocked_by_url


def ensure_labels(repo: str, label_names: set[str], *, apply: bool) -> None:
    definitions = {item["name"]: item for item in load(ROOT / "project/labels.yaml")}
    for name in sorted(label_names):
        definition = definitions.get(
            name,
            {"name": name, "color": "EDEDED", "description": "RIOPA generated label"},
        )
        command = [
            "label",
            "create",
            definition["name"],
            "--repo",
            repo,
            "--color",
            definition["color"],
            "--description",
            definition["description"],
            "--force",
        ]
        if apply:
            gh(command)
        else:
            print("DRY-RUN gh", " ".join(command))


def issue_body(item: dict[str, Any]) -> str:
    return f"{item['body'].rstrip()}\n\n<!-- riopa-issue-key: {item['key']} -->\n"


def update_existing_issue(
    repo: str,
    issue: dict[str, Any],
    item: dict[str, Any],
    *,
    project: str | None,
) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
        handle.write(issue_body(item))
        body_path = handle.name
    try:
        command = [
            "issue",
            "edit",
            str(issue["number"]),
            "--repo",
            repo,
            "--body-file",
            body_path,
        ]
        for label in item.get("labels", []):
            command += ["--add-label", label]
        if project and item.get("project"):
            command += ["--add-project", project]
        gh(command)
    finally:
        Path(body_path).unlink(missing_ok=True)


def create_issue(
    repo: str,
    item: dict[str, Any],
    *,
    parent_url: str | None,
    project: str | None,
    apply: bool,
) -> str | None:
    command = ["issue", "create", "--repo", repo, "--title", item["title"]]
    for label in item.get("labels", []):
        command += ["--label", label]
    if parent_url:
        command += ["--parent", parent_url]
    if project and item.get("project"):
        command += ["--project", project]

    if not apply:
        print("DRY-RUN", repo, item["key"], "parent=", parent_url or "none")
        return None

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
        handle.write(issue_body(item))
        body_path = handle.name
    command += ["--body-file", body_path]
    try:
        output = gh(command)
        return output.splitlines()[-1]
    finally:
        Path(body_path).unlink(missing_ok=True)


def ensure_dependencies(
    repo: str,
    issue_url: str,
    blocked_by: list[str],
    urls: dict[str, str],
    existing_urls: set[str] | None = None,
    *,
    apply: bool,
) -> None:
    if not blocked_by:
        return
    if not apply:
        print("DRY-RUN dependencies", issue_url, "blocked by", blocked_by)
        return

    if existing_urls is None:
        current_payload = json.loads(
            gh(["issue", "view", issue_url, "--repo", repo, "--json", "blockedBy"])
        )
        existing_urls = {
            item.get("url")
            for item in collection(current_payload.get("blockedBy"), "nodes", "items")
            if item.get("url")
        }
    else:
        existing_urls = set(existing_urls)
    for dependency_key in blocked_by:
        dependency_url = urls.get(dependency_key)
        if not dependency_url:
            raise RuntimeError(f"No URL available for dependency key {dependency_key}")
        if dependency_url in existing_urls:
            continue
        gh(["issue", "edit", issue_url, "--repo", repo, "--add-blocked-by", dependency_url])


def update_track_files(results: list[IssueResult]) -> None:
    for result in results:
        if not result.url or ":phase-" in result.key or result.key == "program-epic":
            continue
        metadata_path = ROOT / "conductor" / "tracks" / result.key / "metadata.json"
        index_path = ROOT / "conductor" / "tracks" / result.key / "index.md"
        if metadata_path.exists():
            metadata = load(metadata_path)
            metadata["github_issue"] = result.url
            metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        if index_path.exists():
            text = index_path.read_text(encoding="utf-8")
            if "- **GitHub issue:**" in text:
                text = re.sub(
                    r"- \*\*GitHub issue:\*\* .*",
                    f"- **GitHub issue:** {result.url}",
                    text,
                )
            else:
                text = text.rstrip() + f"\n- **GitHub issue:** {result.url}\n"
            index_path.write_text(text, encoding="utf-8")


def process_repository(
    repo: str,
    items: list[dict[str, Any]],
    *,
    project: str | None,
    apply: bool,
    update_existing: bool,
) -> list[IssueResult]:
    label_names = {label for item in items for label in item.get("labels", [])}
    ensure_labels(repo, label_names, apply=apply)
    by_key, by_title, existing_blocked_by = list_existing(repo) if apply else ({}, {}, {})
    urls: dict[str, str] = {}
    resolved_keys: set[str] = set()
    results: list[IssueResult] = []

    pending = list(items)
    while pending:
        progressed = False
        for item in list(pending):
            parent_key = item.get("parent")
            if parent_key and parent_key not in resolved_keys:
                continue

            existing = by_key.get(item["key"]) or by_title.get(item["title"])
            if existing:
                url = existing["url"]
                if apply and update_existing:
                    update_existing_issue(repo, existing, item, project=project)
                    action = "updated"
                else:
                    action = "reused"
                number = existing["number"]
            else:
                url = create_issue(
                    repo,
                    item,
                    parent_url=urls.get(parent_key) if parent_key else None,
                    project=project,
                    apply=apply,
                )
                number = int(url.rstrip("/").split("/")[-1]) if url else None
                action = "created" if apply else "planned"

            if url:
                urls[item["key"]] = url
            resolved_keys.add(item["key"])
            results.append(
                IssueResult(
                    key=item["key"],
                    repository=repo,
                    url=url,
                    number=number,
                    action=action,
                    mirror_to_umbrella=bool(item.get("mirror_to_umbrella")),
                    project=bool(item.get("project")),
                    phase=item.get("phase"),
                    track_id=item.get("track_id"),
                    target_release=item.get("target_release"),
                    current_maturity=item.get("current_maturity"),
                    maturity_target=item.get("maturity_target"),
                    risk=item.get("risk"),
                    stability_class=item.get("stability_class"),
                    v1_critical=bool(item.get("v1_critical")),
                    priority=item.get("priority"),
                    owner_repository=item.get("owner_repository"),
                    owner_role=item.get("owner_role"),
                    blocking_defects=int(item.get("blocking_defects", 0)),
                )
            )
            pending.remove(item)
            progressed = True

        if not progressed:
            unresolved = [f"{item['key']} parent={item.get('parent')}" for item in pending]
            raise RuntimeError(f"Could not resolve issue hierarchy: {unresolved}")

    if apply:
        for item in items:
            issue_url = urls.get(item["key"])
            if issue_url:
                ensure_dependencies(
                    repo,
                    issue_url,
                    item.get("blocked_by", []),
                    urls,
                    existing_blocked_by.get(issue_url),
                    apply=True,
                )

    return results


def find_project_number(owner: str, title: str) -> int | None:
    payload = json.loads(
        gh(["project", "list", "--owner", owner, "--limit", "100", "--format", "json"]) or "{}"
    )
    for project in collection(payload, "projects"):
        if project.get("title") == title:
            value = project.get("number")
            return int(value) if value is not None else None
    return None


def content_url(item: dict[str, Any]) -> str | None:
    content = item.get("content")
    if isinstance(content, dict):
        return content.get("url")
    return item.get("url")


def project_value_matches(item: dict[str, Any], field_name: str, expected: Any) -> bool:
    """Return whether a Project item already has the requested field value."""

    # ``gh project item-list --format json`` exposes project fields as flattened
    # lower-case keys (for example ``"owner repository"``), while older gh
    # versions may return GraphQL-style ``fieldValues`` nodes.
    flattened_key = field_name.casefold()
    if flattened_key in item:
        return item[flattened_key] == expected
    values = collection(item.get("fieldValues"), "nodes", "items")
    for value in values:
        field = value.get("field")
        if not isinstance(field, dict) or field.get("name") != field_name:
            continue
        for key in ("name", "text", "number", "date"):
            if key in value:
                return value[key] == expected
    return False


def set_single_select(
    *,
    project_id: str,
    item_id: str,
    field: dict[str, Any],
    value: str,
) -> bool:
    option_id = next(
        (option.get("id") for option in field.get("options", []) if option.get("name") == value),
        None,
    )
    if not option_id:
        return False
    gh(
        [
            "project",
            "item-edit",
            "--id",
            item_id,
            "--project-id",
            project_id,
            "--field-id",
            field["id"],
            "--single-select-option-id",
            option_id,
        ]
    )
    return True


def set_text(
    *,
    project_id: str,
    item_id: str,
    field: dict[str, Any],
    value: str,
) -> None:
    gh(
        [
            "project",
            "item-edit",
            "--id",
            item_id,
            "--project-id",
            project_id,
            "--field-id",
            field["id"],
            "--text",
            value,
        ]
    )


def set_number(
    *,
    project_id: str,
    item_id: str,
    field: dict[str, Any],
    value: int,
) -> None:
    gh(
        [
            "project",
            "item-edit",
            "--id",
            item_id,
            "--project-id",
            project_id,
            "--field-id",
            field["id"],
            "--number",
            str(value),
        ]
    )


def sync_project_fields(
    *,
    owner: str,
    project_number: int,
    results: list[IssueResult],
    apply: bool,
    offset: int = 0,
    limit: int | None = None,
) -> dict[str, Any]:
    eligible = [result for result in results if result.project and result.url]
    if offset < 0:
        raise ValueError("project field offset must not be negative")
    if offset:
        eligible = eligible[offset:]
    if limit is not None:
        if limit <= 0:
            raise ValueError("project field limit must be positive")
        eligible = eligible[:limit]
    if not apply:
        return {"project_number": project_number, "planned_items": len(eligible)}

    project = json.loads(
        gh(["project", "view", str(project_number), "--owner", owner, "--format", "json"])
    )
    project_id = project.get("id")
    if not project_id:
        raise RuntimeError(f"Could not resolve project ID for {owner}/{project_number}")

    fields_payload = json.loads(
        gh(
            [
                "project",
                "field-list",
                str(project_number),
                "--owner",
                owner,
                "--limit",
                "100",
                "--format",
                "json",
            ]
        )
    )
    fields = {field.get("name"): field for field in collection(fields_payload, "fields")}

    items_payload = json.loads(
        gh(
            [
                "project",
                "item-list",
                str(project_number),
                "--owner",
                owner,
                "--limit",
                "1000",
                "--format",
                "json",
            ]
        )
    )
    items = collection(items_payload, "items")
    item_by_url = {content_url(item): item for item in items if content_url(item)}
    item_ids_by_url = {url: item.get("id") for url, item in item_by_url.items()}

    added = 0
    for result in eligible:
        if result.url not in item_ids_by_url:
            gh(
                [
                    "project",
                    "item-add",
                    str(project_number),
                    "--owner",
                    owner,
                    "--url",
                    result.url,
                    "--format",
                    "json",
                ]
            )
            added += 1

    if added:
        items_payload = json.loads(
            gh(
                [
                    "project",
                    "item-list",
                    str(project_number),
                    "--owner",
                    owner,
                    "--limit",
                    "1000",
                    "--format",
                    "json",
                ]
            )
        )
        items = collection(items_payload, "items")
        item_by_url = {content_url(item): item for item in items if content_url(item)}
        item_ids_by_url = {url: item.get("id") for url, item in item_by_url.items()}

    missing_options: set[str] = set()
    updated = 0
    for result in eligible:
        item_id = item_ids_by_url.get(result.url)
        if not item_id:
            continue
        item = item_by_url.get(result.url, {})
        if (
            result.phase
            and fields.get("Phase")
            and not project_value_matches(item, "Phase", result.phase)
            and not set_single_select(
                project_id=project_id,
                item_id=item_id,
                field=fields["Phase"],
                value=result.phase,
            )
        ):
            missing_options.add(f"Phase={result.phase}")
        if (
            result.track_id
            and fields.get("Track ID")
            and not project_value_matches(item, "Track ID", result.track_id)
        ):
            set_text(
                project_id=project_id,
                item_id=item_id,
                field=fields["Track ID"],
                value=result.track_id,
            )
        if (
            fields.get("Evidence status")
            and not project_value_matches(item, "Evidence status", "None")
            and not set_single_select(
                project_id=project_id,
                item_id=item_id,
                field=fields["Evidence status"],
                value="None",
            )
        ):
            missing_options.add("Evidence status=None")
        if (
            fields.get("Current maturity")
            and not project_value_matches(item, "Current maturity", result.current_maturity or "M0")
            and not set_single_select(
                project_id=project_id,
                item_id=item_id,
                field=fields["Current maturity"],
                value=result.current_maturity or "M0",
            )
        ):
            missing_options.add(f"Current maturity={result.current_maturity or 'M0'}")
        select_values = {
            "Maturity target": result.maturity_target,
            "Risk": result.risk,
            "Priority": result.priority,
            "Stability class": result.stability_class,
            "V1 critical": "Yes" if result.v1_critical else "No",
        }
        for field_name, value in select_values.items():
            if (
                value
                and fields.get(field_name)
                and not project_value_matches(item, field_name, value)
                and not set_single_select(
                    project_id=project_id,
                    item_id=item_id,
                    field=fields[field_name],
                    value=value,
                )
            ):
                missing_options.add(f"{field_name}={value}")
        if (
            result.target_release
            and fields.get("Target release")
            and not project_value_matches(item, "Target release", result.target_release)
        ):
            set_text(
                project_id=project_id,
                item_id=item_id,
                field=fields["Target release"],
                value=result.target_release,
            )
        if (
            result.owner_repository
            and fields.get("Owner repository")
            and not project_value_matches(item, "Owner repository", result.owner_repository)
        ):
            set_text(
                project_id=project_id,
                item_id=item_id,
                field=fields["Owner repository"],
                value=result.owner_repository,
            )
        if (
            result.owner_role
            and fields.get("Owner role")
            and not project_value_matches(item, "Owner role", result.owner_role)
        ):
            set_text(
                project_id=project_id,
                item_id=item_id,
                field=fields["Owner role"],
                value=result.owner_role,
            )
        if fields.get("Blocking defects") and not project_value_matches(
            item, "Blocking defects", result.blocking_defects
        ):
            set_number(
                project_id=project_id,
                item_id=item_id,
                field=fields["Blocking defects"],
                value=result.blocking_defects,
            )
        updated += 1

    return {
        "project_number": project_number,
        "project_id": project_id,
        "eligible_items": len(eligible),
        "offset": offset,
        "limited": limit is not None,
        "items_added": added,
        "items_updated": updated,
        "missing_field_options": sorted(missing_options),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="edithatogo/riopa-infrastructure")
    parser.add_argument("--owner")
    parser.add_argument("--project-title")
    parser.add_argument("--project-number", type=int)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--update-existing", action="store_true")
    parser.add_argument("--cross-repo", action="store_true")
    parser.add_argument(
        "--project-limit",
        type=int,
        help="limit Project field reconciliation to the first N eligible items",
    )
    parser.add_argument(
        "--project-offset",
        type=int,
        default=0,
        help="skip this many eligible items before Project field reconciliation",
    )
    args = parser.parse_args()

    owner = args.owner or args.repo.split("/", 1)[0]
    local_config = load(ROOT / "project/issues.yaml")
    results = process_repository(
        args.repo,
        local_config["issues"],
        project=args.project_title,
        apply=args.apply,
        update_existing=args.update_existing,
    )

    if args.cross_repo:
        cross_config = load(ROOT / "project/cross-repo-adoption.yaml")
        for item in cross_config["issues"]:
            try:
                results.extend(
                    process_repository(
                        item["repository"],
                        [item],
                        project=None,
                        apply=args.apply,
                        update_existing=args.update_existing,
                    )
                )
            except RuntimeError as error:
                results.append(
                    IssueResult(
                        key=item["key"],
                        repository=item["repository"],
                        url=None,
                        number=None,
                        action="blocked",
                        error=str(error),
                    )
                )

    project_number = args.project_number
    if args.apply and not project_number and args.project_title:
        project_number = find_project_number(owner, args.project_title)
    project_report: dict[str, Any] | None = None
    if project_number:
        project_report = sync_project_fields(
            owner=owner,
            project_number=project_number,
            results=[result for result in results if result.repository == args.repo],
            apply=args.apply,
            offset=args.project_offset,
            limit=args.project_limit,
        )

    if args.apply:
        update_track_files([result for result in results if result.repository == args.repo])

    report = {
        "applied": args.apply,
        "repository": args.repo,
        "owner": owner,
        "project_title": args.project_title,
        "project": project_report,
        "issues": [asdict(result) for result in results],
    }
    report_path = ROOT / "project/bootstrap-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
