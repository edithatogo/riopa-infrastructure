# Evidence index: Canonical domain schemas, identifiers and ontology

- **Track ID:** `canonical_domain_schemas_ontology_20260719`
- **Status:** `validating`
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
| `CANONICAL-SEMANTIC-PANEL-20260825` | Bounded four-lens semantic qualification of canonical schemas, ontology and extension boundaries | `docs/canonical-semantic-panel-qualification-20260825.json`, `tests/test_canonical_semantic_panel_qualification.py` | Repository evidence is qualified for bounded scope; SHACL, publication, migration and external semantic gates remain open |
| `CANONICAL-EXTENSION-POLICY-20260825` | Bounded namespaced extension and migration policy | `docs/ontology/canonical-extension-policy-20260825.json`, `docs/ontology/canonical-extension-policy-20260825.md`, `tests/test_canonical.py` | Fail-closed policy is machine-checked; SHACL, publication, semantic panel and compatibility execution gates remain open |
| `CANONICAL-CROSS-LANGUAGE-PARITY-20260824` | Preserved bounded Python/Node parity receipt for the language-neutral corpus | `docs/ontology/canonical-cross-language-parity-20260824.json`, `scripts/verify_conformance_parity.py`, `tests/test_conformance_parity_receipt.py` | Five corpus cases pass in both runners; SHACL, external-client and stable qualification remain open |
| `CANONICAL-BOUNDED-SHACL-20260824` | Shape-drift and required-property contract for the published Crosswalk SHACL input | `src/riopa_provenance/canonical.py::validate_bounded_shacl_constraints`, `tests/test_conformance.py`, `docs/canonical-crosswalk-validation.md` | Dependency-free bounded contract and negative tests pass; this is not a full RDF/SHACL engine report |
| `CANONICAL-MIGRATION-CONTRACT-CLOSEOUT-20260825` | Repository-owned namespaced extension and additive migration policy | `docs/ontology/canonical-extension-policy-20260825.json`, `docs/ontology/migrations/canonical-crosswalk-1.0.0-to-1.1.0.json`, `tests/test_canonical.py` | Fail-closed policy validation passes; SHACL engine evidence, semantic qualification, compatibility execution and stable publication remain open |
| `CANONICAL-SHACL-EXECUTION-20260825` | Pinned SHACL runtime validates the digest-bound canonical golden fixture | `scripts/validate_canonical_shacl.py`, `docs/canonical-shacl-execution-report-20260825.json`, `docs/canonical-shacl-execution-contract-20260825.json`, `tests/test_canonical_shacl_execution.py`, `docs/ontology/canonical-conformance-manifest-1.0.0.json` | Repository-owned fixture conforms with inference disabled; external semantic qualification, cross-runtime compatibility, publication and authority remain open |
| `CANONICAL-V1-CANDIDATE-FREEZE-20260825` | Digest-bound unpublished candidate freeze for normative schema, ontology, SHACL input, migration and conformance fixtures | `docs/canonical-v1-candidate-freeze-20260825.json`, `tests/test_canonical_candidate_freeze.py` | Candidate integrity passes; SHACL execution, external-client, migration, semantic, publication and authority gates remain open |
| `CANONICAL-CLOSEOUT-EVIDENCE-20260825` | Link implementation, tests, review, migration and release-candidate evidence for the bounded canonical slice | `docs/canonical-closeout-evidence-20260825.json`, `tests/test_canonical_closeout_evidence.py` | Evidence categories are linked and fail-closed; semantic, publication, signing and authority gates remain open |

## Blocking defects and gates

- `shacl-conformance-report` — pending qualifying SHACL engine/report.
- `ontology-publication-identifier` — pending publication decision and persistent identifier.
- `domain-agent-panel-qualification` — pending orchestrated semantic/domain agent-panel qualification.
- `migration-compatibility-qualification` — pending compatibility matrix and migration execution.

## Repository-owned implementation slice (2026-08-25)

The canonical profile now has an explicit, versioned extension-policy draft:
unknown fields are preserved, normative fields cannot be shadowed, and
malformed extensions fail closed. This improves the bounded contract only; it
does not claim semantic qualification, publication or stable-v1 compatibility.

The 2026-08-25 closeout packet links the canonical implementation, test,
review, migration and unsigned candidate-freeze evidence. It does not advance
the track beyond M1 or make the candidate a published normative release.

The same revision’s Conductor regeneration receipt records the methods hash,
roadmap status, generated issue graph and full quality harness. This closes only
the bookkeeping task; it does not change the candidate’s maturity or external
semantic, authority and release gates (`docs/canonical-domain-conductor-regeneration-20260825.json`).

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
