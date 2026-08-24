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
| `CANONICAL-CONTRACTS-20260801` | Versioned schemas, context, ontology descriptor, fixtures and identity tests | `schemas/canonical-crosswalk.schema.json`, `docs/ontology/`, `fixtures/canonical-crosswalk-golden.json`, `tests/test_canonical.py`, `tests/test_lineage_identifiers.py` | Python structural/semantic checks pass; SHACL and broader external-client qualification remain pending |
| `CANONICAL-TYPESCRIPT-BINDING-20260821` | Generated non-Python binding and golden-fixture round trip | `bindings/typescript/`, `scripts/generate_canonical_bindings.py`, `conformance/v1/corpus.json`, `tests/test_canonical_bindings.py`, `tests/test_conformance_parity_receipt.py` | Generated declarations are schema-drift checked; Python and Node reproduce the golden crosswalk digest and structural outcome. Full JSON Schema, SHACL, external-client and stable compatibility qualification remain open |
| `CANONICAL-CROSS-LANGUAGE-PARITY-20260824` | Preserved bounded Python/Node parity receipt for the language-neutral corpus | `docs/ontology/canonical-cross-language-parity-20260824.json`, `scripts/verify_conformance_parity.py`, `tests/test_conformance_parity_receipt.py` | Five corpus cases pass in both runners; SHACL, external-client and stable qualification remain open |
| `CANONICAL-BOUNDED-SHACL-20260824` | Shape-drift and required-property contract for the published Crosswalk SHACL input | `src/riopa_provenance/canonical.py::validate_bounded_shacl_constraints`, `tests/test_conformance.py`, `docs/canonical-crosswalk-validation.md` | Dependency-free bounded contract and negative tests pass; this is not a full RDF/SHACL engine report |

## Blocking defects and gates

- `shacl-conformance-report` — pending qualifying SHACL engine/report.
- `ontology-publication-identifier` — pending publication decision and persistent identifier.
- `domain-agent-panel-qualification` — pending orchestrated semantic/domain agent-panel qualification.
- `migration-compatibility-qualification` — pending compatibility matrix and migration execution.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Governance analyst, API/schema analyst, Data-governance analyst, External-user workflow analyst.

This index is deliberately non-assertive while the track remains `validating`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.

## Review record

- Review scope: repository diff from `d5dee91` through `913f683`.
- Findings: the TypeScript binding was deterministic and bounded correctly, but
  its README described the local `--check` flag as the hosted CI mechanism.
- Review fixes: SHACL shape preparation remains digest-bound and `not-run`; the
  binding README now distinguishes hosted pytest enforcement from local checking.
- Validation: canonical/conformance tests and roadmap validation passed.
- External gates remain open; the track is not complete or archive-eligible.
