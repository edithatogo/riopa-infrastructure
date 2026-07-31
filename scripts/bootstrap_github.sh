#!/usr/bin/env bash
# Create or reconcile the RIOPA repository, GitHub Project, labels and issue graph.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OWNER="edithatogo"
REPO="riopa-infrastructure"
VISIBILITY="public"
CREATE_PROJECT=false
CREATE_ISSUES=false
CROSS_REPO=false
MIRROR_UMBRELLA=false
UPDATE_EXISTING=false
SKIP_PUSH=false
APPLY=false

usage() {
  cat <<'USAGE'
Usage: scripts/bootstrap_github.sh [options]

Options:
  --owner LOGIN             GitHub user or organisation (default: edithatogo)
  --repo NAME               Repository name (default: riopa-infrastructure)
  --visibility LEVEL        public, private or internal (default: public)
  --create-project          Create/reuse and configure the repository Project
  --create-issues           Create/reuse labels, parent issues, sub-issues and dependencies
  --cross-repo              Also create targeted adoption issues in existing repositories
  --mirror-umbrella         Add selected parent issues to RIOPA project 4
  --update-existing         Replace generated issue bodies and reapply labels/project links
  --skip-push               Do not push the local commit after repository creation/reconciliation
  --apply                   Perform writes; without this flag the script is a dry run
  -h, --help                Show this help

Required authentication for writes:
  gh auth login
  gh auth refresh -s repo -s project
USAGE
}

while (($#)); do
  case "$1" in
    --owner) OWNER="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --visibility) VISIBILITY="$2"; shift 2 ;;
    --create-project) CREATE_PROJECT=true; shift ;;
    --create-issues) CREATE_ISSUES=true; shift ;;
    --cross-repo) CROSS_REPO=true; shift ;;
    --mirror-umbrella) MIRROR_UMBRELLA=true; shift ;;
    --update-existing) UPDATE_EXISTING=true; shift ;;
    --skip-push) SKIP_PUSH=true; shift ;;
    --apply) APPLY=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$VISIBILITY" in
  public|private|internal) ;;
  *) echo "--visibility must be public, private or internal" >&2; exit 2 ;;
esac

FULL_REPO="$OWNER/$REPO"
PROJECT_TITLE="$(python - <<'PY'
import json
from pathlib import Path
print(json.loads(Path('project/project.yaml').read_text())['title'])
PY
)"
DESCRIPTION="Open, modular, provenance-first infrastructure for reproducible public-data research and decision analytics."

require() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Required executable not found: $1" >&2
    exit 1
  }
}

run() {
  if $APPLY; then
    printf '+ '
    printf '%q ' "$@"
    printf '\n'
    "$@"
  else
    printf 'DRY-RUN: '
    printf '%q ' "$@"
    printf '\n'
  fi
}

json_project_number() {
  local title="$1"
  python -c '
import json, sys
payload=json.load(sys.stdin)
projects=payload if isinstance(payload,list) else payload.get("projects",[])
title=sys.argv[1]
for project in projects:
    if project.get("title")==title:
        print(project.get("number", ""))
        break
' "$title"
}

json_scalar() {
  local key="$1"
  python -c 'import json,sys; print(json.load(sys.stdin).get(sys.argv[1], ""))' "$key"
}

normalise_github_remote() {
  python - "$1" <<'PYREMOTE'
import re, sys
from urllib.parse import urlsplit
value=sys.argv[1].strip()
match=re.match(r"^(?:[^@]+@)?([^:]+):(.+)$", value)
if match and "://" not in value:
    host, path=match.groups()
else:
    parsed=urlsplit(value)
    host=parsed.hostname or ""
    path=parsed.path
path=path.strip("/")
if path.endswith(".git"):
    path=path[:-4]
parts=[part for part in path.split("/") if part]
if host.casefold() in {"github.com", "www.github.com"} and len(parts)>=2:
    print(f"github.com/{parts[0].casefold()}/{parts[1].casefold()}")
PYREMOTE
}

