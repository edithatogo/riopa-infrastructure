# Independent reproduction protocol

This protocol defines a bounded clean-room review. It does not appoint a
reviewer, assert independence, or approve a release.

## Frozen subject

The requester supplies:

- repository URL and exact commit;
- reviewer-bundle filename and SHA-256;
- expected benchmark identifier;
- supported Python version; and
- an issue or immutable record to receive the result.

The reviewer must not use the implementer's virtual environment, dependency
cache, uncommitted files, generated local state, or unpublished credentials.

## Procedure

1. Record reviewer identity or stable pseudonym, organisation if applicable,
   relationship to the implementer, conflicts, operating system, architecture,
   Python version and UTC start time.
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

## Independence criteria

An external reproduction must be performed outside the implementation run by a
person or organisation able to report adverse findings without instruction from
the implementer. Agents may add review depth but do not replace the required
external person/operator. Conflicts of interest must be disclosed.

## Required evidence record

The returned report must contain the exact commit and bundle SHA-256, reviewer
and environment fields, commands, results, findings, decision, UTC completion
time, and a signature, platform attestation, or content-bound persistent URL.
Mutable comments without a digest do not satisfy the stable gate.
