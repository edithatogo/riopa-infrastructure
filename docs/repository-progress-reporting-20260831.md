# Repository progress reporting

Run `uv run python scripts/report_repository_progress.py` for a readable summary,
or add `--format json` for current tasks, blockers, archive evidence and portable
work-package dispositions. Both commands are read-only and make no network calls.

The report first runs native Conductor validation, including generated issue
drift checks. It reads active and archived track plans, counts top-level task
checkbox rows (not nested subtasks or fenced examples), and includes the current
and next pending tasks with source-file digests. Completed task counts are not
track maturity or release readiness.

The work-package view uses committed reconciliation evidence, not a developer's
machine-local routing overrides. The ordinary Codex orchestrator can still use
explicit local routing choices. Neither view changes track status or supplies
missing operational, preservation, signing or release-authority evidence.

Archive status describes the named recorded receipts, not live provider health.
The validated metadata-only cycle baseline is reported separately; it is a recorded
checkpoint, not an automatically refreshed view of GitHub runs.
Release readiness comes from the existing evaluator; time-limited waivers are
assessed at invocation time. With unchanged inputs and unchanged waiver validity,
the projection is repeatable. It is printed to stdout rather than maintaining
another checked-in status snapshot that can become stale.

Qualification remains a separate process: scheduled observations need actual
hosted evidence, and synthetic recovery tests do not manufacture elapsed cycles.
