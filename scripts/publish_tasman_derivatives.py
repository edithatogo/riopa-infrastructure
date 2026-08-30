#!/usr/bin/env python3
"""Publish verified Tasman projections without confusing DuckDB bytes with semantics."""

from __future__ import annotations

import argparse
import json
import os
import re
import runpy
import shutil
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import duckdb
import pyarrow.parquet as pq
from huggingface_hub import HfApi, hf_hub_download

from riopa_provenance.hashing import sha256_bytes, sha256_file, sha256_json
from riopa_provenance.public_archive_spatial import verify_public_archive_packet
from riopa_provenance.tasman_public_packet import ATTRIBUTION, LICENCE_SHA256, SOURCE

PUBLISHER = runpy.run_path(str(Path(__file__).with_name("publish_tasman_public_packet.py")))
HOSTED = PUBLISHER["HOSTED"]
PUBLIC, PRIVATE = PUBLISHER["PUBLIC"], PUBLISHER["PRIVATE"]
NAMES = {"canonical.json", "features.parquet", "features.duckdb", "manifest.json"}
LIMIT = 512_000_000


def checked(path: Path, root: Path) -> Path:
    if not path.resolve().is_relative_to(root.resolve()) or any(
        p.is_symlink() for p in (path, *path.parents)
    ):
        raise ValueError("unsafe derivative input")
    if not path.is_file() or not 0 < path.stat().st_size <= LIMIT:
        raise ValueError("missing or oversized derivative")
    return path


def rows(path: Path, *, database: bool) -> list[dict[str, Any]]:
    if database:
        with duckdb.connect(str(path), read_only=True) as connection:
            connection.execute("SET enable_external_access=false")
            table = connection.execute(
                "SELECT * EXCLUDE(geometry), ST_AsWKB(geometry) AS geometry "
                "FROM features ORDER BY _riopa_feature_id"
            ).to_arrow_table()
    else:
        table = pq.read_table(path).sort_by("_riopa_feature_id")
    result: list[dict[str, Any]] = json.loads(
        json.dumps(
            table.to_pylist(),
            default=lambda value: value.hex() if isinstance(value, bytes) else str(value),
        )
    )
    return result


def prepare(work: Path) -> tuple[Path, dict[str, Any]]:
    receipt = json.loads(checked(work / "public/tasman-publication.json", work).read_bytes())
    if (
        receipt.get("status") != "public-packet-verified-and-rebuilt"
        or receipt.get("state") != "verified"
        or receipt.get("anonymous_full_packet_verified") is not True
        or receipt.get("reproduction", {}).get("builds") != 2
        or receipt.get("licence") != "CC-BY-4.0"
        or receipt.get("source_id") != SOURCE
        or receipt.get("attribution") != ATTRIBUTION
    ):
        raise ValueError("source publication/rights binding mismatch")
    packet = work / "anonymous-packet"
    manifest = json.loads(checked(packet / "manifest.json", work).read_bytes())
    for key in ("source_id", "licence", "attribution", "rights_capture_id", "rights_object_sha256"):
        if manifest[key] != receipt[key]:
            raise ValueError("source receipt and packet differ")
    binding = PUBLISHER["descriptor"](
        manifest, receipt["packet_manifest_sha256"], receipt["prefix"], receipt["public_revision"]
    )
    verify_public_archive_packet(packet, descriptor=binding)
    rights = json.loads((packet / "objects/sha256" / manifest["rights_object_sha256"]).read_bytes())
    if sha256_bytes(rights["licenseInfo"].encode()) != LICENCE_SHA256:
        raise ValueError("source licence text changed")
    projections = []
    for build in ("first", "second"):
        root = work / "builds" / build
        parquet = checked(root / "spatial/tasman-zones.parquet", work)
        database = checked(root / "spatial/tasman-zones.duckdb", work)
        projected = rows(parquet, database=False)
        if rows(database, database=True) != projected:
            raise ValueError("DuckDB/GeoParquet full-row semantics differ")
        evidence = json.loads(
            checked(root / "records/public-archive-spatial-projection.json", work).read_bytes()
        )
        if (
            evidence["geoparquet"]["sha256"] != sha256_file(parquet)
            or sha256_file(parquet) != receipt["reproduction"]["geoparquet_sha256"]
            or len(projected) != receipt["reproduction"]["feature_count"]
        ):
            raise ValueError("projection byte/count binding mismatch")
        if (
            evidence["packet_manifest_sha256"] != receipt["packet_manifest_sha256"]
            or evidence["packet_revision"] != receipt["public_revision"]
        ):
            raise ValueError("projection source binding mismatch")
        if (
            sha256_json(evidence["canonical_features"])
            != receipt["reproduction"]["canonical_sha256"]
        ):
            raise ValueError("canonical projection binding mismatch")
        projections.append((parquet, database, projected))
    first, second = projections
    if first[2] != second[2] or sha256_file(first[0]) != sha256_file(second[0]):
        raise ValueError("fresh rebuild semantics differ")
    canonical = {
        "record_type": "tasman_canonical_projected_rows",
        "rows": first[2],
        "canonical_features": evidence["canonical_features"],
        "valid_time": "unknown-not-imputed",
        "source_manifest_sha256": receipt["packet_manifest_sha256"],
    }
    identity = {
        "profile": "tasman-derived-v1",
        "producer_sha256": sha256_file(Path(__file__)),
        "source_manifest_sha256": receipt["packet_manifest_sha256"],
        "source_revision": receipt["public_revision"],
        "full_row_semantic_sha256": sha256_json(first[2]),
        "canonical_sha256": sha256_json(canonical),
        "geoparquet_sha256": sha256_file(first[0]),
        "feature_count": len(first[2]),
    }
    logical = sha256_json(identity)
    output = work / "derived-candidate"
    if output.exists():
        raise ValueError("derivative candidate must be fresh")
    output.mkdir()
    (output / "canonical.json").write_text(json.dumps(canonical, sort_keys=True, indent=2) + "\n")
    shutil.copyfile(first[0], output / "features.parquet")
    shutil.copyfile(first[1], output / "features.duckdb")
    result = {
        "schema_version": "1.0.0",
        "record_type": "tasman_derived_public_packet",
        "logical_sha256": logical,
        "identity": identity,
        "licence": "CC-BY-4.0",
        "attribution": ATTRIBUTION,
        "source_repository": PUBLIC,
        "source_prefix": receipt["prefix"],
        "rights_capture_id": manifest["rights_capture_id"],
        "rights_object_sha256": manifest["rights_object_sha256"],
        "transformation": "ArcGIS to canonical rows, GeoParquet and DuckDB; no geometry repair.",
        "non_claims": [
            "No operative legal status, inferred valid time or stable release.",
            "DuckDB reproducibility is semantic, not byte-identical.",
        ],
        "files": {
            p.name: {"sha256": sha256_file(p), "bytes": p.stat().st_size}
            for p in sorted(output.iterdir())
        },
    }
    if sum(item["bytes"] for item in result["files"].values()) > LIMIT:
        raise ValueError("derivative byte budget exceeded")
    HOSTED["write_json"](output / "manifest.json", result)
    return output, result


