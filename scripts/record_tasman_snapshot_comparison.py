#!/usr/bin/env python3
"""Compare current Tasman canonical bytes with the fixed initial public baseline."""

from __future__ import annotations

import argparse
import json
import os
import re
import runpy
import uuid
from pathlib import Path
from typing import Any

from huggingface_hub import HfApi, hf_hub_download

from riopa_provenance.hashing import sha256_file, sha256_json

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "docs/tasman-derived-acceptance-20260831.json"
REPOSITORY = "edithatogo/riopa-infrastructure"
PUBLIC = "edithatogo/riopa-public-data-archive"
ATTRIBUTION = "Tasman District Council (TDC)"
LIMIT = 512_000_000
METADATA_LIMIT = 2_000_000


def digest(value: object, length: int = 64) -> str:
    if not isinstance(value, str) or not re.fullmatch(f"[0-9a-f]{{{length}}}", value):
        raise ValueError("invalid immutable digest")
    return value


def safe(path: Path, root: Path) -> Path:
    if (
        ".." in path.parts
        or not path.resolve().is_relative_to(root.resolve())
        or any(part.is_symlink() for part in (path, *path.parents))
    ):
        raise ValueError("unsafe comparison path")
    return path


def metadata(path: Path, root: Path) -> dict[str, Any]:
    safe(path, root)
    if not path.is_file() or not 0 < path.stat().st_size <= METADATA_LIMIT:
        raise ValueError("missing or oversized metadata")
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError("metadata must be an object")
    return value


def entry(value: dict[str, Any]) -> tuple[str, int]:
    checksum = digest(value.get("sha256"))
    size = value.get("bytes")
    if type(size) is not int or not 0 < size <= LIMIT:
        raise ValueError("canonical byte budget exceeded")
    return checksum, size


def derived_receipt(value: dict[str, Any]) -> None:
    if (
        value.get("status") != "derivatives-published-and-verified"
        or value.get("state") != "verified"
        or value.get("public_repository") != PUBLIC
        or value.get("licence") != "CC-BY-4.0"
        or value.get("attribution") != ATTRIBUTION
    ):
        raise ValueError("unverified or wrong-rights derivative receipt")
    identity = value.get("identity")
    if not isinstance(identity, dict) or identity.get("profile") != "tasman-derived-v1":
        raise ValueError("unsupported canonical profile")
    logical = digest(value.get("logical_sha256"))
    if (
        logical != sha256_json(identity)
        or value.get("prefix") != f"derivatives/tasman-zones/{logical}"
    ):
        raise ValueError("derivative identity/path mismatch")
    digest(value.get("public_revision"), 40)
    digest(value.get("manifest_sha256"))
    digest(identity.get("source_revision"), 40)
    digest(identity.get("source_manifest_sha256"))
    digest(identity.get("canonical_sha256"))
    if type(identity.get("feature_count")) is not int or identity["feature_count"] < 1:
        raise ValueError("invalid canonical feature count")
    entry(value["files"]["canonical.json"])


