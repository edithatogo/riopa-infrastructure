# Evidence index: Shared provenance, transformation and quality profile v1

- **Track ID:** `provenance_profile_v1_20260718`
- **Status:** `active`
- **Target release:** `0.3.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Normative`
- **Risk / priority:** `Critical` / `P0`
- **V1 critical:** `yes`

Closeout sequence: `docs/foundation-provenance-connector-ontology-closeout-plan.md`.
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Core platform maintainer
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/8

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `PROVENANCE-MAPPING-20260801` | Native evidence mapping, semantic classification and migration boundaries | `docs/provenance-profile-mapping-inventory-20260801.md`, `docs/provenance-and-lineage.md` | Repository-owned baseline complete; non-Python parity and agent-panel qualification gates remain open |
| `PROVENANCE-CONTRACT-20260801` | Canonical event, retry, lineage and projection contracts | `schemas/provenance-event.schema.json`, `src/riopa_provenance/validation.py`, `src/riopa_provenance/crate.py`, tests | Python validation and projections pass; non-Python and signed-attestation evidence remains pending |
| `PROVENANCE-CONFORMANCE-20260801` | Bounded conformance status and explicit external-gate boundary | `docs/provenance-profile-conformance-manifest-1.0.0.json`, `tests/test_validation_failures.py` | Python positive/negative suites pass; non-Python parity and signed attestation remain not-run |
| `PROVENANCE-NONPYTHON-MODEL-20260822` | Bounded non-Python validator/model parity surface | `scripts/conformance_node.mjs`, `bindings/typescript/provenance-event-v1.d.ts`, `tests/test_conformance.py` | Node and Python agree on the language-neutral corpus; full profile parity, independent qualification and signed attestation remain open |
| `PROVENANCE-PROJECTION-SHAPES-20260824` | Fail-closed shape validation for generated PROV and OpenLineage projections | `src/riopa_provenance/crate.py:validate_provenance_projections`, `tests/test_crate.py` | Bounded projection envelopes and duplicate-entity handling pass; standards semantic qualification and signed attestation remain open |

## Repository-owned closeout slice (2026-08-24)

The native provenance contract, Python/Node corpus parity and bounded PROV /
OpenLineage projection-shape validator are linked above and pass
`bash scripts/ci_quality.sh` at protected `main` revision
`ed69976d815f064843c3492fa2045807381857ca`. The projection validator is
intentionally structural: native RIOPA events remain normative, and standards
semantic conformance, signed attestation, publication and agent-panel
qualification remain open.

## Blocking defects and gates

- Non-Python validator/model parity and round-trip evidence.
- PROV/OpenLineage semantic-loss agent-panel qualification.
- Stable profile publication identifier, migration/deprecation release evidence.
- Signed v1 attestation and orchestrated agent-panel qualification.

## Decisions, exceptions and limitations

- This is a single-developer repository. Agent panels may assess provenance
  packets, but cannot substitute for independent external reproduction or
  accountable release-authority approval.
- PROV and OpenLineage files are interoperability projections, not source
  truth or proof of standards certification.
- The bounded public, non-operational technical-preview scope remains in
  force; missing non-Python, signed and publication evidence is pending.

## Review and handover

Required agent-panel lenses: API/schema analyst, Provenance analyst, Security analyst, Research-object analyst.

This index is deliberately non-assertive while the track remains `validating`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.

## Review record

- Review scope: track implementation changes through `ef25920`.
- Finding: projection and round-trip tasks must remain partial while signed
  attestation and non-Python parity are not evidenced.
- Fix: task states changed to `[~]`; blockers remain explicit above.
- Validation: focused provenance tests and full roadmap validation passed.

The track remains `validating` at M1 and is not complete or archive-eligible
while the listed conformance, publication, attestation and agent-panel
qualification gates remain open.
