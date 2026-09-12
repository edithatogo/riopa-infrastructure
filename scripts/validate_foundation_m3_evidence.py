"""Rebuild bounded foundation integration evidence without granting promotion."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from riopa_provenance.canonical import validate_migration_fixture
from scripts.validate_archived_real_source_pair import build_packet
from scripts.validate_real_data_release_candidate import validate_candidate

PAIR = "docs/connector-archived-real-source-pair-20260826.json"
CANDIDATE = "docs/publication-real-data-release-candidate-20260825.json"
MIGRATIONS = (
    "docs/provenance-profile-migration-1.0.0-to-1.1.0.json",
    "docs/ontology/migrations/canonical-crosswalk-1.0.0-to-1.1.0.json",
)


def load(root: Path, relative: str) -> Any:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def digest(root: Path, relative: str) -> str:
    return hashlib.sha256((root / relative).read_bytes()).hexdigest()


def build_evidence(root: Path) -> dict[str, Any]:
    pair = build_packet(root)
    recorded = load(root, PAIR)
    # The historical pair receipt predates the already-merged receipt hardening.
    # Accept only that exact known successor; arbitrary drift still fails closed.
    successor_path = "evidence/stats-nz-meshblock-2026-projection/records-manifest.json"
    old_digest = "92b38767943694f42f18fd5b9b1efc398ea9164c2580b27ca776b641aec8d8c1"
    new_digest = "27f278ca5a537b2d97eff92e13d0bf51ef7ae8ae256ca8a4e6cf453adc48ec0e"
    if recorded["file_sha256"][successor_path] != old_digest:
        raise ValueError("historical national manifest receipt changed")
    recorded["file_sha256"][successor_path] = new_digest
    if pair != recorded:
        raise ValueError("archived source pair differs from qualified successor")
    candidate = validate_candidate(root)
    national = pair["sources"]["national"]
    manifest = load(root, national["manifest"])
    national_base = Path(national["manifest"]).parent
    bound = dict(pair["file_sha256"])
    # Verify the source/projection/receipt links, not merely their presence.
    for key in ("source_record", "projection_record", "materialization_receipt"):
        relative = str(national_base / manifest[key])
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError("national evidence path escapes repository")
        actual = digest(root, relative)
        if actual != manifest[f"{key}_sha256"]:
            raise ValueError(f"national {key} digest mismatch")
        bound[relative] = actual
    source = load(root, str(national_base / manifest["source_record"]))["record"]
    council = load(root, candidate["source_manifest"])
    council_source = next(
        item
        for item in council["sources"]
        if item["source_id"] == pair["sources"]["council_planning"]["source_id"]
    )
    migration_results = []
    for relative in MIGRATIONS:
        migration = load(root, relative)
        errors = validate_migration_fixture(migration)
        if errors:
            raise ValueError(f"{relative}: {'; '.join(errors)}")
        migration_results.append(
            {
                "path": relative,
                "from_version": migration["from_version"],
                "to_version": migration["to_version"],
                "status": "declarative-fixture-valid-real-data-execution-unverified",
            }
        )
    bound.update({item["path"]: item["sha256"] for item in candidate["artifacts"]})
    for relative in (PAIR, CANDIDATE, *MIGRATIONS):
        bound[relative] = digest(root, relative)
    return {
        "schema": "riopa.foundation-m3-evidence.v1",
        "evidence_id": "urn:riopa:evidence:foundation-m3-inventory:2026-09-12",
        "track_id": "foundation_architecture_20260718",
        "status": "bounded-integration-verified-m3-qualification-incomplete",
        "promotion_allowed": False,
        "current_maturity": "M2",
        "sources": pair["sources"],
        "historical_receipt_reconciliation": {
            "path": successor_path,
            "historical_sha256": old_digest,
            "successor_sha256": new_digest,
            "successor_commit": "38ae813818e0cca9065ea3d299ca22153a88b206",
            "reason": "merged materialization receipt and manifest hardening in PR #598",
            "historical_receipt_modified": False,
        },
        "rights": {
            "national": source.get("rights", {}),
            "council": {
                key: council_source[key] for key in ("rights_evidence", "rights_disposition")
            },
            "verification_scope": "archived declarations; no fresh rights or authority decision",
        },
        "outputs": candidate["artifacts"],
        "migrations": migration_results,
        "file_sha256": dict(sorted(bound.items())),
        "remaining_m3_gates": [
            "execute applicable old/new-version migration on representative real inputs",
            "qualify loss, rejection, recovery and compatibility against those versions",
            "record candidate-bound foundation integration qualification and finding disposition",
        ],
        "non_claims": [
            "No fresh source retrieval, publication, provider restore or authority approval.",
            "Archived rights declarations are not new redistribution clearance.",
            "Valid migration metadata is not an executed migration or cross-runtime conformance.",
            "Passing this inventory does not satisfy M3 or the later M4-M6 gates.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    packet = build_evidence(args.root.resolve())
    args.output.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
