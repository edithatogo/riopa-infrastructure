# Project Automation

The `.yaml` files in this directory are JSON-compatible YAML so they can be read by standard JSON tooling as well as PyYAML.

- `project.yaml`: project title, fields, recommended views and umbrella-project metadata.
- `labels.yaml`: idempotently created/updated repository labels.
- `issues.yaml`: programme epic, track parent issues, phase sub-issues and dependencies.
- `cross-repo-adoption.yaml`: targeted adoption issues in existing repositories.

Preview issue creation:

```bash
uv run python scripts/create_issues.py --repo edithatogo/riopa-infrastructure
```

Apply locally after authentication:

```bash
uv run python scripts/create_issues.py \
  --repo edithatogo/riopa-infrastructure \
  --project-title "RIOPA Infrastructure Roadmap" \
  --apply
```

Cross-repository writes require an explicit flag:

```bash
uv run python scripts/create_issues.py \
  --repo edithatogo/riopa-infrastructure \
  --cross-repo \
  --apply
```
