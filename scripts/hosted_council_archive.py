#!/usr/bin/env python3
"""Bounded hosted council capture with rights-separated, verified HF checkpoints."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import time
from pathlib import Path, PurePosixPath
from typing import Any

from riopa_provenance.capture import CaptureStore
from riopa_provenance.hashing import sha256_bytes, sha256_file, sha256_json

PRIVATE_REPO = "edithatogo/riopa-nz-spatial-raw"
PUBLIC_REPO = "edithatogo/riopa-public-data-archive"
SCRIPTS = {
    "tasman": "capture_tasman_catalogue.py",
    "npdc": "capture_npdc_map_documents.py",
    "qldc": "qualify_qldc_eplan.py",
}
MAX_BYTES = 512_000_000
MAX_FILES = 10000
MAX_TAR_BYTES = MAX_BYTES + MAX_FILES * 2048 + 10240
MAX_MANIFEST_BYTES = 16_000_000


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def safe_path(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        bool(name)
        and not path.is_absolute()
        and all(part not in ("", ".", "..") for part in name.split("/"))
        and "\\" not in name
    )


def inventory(store: Path) -> list[dict[str, Any]]:
    """Refuse symlinks, non-regular files, corrupt captures and unbounded packets."""
    entries: list[dict[str, Any]] = []
    total = 0
    for path in sorted(store.rglob("*")):
        if path.is_symlink():
            raise ValueError("symlink in archive store")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError("non-regular archive entry")
        size = path.stat().st_size
        total += size
        if total > MAX_BYTES or len(entries) >= MAX_FILES:
            raise ValueError("archive packet budget exceeded")
        entries.append(
            {"path": path.relative_to(store).as_posix(), "bytes": size, "sha256": sha256_file(path)}
        )
    captures = CaptureStore(store)
    for path in (store / "captures").glob("*.json"):
        metadata = json.loads(path.read_text())
        capture_id = metadata["capture_id"]
        if captures.capture_path(capture_id) != path:
            raise ValueError("capture filename mismatch")
        obj = metadata["object"]
        if not re.fullmatch(r"[0-9a-f]{64}", obj["sha256"]):
            raise ValueError("invalid object digest")
        captures.verify_capture_integrity(capture_id)
        if captures.object_path(obj["sha256"]).stat().st_size != obj["size_bytes"]:
            raise ValueError("capture byte count mismatch")
    return entries


def pack(store: Path, output: Path, run: dict[str, Any]) -> dict[str, Any]:
    entries = inventory(store)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / "raw.tar"
    with tarfile.open(archive, "w", format=tarfile.PAX_FORMAT) as tar:
        for entry in entries:
            path = store / entry["path"]
            info = tarfile.TarInfo(entry["path"])
            info.size = entry["bytes"]
            info.mode = 0o644
            with path.open("rb") as handle:
                tar.addfile(info, handle)
    manifest = {
        "schema_version": "1.0.0",
        **run,
        "files": entries,
        "archive_sha256": sha256_file(archive),
        "archive_bytes": archive.stat().st_size,
        "payload_visibility": "private",
        "public_scope": "non-reconstructive-evidence",
    }
    manifest["manifest_sha256"] = sha256_json(manifest)
    write_json(output / "manifest.json", manifest)
    verify_packet(archive, manifest)
    return manifest


def validate_manifest(manifest: dict[str, Any]) -> None:
    if sha256_json(manifest, omit_keys={"manifest_sha256"}) != manifest["manifest_sha256"]:
        raise ValueError("manifest digest mismatch")
    if (
        type(manifest["archive_bytes"]) is not int
        or not 0 < manifest["archive_bytes"] <= MAX_TAR_BYTES
    ):
        raise ValueError("archive exceeds budget")
    entries = manifest["files"]
    if not isinstance(entries, list) or len(entries) > MAX_FILES:
        raise ValueError("invalid file inventory")
    total = 0
    names = set()
    for entry in entries:
        if (
            not safe_path(entry["path"])
            or entry["path"] in names
            or type(entry["bytes"]) is not int
            or entry["bytes"] < 0
            or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])
        ):
            raise ValueError("invalid manifest entry")
        names.add(entry["path"])
        total += entry["bytes"]
    if total > MAX_BYTES:
        raise ValueError("manifest byte budget exceeded")


def verify_packet(archive: Path, manifest: dict[str, Any]) -> None:
    validate_manifest(manifest)
    if (
        archive.stat().st_size != manifest["archive_bytes"]
        or sha256_file(archive) != manifest["archive_sha256"]
    ):
        raise ValueError("archive digest or size mismatch")
    expected = {e["path"]: e for e in manifest["files"]}
    if len(expected) != len(manifest["files"]) or len(expected) > MAX_FILES:
        raise ValueError("duplicate or excessive manifest entries")
    total = 0
    seen = set()
    with tarfile.open(archive, "r:") as tar:
        for member in tar:
            if not member.isfile() or not safe_path(member.name) or member.name in seen:
                raise ValueError("unsafe or duplicate tar member")
            seen.add(member.name)
            entry = expected.get(member.name)
            total += member.size
            if entry is None or member.size != entry["bytes"] or total > MAX_BYTES:
                raise ValueError("tar inventory or size mismatch")
            handle = tar.extractfile(member)
            assert handle is not None
            with handle:
                digest = hashlib.sha256()
                while chunk := handle.read(1024 * 1024):
                    digest.update(chunk)
            if digest.hexdigest() != entry["sha256"]:
                raise ValueError("tar member digest mismatch")
    if seen != set(expected):
        raise ValueError("missing tar members")


def capture(source: str, work: Path, run_id: str, attempt: str, revision: str) -> None:
    store = work / "store"
    if store.exists():
        raise ValueError("new capture requires a fresh work directory")
    store.mkdir(parents=True)
    script = Path(__file__).with_name(SCRIPTS[source])
    # The source subprocess receives no HF/GitHub credential; never log its environment.
    env = {
        k: v
        for k, v in os.environ.items()
        if not any(secret in k.upper() for secret in ("TOKEN", "SECRET", "PASSWORD", "API_KEY"))
    }
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--store", str(store)],
            env=env,
            timeout=600,
            check=False,
            capture_output=True,
        )
        code = result.returncode
    except subprocess.TimeoutExpired:
        code = 124
    run = {
        "source": source,
        "run_id": run_id,
        "attempt": attempt,
        "code_revision": revision,
        "capture_exit_code": code,
        "acquisition_complete": code == 0,
        "scope": "route-qualification-only" if source == "qldc" else "bounded-source-capture",
        "producer_sha256": sha256_file(script),
        "non_claims": [
            "No operative legal status or atomic source snapshot.",
            "No stable release or scheduled-cycle qualification.",
            "Private payload preservation is not public payload permission.",
        ],
    }
    write_json(store / "hosted-run.json", run)
    pack(store, work / "packet", run)


def commit_files(api: Any, repo: str, files: dict[str, Path | bytes]) -> str:
    """Atomic bounded commit with optimistic concurrency and bounded transient retries."""
    from huggingface_hub import CommitOperationAdd
    from huggingface_hub.errors import HfHubHTTPError

    for attempt in range(4):
        try:
            parent = api.repo_info(repo, repo_type="dataset").sha
            result = api.create_commit(
                repo_id=repo,
                repo_type="dataset",
                parent_commit=parent,
                operations=[
                    CommitOperationAdd(path_in_repo=name, path_or_fileobj=value)
                    for name, value in files.items()
                ],
                commit_message="Preserve bounded council capture evidence",
            )
            return str(result.oid)
        except HfHubHTTPError as exc:
            if exc.response.status_code not in (409, 429, 500, 502, 503, 504) or attempt == 3:
                raise
            time.sleep(2**attempt)
    raise AssertionError("bounded commit retry exhausted")


def checked_manifest(api: Any, checkpoint: dict[str, Any], work: Path) -> dict[str, Any]:
    from huggingface_hub import hf_hub_download

    revision, prefix = checkpoint["revision"], checkpoint["prefix"]
    if not re.fullmatch(r"[0-9a-f]{40}", revision) or not re.fullmatch(
        r"campaigns/[0-9]+/(tasman|npdc|qldc)/[0-9]+", prefix
    ):
        raise ValueError("invalid checkpoint reference")
    remote_paths = [f"{prefix}/{name}" for name in ("manifest.json", "raw.tar")]
    sizes = {
        item.path: item.size
        for item in api.get_paths_info(
            PRIVATE_REPO, remote_paths, repo_type="dataset", revision=revision
        )
    }
    if set(sizes) != set(remote_paths) or any(
        type(sizes[path]) is not int or not 0 < sizes[path] <= limit
        for path, limit in zip(remote_paths, (MAX_MANIFEST_BYTES, MAX_TAR_BYTES), strict=True)
    ):
        raise ValueError("remote checkpoint file missing or exceeds readback budget")
    manifest_path = Path(
        hf_hub_download(
            PRIVATE_REPO,
            remote_paths[0],
            repo_type="dataset",
            revision=revision,
            token=api.token,
            local_dir=work,
        )
    )
    manifest: dict[str, Any] = json.loads(manifest_path.read_text())
    validate_manifest(manifest)
    if manifest["archive_bytes"] != sizes[remote_paths[1]]:
        raise ValueError("remote archive size differs from manifest")
    if manifest["manifest_sha256"] != checkpoint["manifest_sha256"]:
        raise ValueError("checkpoint manifest mismatch")
    archive_path = Path(
        hf_hub_download(
            PRIVATE_REPO,
            remote_paths[1],
            repo_type="dataset",
            revision=revision,
            token=api.token,
            local_dir=work,
        )
    )
    verify_packet(archive_path, manifest)
    return manifest


def verify_public_checkpoint(api: Any, checkpoint: dict[str, Any], work: Path) -> None:
    from huggingface_hub import hf_hub_download

    revision = checkpoint["public_revision"]
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("invalid public checkpoint revision")
    entries = checkpoint["public_files"]
    if set(entries) != {"preservation.json", "manifest.json"}:
        raise ValueError("invalid public checkpoint closure")
    names = [f"{checkpoint['prefix']}/{name}" for name in entries]
    sizes = {
        item.path: item.size
        for item in api.get_paths_info(
            PUBLIC_REPO, names, repo_type="dataset", revision=revision, token=False
        )
    }
    if set(sizes) != set(names):
        raise ValueError("original public checkpoint files missing")
    for name, entry in entries.items():
        remote_name = f"{checkpoint['prefix']}/{name}"
        if (
            type(entry["bytes"]) is not int
            or not 0 < entry["bytes"] <= MAX_MANIFEST_BYTES
            or sizes[remote_name] != entry["bytes"]
        ):
            raise ValueError("original public checkpoint size mismatch")
        path = Path(
            hf_hub_download(
                PUBLIC_REPO,
                remote_name,
                repo_type="dataset",
                revision=revision,
                token=False,
                force_download=True,
                local_dir=work / "anonymous-readback",
            )
        )
        if path.stat().st_size != entry["bytes"] or sha256_file(path) != entry["sha256"]:
            raise ValueError("original public evidence digest mismatch")
    evidence = json.loads(
        (work / "anonymous-readback" / checkpoint["prefix"] / "preservation.json").read_text()
    )
    evidence.update(public_revision=revision, anonymous_evidence_verified=True)
    write_json(work / "public/preservation.json", evidence)


def require_visibility(api: Any) -> None:
    if api.repo_info(PRIVATE_REPO, repo_type="dataset").private is not True:
        raise ValueError("raw destination must be private")
    if api.repo_info(PUBLIC_REPO, repo_type="dataset").private is not False:
        raise ValueError("evidence destination must be public")


def publish(api: Any, work: Path, manifest: dict[str, Any]) -> None:
    require_visibility(api)
    prefix = f"campaigns/{manifest['run_id']}/{manifest['source']}/{manifest['attempt']}"
    verify_packet(work / "packet/raw.tar", manifest)
    revision = commit_files(
        api,
        PRIVATE_REPO,
        {
            f"{prefix}/raw.tar": work / "packet/raw.tar",
            f"{prefix}/manifest.json": work / "packet/manifest.json",
        },
    )
    checkpoint = {
        "prefix": prefix,
        "revision": revision,
        "manifest_sha256": manifest["manifest_sha256"],
    }
    verified = checked_manifest(api, checkpoint, work / "readback")
    if verified != manifest:
        raise ValueError("uploaded manifest differs from local packet")
    # Only the non-reconstructive manifest and verification receipt cross the public boundary.
    evidence = {
        "schema_version": "1.0.0",
        "source": manifest["source"],
        "run_id": manifest["run_id"],
        "attempt": manifest["attempt"],
        "private_preservation": checkpoint,
        "raw_bytes_verified": True,
        "acquisition_complete": manifest["acquisition_complete"],
        "public_payload": False,
        "scope": manifest["scope"],
    }
    payload = json.dumps(evidence, indent=2).encode() + b"\n"
    manifest_payload = json.dumps(manifest, indent=2).encode() + b"\n"
    public_revision = commit_files(
        api,
        PUBLIC_REPO,
        {
            f"{prefix}/preservation.json": payload,
            f"{prefix}/manifest.json": manifest_payload,
        },
    )
    durable_checkpoint = {
        **checkpoint,
        "public_revision": public_revision,
        "public_files": {
            name: {"sha256": sha256_bytes(value), "bytes": len(value)}
            for name, value in (("preservation.json", payload), ("manifest.json", manifest_payload))
        },
    }
    verify_public_checkpoint(api, durable_checkpoint, work)
    # Publish the reusable checkpoint only after private and anonymous public verification.
    checkpoint_name = f"campaigns/{manifest['run_id']}/{manifest['source']}/checkpoint.json"
    commit_files(api, PRIVATE_REPO, {checkpoint_name: json.dumps(durable_checkpoint).encode()})


def resume(api: Any, source: str, run_id: str, revision: str, work: Path) -> bool:
    from huggingface_hub import hf_hub_download
    from huggingface_hub.errors import EntryNotFoundError

    require_visibility(api)
    try:
        path = hf_hub_download(
            PRIVATE_REPO,
            f"campaigns/{run_id}/{source}/checkpoint.json",
            repo_type="dataset",
            token=api.token,
            force_download=True,
            local_dir=work / "checkpoint",
        )
    except EntryNotFoundError:
        return False
    checkpoint = json.loads(Path(path).read_text())
    manifest = checked_manifest(api, checkpoint, work / "readback")
    if (manifest["source"], manifest["run_id"], manifest["code_revision"]) != (
        source,
        run_id,
        revision,
    ):
        raise ValueError("checkpoint source/run/code mismatch")
    verify_public_checkpoint(api, checkpoint, work)
    return manifest["acquisition_complete"] is True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("resume", "capture", "publish"))
    parser.add_argument("--source", choices=tuple(SCRIPTS), required=True)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    run_id, attempt, revision = (
        os.environ[name] for name in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_SHA")
    )
    if (
        not run_id.isdecimal()
        or not attempt.isdecimal()
        or not re.fullmatch(r"[0-9a-f]{40}", revision)
    ):
        parser.error("invalid hosted run identity")
    work = args.work.resolve()
    if args.command == "capture":
        capture(args.source, work, run_id, attempt, revision)
        return 0  # Preserve partial packets before reporting source failure in publication step.
    from huggingface_hub import HfApi

    api = HfApi(token=os.environ["HF_TOKEN"])
    if args.command == "resume":
        resumed = resume(api, args.source, run_id, revision, work)
        with Path(os.environ["GITHUB_OUTPUT"]).open("a") as output:
            output.write(f"resumed={str(resumed).lower()}\n")
        return 0
    manifest = json.loads((work / "packet/manifest.json").read_text())
    publish(api, work, manifest)
    return 0 if manifest["acquisition_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
