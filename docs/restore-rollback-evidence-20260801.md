# Restore and rollback evidence (local drill)

This harness records deterministic, **local synthetic** restore and rollback
drills. It copies fixture directories, verifies a SHA-256 tree digest, and
materialises a prior state. It does not contact, modify, or assert anything
about an operational deployment.

Run the evidence tests with `uv run pytest tests/test_recovery.py -q`.

Status as of 2026-08-01:

* Local snapshot/restore and rollback controls: **executed-local** (automated
  tests in `tests/test_recovery.py`).
* Production, hosted, disaster-recovery and operator rollback evidence:
  **pending**. The local drill is not a substitute for time-based beta/RC
  qualification or national-scale recovery evidence.
* Any promotion must attach raw logs, timestamps, recovery-point/object hashes,
  and an accountable release decision; a failed drill resets the qualification
  clock according to `docs/qualification-evidence-gap-plan-20260801.md`.
