"""Command-line interface for the reference implementation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .crate import build_research_object
from .methods import generate_methods_markdown
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
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main(sys.argv[1:])
