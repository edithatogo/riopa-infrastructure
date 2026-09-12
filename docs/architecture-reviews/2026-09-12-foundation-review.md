# Foundation architecture review — 2026-09-12

Evidence ID: `urn:riopa:evidence:foundation-review:2026-09-12`
Track: `foundation_architecture_20260718`
Issue: [#14](https://github.com/edithatogo/riopa-infrastructure/issues/14)

## Scope and disposition

Review base: `f2159611c376246c18377325dad4388c34745781` from refreshed
`origin/main`. The earlier working checkout was at `60331ff` with unrelated
operations changes; this review uses a separate worktree and preserves them.
The foundation has no declared upstream track dependency.

The historical experimental M2 baseline is confirmed for its exact recorded
revision. Current inventory drift is repaired by this review; this is neither a
new maturity promotion nor an assertion that every current component is qualified.
The track remains **validating / M2**, with final **M6 closure blocked**.

Historical ratification, promotion, release evidence and panel records are not
rewritten. The historical all-M1 inventory and hosted passes are now labelled
as revision-specific observations. Target 0.3.0 readiness is evaluated separately
from foundation's M6 completion criteria.

## Findings and remediation

| Finding | Disposition |
|---|---|
| C.3 checked despite four unresolved M3–M6 blockers | Reopened C.3; added explicit M3–M6 qualification tasks. Historical bounded M1 audit retained. |
| Schema ownership matrix covered only 17 of 37 current schemas | Completed the matrix and enforced inventory coverage, unique rows and nonempty owner/policy/migration fields in architecture validation. |
| Governance prose implied a second human and external agent reports | Aligned with distinct advisory agent lenses and sole-developer disposition; factual external receipts and authority remain separate. |
| ADR review status and M1 inventory blurred historical/current evidence | Clarified bounded completed reviews versus later candidate qualification and current metadata. |
| M2 promotion index presented historical 0.3.0 gate state as current | Preserve the original receipt; direct current readiness claims to the live evaluator. |

The root reviewer audited lifecycle, authority and hosted evidence. The separate
`foundation_audit` agent reviewed R01–R05 ownership and governance traceability,
identifying the matrix gap and policy contradictions. These are repository-owned
advisory findings, not independent external qualification or owner approval.
Implementation fixes are exercised by negative regression cases; final candidate
panel requirements remain open. No manifest-selected platform guide was identified
for this change; platform-guide assessment is not applicable. General and Markdown
style guides apply to the changed files.

## Requirement and acceptance traceability

| Requirement | Contract and executable evidence | Qualification boundary |
|---|---|---|
| R01 authoritative component responsibilities | `docs/architecture.md`, `docs/v1-scope-and-boundaries.md`; architecture fitness validation in `src/riopa_provenance/roadmap.py` | Experimental federated boundaries; adapters still need their own integration evidence. |
| R02 owner, compatibility and migration | `docs/contract-ownership-matrix.md`, `docs/v1-release-policy.md`; matrix coverage guard and mutation tests in `tests/test_roadmap_hardening.py` | Inventory completeness does not prove every migration or third-party standard conforms. |
| R03 decisions and exceptions | `docs/adr/README.md`, governance policy, immutable M1 ratification and M2 promotion receipt; roadmap gate/waiver validation | ADR 0005/0006/0009/0011 remain explicitly deferred with owners and conditions/dates. Deferral is not approval. |
| R04 safe parallel implementation | Critical-path rule in `conductor/tracks.md`, synthetic/interface scope in foundation spec | Proceed against explicitly bounded experimental contracts; final dependency closure still required. |
| R05 platform versus data/study claims | `docs/v1-scope-and-boundaries.md`, release policy and machine-readable maturity/release gates | Software release readiness cannot confer source authority, coverage, scientific validity or release approval. |

Acceptance disposition: ADR ownership/deferral, track ownership and acyclic graph
validation, bounded advisory analyses and deterministic issue/status generation
have repository evidence. Stable scope/support/authority approval and later
candidate qualification remain open. Spec acceptance checkboxes are not marked
complete merely from existence of these documents.

## Contracts available to downstream implementation

- Component responsibilities and independent code/schema/source/snapshot/model/
  research-object version axes are usable as experimental architecture contracts.
- Captures require preserved bytes or a preservation reference and a digest;
  successful HTTP alone is insufficient. Transformations declare parents and
  complete/partial/failed outputs.
- Released snapshots and event identities are immutable; repairs and corrections
  create separately evidenced successors. Database/graph/materialisation outputs
  are projections, not replacement archival truth.
- Publication facts derive from manifest evidence. Rights and authority checks
  remain fail-closed; public availability alone is insufficient.
- Synthetic solver/interface work may proceed with explicit assumptions and
  frozen bounded inputs while real sources are acquired. A downstream consumer
  must run its own versioned contract and failure tests before making claims.

This permits implementation; it does not certify road/timetable adapters,
national coverage, stable APIs, clinical use or a publication decision.

## Remaining closure register

| Gate / owner | Exact next action and required closure evidence | Boundary |
|---|---|---|
| M3 — programme owner with capture/archive/schema/provenance maintainers | Build a version-addressed cross-track traceability packet for representative real integrations; include source rights/versions, input/output hashes, migrations, positive/negative/failure results and clean rebuild commands. Reuse valid existing receipts after checking candidate applicability. | Repository integration work can proceed; credentials and exact-source rights must be established before dependent live acquisition. |
| M4 — operations maintainer with programme owner | Reconcile existing campaign ledgers and fix failed cumulative aggregation before claiming sustained operation. Supply required cycles/duration, SLO/incident evidence, agent-operated workflows and bounded compatibility changes for the supported versions. | Hosted execution must be authorized; elapsed evidence cannot be synthesized or inferred from a green local test. |
| M5 — release/security/performance/operations maintainers and advisory panel | Freeze the exact inventory/candidate; bind security, performance, restore and role-separated panel reports to it; resolve findings and complete the required actual RC soak. | Panel is advisory. Candidate changes require evidence applicability review; shared beta/RC criteria come from release contracts. |
| M6 — accountable sole owner/release authority with maintainers | Record supported versions, roster/support commitments, signed and preserved artifact receipts, isolated clean-room reproduction, exact-scope release decision and post-release verification. | Prepare the complete hash-bound decision package first. Signing credentials, publication, announcement and accountable approval are not granted by this review. |

All four stable blocker IDs and maturity thresholds in metadata remain unchanged.
The next foundation action is the M3 traceability packet; it depends on representative
cross-track integration evidence, not more baseline-ratification prose. Stable
publication and post-release verification cannot be completed as part of this
bounded architecture audit.

## Hosted evidence observed in this review

- [PR #614](https://github.com/edithatogo/riopa-infrastructure/pull/614) is merged
  as `ee185a9947f45c2fe411d55793ac66b5f9073ec4`; its recorded head is
  `61ae22f5d9a8a1fa45c3f7745b41c7f173684119`.
- [CI 32949281831](https://github.com/edithatogo/riopa-infrastructure/actions/runs/32949281831)
  and [CodeQL 32949281893](https://github.com/edithatogo/riopa-infrastructure/actions/runs/32949281893)
  both report completed/success at that exact head. Historical 1,149 tests and
  92.68% coverage remain historical receipt values, not this review's measurements.
- [Hosted campaign 34629491783](https://github.com/edithatogo/riopa-infrastructure/actions/runs/34629491783)
  reports failure at base `f2159611c376246c18377325dad4388c34745781`.
  Its bounded lane and receipt-schema steps passed, but cumulative fail-closed
  campaign-ledger construction failed. Root cause and recovery are an operations
  follow-up; this review does not claim campaign qualification.
- Issue #14 remains open. No provider, clinical, publication or release-authority
  decision is inferred from these GitHub observations.

## Validation

The first full run found a historical-digest assertion comparing the August
emergency-health receipt against mutable current roadmap source/tests. All six
receipt digests were verified at the pinned pre-review base `f2159611c376246c18377325dad4388c34745781`.
The test now verifies those historical bytes with `git show`; CI already fetches
full history. Missing history fails closed. The receipt itself is unchanged and
current architecture behaviour is tested separately. This is a required regression
repair, not requalification or promotion of the emergency-health pilot.

Final local results (Python 3.14.6; frozen dev/spatial/preservation environment):

- `uv run pytest --cov=riopa_provenance --cov-branch --cov-report=term --cov-fail-under=90`:
  **1,967 passed, 1 skipped; 90.64% branch-aware coverage**, 60.90 seconds.
- `bash scripts/ci_quality.sh`: passed lint/format, strict types, security scans,
  action/workflow policy, schema/source/roadmap/evidence validation, deterministic
  issue regeneration, packaging, Twine and CycloneDX validation. An initial E501
  formatting finding was corrected before this successful run.
- `bash scripts/ci_reproducibility.sh`: passed deterministic rebuild/checksum checks.
- `uv run riopa roadmap validate --root .`: passed. Current 0.3.0 evaluator is ready;
  later release gates remain separate and this does not approve release.
- Final advisory re-review: no blocking correctness or evidence-boundary finding.
- Functional repair commit: `e77bc5ba5dca9d661bf1654b9af1567fe03dd2ba`. Hosted checks for this successor are not
  covered by historical M2 runs; consult this change's PR exact-head checks.

The first full attempt lacked the preservation extra and failed collection; it
was corrected to the existing CI environment. The next run exposed the historical
hash coupling described above. Only the final full result is reported as passing.
No source payload, provider action, live campaign, publication or release was
performed. Related repositories were not modified.
