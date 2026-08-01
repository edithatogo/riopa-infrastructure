# Open issue → Conductor track → evidence matrix

This snapshot is the repository-owned planning index for the 146 open GitHub issues observed on 2026-08-01. The machine-readable source is [`open-issue-track-evidence-matrix-20260801.json`](open-issue-track-evidence-matrix-20260801.json).

## Current counts

| Dimension | Count |
|---|---:|
| Open issues | 146 |
| Track-parent issues | 28 |
| `v1-critical` issues | 29 |
| Implementation issues | 84 |
| Validation issues | 29 |

Release labels: 0.3.0 (25), 0.4.0 (15), 0.5.0 (10), 0.6.0 (25), 0.7.0 (15), 0.8.0 (31), 0.9.0 (15), 1.0.0 (6).

The matrix is intentionally descriptive rather than a closure mechanism. An issue is only closeable when its linked Conductor track and content-bound evidence satisfy the applicable release gate. The WP-010 bounded pilot is panel-validated for its regional, public-datasets-only, non-operational scope; this does not promote unrelated tracks.

## Refresh command

```sh
gh issue list --state open --limit 300 \
  --json number,title,labels,body,url
```

The `riopa-issue-key` marker in issue bodies is the preferred join key. Where it is absent, use the Conductor track key in the title prefix and manually confirm the join before changing issue state.

## Blocker handling

- `implementation`: implement and test the linked track.
- `validation`: produce content-bound test, reproduction, benchmark or review evidence.
- `operational`: complete resilience, restore, rollback, monitoring or support evidence.
- `governance_or_rights`: preserve decision, scope, provenance and correction/withdrawal evidence.
- `reference`: keep claims bounded to the approved public pilot and record limitations.

The public-source authority approval applies to the currently declared scope. Any expansion to national, operational, clinical or authoritative claims requires a new decision record.
