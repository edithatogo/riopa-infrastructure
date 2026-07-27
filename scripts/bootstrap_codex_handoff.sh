#!/usr/bin/env bash
# Restore/verify the included Git history, bootstrap GitHub and activate the Codex work loop.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

APPLY=false
CLONE_MISSING=false
SKIP_QUALITY=false
SKIP_GITHUB=false
MIRROR_UMBRELLA=false
OWNER="edithatogo"
REPO="riopa-infrastructure"
VISIBILITY="public"
SEARCH_ROOTS=()

usage() {
  cat <<'USAGE'
Usage: scripts/bootstrap_codex_handoff.sh [options]

  --apply                 Perform GitHub writes; otherwise remote steps are a dry run
  --clone-missing         Clone only related repositories explicitly allowed by workspace config
  --search-root PATH      Add a bounded root for clone discovery (repeatable)
  --skip-quality          Skip baseline quality/reproducibility commands
  --skip-github           Do not invoke GitHub repository/Project/issue bootstrap
  --mirror-umbrella       Mirror configured items to the validated umbrella Project
  --owner LOGIN           GitHub owner (default: edithatogo)
  --repo NAME             GitHub repository (default: riopa-infrastructure)
  --visibility LEVEL      public, private or internal (default: public)
  -h, --help              Show this help

The script never force-pushes or rewrites history. It writes machine-local logs only
under ignored .riopa-local/ paths.
USAGE
}

while (($#)); do
  case "$1" in
    --apply) APPLY=true; shift ;;
    --clone-missing) CLONE_MISSING=true; shift ;;
    --search-root) SEARCH_ROOTS+=("$2"); shift 2 ;;
    --skip-quality) SKIP_QUALITY=true; shift ;;
    --skip-github) SKIP_GITHUB=true; shift ;;
    --mirror-umbrella) MIRROR_UMBRELLA=true; shift ;;
    --owner) OWNER="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --visibility) VISIBILITY="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$VISIBILITY" in public|private|internal) ;; *) echo "Invalid visibility: $VISIBILITY" >&2; exit 2 ;; esac

require() {
  command -v "$1" >/dev/null 2>&1 || { echo "Required executable not found: $1" >&2; exit 1; }
}

require git
require python

LOCAL="$ROOT/.riopa-local"
JOURNAL_DIR="$LOCAL/bootstrap"
CODEX_DIR="$LOCAL/codex"
mkdir -p "$JOURNAL_DIR" "$CODEX_DIR"
JOURNAL="$JOURNAL_DIR/$(date -u +%Y%m%dT%H%M%SZ).log"
exec > >(tee -a "$JOURNAL") 2>&1

redacted_environment_summary() {
  for name in LINZ_API_KEY GH_TOKEN GITHUB_TOKEN HF_TOKEN HUGGINGFACE_TOKEN ZENODO_TOKEN; do
    if [[ -n "${!name:-}" ]]; then
      printf '%s=%s\n' "$name" '<set>'
    else
      printf '%s=%s\n' "$name" '<unset>'
    fi
  done
}

restore_git_from_bundle() {
  local bundle="$ROOT/handoff/riopa-infrastructure.bundle"
  [[ -f "$bundle" ]] || {
    echo "No .git directory and recovery bundle is missing: $bundle" >&2
    exit 1
  }
  git bundle verify "$bundle"
  local temp
  temp="$(mktemp -d "${TMPDIR:-/tmp}/riopa-git-restore.XXXXXX")"
  trap 'rm -rf "${temp:-}"' RETURN
  git clone --no-hardlinks "$bundle" "$temp/recovered"
  [[ ! -e "$ROOT/.git" ]] || { echo "Refusing to overwrite an existing .git path" >&2; exit 1; }
  mv "$temp/recovered/.git" "$ROOT/.git"
  git reset --mixed HEAD >/dev/null
  rm -rf "$temp"
  trap - RETURN
}

echo "RIOPA Codex handoff bootstrap"
echo "Root: $ROOT"
echo "UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf 'git: '; git --version
printf 'python: '; python --version
if command -v uv >/dev/null 2>&1; then printf 'uv: '; uv --version; fi
if command -v gh >/dev/null 2>&1; then printf 'gh: '; gh --version | head -n 1; fi
redacted_environment_summary

if [[ ! -d .git ]]; then
  echo "Restoring Git metadata from the included bundle."
  restore_git_from_bundle
fi

