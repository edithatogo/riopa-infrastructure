# Operational-readiness evidence inventory

**As at:** 2026-08-01  
**Scope:** repository-owned evidence for the public-datasets-only regional
technical preview.

This inventory makes the current operational evidence discoverable without
implying beta, release-candidate or stable qualification.  It records what is
exercised locally and what still requires time-based or accountable evidence.

## Repository-owned evidence

| Control | Evidence | Verification |
|---|---|---|
| Bounded network retries | Idempotency-aware retry policy, retry-after parsing and attempt limits | `tests/test_retry.py`; `tests/test_capture.py` |
| Circuit breaking | Threshold, cooldown and single half-open probe behaviour | `tests/test_retry.py`; `tests/test_capture.py` |
| Failure/quarantine handling | Transport and HTTP failure receipts remain content-addressed | `tests/test_capture.py`; capture receipt fixtures |
| Backfill isolation | Batches bound by item count and estimated bytes; unknown/oversize work is isolated | `tests/test_linz_inventory.py` |
| Recovery journal integrity | Corrupt or mismatched application journals are rejected | `tests/test_linz.py` |
| Publication consistency | Manifest, decision record and preservation identifiers are cross-checked | `tests/test_wp010_publication_consistency.py` |

The reproducible check for this inventory is:

```text
uv run pytest -q tests/test_retry.py tests/test_capture.py tests/test_linz.py \
  tests/test_linz_inventory.py tests/test_wp010_publication_consistency.py
```

## Evidence that remains open

The following cannot be established by the local test suite and remain
release-gating evidence under `docs/operations-slo.md` and
`docs/v1-release-gates.md`:

- 90 consecutive days of representative beta operation and three complete
  failure/backfill/recovery cycles;
- 30-day release-candidate soak and capacity/cost measurements;
- restore, rollback, correction and withdrawal drills with raw observations;
- named operational ownership, incident records and alert acknowledgement;
- national/reference workloads and any operational or authoritative claim.

Until those records exist, the repository must retain its regional,
research-only, non-authoritative and non-operational posture.  A green local
test run is necessary preparation, not a substitute for the time-based or
accountable evidence above.
