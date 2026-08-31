# Hosted Tasman cycle metadata preservation

Track: `nz_spatial_archive_mvp_20260718`, issue #49, task 3.11.

`scripts/preserve_tasman_cycle_ledger.py` connects the offline ledger to the existing
Tasman publication workflow after source, derivative, run-provenance and comparison
verification. The workflow can follow a successful scheduled council run or execute
a manual replay; installing this step does not establish that either occurred.

Only the four bounded, shape-allowlisted metadata receipts and their observation
ledger are uploaded to the existing public dataset
`edithatogo/riopa-public-data-archive`, under
`operational/tasman-cycle-ledger/v1`. No raw payload directory is uploaded. The
current GitHub repository, main ref, run, attempt and code revision must match the
receipt context. The step alone receives its publication token; all readbacks are
anonymous and pinned to an immutable revision.

Each update atomically adds content-addressed receipt and ledger objects with a
head pointer. The commit uses the exact previously read parent revision. A conflict
reloads and revalidates the current ledger before recomputing, with at most four
attempts; it never retries stale head bytes against a newer parent. Existing
content-addressed objects must match and are not replaced. A missing head with
retained namespace history is an error, not permission to reset the ledger.

The first checkpoint starts from the current verified workflow receipts. The
checked-in historical offline baseline is not automatically imported because its
four receipt bytes are not part of that checkpoint. This distinction is explicit
in the preservation receipt. Repeated source runs do not become new cycles.

Limits are 100 ledger events, 2 MB per file, 16 MB of retained historical receipt
bytes and four parallel workers for final readback of at most six files. Dependent
head/history validation remains ordered. Council acquisition retains its existing
parallel source matrix. A successful commit followed by failed readback remains
unaccepted locally; retry verifies the committed checkpoint without duplicating it.
The Actions artifact retains sanitized local failure metadata. Prior local success
receipts are retained under distinct names rather than left as the current result.

The pure ledger still reports `three_cycle_gate_qualified=false`. Fixed-baseline
comparison is not adjacent-cycle change evidence; signed final hosted completion,
representative change/recovery and elapsed qualification remain separate work.
The existing same-repository/main/successful-matrix trigger is unchanged. A failed
matrix does not automatically promote a source-specific checkpoint.

Repository tests cover atomic updates, replay, concurrent writers, missing/corrupt
history, metadata-only boundaries, visibility, byte limits, safe failure paths and
commit/readback recovery. Hosted acceptance must be recorded separately after an
actual Actions execution; these fixtures do not establish provider acceptance.

## Hosted acceptance

`tasman-cycle-preservation-acceptance-20260831.json` records successful run
33360096774 on merged `ac984b7`, attempts 1 and 2. Both anonymously verified their
immutable public checkpoints; attempt 2 retained the first observation while
keeping one distinct source run. Original source and derivative receipts remain
byte-identical. The embedded in-progress publication observation is preserved;
final job completion was checked separately. These were manual replays, not
scheduled captures, adjacent-cycle changes or hosted outage/recovery exercises.
