# RIOPA repository-template support and upgrade policy

This policy applies to the single-developer RIOPA template and its additive
profile surfaces. It documents repository-owned support boundaries; it is not
evidence that a related repository has adopted the template.

## Compatibility

- The template contract is versioned by `template_id` and its JSON schema.
- Generated files are limited to the boundaries declared by the contract.
- Hand-authored Conductor plans, evidence indexes, source records and local
  customisations are preserved across inspection and upgrade recommendations.
- A profile classification of `exact`, `approximate`, `extension-only` or
  `unmapped` remains visible; compatibility never upgrades a weaker mapping.

## Upgrade procedure

1. Run `scripts/check_template_drift.py` against the target root.
2. Review the read-only report and preserve the report with the proposed
   revision.
3. Apply changes in a separate branch or worktree after inspecting local
   customisations.
4. Run the repository's quality, roadmap and reproducibility checks.
5. Record semantic losses, feedback and migration effort separately; unknown
   values remain unknown.

The drift checker never overwrites source bytes, `.git/`, or local files
outside its declared generated boundary.

## Support and limits

Support is limited to the documented Python 3.14 toolchain and the bounded
technical-preview contracts. Issues must include the exact revision, command,
environment and evidence artifact. External onboarding, independent
reproduction, source authority, production operations and release approval
remain separate gates.
