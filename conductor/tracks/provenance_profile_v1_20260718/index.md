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
| `PROVENANCE-MAPPING-20260801` | Native evidence mapping, semantic classification and migration boundaries | `docs/provenance-profile-mapping-inventory-20260801.md`, `docs/provenance-and-lineage.md` | Repository-owned baseline complete; external parity/review gates remain open |
| `PROVENANCE-CONTRACT-20260801` | Canonical event, retry, lineage and projection contracts | `schemas/provenance-event.schema.json`, `src/riopa_provenance/validation.py`, `src/riopa_provenance/crate.py`, tests | Python validation and projections pass; non-Python and signed-attestation evidence remains pending |

## Blocking defects and gates

- Non-Python validator/model parity and round-trip evidence.
- Independent PROV/OpenLineage semantic-loss review.
- Stable profile publication identifier, migration/deprecation release evidence.
- Signed v1 attestation and independent review.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required reviewer roles: API/schema reviewer, Provenance reviewer, Security reviewer, Research-object reviewer.

This index is deliberately non-assertive while the track remains `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
