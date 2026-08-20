# Open issue → Conductor track → evidence matrix (2026-08-02)

This is a fresh, content-addressed reconciliation of the live GitHub open-issue
export. It covers all 28 registered Conductor tracks and 138 explicitly linked
open issues. The machine-readable source is
[`open-issue-track-evidence-matrix-20260802.json`](open-issue-track-evidence-matrix-20260802.json).

## Reconciliation result

| Measure | Result |
|---|---:|
| Open issues fetched | 146 |
| Registered Conductor tracks | 28 |
| Tracks with explicit linked issues | 28 |
| Tracks missing a matrix row | 0 |
| Issues outside a track marker | 8 |

Rows use the explicit `riopa-issue-key` marker and verified issue labels. They
are planning evidence only: they do not close issues, qualify a track, or grant
release authority. Eight unscoped issues (including the programme epic and
bounded-pilot decision/reproduction work) remain separately tracked.

## Fail-closed boundaries

- `M1/open` is not implementation or release completion.
- Panel qualification, external reproduction, operational cycles, RC soak and
  release-authority decisions remain independent gates.
- Missing, ambiguous or label-only classifications must be resolved with
  content-bound evidence before issue closure.

## Reproduction

```sh
gh issue list --state open --limit 300 --json number,title,labels,body,url > /tmp/open-issues.json
python scripts/reconcile_open_issue_matrix.py /tmp/open-issues.json docs/open-issue-track-evidence-matrix-YYYY-MM-DD.json --observed YYYY-MM-DD
```
