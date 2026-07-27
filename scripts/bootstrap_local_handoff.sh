#!/usr/bin/env bash
# Guarded local-to-GitHub bootstrap for an extracted RIOPA handoff bundle.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OWNER="edithatogo"
REPO="riopa-infrastructure"
VISIBILITY="public"
APPLY=false
CLONE_MISSING=false
CREATE_PROJECT=false
CREATE_ISSUES=false
CROSS_REPO=false
MIRROR_UMBRELLA=false
UPDATE_EXISTING=false
CONFIGURE_REPOSITORY=false
SEARCH_ROOTS=()

usage() {
  cat <<'USAGE'
Usage: scripts/bootstrap_local_handoff.sh [options]

Local preparation:
  --search-root PATH       Add a root to scan for existing local clones (repeatable)
  --clone-missing          Clone configured missing repositories into ../riopa-related

GitHub target:
  --owner LOGIN            GitHub owner (default: edithatogo)
  --repo NAME              Repository name (default: riopa-infrastructure)
  --visibility LEVEL       public, private, or internal (default: public)
  --configure-repository   Apply conservative repository settings and read-only Actions token defaults
  --create-project         Create/reuse the configured GitHub Project
  --create-issues          Create/reuse the generated issue graph
  --cross-repo             Create/reuse configured issues in related repositories
  --mirror-umbrella        Mirror selected issues to the configured umbrella project
  --update-existing        Reconcile generated issue bodies and labels
  --apply                  Perform writes; otherwise print a dry-run
  -h, --help               Show this help

The script never force-pushes, never deletes a remote, and never commits .riopa-local/.
USAGE
}

while (($#)); do
  case "$1" in
    --owner) OWNER="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --visibility) VISIBILITY="$2"; shift 2 ;;
    --search-root) SEARCH_ROOTS+=("$2"); shift 2 ;;
    --clone-missing) CLONE_MISSING=true; shift ;;
    --configure-repository) CONFIGURE_REPOSITORY=true; shift ;;
    --create-project) CREATE_PROJECT=true; shift ;;
    --create-issues) CREATE_ISSUES=true; shift ;;
    --cross-repo) CROSS_REPO=true; shift ;;
    --mirror-umbrella) MIRROR_UMBRELLA=true; shift ;;
    --update-existing) UPDATE_EXISTING=true; shift ;;
    --apply) APPLY=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$VISIBILITY" in public|private|internal) ;; *) echo "invalid visibility" >&2; exit 2 ;; esac

require() {
  command -v "$1" >/dev/null 2>&1 || { echo "Required executable not found: $1" >&2; exit 1; }
}

require git
require python

if [[ ! -d .git ]]; then
  if $APPLY; then
    git init -b main
  else
    echo "DRY-RUN: git init -b main"
  fi
fi

if [[ -d .git ]]; then
  current_root="$(git rev-parse --show-toplevel)"
  [[ "$(cd "$current_root" && pwd)" == "$ROOT" ]] || {
    echo "Refusing to bootstrap from a nested Git repository: $current_root" >&2
    exit 1
  }
fi

discovery=(python scripts/discover_workspace_repositories.py --repo-root .)
for search_root in ${SEARCH_ROOTS[@]+"${SEARCH_ROOTS[@]}"}; do
  discovery+=(--search-root "$search_root")
done
$CLONE_MISSING && discovery+=(--clone-missing)
if $APPLY || [[ -d .git ]]; then
  "${discovery[@]}" || {
    status=$?
    if [[ $status -ne 2 ]]; then exit "$status"; fi
    echo "Workspace discovery found missing required related repositories; see .riopa-local/workspace-repositories.md" >&2
  }
else
  echo "DRY-RUN: ${discovery[*]}"
fi

bootstrap=(
  scripts/bootstrap_github.sh
  --owner "$OWNER"
  --repo "$REPO"
  --visibility "$VISIBILITY"
)
$CREATE_PROJECT && bootstrap+=(--create-project)
$CREATE_ISSUES && bootstrap+=(--create-issues)
$CROSS_REPO && bootstrap+=(--cross-repo)
$MIRROR_UMBRELLA && bootstrap+=(--mirror-umbrella)
$UPDATE_EXISTING && bootstrap+=(--update-existing)
$APPLY && bootstrap+=(--apply)
"${bootstrap[@]}"

FULL_REPO="$OWNER/$REPO"
if $CONFIGURE_REPOSITORY; then
  if ! $APPLY; then
    cat <<EOF
DRY-RUN: configure $FULL_REPO with issues/projects/discussions enabled, wiki disabled,
         squash and rebase merging enabled, merge commits disabled, branches deleted on merge,
         auto-merge enabled, and default Actions token permissions set to read-only.
EOF
  else
    require gh
    gh repo edit "$FULL_REPO" \
      --enable-issues \
      --enable-projects \
      --enable-discussions \
      --enable-wiki=false \
      --enable-squash-merge \
      --squash-merge-commit-message pr-title-description \
      --enable-rebase-merge \
      --enable-merge-commit=false \
      --delete-branch-on-merge \
      --enable-auto-merge \
      --allow-update-branch \
      --add-topic provenance,reproducibility,geospatial,research-data,new-zealand
    gh api \
      --method PUT \
      -H "Accept: application/vnd.github+json" \
      "repos/$FULL_REPO/actions/permissions/workflow" \
      -f default_workflow_permissions=read \
      -F can_approve_pull_request_reviews=false >/dev/null
    gh api --method PUT -H "Accept: application/vnd.github+json" \
      "repos/$FULL_REPO/environments/release" >/dev/null
    gh repo set-default "$FULL_REPO"
  fi
fi

cat <<EOF
Local handoff bootstrap finished.
Repository target: https://github.com/$FULL_REPO
Mode: $($APPLY && echo apply || echo dry-run)
Workspace map: .riopa-local/workspace-repositories.json
EOF
