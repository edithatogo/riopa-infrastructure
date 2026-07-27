# Git history provenance

The earlier RIOPA ZIP deliveries did not contain a `.git` directory. This handoff therefore reconstructs a transparent, auditable local history from the available immutable artifact snapshots rather than pretending that an unavailable original authoring history was preserved.

The first three commits correspond to:

1. the delivered v0.1.0 architecture artifact;
2. the delivered v0.2.0 stable-v1 roadmap artifact;
3. the delivered development snapshot containing the catalogue-wide LINZ archival implementation.

The next commit adds the Codex bootstrap, persistent `AGENTS.md` instructions, local work-package orchestrator, Git-bundle recovery and handoff documentation.

Commit messages explicitly use “reconstruct” or “import” terminology. The repository bundle under `handoff/riopa-infrastructure.bundle` contains the complete reconstructed history and can restore `.git` if an extraction tool omits hidden directories. It is intentionally ignored by Git to avoid a recursive repository artifact.
