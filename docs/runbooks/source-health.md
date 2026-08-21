# Source-health runbook

Trigger this runbook when a source is missing, degraded, changed, or outside
its declared freshness window.

1. Freeze incorporation and retain the failed observation and source locator.
2. Confirm the exact source revision, capture policy, rights record, and last
   known-good receipt.
3. Retry only within the bounded policy; never substitute a live or unrelated
   source for the failed capture.
4. Record a successor observation, disposition, owner, and expiry.

Stop conditions: unknown rights, an unbound revision, repeated failure, or an
unapproved scope change. Missing health is `unknown-not-healthy`.
