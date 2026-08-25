"""Emit a read-only, staged RIOPA adoption profile for a repository root."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_SCAFFOLDING = (
    "AGENTS.md",
    "conductor/workflow.md",
    ".github/workflows/validate.yml",
    "docs/operations-and-support.md",
)


def build_adoption_profile(root: str | Path) -> dict[str, Any]:
    """Describe additive profile/research-object readiness without mutation."""

    repository = Path(root).resolve()
    if not repository.is_dir():
        raise ValueError(f"repository root does not exist: {repository}")
    scaffolding = {path: (repository / path).is_file() for path in REQUIRED_SCAFFOLDING}
    profile_available = all(scaffolding.values())
    research_object_available = (repository / "src/riopa_provenance/crate.py").is_file() and (
        repository / "schemas/snapshot-manifest.schema.json"
    ).is_file()
    return {
        "schema_version": "1.0.0",
        "record_type": "riopa_additive_adoption_profile",
        "template_id": "urn:riopa:template:riopa-single-developer-2026-08-22",
        "repository": repository.name,
        "waves": [
            {
                "wave": 1,
                "surface": "profile",
                "status": "available" if profile_available else "blocked",
                "scaffolding": scaffolding,
            },
            {
                "wave": 2,
                "surface": "research-object-emission",
                "status": "available" if research_object_available else "blocked",
                "entrypoint": "riopa research-object --manifest ... --output-dir ...",
                "requires": ["validated snapshot manifest", "closed local evidence references"],
            },
        ],
        "semantic_loss_boundaries": [
            "Profile readiness does not imply source adoption or semantic equivalence.",
            "Approximate, extension-only and unmapped fields remain visible in adapter mappings.",
            "The emitter is read-only and never overwrites source bytes or local customisation.",
        ],
        "external_gates": [
            "fresh revision capture",
            "native conformance in each related repository",
            "independent reproduction",
            "release authority",
        ],
        "promotion_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build_adoption_profile(args.root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Adoption profile written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
