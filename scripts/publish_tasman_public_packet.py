#!/usr/bin/env python3
"""Publish one qualified Tasman packet and verify anonymous two-build reproduction."""

from __future__ import annotations

import argparse
import json
import os
import re
import runpy
import shutil
import tarfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from huggingface_hub import HfApi, hf_hub_download

from riopa_provenance.hashing import sha256_file, sha256_json
from riopa_provenance.public_archive_spatial import (
    PublicArchiveDescriptor,
    materialize_public_arcgis_packet,
    verify_public_archive_packet,
)

HOSTED = runpy.run_path(str(Path(__file__).with_name("hosted_council_archive.py")))
PREPARE = runpy.run_path(str(Path(__file__).with_name("prepare_tasman_public_packet.py")))[
    "prepare"
]
PRIVATE = HOSTED["PRIVATE_REPO"]
PUBLIC = HOSTED["PUBLIC_REPO"]


def control(api: Any, name: str, work: Path, *, missing: bool = False) -> dict[str, Any] | None:
    """Read a small checkpoint at a pinned private repository revision."""
    revision = api.repo_info(PRIVATE, repo_type="dataset").sha
    entries = api.get_paths_info(PRIVATE, [name], repo_type="dataset", revision=revision)
    if not entries and missing:
        return None
    if len(entries) != 1 or not 0 < entries[0].size <= 65536:
        raise ValueError("missing or oversized checkpoint")
    path = hf_hub_download(
        PRIVATE,
        name,
        repo_type="dataset",
        revision=revision,
        token=api.token,
        cache_dir=work / "cache",
    )
    value = json.loads(Path(path).read_bytes())
    if not isinstance(value, dict):
        raise ValueError("checkpoint must be an object")
    return value


def restore(archive: Path, manifest: dict[str, Any], destination: Path) -> None:
    HOSTED["verify_packet"](archive, manifest)
    if destination.exists():
        raise ValueError("restore requires fresh destination")
    destination.mkdir(parents=True)
    with tarfile.open(archive, "r:") as tar:
        for member in tar:
            if not HOSTED["safe_path"](member.name) or not member.isfile():
                raise ValueError("unsafe archive member")
            target = destination / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(member)
            assert source is not None
            with source, target.open("xb") as output:
                shutil.copyfileobj(source, output, 1024 * 1024)
    HOSTED["inventory"](destination)


def descriptor(
    manifest: dict[str, Any], digest: str, prefix: str, revision: str
) -> PublicArchiveDescriptor:
    return PublicArchiveDescriptor(
        dataset_repository=PUBLIC,
        packet_revision=revision,
        packet_path=prefix,
        manifest_sha256=digest,
        source_id=manifest["source_id"],
        licence=manifest["licence"],
        attribution=manifest["attribution"],
        rights_capture_id=manifest["rights_capture_id"],
        rights_object_sha256=manifest["rights_object_sha256"],
        rights_licence_text=manifest["rights_licence_text"],
    )


def readback(
    api: Any,
    candidate: Path,
    target: Path,
    cache: Path,
    binding: PublicArchiveDescriptor,
    *,
    workers: int = 4,
) -> None:
    if not 1 <= workers <= 4 or target.exists():
        raise ValueError("readback requires fresh destination and 1..4 workers")
    verify_public_archive_packet(candidate, descriptor=binding)
    local = {p.relative_to(candidate).as_posix(): p for p in candidate.rglob("*") if p.is_file()}
    if len(local) > HOSTED["MAX_FILES"]:
        raise ValueError("packet file budget exceeded")
    names = {f"{binding.packet_path}/{name}": name for name in local}
    observed: dict[str, int] = {}
    for item in api.list_repo_tree(
        PUBLIC,
        path_in_repo=binding.packet_path,
        recursive=True,
        repo_type="dataset",
        revision=binding.packet_revision,
        token=False,
    ):
        if hasattr(item, "size"):
            observed[item.path] = item.size
            if len(observed) > len(names):
                raise ValueError("public packet has extra files")
    if set(observed) != set(names) or any(
        observed[n] != local[names[n]].stat().st_size for n in names
    ):
        raise ValueError("public packet closure/size mismatch")
    target.mkdir(parents=True)

    def fetch(remote: str) -> None:
        name = names[remote]
        path = Path(
            hf_hub_download(
                PUBLIC,
                remote,
                repo_type="dataset",
                revision=binding.packet_revision,
                token=False,
                force_download=True,
                cache_dir=cache,
            )
        )
        if path.stat().st_size != observed[remote] or sha256_file(path) != sha256_file(local[name]):
            raise ValueError("anonymous packet byte mismatch")
        output = target / name
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, output)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(fetch, names))
    verify_public_archive_packet(target, descriptor=binding)


def rebuild(packet: Path, binding: PublicArchiveDescriptor, work: Path) -> dict[str, Any]:
    evidence = []
    for name in ("first", "second"):
        projection = materialize_public_arcgis_packet(
            packet,
            descriptor=binding,
            output_dir=work / name / "spatial",
            records_dir=work / name / "records",
            base_name="tasman-zones",
        )
        evidence.append(json.loads(projection.evidence_path.read_bytes()))
    for key in ("canonical_features", "geoparquet", "duckdb", "feature_count"):
        if evidence[0][key] != evidence[1][key]:
            raise ValueError(f"independent rebuild differs: {key}")
    return {
        "feature_count": evidence[0]["feature_count"],
        "canonical_sha256": sha256_json(evidence[0]["canonical_features"]),
        "geoparquet_sha256": evidence[0]["geoparquet"]["sha256"],
        "duckdb_semantic_sha256": evidence[0]["duckdb"]["semantic_sha256"],
        "builds": 2,
    }


