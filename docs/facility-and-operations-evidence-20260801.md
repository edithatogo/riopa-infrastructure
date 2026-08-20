# Facility and operations evidence (2026-08-01)

This slice records the repository-owned evidence for the public-datasets-only
facility and spatial operations tracks. It does not claim authoritative
coverage or operational readiness.

## Implemented controls

- `facility_registry` preserves source-specific assertions and emits a stable,
  sorted JSON snapshot; duplicate assertion identifiers fail closed.
- Reconciliation remains one-to-one and produces candidate/source-only
  dispositions without silently creating an authoritative facility record.
- Spatial snapshot comparison retains added, removed, attribute and geometry
  change classes with content hashes.
- Preservation and archive workflows retain source bytes separately from
  derived products and require explicit provenance links.
- Archive manifests can be checked with a root-scoped digest verifier that
  rejects traversal, missing files and content mismatches without mutating
  the archive.

## Remaining qualification evidence

- authoritative custodian confirmation is outside this public-only scope;
- freshness, completeness and national coverage are not implied;
- restore/rollback, long-running soak and incident ownership evidence remain
  required before operational or stable-v1 claims;
- emergency-health pilot outputs remain regional, research-only and
  non-operational.

The panel may review these controls, but a passing local test is not evidence
of production service-level objectives.
