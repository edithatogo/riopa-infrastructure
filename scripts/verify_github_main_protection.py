#!/usr/bin/env python3
"""Verify the live single-developer protection contract for GitHub main."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

EXPECTED_CHECKS = {
    "Quality, contracts, and packaging",
    "Tests on Python 3.14",
    "Analyze Python",
}

QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    branchProtectionRules(first: 100) {
      nodes {
        pattern
        requiresApprovingReviews
        requiredApprovingReviewCount
        requiresStatusChecks
        requiresStrictStatusChecks
        requiredStatusCheckContexts
        requiresConversationResolution
        requiresLinearHistory
        allowsForcePushes
        allowsDeletions
        isAdminEnforced
      }
    }
  }
}
"""


def validate(payload: dict[str, object], branch: str = "main") -> list[str]:
    errors: list[str] = []
    try:
        repository = payload["data"]["repository"]  # type: ignore[index]
        nodes = repository["branchProtectionRules"]["nodes"]  # type: ignore[index]
        rule = next(node for node in nodes if node["pattern"] == branch)
    except (KeyError, TypeError, StopIteration):
        return [f"no branch-protection rule found for {branch}"]

    expected_true = (
        "requiresStatusChecks",
        "requiresStrictStatusChecks",
        "requiresConversationResolution",
        "requiresLinearHistory",
        "isAdminEnforced",
    )
    for field in expected_true:
        if rule.get(field) is not True:
            errors.append(f"{field} must be true")
    for field in ("allowsForcePushes", "allowsDeletions", "requiresApprovingReviews"):
        if rule.get(field) is not False:
            errors.append(f"{field} must be false")
    if rule.get("requiredApprovingReviewCount") is not None:
        errors.append("requiredApprovingReviewCount must be null when reviews are disabled")
    observed_checks = set(rule.get("requiredStatusCheckContexts", []))
    if observed_checks != EXPECTED_CHECKS:
        errors.append(
            "required checks differ: "
            f"expected={sorted(EXPECTED_CHECKS)} observed={sorted(observed_checks)}"
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default="edithatogo/riopa-infrastructure")
    parser.add_argument("--branch", default="main")
    args = parser.parse_args()
    owner, separator, name = args.repository.partition("/")
    if not separator or not owner or not name:
        parser.error("--repository must be in owner/name form")
    completed = subprocess.run(  # noqa: S603
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={QUERY}",
            "-F",
            f"owner={owner}",
            "-F",
            f"name={name}",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        print(completed.stderr.strip(), file=sys.stderr)
        return completed.returncode
    payload = json.loads(completed.stdout)
    errors = validate(payload, args.branch)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"PASS {args.repository}:{args.branch} single-developer protection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
