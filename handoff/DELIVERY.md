# Codex handoff delivery contract

The downloadable ZIP is intended to be copied into an otherwise ordinary workspace folder and opened by Codex with the separate covering brief.

It contains:

- the full RIOPA working tree;
- `.git/` with reconstructed artifact history;
- an ignored `handoff/riopa-infrastructure.bundle` fallback containing the same refs;
- root `AGENTS.md` and `CODEX_AUTONOMOUS_IMPLEMENTATION.md` instructions;
- guarded local/GitHub/Project/issue bootstrap automation;
- related-repository discovery configuration;
- a machine-local implementation queue and continuation protocol.

The bootstrap must not be treated as a release qualification. It creates or reconciles the software/control-plane repository, then continues implementation against the Conductor stable-v1 programme.

## Expected local sequence

1. Safely extract the ZIP.
2. Verify that `riopa-infrastructure/.git` exists, or allow the included bootstrap to restore it from the bundle.
3. Read `AGENTS.md` and `CODEX_AUTONOMOUS_IMPLEMENTATION.md`.
4. Run `bash scripts/bootstrap_codex_handoff.sh --apply --clone-missing`.
5. Continue with `.riopa-local/codex/NEXT_WORK_PACKAGE.md`.
6. Commit and normally push each coherent verified increment.

## Expected remote sequence

- create or reuse `edithatogo/riopa-infrastructure`;
- verify and wire `origin` without force;
- push the reconstructed history on `main`;
- configure conservative repository and Actions defaults;
- create/reconcile the Project, fields, labels, epic, track issues, phase issues, dependencies and configured cross-repository issues;
- write returned references into Conductor records;
- continue implementation rather than ending after remote setup.
