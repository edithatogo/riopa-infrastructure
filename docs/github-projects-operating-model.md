# GitHub Projects Operating Model

## Project surfaces

1. **Repository project:** `RIOPA Infrastructure Roadmap` is the operational board for this repository.
2. **RIOPA umbrella project:** selected parent issues are mirrored to the existing cross-repository programme project.
3. **Source-repository boards:** adoption issues remain owned and executed in `fyi-cli`, `fyi-archive`, `nlp-policy-nz`, `healthpoint-rs` and other repositories.

## Issue hierarchy

```text
Programme epic
├── Track parent issue
│   ├── implementation sub-issue
│   ├── validation sub-issue
│   └── documentation/publication sub-issue
└── Cross-repository adoption links
```

GitHub issue dependencies mirror Conductor `depends_on`. A task blocked by a schema decision is marked as blocked, not merely placed later in a list.

## Project fields

| Field | Type | Values/purpose |
|---|---|---|
| Status | built in | Todo, In Progress, Done |
| Phase | single select | Foundation, Core, NZ Spatial, Analytics, Applications, Publication |
| Track ID | text | exact Conductor track identifier |
| Evidence status | single select | None, Partial, Validated, Released |
| Reproducibility | single select | R0, R1, R2, R3, R4 |
| Mirror source | single select | `riopa-infrastructure` for umbrella mirroring |
| Target release | text | schema/code/data/research-object release |

## Automation contract

The local bootstrap:

- creates or reuses repository labels;
- creates or reuses the repository project;
- creates parent and sub-issues from `project/issues.yaml`;
- applies dependencies;
- adds issues to the repository project;
- links the project to the repository;
- emits `project/bootstrap-report.json`.

The umbrella mirror remains intentionally narrow: add selected issue/PR items, set `Mirror source`, and post a project status update. It must not emulate native issue lifecycle automation.

## Idempotency

Each generated issue contains:

```html
<!-- riopa-issue-key: provenance-profile -->
```

The script searches for this key/title before creating an issue. Existing human-edited issue bodies are not overwritten unless `--update-existing` is explicitly supplied.

## Manual steps

GitHub project views are configured in the UI after project creation:

- By phase
- By track
- Blocked work
- Evidence queue
- Cross-repository adoption
- Release readiness

The bootstrap prints these remaining steps rather than claiming they were automated.
