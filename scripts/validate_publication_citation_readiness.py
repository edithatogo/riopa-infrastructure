"""Validate the bounded publication citation contract without contacting a source."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

GUIDANCE = Path("docs/publication-citation-guidance-20260825.json")
CANDIDATE = Path("docs/publication-real-data-release-candidate-20260825.json")
OUTPUT = Path("docs/publication-citation-readiness-validation-20260826.json")
REVISION = re.compile(r"^[0-9a-f]{40}$")


def build_report(root: Path) -> dict[str, Any]:
    guidance = json.loads((root / GUIDANCE).read_text())
    candidate = json.loads((root / CANDIDATE).read_text())
    template = guidance["citation_template"]
    revision = candidate["software_revision"]
    required_tokens = ("<sha>", "<archive/source digest>", "exact revision")
    checks = {
        "preview_status": guidance["status"] == "preview-guidance-not-stable-publication",
        "candidate_is_not_publication": candidate["status"]
        == "owner-agent-reproduced-bounded-candidate",
        "revision_is_content_bound": isinstance(revision, str)
        and REVISION.fullmatch(revision) is not None
        and "exact revision" in guidance["software_citation"]["include"],
        "source_digest_is_required": "content digest" in guidance["data_citation"]["include"],
        "archived_packet_is_source_truth": "archived packet"
        in guidance["data_citation"]["live_endpoint_policy"],
        "template_has_required_placeholders": all(token in template for token in required_tokens),
        "promotion_disabled": guidance["promotion_allowed"] is False
        and candidate["promotion_allowed"] is False,
        "persistent_identifier_deferred": guidance["persistent_identifier"]["status"]
        == "pending-for-stable-publication",
    }
    return {
        "schema": "riopa.publication-citation-readiness-validation.v1",
        "status": "bounded-citation-contract-validated"
        if all(checks.values())
        else "citation-contract-invalid",
        "guidance": str(GUIDANCE),
        "candidate": str(CANDIDATE),
        "checks": checks,
        "promotion_allowed": False,
        "open_gates": [
            "clean-room or external reproduction",
            "protected artifact attestation",
            "preservation deposit and anonymous restore",
            "elapsed beta/RC qualification",
            "accountable release-authority decision",
        ],
        "nonclaims": [
            "This validates citation readiness for a bounded preview only.",
            "It does not create a DOI, preservation receipt, external reproduction, "
            "or release approval.",
        ],
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    report = build_report(root)
    (root / OUTPUT).write_text(json.dumps(report, indent=2) + "\n")
    print(report["status"])
    return 0 if report["status"] == "bounded-citation-contract-validated" else 1


if __name__ == "__main__":
    raise SystemExit(main())
