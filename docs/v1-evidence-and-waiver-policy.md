# Evidence, defects and waiver policy

Evidence is part of the product, not project-management commentary. The normative
record shape is `schemas/release-evidence.schema.json`; the release-specific
thresholds are in `conductor/releases.json` and `conductor/v1-gate.json`.

## Release evidence record

Each release can have one `conductor/release-evidence/<version>.json` record. It
contains:

- a stable evidence-record identifier, release, evaluation time, evaluator, tool and
  exact source revision;
- one result for every evaluated gate, including status, reviewer, review date,
  expiry and evidence references;
- defect counts using the same field names as the global v1 policy;
- qualification metrics for independent review, clean-room/external reproduction,
  external users/operators, operational cycles, operational evidence and RC soak;
- role-specific approvals and signed decision references;
- immutable release-artifact references; and
- known limitations that remain true at release time.

Every evidence reference records an identifier, kind, location, immutability claim,
optional SHA-256 digest, generation time and description. Local paths remain inside
the repository and their declared digests are checked. Stable v1 requires immutable
identifiers for all gate and release evidence. Every local stable-v1 evidence file
must carry a verified SHA-256 digest; external evidence must carry either a digest or
a recognised content-addressed persistent identifier. Mutable URLs and generic URNs
without content binding are insufficient.

`planned` or `in-progress` evidence never satisfies a blocking gate. A passed gate
requires non-empty evidence and review metadata. Evidence expiry or excessive age
blocks the stable release.

## Defects

Stable v1 permits zero open P0 or P1 defects, zero release-blocking P2 defects, zero
critical security findings, zero governance prohibitions and zero expired waivers.
Lower-severity known defects remain visible with owner, impact, workaround and target
release.

Defect counts are release evidence, not substitutes for the underlying issue,
security and governance registers. The release authority must be able to trace each
count to a frozen query or signed report.

## Waivers

A waiver records category, scope, reason, owner, approver, creation and expiry,
mitigation, remediation issue and a public summary where safe. Waivers expire within
90 days. Critical security, governance prohibition, integrity failure and unresolved
P0/P1 categories are not waivable.

A waiver does not mark a requirement complete. It records a bounded exception for a
specific release. Its evidence, reviewer and expiry are evaluated like a passed gate.
Expired, overlong, unsigned or prohibited waivers block release.

## Independence

M5 and M6 cannot be established entirely by the implementer. Stable v1 requires at
least two independent reviewers, two clean-room reproductions including one external
reproduction, two external user workflows and one external operator workflow.
Conflicts of interest are disclosed in the release decision.

## Release authority

Stable approval is role based. Release management, security, governance,
scientific-method and independent-reproducibility roles must each approve and provide
a signed or attested decision reference. Missing, rejecting, abstaining or unsigned
required roles block general availability.

## Evidence maintenance

Gate evidence is version addressed and append-only once published. A correction
creates a successor record and preserves the superseded record. The stable evidence
record is retained with the signed release manifest and preservation deposit. Annual
revalidation produces new evidence rather than rewriting the v1.0 decision.
