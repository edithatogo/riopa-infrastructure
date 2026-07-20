# RIOPA repository handoff prompt

Paste the text below into a coding agent that has shell access to the folder containing the RIOPA ZIP. The agent must execute the work, not merely describe commands.

---

You are the implementation and repository-bootstrap agent for the RIOPA programme. Work directly in the current folder. It contains a RIOPA repository ZIP and normally its SHA-256 checksum file.

## Objective

Safely unpack the handoff, establish a correct local Git repository, discover and map all relevant existing local clones, create or reconcile the GitHub repository `edithatogo/riopa-infrastructure`, wire `origin`, push the repository without rewriting history, configure the GitHub repository conservatively, create/reconcile the configured GitHub Project and issue graph, and leave a complete machine-readable and human-readable bootstrap report.

Do not stop after producing a plan. Execute each safe step in the current session. Use the repository’s own scripts and Conductor records as the source of truth.

## Defaults

- Expected archive: `riopa-infrastructure-dev-handoff-2026-07-20.zip`
- Expected checksum file: `RIOPA_DEV_HANDOFF_SHA256SUMS.txt`
- GitHub owner: `edithatogo`
- GitHub repository: `riopa-infrastructure`
- Visibility: `public`
- Default branch: `main`
- Repository folder: `riopa-infrastructure`
- Related clones configuration: `config/workspace/repositories.json`
- Machine-local workspace map: `.riopa-local/workspace-repositories.json`
- This archive is an **unreleased development handoff based on v0.2.0**. Do not tag it as v1.0 or claim stable-release maturity.

## Non-negotiable safety rules

1. Never print, persist, commit, or include credentials in logs. In particular, protect `LINZ_API_KEY`, GitHub tokens, Hugging Face tokens, and Zenodo tokens.
2. Never force-push, delete a remote repository, delete an existing worktree, rewrite published history, or use `git reset --hard` on a pre-existing repository.
3. Never overwrite an unrelated non-empty directory. Extract to a staging directory first and inspect the archive paths before moving files.
4. Never modify a related repository that is dirty. Record it as dirty and leave it untouched.
5. Never commit `.riopa-local/`, `.env`, downloaded GIS payloads, DuckDB files, Parquet/GeoParquet, credentials, virtual environments, caches, or build outputs.
6. Do not rewrite the historical `conductor/release-evidence/0.2.0.json` merely because newer development files have different hashes. Generate new development evidence only after the tree is frozen and verified.
7. Do not create duplicate GitHub Projects, labels, issues, cross-repository issues, or remotes. Reuse and reconcile existing objects by stable keys.
8. Do not create `edithatogo/nz-spatial-archive` in this bootstrap. It is a planned follow-on repository and needs its own approved handoff.
9. Do not upload LINZ or council data, create Hugging Face datasets, or create Zenodo deposits during repository bootstrap. This task establishes the software/control plane only.
10. Keep an execution journal under `.riopa-local/bootstrap/` with commands, outcomes, versions, discovered paths, and any unresolved blockers, but never secrets.

## Phase 1 — identify and safely unpack the archive

1. List the current directory. Prefer the exact handoff ZIP named in the accompanying checksum file. If several `riopa-infrastructure*.zip` files exist, choose the newest **development handoff** only after displaying their names, sizes, modification times, and SHA-256 values.
2. Verify the checksum using the supplied checksum file. If there is no checksum file, calculate the ZIP SHA-256 and record it before extraction.
3. Inspect every ZIP member before extraction. Reject absolute paths, `..` traversal, drive-qualified paths, symlinks escaping the extraction root, duplicate paths, and unexpected top-level directories.
4. Extract to a staging directory such as `.riopa-local/extract-staging-<digest-prefix>`.
5. Confirm the archive contains one top-level `riopa-infrastructure/` directory and expected files including `pyproject.toml`, `conductor/`, `project/`, `scripts/bootstrap_github.sh`, and `BOOTSTRAP_AGENT_PROMPT.md`.
6. If the target directory does not exist, atomically move the extracted top-level directory into place. If it exists:
   - inspect whether it is the same project;
   - preserve all local and untracked work;
   - do not overlay blindly;
   - compare trees and merge only when the relationship is clear;
   - otherwise keep the staged extraction separate and report the conflict.
7. Change into the repository root and confirm it is not nested inside an unrelated Git repository.
8. Safe extraction libraries may not restore Unix executable bits. Explicitly run `chmod +x scripts/*.sh scripts/*.py` and verify that the bootstrap and CI scripts are executable. This is a permission repair only; do not otherwise mutate source files during extraction.