def record(work: Path) -> dict[str, Any]:
    if (
        os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("GITHUB_REF") != "refs/heads/main"
        or os.environ.get("GITHUB_REPOSITORY") != REPOSITORY
    ):
        raise ValueError("main Actions repository context required")
    work = safe(work.absolute(), work.absolute())
    if work.is_relative_to(ROOT) and not work.is_relative_to(ROOT / ".riopa-local"):
        raise ValueError("ignored or external work directory required")
    output = safe(work / "public/tasman-snapshot-comparison.json", work)
    diagnostics_output = safe(work / "public/tasman-attribute-diagnostics.json", work)
    if output.exists() or diagnostics_output.exists():
        raise ValueError("comparison evidence must be fresh")
    source_path = work / "public/tasman-publication.json"
    derived_path = work / "public/tasman-derivatives.json"
    source, current = metadata(source_path, work), metadata(derived_path, work)
    derived_receipt(current)
    identity = current["identity"]
    if (
        source.get("status") != "public-packet-verified-and-rebuilt"
        or source.get("state") != "verified"
        or source.get("anonymous_full_packet_verified") is not True
        or source.get("source_id") != "urn:riopa:source:tasman:geohub"
        or source.get("public_dataset_repository") != PUBLIC
        or source.get("licence") != "CC-BY-4.0"
        or source.get("attribution") != ATTRIBUTION
        or source.get("packet_manifest_sha256") != identity["source_manifest_sha256"]
        or source.get("public_revision") != identity["source_revision"]
        or source.get("reproduction", {}).get("feature_count") != identity.get("feature_count")
        or source.get("reproduction", {}).get("geoparquet_sha256")
        != identity.get("geoparquet_sha256")
    ):
        raise ValueError("source and derivative receipt bindings differ")
    candidate = work / "derived-candidate"
    manifest = metadata(candidate / "manifest.json", work)
    if (
        manifest.get("record_type") != "tasman_derived_public_packet"
        or manifest.get("identity") != identity
        or manifest.get("logical_sha256") != current["logical_sha256"]
        or manifest.get("licence") != current["licence"]
        or manifest.get("attribution") != current["attribution"]
        or manifest.get("files", {}).get("canonical.json") != current["files"]["canonical.json"]
    ):
        raise ValueError("current canonical manifest differs from verified receipt")
    current_hash, current_size = entry(manifest["files"]["canonical.json"])
    canonical = safe(candidate / "canonical.json", work)
    if (
        not canonical.is_file()
        or canonical.stat().st_size != current_size
        or sha256_file(canonical) != current_hash
    ):
        raise ValueError("current canonical bytes mismatch")
    acceptance = metadata(BASELINE, BASELINE.parent)
    if (
        acceptance.get("status") != "hosted-derived-publication-and-replay-verified"
        or acceptance.get("track") != "nz_spatial_archive_mvp_20260718"
    ):
        raise ValueError("unaccepted fixed baseline")
    baseline = acceptance["publication_receipt"]
    derived_receipt(baseline)
    baseline_hash, baseline_size = entry(baseline["files"]["canonical.json"])
    remote = f"{baseline['prefix']}/canonical.json"
    api = HfApi(token=False)
    if api.repo_info(PUBLIC, repo_type="dataset", token=False).private is not False:
        raise ValueError("baseline repository is not public")
    infos = api.get_paths_info(
        PUBLIC, [remote], repo_type="dataset", revision=baseline["public_revision"], token=False
    )
    if (
        len(infos) != 1
        or infos[0].path != remote
        or type(getattr(infos[0], "size", None)) is not int
        or getattr(infos[0], "size", None) != baseline_size
    ):
        raise ValueError("baseline remote size/path mismatch")
    download_root = safe(work / f"snapshot-baseline-{uuid.uuid4()}", work)
    if download_root.exists():
        raise ValueError("baseline download must be fresh")
    downloaded = Path(
        hf_hub_download(
            PUBLIC,
            remote,
            repo_type="dataset",
            revision=baseline["public_revision"],
            token=False,
            force_download=True,
            local_dir=download_root,
        )
    )
    safe(downloaded, download_root)
    if (
        downloaded != download_root / remote
        or not downloaded.is_file()
        or downloaded.stat().st_size != baseline_size
        or sha256_file(downloaded) != baseline_hash
    ):
        raise ValueError("baseline canonical byte mismatch")
    comparator = runpy.run_path(str(ROOT / "scripts/compare_tasman_snapshots.py"))["compare"]
    comparison = comparator(downloaded, canonical, baseline_hash, current_hash)
    for label, path, receipt in (("before", downloaded, baseline), ("after", canonical, current)):
        expected = receipt["identity"]
        observed = comparison[label]
        if (
            observed["source_manifest_sha256"] != expected["source_manifest_sha256"]
            or observed["feature_count"] != expected["feature_count"]
            or sha256_json(json.loads(path.read_bytes())) != expected["canonical_sha256"]
        ):
            raise ValueError("canonical semantics differ from receipt identity")
    result = {
        "schema_version": "1.0.0",
        "record_type": "tasman_fixed_baseline_snapshot_comparison",
        "status": "compared",
        "baseline_role": "fixed-initial-accepted-packet-not-previous-cycle",
        "baseline_acceptance_sha256": sha256_file(BASELINE),
        "baseline_public_revision": baseline["public_revision"],
        "baseline_canonical_sha256": baseline_hash,
        "source_receipt_sha256": sha256_file(source_path),
        "derived_receipt_sha256": sha256_file(derived_path),
        "source_public_revision": source["public_revision"],
        "source_packet_manifest_sha256": source["packet_manifest_sha256"],
        "derived_public_revision": current["public_revision"],
        "current_canonical_sha256": current_hash,
        "comparison": comparison,
        "release_cycle_qualified": False,
        "non_claims": [
            "Fixed initial baseline comparison is not previous-cycle change or recovery evidence.",
            "No scheduled-cycle, operative-status, clean-room or release qualification.",
        ],
    }
    diagnostic = runpy.run_path(str(ROOT / "scripts/diagnose_tasman_attribute_changes.py"))[
        "diagnose"
    ](downloaded, canonical, baseline_hash, current_hash, comparison["comparison_sha256"])
    with output.open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    with diagnostics_output.open("x") as stream:
        stream.write(json.dumps(diagnostic, indent=2) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    work = safe(args.work.absolute(), args.work.absolute())
    if work.is_relative_to(ROOT) and not work.is_relative_to(ROOT / ".riopa-local"):
        parser.error("ignored or external work directory required")
    try:
        result = record(work)
    except Exception as error:
        failure = {"status": "failed", "error_class": type(error).__name__[:128]}
        try:
            path = safe(work / "public/tasman-snapshot-comparison-failure.json", work)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(failure) + "\n")
        except Exception as secondary:
            failure["record_error_class"] = type(secondary).__name__[:128]
        print(json.dumps(failure))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
