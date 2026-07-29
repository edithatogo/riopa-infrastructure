# Architecture decision register

This register reconciles the v0.1 architecture decisions with the stable-v1
Conductor model. Individual ADRs remain the normative records of their
decisions and consequences.

| ADR | Topic | v1 disposition | Owner | Follow-up |
|---|---|---|---|---|
| 0001 | Repository ecosystem | accepted as the federated boundary model | Programme owner | Reconfirm after two external adoptions |
| 0002 | Provenance event log | accepted; v1 profile supersedes differing fields | Provenance maintainer | Publish compatibility mapping |
| 0003 | Materialisations | accepted; projections are not archival truth | Archive maintainer | Add cross-format rebuild evidence at M3 |
| 0004 | Bitemporal spatial versioning | accepted for the spatial reference implementation | Spatial maintainer | Add real-source migration evidence |
| 0005 | Knowledge-graph projection | deferred; optional, not a platform dependency | Architecture reviewer | Reassess after query benchmarks |
| 0006 | Standards profile | explicitly deferred pending conformance inventory | Interoperability maintainer | Revisit by 2026-10-31; issue `interoperability_conformance_sdks_20260719` |
| 0007 | Governance and rights | accepted as a fail-closed constraint | Governance reviewer | Ratify sovereignty review and exceptions |
| 0008 | Stable contracts/versioning | accepted; expanded by the v1 compatibility policy | API/schema reviewer | Add migration fixtures before M2 |
| 0009 | Security/trust model | explicitly deferred pending qualification evidence | Security reviewer | Revisit by 2026-10-31; issue `security_supply_chain_20260719` |
| 0010 | Operations/preservation | accepted as target architecture; claims deferred | Operations maintainer | Produce SLO, restore and fixity evidence |
| 0011 | v1 release authority | explicitly deferred pending named signatories and reproduction evidence | Release authority | Revisit by 2026-12-31; issue `v1_release_hardening_20260719` |

## Reconciliation rules

- “Accepted” records architectural direction, not maturity or release readiness.
- “Proposed” and “deferred” decisions remain open gates and cannot be treated
  as approvals by automated validation.
- A later ADR supersedes an earlier decision only when it names the earlier ADR,
  states compatibility impact and records a migration path.
- Normative contract changes require an ADR or amendment plus positive,
  negative and compatibility fixtures.

## Review state

This is an implementation artifact for the foundation track. Governance,
API/schema and external-user reviews remain outstanding and must be appended to
the track evidence ledger before closeout.