## Phase 2 — toolchain and authentication

1. Record versions of `git`, `gh`, `python`, and `uv` if available.
2. Require Python 3.12 or 3.13.
3. Verify GitHub authentication with `gh auth status`.
4. Confirm the active GitHub login is authorised to create `edithatogo/riopa-infrastructure` and write Projects/issues in the relevant repositories. If the wrong account is active, use `gh auth switch` rather than continuing under the wrong identity.
5. Ensure the token has the `repo`, `project`, and `workflow` scopes. Use `gh auth refresh --scopes repo,project,workflow` when an interactive refresh is required.
6. Do not set repository secrets automatically. Record required secret names and whether corresponding local environment variables exist without printing their values.

## Phase 3 — initialise Git locally without losing anything

1. If `.git` is absent, run `git init -b main` in the extracted repository root.
2. If `.git` exists, verify its top-level path is exactly the current repository and inspect all remotes, branches, status, and history before changing anything.
3. Configure `user.name` and `user.email` locally only if missing. Prefer values reported by GitHub; do not overwrite global Git configuration.
4. Confirm `.riopa-local/` is ignored.
5. Run a secret scan over tracked candidates before the first commit. At minimum reject obvious API keys, bearer tokens, private keys, `.env` files, and URLs containing embedded credentials.
6. Do not stage generated local workspace maps or data artifacts.

## Phase 4 — discover existing local clones

1. Use `config/workspace/repositories.json` as the expected GitHub and Hugging Face repository inventory.
2. Search the repository parent, grandparent, and existing common workspace roots such as `~/src`, `~/code`, `~/dev`, `~/projects`, `~/Projects`, and `~/Documents/GitHub`. Do not recursively scan the entire filesystem or system directories.
3. Match clones by normalised remote URL, not merely folder name. Recognise HTTPS and SSH GitHub URLs plus Hugging Face dataset Git remotes, and report duplicate clones.
4. Run:

   ```bash
   python scripts/discover_workspace_repositories.py \
     --repo-root . \
     --clone-missing
   ```

   Add explicit `--search-root` values for any obvious workspace roots discovered nearby.
5. The script may clone only repositories marked `clone_if_missing: true`, into the sibling `../riopa-related/` directory. It must not clone the primary repository over itself or create the planned `nz-spatial-archive` repository.
6. Review `.riopa-local/workspace-repositories.md`. For each related repository record:
   - preferred clone path;
   - all duplicate clone paths;
   - remotes;
   - branch and HEAD;
   - upstream divergence where available;
   - clean/dirty state;
   - intended write policy.
7. Do not modify related repositories in this bootstrap. Later work must use issue-linked feature branches and must skip dirty clones.

## Phase 5 — install and establish the baseline

1. Prefer `uv`:

   ```bash
   uv sync --extra dev --extra spatial --frozen
   ```

   If the lock file is legitimately stale because this handoff added dependencies, update it once with `uv lock`, inspect the diff, then rerun the frozen sync. Do not update unrelated dependencies casually.
2. Run syntax/import checks before the full harness:

   ```bash
   uv run python -m compileall -q src scripts
   uv run riopa --help
   uv run riopa registry validate \
     --registry config/source-registry/nz-spatial-pilot.yaml \
     --schema schemas/source-registry.schema.json
   ```
3. Run the repository quality and reproducibility harnesses:

   ```bash
   scripts/ci_quality.sh
   uv run pytest --cov=riopa_provenance --cov-branch --cov-report=term-missing
   scripts/ci_reproducibility.sh
   ```
4. Read `HANDOFF_STATUS.md` before interpreting the results. The merged development modules are known not yet to satisfy the repository-wide 90% branch-coverage release gate. Do not lower, omit, or bypass that stable target; record the measured baseline and create a P0/P1 test-restoration issue linked to the appropriate Conductor quality/hardening track.
5. Distinguish genuine implementation failures from deliberately stale historical release evidence. Fix code, schema, packaging, CI, or lock-file defects. Do not falsify old release evidence.
6. Record every command and result in `.riopa-local/bootstrap/baseline.md`.
7. The initial repository may be pushed as a development handoff only after imports, package build, source-registry validation, workflow-policy checks, reproducibility checks, and core tests pass. Record every remaining known failure prominently in `HANDOFF_STATUS.md` and the first GitHub issue. Do not tag or enable protected release publication while the full-package coverage gate is failing.

## Phase 6 — create or reconcile the GitHub repository

