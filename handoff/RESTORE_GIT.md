# Restoring Git metadata

The preferred ZIP includes `.git/`. When an extraction tool omits hidden files, restore the same history from the included bundle:

```bash
bash scripts/bootstrap_codex_handoff.sh --skip-github --skip-quality
```

The script verifies `handoff/riopa-infrastructure.bundle`, clones it to a temporary location, moves only the recovered `.git` metadata into this worktree, verifies the repository root and branch, and refuses to overwrite an existing `.git` path.

Manual recovery is also possible in a separate empty directory:

```bash
git clone handoff/riopa-infrastructure.bundle riopa-infrastructure-recovered
```
