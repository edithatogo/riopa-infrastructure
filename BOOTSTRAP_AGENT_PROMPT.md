# RIOPA Codex bootstrap prompt

This file remains for compatibility with earlier handoffs. The authoritative persistent instructions are now:

- `AGENTS.md`
- `CODEX_AUTONOMOUS_IMPLEMENTATION.md`
- `START_HERE.md`

A coding agent working in this repository must execute, not merely describe:

```bash
bash scripts/bootstrap_codex_handoff.sh --apply --clone-missing
```

It must then read `.riopa-local/codex/ACTIVE_PROMPT.md` and `.riopa-local/codex/NEXT_WORK_PACKAGE.md` and continue implementation autonomously. All safety, Git, related-repository, provenance, quality, rights and release rules in `AGENTS.md` apply.
