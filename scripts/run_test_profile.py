#!/usr/bin/env python3
"""Run a bounded pytest feedback profile with auditable collection counts."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import time


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "profile",
        choices=("fast", "full", "parallel", "testmon"),
        help="feedback profile to execute",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="bounded xdist worker count for the parallel profile (default: 2)",
    )
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER, help="additional pytest arguments")
    return parser


def _require_positive_workers(workers: int) -> None:
    if workers < 1:
        raise SystemExit("--workers must be a positive integer")


def _command(profile: str, workers: int, extra: list[str]) -> list[list[str]]:
    base = ["uv", "run", "pytest"]
    if profile == "fast":
        selection = ["-m", "not slow and not serial"]
        return [base + ["--collect-only", *selection, *extra], base + [*selection, *extra]]
    if profile == "full":
        return [base + ["--collect-only", *extra], base + extra]
    if profile == "parallel":
        if importlib.util.find_spec("xdist") is None:
            raise SystemExit(
                "parallel profile requires the optional pytest-xdist dependency; "
                "install it in the local environment without changing authoritative CI"
            )
        return [
            base + ["--collect-only", "-m", "not serial", *extra],
            base + ["-n", str(workers), "-m", "not serial", *extra],
            base + ["-m", "serial", *extra],
        ]
    if importlib.util.find_spec("testmon") is None:
        raise SystemExit(
            "testmon profile requires the optional pytest-testmon dependency; "
            "rebuild its database after dependency or test-inventory changes"
        )
    return [base + ["--collect-only"], base + ["--testmon", *extra]]


def _run(command: list[str]) -> tuple[int, float, str]:
    started = time.monotonic()
    process = subprocess.run(command, check=False, text=True, capture_output=True)
    elapsed = time.monotonic() - started
    output = process.stdout + process.stderr
    print(output, end="")
    return process.returncode, elapsed, output


def _collected(output: str) -> int | None:
    for line in output.splitlines():
        match = re.search(r"(\d+) tests? collected", line)
        if match:
            return int(match.group(1))
    return None


def main() -> int:
    args = _parser().parse_args()
    _require_positive_workers(args.workers)
    commands = _command(args.profile, args.workers, args.pytest_args or [])
    observations: list[dict[str, object]] = []
    for command in commands:
        returncode, elapsed, output = _run(command)
        observations.append(
            {
                "command": command,
                "returncode": returncode,
                "elapsed_seconds": round(elapsed, 3),
                "collected_tests": _collected(output),
            }
        )
        if returncode:
            break
    print(json.dumps({"profile": args.profile, "observations": observations}, indent=2))
    return int(any(observation["returncode"] for observation in observations))


if __name__ == "__main__":
    raise SystemExit(main())
