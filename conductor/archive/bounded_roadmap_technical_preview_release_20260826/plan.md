# Plan: bounded_roadmap_technical_preview_release_20260826

## 1. Freeze the bounded contract

- [x] Fix source at `4ffe73eb144c5c1a4acad34706a5f5937491d1ad`.
- [x] Define M1 scope, non-claims and owner authorization.
- [x] Publish twelve-month support, correction and withdrawal policy.

## 2. Acquire publication evidence

- [x] Merge preparation PR #606 with all required Actions passing.
- [x] Create annotated `v0.2.0` tag at the exact historical commit.
- [x] Resolve package-gateway, lock-transport and publication blockers through
  reviewed PRs #607-#611.
- [x] Pass historical validation, build, checksums and provenance verification
  in Actions run #32865862594.
- [x] Publish the GitHub prerelease and independently reverify downloaded assets.
- [x] Open three-role external participant recruitment in issue #605.

## 3. Review fixes

- [x] Preserve the original historical lock bytes and enforce all frozen hashes.
- [x] Fail closed on write permissions and constrain recovery to one tag/SHA.
- [x] Disclose the unsigned tag and unavailable DOI credential.
- [x] Record zero external participant completions and preserve later gates.

## 4. Closeout

- [x] Record immutable evidence and exact support end.
- [x] Confirm all 28 later tracks continue unchanged.
- [x] Complete at M1 and move this bounded track to `conductor/archive/`.
