# Release-decision readiness projection

[`release-decision-readiness-20260801.json`](release-decision-readiness-20260801.json)
reconciles the panel template manifest with the open issue/track evidence
matrix. It intentionally reports `release_ready: false`: every track has
pending panel qualification and release authority, and tracks absent from the
issue matrix are explicitly marked as blockers. This is a planning projection,
not a release decision or a substitute for content-bound evidence.

Regenerate with:

```sh
uv run python scripts/generate_release_decision_readiness.py
```
