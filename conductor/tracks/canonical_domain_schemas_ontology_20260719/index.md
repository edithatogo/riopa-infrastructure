# Evidence index: Canonical domain schemas, identifiers and ontology

- **Track ID:** `canonical_domain_schemas_ontology_20260719`
- **Status:** `active`
- **Target release:** `0.3.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Normative`
- **Risk / priority:** `High` / `P0`
- **V1 critical:** `yes`

Closeout sequence: `docs/foundation-provenance-connector-ontology-closeout-plan.md`.
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Core platform maintainer
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/2

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-005-projection-reconciliation-20260731` | Deterministic stale-node removal preserves identities referenced by authoritative manifest edges | `src/riopa_provenance/lineage.py`, `tests/test_lineage.py`, `docs/change-and-impact-queries.md` | Synthetic relational projection fixture passes; normative schema/ontology migration evidence remains open |
| `CANONICAL-INVENTORY-20260801` | Entity, identity, collision and extension inventory | `docs/canonical-domain-inventory-20260801.md`, `src/riopa_provenance/canonical.py`, `tests/test_canonical.py` | Repository-owned baseline complete; SHACL, non-Python and domain-owner gates remain open |
| `CANONICAL-CONTRACTS-20260801` | Versioned schemas, context, ontology descriptor, fixtures and identity tests | `schemas/canonical-crosswalk.schema.json`, `docs/ontology/`, `fixtures/canonical-crosswalk-golden.json`, `tests/test_canonical.py`, `tests/test_lineage_identifiers.py` | Python structural/semantic checks pass; SHACL and non-Python round-trip remain pending |

## Blocking defects and gates

- `shacl-conformance-report` — pending qualifying SHACL engine/report.
- `non-python-round-trip` — pending independent non-Python runtime evidence.
- `ontology-publication-identifier` — pending publication decision and persistent identifier.
- `domain-owner-review` — pending independent semantic/domain review.
- `migration-compatibility-qualification` — pending compatibility matrix and migration execution.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required reviewer roles: Governance reviewer, API/schema reviewer, Data steward, External user reviewer.

This index is deliberately non-assertive while the track remains `validating`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.

## Review record

- Review scope: repository diff from `d5dee91` through `1ac750a`.
- Findings: no correctness, security, metadata or digest-integrity defects.
- Review fixes: SHACL shape preparation is digest-bound and explicitly remains
  `not-run` until a qualifying engine/report exists.
- Validation: canonical/conformance tests and roadmap validation passed.
- External gates remain open; the track is not complete or archive-eligible.
