"""Command-line interface for the reference implementation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .crate import build_research_object
from .methods import generate_methods_markdown
from .roadmap import (
    render_status_markdown,
    roadmap_status,
    validate_roadmap,
    write_issue_configuration,
)
from .validation import validate_bundle


def _validate(args: argparse.Namespace) -> int:
    results = validate_bundle(args.root)
    failures = 0
    for result in results:
        relative = result.path
        if result.valid:
            print(f"PASS {relative}")
        else:
            failures += 1
            print(f"FAIL {relative}")
            for error in result.errors:
                print(f"  - {error}")
    print(f"Validated {len(results)} item(s); {failures} failure(s).")
    return 1 if failures else 0


def _methods(args: argparse.Namespace) -> int:
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(generate_methods_markdown(args.manifest), encoding="utf-8")
    print(f"Methods written to {output}")
    return 0


def _research_object(args: argparse.Namespace) -> int:
    output = build_research_object(args.manifest, args.output_dir)
    print(f"Research object written to {output}")
    return 0


def _roadmap_validate(args: argparse.Namespace) -> int:
    problems = validate_roadmap(args.root, check_generated_issues=not args.skip_issue_drift)
    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        print(f"Roadmap validation failed with {len(problems)} problem(s).")
        return 1
    print("PASS roadmap, maturity, release, track, evidence, and issue-graph validation")
    return 0


def _roadmap_status(args: argparse.Namespace) -> int:
    status = roadmap_status(args.root, args.release)
    text = (
        json.dumps(status, indent=2, ensure_ascii=False) + "\n"
        if args.format == "json"
        else render_status_markdown(status)
    )
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"Roadmap status written to {output}")
    else:
        print(text, end="")
    return 0


def _roadmap_generate_issues(args: argparse.Namespace) -> int:
    output = write_issue_configuration(args.root, args.output)
    print(f"Issue configuration written to {output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="riopa")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate schemas and examples")
    validate.add_argument("--root", default=".")
    validate.set_defaults(func=_validate)

    methods = subparsers.add_parser("methods", help="generate methods from a manifest")
    methods.add_argument("--manifest", required=True)
    methods.add_argument("--output", required=True)
    methods.set_defaults(func=_methods)

    crate = subparsers.add_parser("research-object", help="build a minimal RO-Crate")
    crate.add_argument("--manifest", required=True)
    crate.add_argument("--output-dir", required=True)
    crate.set_defaults(func=_research_object)

    roadmap = subparsers.add_parser("roadmap", help="validate and report the v1 roadmap")
    roadmap_subparsers = roadmap.add_subparsers(dest="roadmap_command", required=True)

    roadmap_validate = roadmap_subparsers.add_parser(
        "validate", help="validate tracks, releases, maturity gates, and generated issues"
    )
    roadmap_validate.add_argument("--root", default=".")
    roadmap_validate.add_argument("--skip-issue-drift", action="store_true")
    roadmap_validate.set_defaults(func=_roadmap_validate)

    roadmap_status_parser = roadmap_subparsers.add_parser(
        "status", help="report readiness for one or every planned release"
    )
    roadmap_status_parser.add_argument("--root", default=".")
    roadmap_status_parser.add_argument("--release")
    roadmap_status_parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    roadmap_status_parser.add_argument("--output")
    roadmap_status_parser.set_defaults(func=_roadmap_status)

    roadmap_issues = roadmap_subparsers.add_parser(
        "generate-issues", help="regenerate project/issues.yaml from Conductor tracks"
    )
    roadmap_issues.add_argument("--root", default=".")
    roadmap_issues.add_argument("--output")
    roadmap_issues.set_defaults(func=_roadmap_generate_issues)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main(sys.argv[1:])
