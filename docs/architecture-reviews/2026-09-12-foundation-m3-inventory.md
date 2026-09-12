# Foundation M3 integration evidence inventory

This successor follows PR #772, merged at
`e77bc5ba5dca9d661bf1654b9af1567fe03dd2ba`. It does not promote foundation from M2.
The schema ownership repair remains retrievable at that squash commit; the
plan and review reference are updated accordingly.

## Evidence verified

The deterministic `docs/foundation-m3-evidence-20260912.json` binds the archived
Stats NZ capture family, its source/projection/materialization receipt links,
the one-feature Wellington planning capture set and three materialized output
hashes. Archived rights declarations are included with their narrow scope;
this is not a fresh licence or authority decision. The national bulk output
is not re-materialized by this inventory.

The historical source-pair receipt contains the earlier national records-manifest
digest. Git history shows PR #598 (`38ae813818e0cca9065ea3d299ca22153a88b206`)
changed only the manifest and materialization-receipt digest references in that
file. The inventory explicitly reconciles this exact known successor and then
verifies the linked evidence. Arbitrary source-pair drift still fails. Historical
receipts are unchanged.

Hosted Tasman run provenance `33336884257` and derived publication run
`33335595270` were re-read from GitHub during this work: both report success at
the revisions in their tracked receipts. These corroborate bounded integration
history; no provider bytes were newly retrieved and they do not qualify a new
foundation candidate or establish national coverage.

## Remaining M3 work

| Owner | Next action | Required evidence / boundary |
|---|---|---|
| Canonical/provenance maintainers | Choose the actual published source/target contract versions applicable to representative inputs and execute their migration. | The existing 1.0.0-to-1.1.0 files are declarative fixtures. Their shape validation does not establish a real migration. Do not manufacture a version transition solely to clear this gate. |
| Archive/schema maintainers | Evaluate semantic preservation, rejected records, recovery and compatibility for that migration. | Version-bound input/output hashes and positive, negative, loss and recovery results. Scope changes or new data need applicable rights/access evidence. |
| Programme owner and advisory panel | Disposition the foundation integration packet against R01–R05 and M3 acceptance after missing migration evidence exists. | Exact candidate, separately attributed findings and disposition; panel advice is not release authority. |

M4 operation/SLOs, M5 candidate/panel/soak and M6 support/signing/preservation/
release decisions remain unchanged. Current task 6.1 is in progress, not complete.
This inventory completes the available evidence consolidation and drift repair;
it cannot create missing historical migration or elapsed qualification evidence.

## Reproduction and validation

Run `uv run python -m scripts.validate_foundation_m3_evidence --root . --output /tmp/foundation-m3.json`.
Compare the result with the tracked packet. Focused tests exercise altered capture,
national receipt and Wellington output bytes, invalid migration versions and
historical receipt mutation.

Validation on the successor (Python 3.14.6, frozen dev/spatial/preservation):

- Focused integration/conformance tests: 40 passed.
- Full `uv run pytest --cov=riopa_provenance --cov-branch --cov-report=term --cov-fail-under=90`:
  1,973 passed, 1 skipped; 90.64% branch-aware package coverage.
- `bash scripts/ci_quality.sh` and `bash scripts/ci_reproducibility.sh`: passed.
- Roadmap validation, generated issue configuration and tracked-secret scan: passed.
- Separate advisory diff review found no blocking finding; it did not independently
  verify hosted runs or grant qualification.

Hosted checks for this successor are separate from the historical runs above.
No live capture, provider publication, authority decision or maturity promotion
was performed.