verify_origin() {
  local expected
  expected="github.com/$(printf '%s' "$FULL_REPO" | tr '[:upper:]' '[:lower:]')"
  if git remote get-url origin >/dev/null 2>&1; then
    local actual_url actual
    actual_url="$(git remote get-url origin)"
    actual="$(normalise_github_remote "$actual_url")"
    if [[ "$actual" != "$expected" ]]; then
      echo "Refusing to use origin '$actual_url'; expected https://github.com/$FULL_REPO.git" >&2
      exit 1
    fi
  fi
}

push_main_safely() {
  verify_origin
  git fetch origin --prune
  if git show-ref --verify --quiet refs/remotes/origin/main; then
    if ! git merge-base --is-ancestor origin/main HEAD; then
      echo "Remote main is not an ancestor of local HEAD; refusing a divergent push." >&2
      echo "Reconcile histories with a normal merge or pull request; never force-push." >&2
      exit 1
    fi
  fi
  git push -u origin main
}

require python
require git
if command -v uv >/dev/null 2>&1; then
  echo "Validating scaffold with uv..."
  if ! uv run --no-sync python -m riopa_provenance.cli validate --root .; then
    echo "Locked validator dependencies are unavailable; running dependency-free repository checks."
    git fsck --full
    python -m compileall -q scripts
    python scripts/codex_orchestrator.py status >/dev/null
  fi
else
  echo "Validating scaffold with the active Python environment..."
  PYTHONPATH=src python -m riopa_provenance.cli validate --root .
fi

if ! $APPLY; then
  echo "Dry-run target: $FULL_REPO"
  echo "Dry-run project: $PROJECT_TITLE"
fi

PROJECT_NUMBER=""

if $APPLY; then
  require gh
  gh auth status >/dev/null

  if [[ ! -d .git ]]; then
    git init -b main
  fi
  [[ "$(git rev-parse --show-toplevel)" == "$ROOT" ]] || {
    echo "Refusing to bootstrap from a nested Git repository." >&2
    exit 1
  }
  current_branch="$(git branch --show-current)"
  if [[ -n "$current_branch" && "$current_branch" != "main" ]]; then
    echo "Refusing to bootstrap from branch '$current_branch'; expected main." >&2
    exit 1
  fi
  if ! git config user.name >/dev/null; then
    git config user.name "$OWNER"
  fi
  if ! git config user.email >/dev/null; then
    git config user.email "$OWNER@users.noreply.github.com"
  fi

  git add -A
  if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
    git commit -m "feat: bootstrap RIOPA provenance-first infrastructure"
  elif ! git diff --cached --quiet; then
    git commit -m "chore: reconcile RIOPA architecture bundle"
  fi

  if gh repo view "$FULL_REPO" >/dev/null 2>&1; then
    echo "Reusing existing repository $FULL_REPO"
    if ! git remote get-url origin >/dev/null 2>&1; then
      git remote add origin "https://github.com/$FULL_REPO.git"
    fi
    verify_origin
    gh repo set-default "$FULL_REPO"
    if ! $SKIP_PUSH; then
      push_main_safely
    fi
  else
    if git remote get-url origin >/dev/null 2>&1; then
      verify_origin
    fi
    repo_args=(repo create "$FULL_REPO" "--$VISIBILITY" --description "$DESCRIPTION" --disable-wiki --source=. --remote=origin)
    if ! $SKIP_PUSH; then
      repo_args+=(--push)
    fi
    run gh "${repo_args[@]}"
    gh repo set-default "$FULL_REPO"
  fi
else
  run gh repo create "$FULL_REPO" "--$VISIBILITY" --description "$DESCRIPTION" --source=. --remote=origin --push
fi

