# Capacity and cost runbook

Trigger this runbook when storage, runtime, concurrency, rate, or cost signals
breach their declared envelope.

1. Stop new promotion and bound concurrency, retries, and retention growth.
2. Preserve the measurement, workload manifest, revision, and cost context.
3. Reduce scope or schedule a reviewed continuation; do not silently drop
   records, relax integrity checks, or claim national-scale capacity.
4. Record the owner, mitigation, expiry, and revalidation result.

Stop conditions: unbounded spend, missing workload identity, data loss risk, or
an unapproved change to the supported envelope.
