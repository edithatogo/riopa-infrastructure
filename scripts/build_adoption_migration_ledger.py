"""Build a fail-closed semantic-loss and migration-cost ledger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

CLASSIFICATIONS = ("exact", "approximate", "extension-only", "unmapped")


def build_migration_ledger(root: str | Path) -> dict[str, Any]:
    """Summarize recorded adapter losses and preserve unknown work as unknown."""

    repository = Path(root).resolve()
    adapter_dir = repository / "conformance" / "adapters"
    mappings: list[dict[str, Any]] = []
    if adapter_dir.is_dir():
        for path in sorted(adapter_dir.glob("*.json")):
            if path.name in {"report.json"}:
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and isinstance(payload.get("mappings"), list):
                mappings.append(payload)
    repositories = []
    for mapping in mappings:
        counts = {
            classification: sum(
                item.get("classification") == classification
                for item in mapping["mappings"]
                if isinstance(item, dict)
            )
            for classification in CLASSIFICATIONS
        }
        repositories.append(
            {
                "repository": mapping.get("repository", "unknown"),
                "source_revision": mapping.get("source_revision"),
                "classification_counts": counts,
                "semantic_losses": [
                    item.get("field")
                    for item in mapping["mappings"]
                    if isinstance(item, dict)
                    and item.get("classification") in {"approximate", "extension-only", "unmapped"}
                ],
            }
        )
    return {
        "schema_version": "1.0.0",
        "record_type": "riopa_adoption_migration_ledger",
        "repository": repository.name,
        "adapter_repositories": repositories,
        "contributor_feedback": {
            "status": "not-collected",
            "evidence": [],
            "non_claim": "No contributor or external-user feedback is inferred from fixtures.",
        },
        "migration_costs": {
            "status": "not-measured",
            "dimensions": [
                "schema and profile changes",
                "adapter implementation",
                "validation and documentation",
                "review and maintenance",
            ],
            "values": None,
        },
        "promotion_allowed": False,
        "external_gates": [
            "fresh related-repository revisions",
            "native conformance",
            "contributor or external-user feedback",
            "measured migration effort",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build_migration_ledger(args.root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Migration ledger written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
