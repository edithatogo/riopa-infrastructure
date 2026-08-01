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
| `WP-010-bounded-reconciliation-20260801` | Independent assertions retain source identity, coordinates, rights and authority class; deterministic matching preserves conflicts and requires accountable review | `src/riopa_provenance/facility_registry.py`, `tests/test_facility_registry.py`, `scripts/compare_wp010_facility_sources.py`, `reports/wp010-facility-source-sensitivity.md` | Reference implementation and bounded council/OSM sensitivity pass locally; no candidate is adjudicated or promoted to authoritative status |
| `WP-010-bounded-pilot-decision-20260801` | Pilot scope, source exclusions and publication conditions are explicit | `docs/wp010-bounded-pilot-decision.md` | Decision remains pending; rights-uncertain and metadata-only sources are excluded or deferred |

## Blocking defects

- Independent reproduction issue #149 has no reviewer response.
- National authoritative ambulance coverage, supermarket-source rights, reviewed performance
  estimates, preservation deposit and authorised release remain external gates.

## Decisions, exceptions and limitations

- The bounded comparison reports one 5.660 m candidate pair and three source-only assertions.
  It is not a national completeness, currency or accuracy estimate.
- Accountable review may be performed by a human or agent analyst; no separate-human rule applies.

## Review and handover

Required reviewer roles: Governance reviewer, Provenance reviewer, Data steward, Scientific reviewer.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
