#!/usr/bin/env python3
"""Best-effort mirror of selected parent issues to the existing RIOPA project."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def gh(args: list[str], *, check: bool = True) -> str:
    process = subprocess.run(["gh", *args], text=True, capture_output=True, check=False)
    if check and process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip())
    return process.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", default="edithatogo")
    parser.add_argument("--project-number", type=int, default=4)
    parser.add_argument("--source-option", default="riopa-infrastructure")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    report_path = ROOT / "project/bootstrap-report.json"
    if not report_path.exists():
        raise SystemExit("Run create_issues.py first; bootstrap-report.json is missing.")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    urls = [
        item["url"]
        for item in report["issues"]
        if item.get("mirror_to_umbrella") and item.get("url")
    ]

    if not args.apply:
        for url in urls:
            print(f"DRY-RUN add {url} to {args.owner} project {args.project_number}")
        return 0

    project = json.loads(
        gh(
            [
                "project",
                "view",
                str(args.project_number),
                "--owner",
                args.owner,
                "--format",
                "json",
            ]
        )
    )
    project_id = project.get("id")
    fields = json.loads(
        gh(
            [
                "project",
                "field-list",
                str(args.project_number),
                "--owner",
                args.owner,
                "--format",
                "json",
            ]
        )
    ).get("fields", [])
    mirror_field = next((field for field in fields if field.get("name") == "Mirror source"), None)
    option_id = None
    if mirror_field:
        option_id = next(
            (
                option.get("id")
                for option in mirror_field.get("options", [])
                if option.get("name") == args.source_option
            ),
            None,
        )

    for url in urls:
        gh(
            [
                "project",
                "item-add",
                str(args.project_number),
                "--owner",
                args.owner,
                "--url",
                url,
            ]
        )

    if mirror_field and option_id and project_id:
        items = json.loads(
            gh(
                [
                    "project",
                    "item-list",
                    str(args.project_number),
                    "--owner",
                    args.owner,
                    "--limit",
                    "1000",
                    "--format",
                    "json",
                ]
            )
        ).get("items", [])
        by_url = {(item.get("content") or {}).get("url"): item.get("id") for item in items}
        for url in urls:
            item_id = by_url.get(url)
            if not item_id:
                continue
            gh(
                [
                    "project",
                    "item-edit",
                    "--id",
                    item_id,
                    "--project-id",
                    project_id,
                    "--field-id",
                    mirror_field["id"],
                    "--single-select-option-id",
                    option_id,
                ]
            )
    else:
        print(
            "Items were added, but the 'Mirror source' field does not contain the "
            f"'{args.source_option}' option. Add that option in the project UI, then rerun."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
