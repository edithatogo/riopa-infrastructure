# Exact-plan-bound publication recovery

This repository-owned WP-003 slice belongs to issue #129 and publication
validation task 2.2. It does not publish or contact a provider.

`build_publication_resume_plan(plan, state, receipts=())` binds a restored
journal to the caller's exact ready publication plan before reconciling receipts.
Internal journal integrity alone cannot establish this correspondence: a
resealed journal with an omitted target could otherwise appear consistent.

The projection requires matching publication identity, canonical plan digest,
exact target membership and derived operation keys. It rejects malformed
identity/hash/target bindings, non-ready plans, stale journals and conflicting
receipts. It does not validate the full publication-plan schema. The caller must
supply the intended plan; a content digest is not a signature, a current rights
review or authentication of the caller's choice.

Targets are sorted deterministically and classified as either
`receipt-recorded` or `provider-reconciliation-required`. A missing local receipt
does not mean a remote operation failed: a provider may have accepted a deposit
before the response or journal write was lost. A provider adapter must inspect
remote state and reconcile the existing operation before deciding whether any
new remote write is appropriate. The projection authorizes no remote writes.

The result binds the input and reconciled journal digests and contains detached
reconciled state. Repeated identical inputs produce the same projection;
conflicting receipts fail without mutating the supplied plan, journal or batch.
Existing journal formats and their standalone validation API remain compatible.

Validation is covered by `tests/test_publication.py`, including omitted and
injected targets, a different exact plan, partial/all-target recovery, receipt
conflicts, ordering and input immutability. Local journal status `published`
means all planned receipts are recorded and internally validated; it does not
prove provider acceptance, immutable remote bytes, a DOI or release approval.

WP-003 remains partial. Generalized authenticated provider reconciliation and
conflict/recovery acceptance across GitHub, Hugging Face and Zenodo remain open.
No track is archived or promoted by this bounded recovery contract.

## Local validation and review

Python 3.14.5: 75 focused publication/staging tests pass. The full suite passes
1,814 tests with one skip and 90.60% branch-aware coverage against the 90% gate.
The full engineering quality harness passes, including strict types, lint,
security, Conductor/issue-graph validation and packaging. One implementation
subagent and two independent review subagents checked this slice; the review
clarification about full-schema validation is incorporated above. Hosted checks
remain a separate delivery requirement.
