# Corruption and integrity runbook

Trigger this runbook when a checksum, manifest closure, archive restore, or
projection invariant fails.

1. Preserve the failed bytes, receipt, logs, and digest as immutable evidence.
2. Fail closed and quarantine the affected artifact and every dependent
   projection.
3. Restore from the last verified independent target, then verify checksums,
   closure, provenance, and rights before rebuilding.
4. Issue a successor correction record; never overwrite or silently repair the
   failed evidence.

Stop conditions: no verified restore point, mismatched source locator, or an
unexplained digest change.
