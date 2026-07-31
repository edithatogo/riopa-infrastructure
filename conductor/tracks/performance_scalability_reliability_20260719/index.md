# Evidence index: Performance, scalability and reliability qualification

- **Track ID:** `performance_scalability_reliability_20260719`
- **Status:** `specified`
- **Target release:** `0.9.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Operational`
- **Risk / priority:** `Critical` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Release manager
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/134

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-004-resource-envelopes-20260731` | Every sharded archive job has enforced storage and egress ceilings | `src/riopa_provenance/linz_pipeline.py`, `src/riopa_provenance/linz_inventory.py`, `tests/test_linz_pipeline.py`, `tests/test_linz_inventory.py` | Boundary and overrun tests pass; national-scale benchmark remains open |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required reviewer roles: Performance reviewer, Operations reviewer, Security reviewer, Data steward, Quantitative methods reviewer, External user reviewer.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
