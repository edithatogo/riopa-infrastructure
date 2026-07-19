# Project automation

The `.yaml` files in this directory are JSON-compatible YAML so standard JSON tooling
and PyYAML can both read them.

- `project.yaml`: stable-v1 Project title, fields, views and umbrella-project metadata.
- `labels.yaml`: idempotently created or updated repository labels.
- `issues.yaml`: generated programme epic, 28 track parents, phase sub-issues and dependencies.
- `cross-repo-adoption.yaml`: targeted adoption issues in existing repositories.
- `bootstrap-report.json`: non-writing or applied reconciliation result; never proof of remote state by itself.

Regenerate and validate the issue graph before previewing GitHub changes:

```bash
uv run riopa roadmap generate-issues --root .
uv run riopa roadmap validate --root .
```

Preview issue creation:

```bash
uv run python scripts/create_issues.py \
  --repo edithatogo/riopa-infrastructure \
  --project-title "RIOPA Stable v1.0 Roadmap"
```

Apply locally after authentication:

```bash
uv run python scripts/create_issues.py \
  --repo edithatogo/riopa-infrastructure \
  --project-title "RIOPA Stable v1.0 Roadmap" \
  --apply
```

Cross-repository writes require an explicit flag:

```bash
uv run python scripts/create_issues.py \
  --repo edithatogo/riopa-infrastructure \
  --cross-repo \
  --apply
```

The generated issue file is a projection of Conductor. Track specifications, plans and
metadata remain the source of truth. Applied issue URLs and numbers are written back to
track evidence only after successful remote creation.
