#!/usr/bin/env python3
"""Validate the bounded mutmut result and emit a machine-readable receipt."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

STATUSES = ("killed", "survived", "timeout", "no tests", "suspicious")


def mutation_counts(text: str) -> dict[str, int]:
    counts = {status: 0 for status in STATUSES}
    pattern = re.compile(r": (killed|survived|timeout|no tests|suspicious)$")
    for line in text.splitlines():
        match = pattern.search(line.strip())
        if match:
            counts[match.group(1)] += 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--minimum", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    counts = mutation_counts(args.results.read_text(encoding="utf-8"))
    total = sum(counts.values())
    killed = counts["killed"]
    score = killed / total if total else 0.0
    receipt = {
        "scope": "validation.py and publication.py",
        "tool": "mutmut",
        "minimum_score": args.minimum,
        "counts": counts,
        "total": total,
        "killed": killed,
        "score": round(score, 6),
        "passed": score >= args.minimum and total > 0,
    }
    args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"Mutation score: {score:.2%} ({killed}/{total}); minimum: {args.minimum:.2%}")
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