def verify_remote(
    api: Any,
    prefix: str,
    revision: str,
    expected: dict[str, Any],
    work: Path,
    manifest_sha256: str | None = None,
) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("invalid immutable revision")
    remote = {}
    for item in api.list_repo_tree(
        PUBLIC,
        path_in_repo=prefix,
        recursive=True,
        repo_type="dataset",
        revision=revision,
        token=False,
    ):
        if hasattr(item, "size"):
            remote[item.path] = item.size
            if len(remote) > 4:
                raise ValueError("extra derivative files")
    if (
        set(remote) != {f"{prefix}/{name}" for name in NAMES}
        or any(type(n) is not int or not 0 < n <= LIMIT for n in remote.values())
        or sum(remote.values()) > LIMIT + 65536
    ):
        raise ValueError("derivative closure/size bounds mismatch")
    if remote[f"{prefix}/manifest.json"] > 65536:
        raise ValueError("oversized manifest")
    target = work / str(uuid.uuid4())
    target.mkdir(parents=True)

    def fetch(name: str) -> Path:
        cached = Path(
            hf_hub_download(
                PUBLIC,
                f"{prefix}/{name}",
                repo_type="dataset",
                revision=revision,
                token=False,
                force_download=True,
                cache_dir=work / "cache",
            )
        )
        if cached.stat().st_size != remote[f"{prefix}/{name}"]:
            raise ValueError("download size mismatch")
        shutil.copyfile(cached, target / name)
        return target / name

    manifest_path = fetch("manifest.json")
    if manifest_sha256 is not None and sha256_file(manifest_path) != manifest_sha256:
        raise ValueError("original manifest byte binding mismatch")
    original = json.loads(manifest_path.read_bytes())
    if {k: v for k, v in original.items() if k != "files"} != {
        k: v for k, v in expected.items() if k != "files"
    }:
        raise ValueError("original provenance metadata differs")
    if (
        original.get("logical_sha256") != expected["logical_sha256"]
        or original.get("identity") != expected["identity"]
        or original.get("licence") != "CC-BY-4.0"
        or original.get("attribution") != ATTRIBUTION
    ):
        raise ValueError("original derivative identity differs")
    if set(original["files"]) != NAMES - {"manifest.json"}:
        raise ValueError("manifest closure differs")
    with ThreadPoolExecutor(max_workers=3) as pool:
        for path in pool.map(fetch, sorted(original["files"])):
            entry = original["files"][path.name]
            if path.stat().st_size != entry["bytes"] or sha256_file(path) != entry["sha256"]:
                raise ValueError("original derivative bytes corrupted")
    canonical = json.loads((target / "canonical.json").read_bytes())
    projected = rows(target / "features.parquet", database=False)
    if (
        canonical["rows"] != projected
        or rows(target / "features.duckdb", database=True) != projected
        or sha256_json(projected) != expected["identity"]["full_row_semantic_sha256"]
        or sha256_json(canonical) != expected["identity"]["canonical_sha256"]
        or sha256_file(target / "features.parquet") != expected["identity"]["geoparquet_sha256"]
    ):
        raise ValueError("original derivative semantics differ from fresh rebuild")
    return {**original, "_manifest_sha256": sha256_file(manifest_path)}


