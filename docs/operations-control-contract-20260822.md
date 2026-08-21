# Operations-control contract (bounded preview)

`docs/operations-control-contract-20260822.json` defines the repository-owned
semantics for scheduled jobs, retries, partial failure, quarantine,
backpressure, service-level indicators and incident handling. The JSON record
is intentionally marked `candidate-not-measured`: it defines how evidence will
be calculated and does not claim that a target has been met.

The contract is compatible with the existing retry/capture/health and hosted
campaign controls. Every retry is bounded and idempotency-aware; partial or
ambiguous output is diagnostic and fail-closed; quarantine release requires
review; and upstream exclusions are counted rather than silently removed.

This is repository-owned preparation only. It does not close the beta elapsed
period, RC soak, production restore/DR, national-scale, external-participant,
preservation or release-authority gates.