def publish(api: Any, source_run: str, work: Path) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9]+", source_run) or work.exists():
        raise ValueError("source run must be numeric and work directory fresh")
    HOSTED["require_visibility"](api)
    work.mkdir(parents=True)
    checkpoint = control(api, f"campaigns/{source_run}/tasman/checkpoint.json", work)
    assert checkpoint is not None
    original = HOSTED["checked_manifest"](api, checkpoint, work / "private-readback")
    if (
        original.get("source") != "tasman"
        or original.get("run_id") != source_run
        or original.get("acquisition_complete") is not True
    ):
        raise ValueError("source checkpoint is not a complete Tasman acquisition")
    HOSTED["verify_public_checkpoint"](api, checkpoint, work / "original-evidence")
    archive = work / "private-readback" / checkpoint["prefix"] / "raw.tar"
    restore(archive, original, work / "store")
    report = PREPARE(work)
    candidate = work / "tasman-public-candidate"
    manifest = json.loads((candidate / "manifest.json").read_bytes())
    digest = report["manifest_sha256"]
    prefix = f"snapshots/tasman-zones/{digest}"
    # Validate closure/rights before any upload; current HEAD is only a local
    # descriptor validation input, never reported as this packet's publication.
    verify_public_archive_packet(
        candidate,
        descriptor=descriptor(
            manifest, digest, prefix, api.repo_info(PUBLIC, repo_type="dataset").sha
        ),
    )
    checkpoint_name = f"publications/tasman/{original['manifest_sha256']}.json"
    existing = control(api, checkpoint_name, work, missing=True)
    if existing is not None:
        if (
            existing.get("private_manifest_sha256") != original["manifest_sha256"]
            or existing.get("packet_manifest_sha256") != digest
            or existing.get("prefix") != prefix
        ):
            raise ValueError("publication checkpoint identity mismatch")
        revision = existing["public_revision"]
    else:
        found = api.get_paths_info(
            PUBLIC, [f"{prefix}/manifest.json"], repo_type="dataset", expand=True
        )
        if found:
            # Recover the original manifest commit after a checkpoint-write crash.
            revision = found[0].last_commit.oid
            readback(
                api,
                candidate,
                work / "recovered-packet",
                work / "recovery-cache",
                descriptor(manifest, digest, prefix, revision),
            )
        else:
            revision = HOSTED["commit_files"](
                api,
                PUBLIC,
                {
                    f"{prefix}/{p.relative_to(candidate).as_posix()}": p
                    for p in candidate.rglob("*")
                    if p.is_file()
                },
            )
        existing = {
            "private_manifest_sha256": original["manifest_sha256"],
            "packet_manifest_sha256": digest,
            "prefix": prefix,
            "public_revision": revision,
            "state": "uploaded-verification-pending",
        }
        HOSTED["commit_files"](api, PRIVATE, {checkpoint_name: json.dumps(existing).encode()})
    binding = descriptor(manifest, digest, prefix, revision)
    readback(api, candidate, work / "anonymous-packet", work / "anonymous-cache", binding)
    reproduction = rebuild(work / "anonymous-packet", binding, work / "builds")
    result = {
        "schema_version": "1.0.0",
        "status": "public-packet-verified-and-rebuilt",
        **existing,
        "state": "verified",
        "source_run": source_run,
        "public_dataset_repository": PUBLIC,
        "private_revision": checkpoint["revision"],
        "private_prefix": checkpoint["prefix"],
        "licence": manifest["licence"],
        "attribution": manifest["attribution"],
        "rights_capture_id": manifest["rights_capture_id"],
        "rights_object_sha256": manifest["rights_object_sha256"],
        "rights_licence_text": manifest["rights_licence_text"],
        "source_id": manifest["source_id"],
        "capture_set_id": manifest["capture_set_id"],
        "file_count": len(manifest["files"]),
        "file_bytes": sum(item["bytes"] for item in manifest["files"]),
        "anonymous_full_packet_verified": True,
        "reproduction": reproduction,
        "non_claims": [
            "No operative legal status, valid-time inference, atomic snapshot or stable release.",
            "Spatial projections rebuilt locally on runner; only source packet publicly uploaded.",
        ],
    }
    HOSTED["commit_files"](api, PRIVATE, {checkpoint_name: json.dumps(result).encode()})
    HOSTED["write_json"](work / "public/tasman-publication.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", required=True)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    if (
        os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("GITHUB_REF") != "refs/heads/main"
    ):
        parser.error("publication is restricted to main GitHub Actions execution")
    work = args.work.resolve()
    root = Path(__file__).resolve().parents[1]
    if work.is_relative_to(root) and not work.is_relative_to(root / ".riopa-local"):
        parser.error("work must be outside Git or within .riopa-local")
    result = publish(HfApi(token=os.environ["HF_TOKEN"]), args.source_run, work)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
