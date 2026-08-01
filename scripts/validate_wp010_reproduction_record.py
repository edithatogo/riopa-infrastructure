#!/usr/bin/env python3
"""Fail-closed validation for the WP-010 external reproduction record."""
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

REQUIRED = ("Selection approver", "Report URI", "Report digest", "Acceptance decision")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ZENODO_DOI = "10.5281/zenodo.21735818"


def _value(text: str, label: str) -> str:
    match = re.search(rf"^-\s*{re.escape(label)}(?:\s+or\s+issue\s+#149\s+comment)?:\s*`?([^`\n]+?)`?\s*$", text, re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _line_value(text: str, pattern: str) -> str:
    match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _is_report_uri(value: str) -> bool:
    if value.startswith("issue #149"):
        return True
    parsed = urlparse(value)
    return parsed.scheme in {"https", "http"} and bool(parsed.netloc)

def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/wp010-external-reproduction-approval-record.md")
    text = path.read_text(encoding="utf-8")
    missing = [field for field in REQUIRED if field not in text]
    if missing:
        print("missing required fields: " + ", ".join(missing), file=sys.stderr)
        return 2
    if "`TBD`" in text:
        print("pending: approval/reproduction record contains TBD fields", file=sys.stderr)
        return 3
    if "bf22b88342d577ca84ce554b77cba90cf38c6df3e617a125c1801eb5d7291d9b" not in text:
        print("missing deposited packet digest", file=sys.stderr)
        return 4
    # The acceptance record must bind the report to the exact preserved pilot,
    # rather than relying on a free-form confirmation string alone.
    if ZENODO_DOI not in text:
        print("missing deposited Zenodo DOI", file=sys.stderr)
        return 4
    report_digest = _value(text, "Report digest")
    if not SHA256.fullmatch(report_digest):
        print("invalid report digest: expected a 64-character lowercase SHA-256", file=sys.stderr)
        return 5
    operator = _line_value(text, r"^-\s*Operator/person or accountable organisation:\s*`?([^`\\n]+?)`?\s*$")
    if not operator or operator.lower() in {"tbd", "none", "n/a"}:
        print("missing external operator identity", file=sys.stderr)
        return 6
    approver = _line_value(text, r"^-\s*Selection approver(?: and date)?:\s*`?([^`\\n]+?)`?\s*$")
    if not approver or approver.lower() in {"tbd", "none", "n/a"}:
        print("missing operator selection approval", file=sys.stderr)
        return 6
    independence = _value(text, "Independence/conflict statement received")
    if not independence or independence.lower() in {"none", "no", "n/a"}:
        print("missing operator independence/conflict statement", file=sys.stderr)
        return 6
    report_uri = _line_value(text, r"^-\s*Report URI(?: or issue #149 comment)?:\s*`?([^`\\n]+?)`?\s*$")
    if not _is_report_uri(report_uri):
        print("invalid report URI: expected an immutable HTTP(S) artifact or issue #149", file=sys.stderr)
        return 9
    zenodo_line = _line_value(text, r"^-\s*Zenodo DOI and deposited packet digest match:\s*`?([^`\\n]+?)`?\s*$")
    if zenodo_line.lower() not in {"yes", "true", "match", "passed"}:
        print("Zenodo DOI/deposited packet digest match not confirmed", file=sys.stderr)
        return 10
    commands = _line_value(text, r"^-\s*Commands/logs complete and reproducible:\s*`?([^`\\n]+?)`?\s*$")
    if commands.lower() not in {"yes", "true", "complete", "passed"}:
        print("complete reproducible command logs not confirmed", file=sys.stderr)
        return 11
    adjudicated = _line_value(text, r"^-\s*Deviations, safety and rights findings adjudicated:\s*`?([^`\\n]+?)`?\s*$")
    if adjudicated.lower() not in {"yes", "true", "none", "complete", "passed"}:
        print("safety/rights adjudication not confirmed", file=sys.stderr)
        return 12
    match = re.search(r"Exact revision and reviewer-bundle digest match:\s*`?([^`\n]+?)`?\s*$", text, re.MULTILINE | re.IGNORECASE)
    if not match or match.group(1).strip().lower() not in {"yes", "true", "match", "passed"}:
        print("exact revision/reviewer-bundle digest match not confirmed", file=sys.stderr)
        return 7
    decision = _value(text, "Acceptance decision")
    if decision.lower() not in {"pass", "pass-with-limitations"}:
        print("acceptance decision is not an accepted bounded-pilot result", file=sys.stderr)
        return 8
    print("PASS WP-010 reproduction approval record")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
