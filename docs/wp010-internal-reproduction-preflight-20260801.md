# WP-010 internal reproduction preflight (non-qualifying)

**Prepared:** 2026-08-01  
**Status:** internal panel rehearsal only; does **not** satisfy the external person/operator reproduction gate and does not authorise beta, release-candidate or stable-v1 promotion.

## Purpose and frozen references

This report records the panel's preparation of a clean-room reproduction handoff. It is content-bound to the repository state observed on 2026-08-01 and is intended to make the remaining external work executable without using the implementer's environment.

- Repository: `https://github.com/edithatogo/riopa-infrastructure`
- Frozen repository revision: `8cac8b019cd20f7ba276147567442003489ac5b5`
- Successor preservation record: [Zenodo 10.5281/zenodo.21737563](https://doi.org/10.5281/zenodo.21737563)
- Submitted successor packet SHA-256: `e0dcf5eb08e9b4530929da92a439d2cb97ced51bfe34f4848d1a2ef94c15abe5`
- Expected benchmark: `urn:riopa:benchmark:wp010:synthetic-methods:1.0.0`
- Reviewer-bundle builder: `scripts/build_wp010_reviewer_bundle.py`
- Expected reviewer-bundle SHA-256 (from the frozen manifest): `26bf2281f67c35f3327ebadeda3c8d5e7c6460e5b447dfc8417c851bcb0b6813`
- Result issue: [#149](https://github.com/edithatogo/riopa-infrastructure/issues/149)

The Zenodo packet is an immutable preservation snapshot. The repository revision above records the successor DOI after publication; neither reference should be treated as evidence that an external reproduction has occurred.

## Exact external-operator procedure

An operator must perform these steps in a fresh checkout and temporary directory outside the implementation run. The operator must record the exact commit, operating system, architecture, Python version, UTC start/end times, identity or stable pseudonym, organisation, relationship/conflict disclosure, all commands, exit statuses, deviations and findings. Do not include secrets or sensitive machine paths.

```sh
git clone https://github.com/edithatogo/riopa-infrastructure.git
cd riopa-infrastructure
git checkout 8cac8b019cd20f7ba276147567442003489ac5b5
test -z "$(git status --porcelain)"
python scripts/build_wp010_reviewer_bundle.py --output /tmp/wp010-a.zip
python scripts/build_wp010_reviewer_bundle.py --output /tmp/wp010-b.zip
cmp /tmp/wp010-a.zip /tmp/wp010-b.zip
shasum -a 256 /tmp/wp010-a.zip
unzip -q /tmp/wp010-a.zip -d /tmp/wp010-review
python /tmp/wp010-review/verify.py
```

The returned report must include the complete stdout/stderr digest, generated bundle digest, dependency observations, deviations, findings and exactly one decision: `pass`, `pass-with-limitations` or `fail`. It must be published as an immutable or content-bound artifact and linked from issue #149.

## Panel checks completed before handoff

The internal panel checked that the successor DOI and packet digest are recorded in the preservation manifest, that the deterministic bundle builder and expected digest are named, and that the handoff/protocol documents retain the clean-room and independence requirements. These checks are preparation and traceability checks; they are not an execution by an independent operator.

## Limitations and open gates

- No person or organisation outside the implementation run has yet executed the procedure or reported adverse findings.
- Subagents and internal panel members cannot substitute for the required external operator; their output is rehearsal evidence only.
- The pilot remains regional, non-authoritative and non-operational.
- Custodian confirmation for any authoritative national ambulance dataset and accountable release-authority approval remain outstanding.
- This preflight must not be cited as a beta, release-candidate or stable-v1 qualification record.

**Panel disposition:** `non-qualifying-preflight`; external reproduction remains `required-for-beta-and-stable`.
