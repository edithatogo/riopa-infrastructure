# Qualification evidence gap plan

**As at:** 2026-08-01  
**Scope:** public-datasets-only regional preview progressing toward beta, release candidate (RC) and stable v1.  
**Purpose:** map each remaining qualification gate to repository preparation, the evidence still required, and a fail-closed contingency. This is an execution plan, not a waiver or a change to the normative release policy.

## Decision options

| Option | Disposition | Consequence |
|---|---|---|
| A. Keep the regional technical preview while collecting evidence | **Recommended** | No higher-tier claim is made; time-based and accountable evidence can accumulate safely. |
| B. Qualify a narrow beta candidate | Conditional | Requires every beta prerequisite below, a frozen revision and a signed tier decision; unmet gates keep beta blocked. |
| C. Promote directly to RC/stable | Not recommended | Prohibited until all M5/M6 evidence, independent/external requirements and release-authority signatures are present. |

## Gate-to-evidence map

| Gate / blocker | Repository preparation and executable checks | Evidence still required for beta/RC/v1 | Contingency if evidence fails or is delayed |
|---|---|---|---|
| Normative inventory and conformance | `scripts/conformance_node.mjs`, `tests/test_conformance.py`, `tests/test_canonical.py`, `docs/ontology/canonical-conformance-manifest-1.0.0.json` | Frozen inventory, complete corpus, cross-language outputs and agent-panel disposition | Freeze affected vocabulary; fail closed on unmapped fields and narrow claims. |
| Security and supply chain | `scripts/build_sbom.sh`, `scripts/check_action_pins.py`, `scripts/check_workflow_policy.py`, hosted CodeQL/CI | Current SBOM, dependency/advisory review, signed attestations and zero prohibited findings | Block promotion; remediate or document only a time-limited permitted waiver. |
| Deterministic reproduction | `scripts/build_wp010_reviewer_bundle.py`, `scripts/validate_wp010_reproduction_record.py`, `scripts/ci_reproducibility.sh`, panel report | Two clean-room reproductions, including the qualifying external/operator path required by the normative policy | Retain panel output as rehearsal/preview evidence; keep higher-tier gate open. |
| Agent user/operator workflows | `docs/wp010-external-reproduction-handoff.md`, `docs/wp010-external-reproduction-report-template.md` | Two owner-authorized agent workflows with environment, deviations, adverse findings and disposition | Keep preview label until agent evidence, elapsed evidence and the owner's tier decision are recorded. |
| Operational beta period | Retry/capture/recovery tests: `tests/test_retry.py`, `tests/test_capture.py`, `tests/test_linz.py`, `tests/test_linz_inventory.py` | 90 consecutive representative days, three complete failure/backfill/recovery cycles, raw observations and incident records | Reset the clock after material failure; narrow workload or remain preview. |
| RC soak and capacity | Existing benchmark coverage: `tests/test_wp010_benchmark.py`; record runner/environment with each result | 30-day RC soak, national/reference workload, latency/throughput/resource/storage/cost measurements | Defer RC; publish measured envelope only, not unmeasured scale claims. |
| Restore, rollback, correction and withdrawal | `docs/adr/0010-operations-preservation.md`, publication consistency tests and preservation packet tooling | Executed drills with timestamps, raw logs, recovery point/object hashes and owner acknowledgement | Block promotion; preserve the failed drill and remediate runbooks before retry. |
| Provenance, fixity and publication | `tests/test_wp010_publication_consistency.py`, `scripts/build_research_object.py`, Zenodo successor `10.5281/zenodo.21737563` | Immutable identifiers, checksums, source/version metadata, generated-artifact lineage and independent verification | Create a successor packet; never mutate a published evidence object. |
| Defect and waiver policy | `uv run riopa roadmap validate`; `conductor/v1-gate.json` defect policy | Zero open P0/P1/release-blocking P2, zero critical security findings and no expired waivers | Fail closed; waiver cannot cover non-waivable categories. |
| Release authority | `docs/release-authority-decision-draft-20260801.md`, `docs/release-gate-evidence-matrix.md` | Named accountable signatories, scope/exclusions, expiry, rollback route and evidence index for each tier | No promotion; retain current approved preview and record the decision as pending. |

## Execution sequence

1. Freeze a candidate commit and dependency set; generate the machine-readable evidence index.
2. Run conformance, security, reproducibility and benchmark checks; attach immutable logs and hashes.
3. Start the 90-day beta evidence clock and record all three operating cycles, incidents and exclusions.
4. Run restore/rollback/correction/withdrawal drills and remediate any failed control.
5. After beta evidence is complete, freeze the RC and begin the 30-day soak with capacity/cost measurements.
6. Re-run all validators, verify evidence age and defect policy, then obtain the tier-specific signed decision.

## Review and stop conditions

The current approved posture remains regional, research-only, non-authoritative and non-operational. A source, scope or safety change creates a new candidate and reopens affected gates. Review this plan by **2026-08-31**, or sooner after any material change. Local green tests are preparation only; absence of an evidence artifact is a failing gate.
