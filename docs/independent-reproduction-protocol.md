# Isolated multi-agent clean-room reproduction protocol

This protocol defines the repository's bounded clean-room reproduction gate for
a sole-developer project. Process separation is provided by separately prompted
subagents; it does not claim another human or organisation participated and it
does not approve a release.

## Frozen subject

The requester supplies:

- repository URL and exact commit;
- reviewer-bundle filename and SHA-256;
- expected benchmark identifier;
- supported Python version; and
- an issue or immutable record to receive the result.

Each reproducer subagent must not use the implementation virtual environment, dependency
cache, uncommitted files, generated local state, or unpublished credentials.

## Procedure

1. Record agent role, session and model identity, prompt digest, conflicts,
   operating system, architecture, Python version and UTC start time.
2. Obtain a clean checkout at the exact commit and confirm `git status
   --porcelain` is empty.
3. Build the reviewer bundle twice and confirm byte identity:

   ```sh
   python scripts/build_wp010_reviewer_bundle.py --output /tmp/wp010-a.zip
   python scripts/build_wp010_reviewer_bundle.py --output /tmp/wp010-b.zip
   cmp /tmp/wp010-a.zip /tmp/wp010-b.zip
   shasum -a 256 /tmp/wp010-a.zip
   ```

4. Extract one bundle into a new directory and run `python verify.py` without
   installing the project.
5. Record exit status, complete stdout/stderr digest, bundle digest, unexpected
   dependencies, deviations and findings. Do not include secrets or sensitive
   machine paths.
6. State one decision: `pass`, `pass-with-limitations`, or `fail`. A pass covers
   only the fixed synthetic calculation and deterministic handoff.

## Isolation and panel criteria

Two reproducer subagents run outside the implementation context with distinct
prompts and clean environments. An adversarial reviewer challenges failure
paths, an evidence auditor checks hashes, provenance, rights, limitations and
claim alignment, a relevant domain reviewer assesses bounded use, and a
synthesizer records agreement and dissent without overriding it. The sole
repository owner dispositions every finding and remains the release authority.

## Required evidence record

The content-bound panel manifest must contain the exact commit and bundle
SHA-256, agent/session/model/prompt and environment fields, commands, results,
findings, dissent, remediation, rerun outcome, decision and UTC completion time.
The sole owner signs or attests the manifest digest. Mutable comments without a
digest do not satisfy the stable gate.