1. Set the target to `edithatogo/riopa-infrastructure`.
2. Query it first:

   ```bash
   gh repo view edithatogo/riopa-infrastructure \
     --json nameWithOwner,url,sshUrl,isEmpty,defaultBranchRef,viewerPermission
   ```

3. If the repository does not exist, create it from the local source without adding a second README, licence, or `.gitignore`:

   ```bash
   gh repo create edithatogo/riopa-infrastructure \
     --public \
     --description "Open, modular, provenance-first infrastructure for reproducible public-data research and decision analytics" \
     --disable-wiki \
     --source=. \
     --remote=origin
   ```

4. If it exists, verify that it is the intended repository. Fetch it before pushing. If it has unrelated or divergent history, do not force anything; create a reconciliation report and use an ordinary merge or pull request only when provenance is clear.
5. Verify `origin` normalises to `github.com/edithatogo/riopa-infrastructure`. If another `origin` exists, do not overwrite it silently. Rename an intentional prior remote to `upstream` only after documenting why.
6. Create an atomic initial commit if needed. Use a message such as:

   ```text
   feat: bootstrap RIOPA infrastructure development handoff
   ```

7. Push `main` normally and set its upstream. Never use `--force` or `--force-with-lease`.
8. Run `gh repo set-default edithatogo/riopa-infrastructure`.

## Phase 7 — configure GitHub and activate Conductor

1. Apply conservative repository settings:
   - issues, Projects, and Discussions enabled;
   - wiki disabled;
   - squash and rebase merge enabled;
   - merge commits disabled;
   - branches deleted after merge;
   - auto-merge and update-branch enabled;
   - topics for provenance, reproducibility, geospatial research data, and New Zealand.
2. Set default `GITHUB_TOKEN` workflow permissions to read-only and prevent Actions from approving pull requests.
3. Create the `release` environment, but do not add secrets or publish a release.
4. Execute a dry run first:

   ```bash
   scripts/bootstrap_local_handoff.sh \
     --owner edithatogo \
     --repo riopa-infrastructure \
     --visibility public \
     --clone-missing \
     --configure-repository \
     --create-project \
     --create-issues \
     --cross-repo
   ```

5. Inspect the dry-run report and issue keys. Confirm that all cross-repository targets refer to the intended repositories and that no duplicate stable keys already exist.
6. Apply the idempotent bootstrap:

   ```bash
   scripts/bootstrap_local_handoff.sh \
     --owner edithatogo \
     --repo riopa-infrastructure \
     --visibility public \
     --clone-missing \
     --configure-repository \
     --create-project \
     --create-issues \
     --cross-repo \
     --apply
   ```

7. Use `--mirror-umbrella` only after verifying that the configured project number is actually the current RIOPA umbrella Project. Do not assume project number 4 is correct merely because an older script used it.
8. After the bootstrap generates GitHub references, commit those tracked updates and push normally.
9. Do not create branch protection or rulesets that could lock out the sole maintainer. Prepare a recommended ruleset and enable it only after the first CI run reveals the exact required check names and an administrator bypass path is verified.

## Phase 8 — verify remote state

Verify and record:

- local `main` tracks `origin/main`;
- local HEAD equals remote `main` HEAD;
- repository description, visibility, topics, merge settings, and Actions permissions;
- Project number and URL;
- number of labels, parent issues, sub-issues, dependencies, and cross-repository issues created or reused;
- GitHub Actions workflows visible on the remote;
- `release` environment exists;
- no repository secrets were printed or committed;
- `.riopa-local/` remains untracked;
- related repositories remain unmodified;
- a clean `git status` at completion.

Run the remote-default and repository checks using `gh repo set-default --view`, `gh repo view --json ...`, `gh project list`, `gh issue list`, and `gh api` as appropriate.

## Required final report

Create `.riopa-local/bootstrap/FINAL_REPORT.md` and then report to me with:

1. exact repository root;
2. ZIP SHA-256;
3. local Git HEAD and branch;
4. GitHub repository URL and remote URL;
5. Project URL/number;
6. issue and cross-repository issue counts;
7. discovered preferred paths for every relevant local clone;
8. duplicate and dirty clone warnings;
9. toolchain versions;
10. baseline test, lint, type, security, packaging, and reproducibility results;
11. required but unset secret names, without values;
12. unresolved blockers and the next highest-priority Conductor track.

Do not claim that LINZ/council data, Hugging Face datasets, Zenodo deposits, DOI releases, operational history, or stable v1 maturity exist unless you have independently verified those remote artifacts.

---
