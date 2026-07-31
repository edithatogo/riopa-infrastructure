# Evidence index: Versioned multi-source facility registry

- **Track ID:** `facility_registry_20260719`
- **Status:** `specified`
- **Target release:** `0.6.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Reference`
- **Risk / priority:** `High` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Methods and analytics lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/59

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-007-public-hospital-source-20260731` | Official certified public-hospital provider CSV is preserved with content hash, HTTP receipt, rights reference and source limitation | `evidence/wp007-real-slice/manifest.json`, `reports/wp007-bounded-real-slice.md` | Real single-source capture passes; multi-source reconciliation, coordinates, history and review metrics remain open |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required reviewer roles: Governance reviewer, Provenance reviewer, Data steward, Scientific reviewer.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