if $CREATE_PROJECT; then
  if $APPLY; then
    project_list="$(gh project list --owner "$OWNER" --limit 100 --format json)"
    PROJECT_NUMBER="$(printf '%s' "$project_list" | json_project_number "$PROJECT_TITLE")"
    if [[ -z "$PROJECT_NUMBER" ]]; then
      created="$(gh project create --owner "$OWNER" --title "$PROJECT_TITLE" --format json)"
      PROJECT_NUMBER="$(printf '%s' "$created" | json_scalar number)"
      if [[ -z "$PROJECT_NUMBER" ]]; then
        echo "GitHub created a project but did not return a project number." >&2
        exit 1
      fi
      echo "Created project $PROJECT_NUMBER: $PROJECT_TITLE"
    else
      echo "Reusing project $PROJECT_NUMBER: $PROJECT_TITLE"
    fi

    # Link is idempotent at the API level on current GitHub; tolerate an already-linked response.
    if ! gh project link "$PROJECT_NUMBER" --owner "$OWNER" --repo "$REPO" 2>/tmp/riopa-project-link.err; then
      if ! grep -Eqi 'already|linked' /tmp/riopa-project-link.err; then
        cat /tmp/riopa-project-link.err >&2
        exit 1
      fi
    fi
    rm -f /tmp/riopa-project-link.err

    existing_fields="$(gh project field-list "$PROJECT_NUMBER" --owner "$OWNER" --limit 100 --format json)"
    while IFS=$'\t' read -r field_name field_type field_options; do
      [[ -n "$field_name" ]] || continue
      exists="$(printf '%s' "$existing_fields" | python -c '
import json,sys
payload=json.load(sys.stdin)
fields=payload if isinstance(payload,list) else payload.get("fields",[])
print("yes" if any(f.get("name")==sys.argv[1] for f in fields) else "no")
' "$field_name")"
      if [[ "$exists" == "yes" ]]; then
        echo "Reusing project field: $field_name"
        continue
      fi
      field_args=(project field-create "$PROJECT_NUMBER" --owner "$OWNER" --name "$field_name" --data-type "$field_type" --format json)
      if [[ "$field_type" == "SINGLE_SELECT" ]]; then
        field_args+=(--single-select-options "$field_options")
      fi
      run gh "${field_args[@]}" >/dev/null
    done < <(python - <<'PY'
import json
from pathlib import Path
config=json.loads(Path('project/project.yaml').read_text())
for field in config['fields']:
    options=','.join(field.get('options', []))
    print(f"{field['name']}\t{field['type']}\t{options}")
PY
)
  else
    echo "DRY-RUN: create/reuse project '$PROJECT_TITLE', link it to $FULL_REPO, and create configured fields"
  fi
fi

if $CREATE_ISSUES; then
  issue_args=(python scripts/create_issues.py --repo "$FULL_REPO" --owner "$OWNER")
  if [[ -n "$PROJECT_NUMBER" ]]; then
    issue_args+=(--project-title "$PROJECT_TITLE" --project-number "$PROJECT_NUMBER")
  elif $CREATE_PROJECT; then
    issue_args+=(--project-title "$PROJECT_TITLE")
  fi
  $CROSS_REPO && issue_args+=(--cross-repo)
  $UPDATE_EXISTING && issue_args+=(--update-existing)
  if $APPLY; then
    issue_args+=(--apply)
    run "${issue_args[@]}"
  else
    "${issue_args[@]}"
  fi
fi

if $MIRROR_UMBRELLA; then
  mirror_args=(python scripts/mirror_to_umbrella.py --owner "$OWNER" --project-number 4)
  if $APPLY; then
    mirror_args+=(--apply)
    run "${mirror_args[@]}"
  else
    "${mirror_args[@]}"
  fi
fi

if $APPLY; then
  cat > project/bootstrap-summary.md <<EOF
# GitHub bootstrap summary

- Repository: https://github.com/$FULL_REPO
- Repository project: ${PROJECT_NUMBER:-not-created} — $PROJECT_TITLE
- Cross-repository adoption: $CROSS_REPO
- Umbrella mirroring requested: $MIRROR_UMBRELLA
- Generated report: \`project/bootstrap-report.json\`

## Remaining manual project configuration

GitHub does not expose saved-view creation through the current project CLI/API surface. Create the views listed in \`project/project.yaml\` in the GitHub UI.
EOF
  git add conductor project
  if ! git diff --cached --quiet; then
    git commit -m "chore: record GitHub programme bootstrap"
    if ! $SKIP_PUSH; then
      git push origin main
    fi
  fi
fi

cat <<EOF
Bootstrap complete.
Repository: https://github.com/$FULL_REPO
Project: ${PROJECT_NUMBER:-not created in this run} ($PROJECT_TITLE)
Mode: $($APPLY && echo apply || echo dry-run)
EOF
