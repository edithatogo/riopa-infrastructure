#!/usr/bin/env python3
"""Fail-closed validation for the WP-010 external reproduction record."""
from pathlib import Path
import sys

REQUIRED = ("Selection approver", "Report URI", "Report digest", "Acceptance decision")

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
    print("PASS WP-010 reproduction approval record")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