def publish(api: Any, work: Path) -> dict[str, Any]:
    stage = "visibility"
    visible = False
    identity = None
    revision = None
    try:
        HOSTED["require_visibility"](api)
        visible = True
        stage = "prepare"
        candidate, manifest = prepare(work)
        identity = manifest["logical_sha256"]
        prefix = f"derivatives/tasman-zones/{identity}"
        name = f"publications/tasman-derivatives/{identity}.json"
        checkpoint = PUBLISHER["control"](api, name, work, missing=True)
        stage = "upload-or-recover"
        if checkpoint:
            if checkpoint.get("logical_sha256") != identity or checkpoint.get("prefix") != prefix:
                raise ValueError("derivative checkpoint identity mismatch")
            revision = checkpoint["public_revision"]
        else:
            found = api.get_paths_info(
                PUBLIC, [f"{prefix}/manifest.json"], repo_type="dataset", expand=True
            )
            if found:
                revision = found[0].last_commit.oid
                recovered = verify_remote(
                    api, prefix, revision, manifest, work / "derivative-readback"
                )
                original_manifest_sha = recovered["_manifest_sha256"]
            else:
                if {p.name for p in candidate.iterdir()} != NAMES:
                    raise ValueError("candidate closure changed")
                files = {name: checked(candidate / name, candidate) for name in sorted(NAMES)}
                if sum(p.stat().st_size for p in files.values()) > LIMIT + 65536:
                    raise ValueError("candidate byte budget exceeded")
                revision = HOSTED["commit_files"](
                    api, PUBLIC, {f"{prefix}/{name}": path for name, path in files.items()}
                )
                original_manifest_sha = sha256_file(candidate / "manifest.json")
            checkpoint = {
                "logical_sha256": identity,
                "prefix": prefix,
                "public_revision": revision,
                "manifest_sha256": original_manifest_sha,
                "state": "uploaded-verification-pending",
            }
            HOSTED["commit_files"](api, PRIVATE, {name: json.dumps(checkpoint).encode()})
        stage = "anonymous-verification"
        original = verify_remote(
            api,
            prefix,
            revision,
            manifest,
            work / "derivative-readback",
            checkpoint["manifest_sha256"],
        )
        result = {
            **checkpoint,
            "state": "verified",
            "public_repository": PUBLIC,
            "status": "derivatives-published-and-verified",
            "identity": original["identity"],
            "files": original["files"],
            "licence": "CC-BY-4.0",
            "attribution": ATTRIBUTION,
        }
        stage = "verified-checkpoint"
        HOSTED["commit_files"](api, PRIVATE, {name: json.dumps(result).encode()})
        HOSTED["write_json"](work / "public/tasman-derivatives.json", result)
        return result
    except Exception as error:
        failure = {
            "status": "failed",
            "stage": stage,
            "error_class": type(error).__name__[:128],
            "attempt_id": str(uuid.uuid4()),
        }
        if isinstance(identity, str) and re.fullmatch(r"[0-9a-f]{64}", identity):
            failure["logical_sha256"] = identity
        if isinstance(revision, str) and re.fullmatch(r"[0-9a-f]{40}", revision):
            failure["public_revision"] = revision
        try:
            HOSTED["write_json"](work / "public/tasman-derivatives-failure.json", failure)
        except Exception as secondary:
            failure["local_error_class"] = type(secondary).__name__[:128]
        if visible:
            try:
                attempt_path = (
                    f"publications/tasman-derivatives/attempts/{failure['attempt_id']}.json"
                )
                saved_revision = HOSTED["commit_files"](
                    api,
                    PRIVATE,
                    {attempt_path: json.dumps(failure).encode()},
                )
                failure["durable_record_revision"] = saved_revision
            except Exception as secondary:
                failure["durable_error_class"] = type(secondary).__name__[:128]
        try:
            HOSTED["write_json"](work / "public/tasman-derivatives-failure.json", failure)
        except Exception as secondary:
            failure["local_error_class"] = type(secondary).__name__[:128]
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    if (
        os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("GITHUB_REF") != "refs/heads/main"
    ):
        parser.error("main Actions execution required")
    work = args.work.resolve()
    root = Path(__file__).resolve().parents[1]
    if work.is_relative_to(root) and not work.is_relative_to(root / ".riopa-local"):
        parser.error("ignored or external work directory required")
    try:
        result = publish(HfApi(token=os.environ["HF_TOKEN"]), work)
    except Exception as error:
        print(json.dumps({"status": "failed", "error_class": type(error).__name__[:128]}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
