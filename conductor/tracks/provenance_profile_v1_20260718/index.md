# Evidence index: Shared provenance, transformation and quality profile v1

- **Track ID:** `provenance_profile_v1_20260718`
- **Status:** `validating`
- **Target release:** `0.3.0`
- **Current maturity:** `M2`
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
| `PROVENANCE-COMPATIBILITY-DRAFT-20260825` | Versioned compatibility matrix and executable migration fixture | `docs/provenance-profile-compatibility-matrix-20260825.json`, `docs/provenance-profile-migration-1.0.0-to-1.1.0.json`, `tests/test_conformance.py` | Additive bounded migration is validated; publication identifier, stable profile, signed attestation and independent qualification remain open |
| `PROVENANCE-PROJECTION-SHAPES-20260824` | Fail-closed shape validation for generated PROV and OpenLineage projections | `src/riopa_provenance/crate.py:validate_provenance_projections`, `tests/test_crate.py` | Bounded projection envelopes and duplicate-entity handling pass; standards semantic qualification and signed attestation remain open |
| `PROVENANCE-CONFORMANCE-CONTRACT-CLOSEOUT-20260825` | Repository-owned bounded projection-shape and positive/negative/round-trip conformance suite | `src/riopa_provenance/crate.py`, `tests/test_crate.py`, `tests/test_validation_failures.py`, `tests/test_conformance_parity_receipt.py` | Bounded checks and Python/Node parity receipt pass; semantic-loss qualification, trusted signed attestation and full-profile qualification remain open |
| `PROVENANCE-MIGRATION-CONTRACT-CLOSEOUT-20260825` | Repository-owned additive profile compatibility matrix and migration fixture | `docs/provenance-profile-compatibility-matrix-20260825.json`, `docs/provenance-profile-migration-1.0.0-to-1.1.0.json`, `tests/test_conformance.py` | Migration contract passes; publication identifier, signed attestation, independent qualification and stable release remain open |
| `PROVENANCE-PANEL-QUALIFICATION-20260825` | Bounded four-lens agent-panel qualification of the provenance profile and migration contract | `docs/provenance-profile-panel-qualification-20260825.json`, `tests/test_provenance_profile_panel_qualification.py` | Repository evidence is qualified for bounded scope; non-Python parity, semantic-loss, publication, signed-attestation and authority gates remain open |
| `PROVENANCE-V1-CANDIDATE-FREEZE-20260825` | Digest-bound unsigned candidate freeze for the native profile, compatibility, migration, panel and TypeScript artifacts | `docs/provenance-profile-v1-candidate-freeze-20260825.json`, `tests/test_provenance_profile_candidate_freeze.py` | Candidate integrity passes; trusted signature, full semantic/non-Python, publication, isolated role-separated clean-room agent reproduction and authority gates remain open |
| `PROVENANCE-M2-PROMOTION-20260827` | Exact-tree event, hashing, retry, lineage, assistance, negative-fixture, Python/Node parity, projection, migration and candidate evidence | `docs/provenance-m2-promotion-20260827.json`, `tests/test_provenance_m2_promotion.py`, [PR #619](https://github.com/edithatogo/riopa-infrastructure/pull/619) | Promoted to experimental M2 only; representative integration, repeated external use, RC qualification, publication, isolated role-separated clean-room agent reproduction and stable authority remain open |

## Repository-owned closeout slice (2026-08-24)

The native provenance contract, Python/Node corpus parity and bounded PROV /
OpenLineage projection-shape validator are linked above and pass
`bash scripts/ci_quality.sh` at protected `main` revision
`ed69976d815f064843c3492fa2045807381857ca`. The projection validator is
intentionally structural: native RIOPA events remain normative, and standards
semantic conformance, signed attestation, publication and agent-panel
qualification remain open.

## Blocking maturity gates

- M3 requires representative real-data/cross-runtime conformance and migration
  and failure-handling evidence.
- M4 requires repeated external profile use and SLO evidence.
- M5 requires RC semantic, security, recovery, agent-panel and soak qualification.
- M6 requires a stable published identifier, signed attestation, independent
  isolated role-separated clean-room agent reproduction and accountable stable-release authority.

The repository-owned executable and negative tests, bounded Python/Node parity,
projection validation, migration fixture, agent-panel advice and digest-bound
candidate satisfy this experimental M2 boundary only. Both dependencies are M2;
dependency maturity remains evaluated separately at later thresholds.

## Repository-owned implementation slice (2026-08-25)

The compatibility matrix and migration fixture define an additive, optional
facet change from profile 1.0.0 to 1.1.0 and are validated by the Python
contract suite. They are a bounded draft only: they do not claim a published
profile, non-Python round-trip, semantic-loss qualification, signed attestation
or release-authority approval.

## Decisions, exceptions and limitations

- This is a single-developer repository. Role-separated subagent panels provide
  the repository clean-room reproduction evidence but cannot substitute for
  trusted signing, external-system receipts or accountable release-authority
  approval.
- PROV and OpenLineage files are interoperability projections, not source
  truth or proof of standards certification.
- The bounded public, non-operational technical-preview scope remains in
  force; missing non-Python, signed and publication evidence is pending.

## Review and handover

Required agent-panel lenses: API/schema analyst, Provenance analyst, Security analyst, Research-object analyst.

This index is deliberately non-assertive while the track remains `validating`
at experimental M2. Status may advance only through `conductor/workflow.md`;
evidence must be immutable or version-addressed, agent-panel qualified where
required, and sufficient for the applicable later release gates.

## Review record

- Review scope: track implementation changes through `ef25920`.
- Finding: projection and round-trip tasks must remain partial while signed
  attestation and non-Python parity are not evidenced.
- Fix: task states changed to `[~]`; blockers remain explicit above.
- Validation: focused provenance tests and full roadmap validation passed.

The track remains `validating` at M2 and is not complete or archive-eligible.
The exact-tree promotion closes only the experimental executable-proof boundary;
M3-M6 integration, operation, RC, publication, reproduction and authority gates
remain open.
