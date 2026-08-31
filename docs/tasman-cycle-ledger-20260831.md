# Tasman offline cycle ledger

Track: `nz_spatial_archive_mvp_20260718` / issue #49.

`scripts/tasman_cycle_ledger.py` assembles metadata observations, not an operational
qualification certificate. The caller supplies four exact expected byte hashes for
the existing source publication, derivative publication, run provenance and fixed
baseline comparison receipts. Expected hashes must come from a trusted acceptance
record; computing them from arbitrary inputs does not authenticate those inputs.

`append_observation(ledger, documents, expected_sha256)` is offline and deterministic.
The two dictionaries use `provenance`, `comparison`, `source`, and `derived` keys;
documents contain bytes. Passing `None` starts a ledger. Each event names its preceding
event digest; new source runs also name the preceding distinct source run. Replaying
identical publication attempts is idempotent. New attempts remain separate outcomes
but do not increase the distinct-source-run count. Conflicting identities, changed
same-attempt evidence and out-of-order new captures fail closed.

The CLI takes `--provenance`, `--comparison`, `--source`, `--derived`, matching
`--NAME-sha256` flags, and a fresh `--output`. Optional `--ledger` requires its exact
`--ledger-sha256`. All inputs are bounded to 2 MB, ledgers to 100 events; symlinks,
path traversal, duplicate JSON keys and overwriting outputs are rejected. No network
access, publication, signing or workflow dispatch occurs. Persist working outputs
outside Git, retaining previous ledger bytes as immutable checkpoints. A reviewed,
metadata-only checkpoint may be committed as evidence; never commit source payloads.

`tasman-cycle-ledger-baseline-20260831.json` is such a checkpoint, constructed from
the four retained metadata receipts of accepted publication run 33345370638. It
records one source run (33301038921), zero scheduled automatic source runs and no
qualified cycle. This is offline evidence indexing, not another hosted execution.
Automatic collection and durable advancement of this ledger are not wired into
the scheduled workflow by this bounded offline implementation.

`record_rejected_attempt(ledger, attempt_id, error_class)` preserves a bounded local
validation failure without exception text. Restoring the original input and retrying
can produce the same deterministic successful observation. Such tests and entries
are explicitly local/synthetic, not evidence of hosted outage recovery.

Even three scheduled automatic observations leave `three_cycle_gate_qualified=false`.
The ledger consumes no signed final hosted-job completion evidence. The current
comparison describes change from the fixed initial accepted packet, not an adjacent
cycle. Verified hosted completion, adjacent change and operational recovery evidence
remain qualification gaps. Manual publication replays are explicitly ineligible;
source-run deduplication prevents retries being counted as extra cycles. Capture time
does not establish legal valid time, operative status or stable release readiness.