TOP="$(git rev-parse --show-toplevel)"
[[ "$(cd "$TOP" && pwd)" == "$ROOT" ]] || {
  echo "Refusing nested or unrelated Git repository: $TOP" >&2
  exit 1
}
[[ "$(git branch --show-current)" == "main" ]] || {
  echo "Expected branch main; found $(git branch --show-current)" >&2
  exit 1
}
git fsck --full
git --no-pager log --oneline --decorate -5

if [[ -n "$(git status --porcelain --untracked-files=all)" ]]; then
  echo "Working tree contains unexpected changes before bootstrap:" >&2
  git status --short >&2
  echo "Resolve or document them before remote bootstrap; ignored handoff bundle files do not appear here." >&2
  exit 1
fi

DISCOVERY=(python scripts/discover_workspace_repositories.py --repo-root .)
for root in "${SEARCH_ROOTS[@]}"; do DISCOVERY+=(--search-root "$root"); done
$CLONE_MISSING && DISCOVERY+=(--clone-missing)
set +e
"${DISCOVERY[@]}"
DISCOVERY_STATUS=$?
set -e
if [[ $DISCOVERY_STATUS -ne 0 && $DISCOVERY_STATUS -ne 2 ]]; then
  echo "Workspace discovery failed with status $DISCOVERY_STATUS" >&2
  exit "$DISCOVERY_STATUS"
fi
if [[ $DISCOVERY_STATUS -eq 2 ]]; then
  echo "Some required related clones remain unavailable; continuing with the primary repository."
fi

if ! $SKIP_QUALITY; then
  require uv
  uv sync --extra dev --extra spatial --frozen
  uv run python -m compileall -q src scripts
  uv run riopa --help >/dev/null
  uv run riopa registry validate \
    --registry config/source-registry/nz-spatial-pilot.yaml \
    --schema schemas/source-registry.schema.json
  uv run pytest -q

  set +e
  scripts/ci_quality.sh
  QUALITY_STATUS=$?
  scripts/ci_reproducibility.sh
  REPRO_STATUS=$?
  uv run pytest --cov=riopa_provenance --cov-branch --cov-report=term-missing \
    >"$JOURNAL_DIR/coverage.txt" 2>&1
  COVERAGE_STATUS=$?
  set -e
  printf 'quality_status=%s\nreproducibility_status=%s\ncoverage_status=%s\n' \
    "$QUALITY_STATUS" "$REPRO_STATUS" "$COVERAGE_STATUS" \
    > "$JOURNAL_DIR/baseline-status.env"
  if [[ $QUALITY_STATUS -ne 0 || $REPRO_STATUS -ne 0 || $COVERAGE_STATUS -ne 0 ]]; then
    echo "One or more development qualification checks are not yet green."
    echo "This is recorded as implementation work; no stable release claim is made."
  fi
fi

if ! $SKIP_GITHUB; then
  BOOTSTRAP=(
    scripts/bootstrap_local_handoff.sh
    --owner "$OWNER"
    --repo "$REPO"
    --visibility "$VISIBILITY"
    --configure-repository
    --create-project
    --create-issues
    --cross-repo
    --update-existing
  )
  $CLONE_MISSING && BOOTSTRAP+=(--clone-missing)
  for root in "${SEARCH_ROOTS[@]}"; do BOOTSTRAP+=(--search-root "$root"); done
  $MIRROR_UMBRELLA && BOOTSTRAP+=(--mirror-umbrella)
  $APPLY && BOOTSTRAP+=(--apply)

  if $APPLY; then
    require gh
    gh auth status
  fi
  "${BOOTSTRAP[@]}"
fi

cp CODEX_AUTONOMOUS_IMPLEMENTATION.md "$CODEX_DIR/ACTIVE_PROMPT.md"
python scripts/codex_orchestrator.py next --write

cat > "$JOURNAL_DIR/CONTINUE.md" <<'EOF_CONTINUE'
# Continue autonomous implementation

1. Read `.riopa-local/codex/ACTIVE_PROMPT.md`.
2. Read `.riopa-local/codex/NEXT_WORK_PACKAGE.md`.
3. Run `python scripts/codex_orchestrator.py start WP-001` unless another package is already active.
4. Continue implementation; do not stop at repository bootstrap.
EOF_CONTINUE

cat <<EOF_DONE

Bootstrap phase complete.
Git HEAD: $(git rev-parse HEAD)
Origin: $(git remote get-url origin 2>/dev/null || echo '<not configured>')
Journal: ${JOURNAL#$ROOT/}
Active prompt: .riopa-local/codex/ACTIVE_PROMPT.md
Next work packet: .riopa-local/codex/NEXT_WORK_PACKAGE.md

Continue autonomous implementation now; do not end at this message.
EOF_DONE
