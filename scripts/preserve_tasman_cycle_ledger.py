#!/usr/bin/env python3
"""Publish bounded metadata-only Tasman observations with a compare-and-swap head."""

from __future__ import annotations

import argparse
import json
import os
import re
import runpy
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from huggingface_hub import CommitOperationAdd, HfApi, hf_hub_download
from huggingface_hub.errors import HfHubHTTPError

from riopa_provenance.hashing import sha256_bytes

ROOT = Path(__file__).resolve().parents[1]
CORE = runpy.run_path(str(ROOT / "scripts/tasman_cycle_ledger.py"))
PUBLIC = "edithatogo/riopa-public-data-archive"
PREFIX = "operational/tasman-cycle-ledger/v1"
HEAD = PREFIX + "/head.json"
LIMIT = 2_000_000
FILES = {
    "source": "tasman-publication.json",
    "derived": "tasman-derivatives.json",
    "provenance": "tasman-run-provenance.json",
    "comparison": "tasman-snapshot-comparison.json",
}


def check(condition: bool) -> None:
    if not condition:
        raise ValueError("ledger preservation contract failed")


def encode(value: Any) -> bytes:
    body = (json.dumps(value, indent=2) + "\n").encode()
    check(len(body) <= LIMIT)
    return body


def safe(path: Path) -> Path:
    check(".." not in path.parts and not any(p.is_symlink() for p in (path, *path.parents)))
    return path


def revision(value: Any) -> str:
    check(isinstance(value, str) and re.fullmatch(r"[a-f0-9]{40}", value) is not None)
    return str(value)


def work_path(path: Path) -> Path:
    path = safe(path.absolute())
    check(not path.is_relative_to(ROOT) or path.is_relative_to(ROOT / ".riopa-local"))
    return path


def templates() -> dict[str, Any]:
    def read(name: str) -> Any:
        return json.loads((ROOT / "docs" / name).read_bytes())

    return {
        "source": read("tasman-publication-acceptance-20260830.json")["publication_receipt"],
        "derived": read("tasman-derived-acceptance-20260831.json")["publication_receipt"],
        "provenance": read("tasman-run-provenance-acceptance-20260831.json")["attempts"][0][
            "receipt"
        ],
        "comparison": read("tasman-feature-comparison-acceptance-20260831.json")[
            "comparison_receipt"
        ],
    }


def metadata_shape(value: Any, template: Any, key: str = "") -> None:
    """Fail closed on unrecognised fields; do not upload arbitrary local JSON."""
    if key == "change_hashes":
        check(isinstance(value, dict) and len(value) <= 100_000)
        for oid, sides in value.items():
            check(re.fullmatch(r"-?[0-9]{1,20}", oid) is not None)
            check(isinstance(sides, dict) and set(sides) == {"before", "after"})
            for side in sides.values():
                if side is not None:
                    check(
                        isinstance(side, dict)
                        and set(side) == {"attributes_sha256", "geometry_sha256"}
                    )
                    for digest in side.values():
                        CORE["digest"](digest)
    elif isinstance(template, dict):
        check(isinstance(value, dict) and set(value) == set(template))
        for name, child in template.items():
            metadata_shape(value[name], child, name)
    elif isinstance(template, list):
        check(isinstance(value, list) and len(value) <= 100_000)
        for item in value:
            check(isinstance(item, str) and len(item) <= 2048)
    elif template is None and key == "conclusion":
        check(value is None or value == "success")
    else:
        check(type(value) is type(template))
        if isinstance(value, str):
            check(len(value) <= 16_384)


def fetch(api: Any, name: str, sha: str, work: Path, *, missing: bool = False) -> bytes | None:
    infos = api.get_paths_info(PUBLIC, [name], repo_type="dataset", revision=sha, token=False)
    if not infos and missing:
        return None
    check(len(infos) == 1 and infos[0].path == name)
    check(type(infos[0].size) is int and 0 < infos[0].size <= LIMIT)
    directory = safe(work / ("readback-" + str(uuid.uuid4())))
    path = Path(
        hf_hub_download(
            PUBLIC,
            name,
            repo_type="dataset",
            revision=sha,
            token=False,
            force_download=True,
            local_dir=directory,
        )
    )
    check(path == directory / name)
    body = CORE["read"](safe(path))
    check(len(body) == infos[0].size)
    return bytes(body)


def load_head(
    api: Any, sha: str, work: Path
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    body = fetch(api, HEAD, sha, work, missing=True)
    if body is None:
        check(
            not api.get_paths_info(PUBLIC, [PREFIX], repo_type="dataset", revision=sha, token=False)
        )
        return None, None
    head = CORE["parse"](body)
    check(set(head) == {"schema_version", "ledger_path", "ledger_sha256", "ledger_bytes"})
    check(head["schema_version"] == "1.0.0")
    digest = CORE["digest"](head["ledger_sha256"])
    check(head["ledger_path"] == f"{PREFIX}/ledgers/{digest}.json")
    body = fetch(api, head["ledger_path"], sha, work)
    if body is None:
        raise ValueError("missing ledger bytes")
    check(type(head["ledger_bytes"]) is int and len(body) == head["ledger_bytes"])
    check(sha256_bytes(body) == digest)
    ledger = CORE["parse"](body)
    CORE["validate"](ledger)
    retained = 0
    receipts: dict[str, bytes] = {}
    for event in ledger["events"]:
        check(event["kind"] == "observation")
        documents = {}
        for name, digest in event["evidence_sha256"].items():
            CORE["digest"](digest)
            if digest not in receipts:
                receipt = fetch(api, f"{PREFIX}/receipts/{digest}.json", sha, work)
                if receipt is None:
                    raise ValueError("missing historical receipt")
                check(sha256_bytes(receipt) == digest)
                retained += len(receipt)
                check(retained <= 16_000_000)
                receipts[digest] = receipt
            documents[name] = receipts[digest]
        observed = CORE["observation"](documents, event["evidence_sha256"])
        check(
            observed
            == {
                k: v
                for k, v in event.items()
                if k not in ("previous_event_sha256", "event_sha256", "predecessor_source_run")
            }
        )
    return dict(head), dict(ledger)


def preserve(api: Any, work: Path) -> dict[str, Any]:
    check(os.environ.get("GITHUB_ACTIONS") == "true")
    check(os.environ.get("GITHUB_REF") == "refs/heads/main")
    check(os.environ.get("GITHUB_REPOSITORY") == "edithatogo/riopa-infrastructure")
    work = work_path(work)
    documents = {name: CORE["read"](safe(work / "public" / path)) for name, path in FILES.items()}
    schemas = templates()
    for name, body in documents.items():
        metadata_shape(CORE["parse"](body), schemas[name])
    hashes = {name: sha256_bytes(body) for name, body in documents.items()}
    observed = CORE["observation"](documents, hashes)
    check(observed["publication"]["run_id"] == os.environ.get("GITHUB_RUN_ID"))
    check(observed["publication"]["attempt"] == os.environ.get("GITHUB_RUN_ATTEMPT"))
    check(observed["publication"]["code_sha"] == os.environ.get("GITHUB_SHA"))
    for attempt in range(4):
        info = api.repo_info(PUBLIC, repo_type="dataset", token=False)
        check(info.private is False)
        parent = revision(info.sha)
        old_head, old = load_head(api, parent, work)
        ledger = CORE["append_observation"](old, documents, hashes)
        body = encode(ledger)
        digest = sha256_bytes(body)
        ledger_path = f"{PREFIX}/ledgers/{digest}.json"
        files = {f"{PREFIX}/receipts/{hashes[name]}.json": body for name, body in documents.items()}
        files[ledger_path] = body
        pointer = {
            "schema_version": "1.0.0",
            "ledger_path": ledger_path,
            "ledger_sha256": digest,
            "ledger_bytes": len(body),
        }
        files[HEAD] = encode(pointer)
        if old_head == pointer:
            committed = parent
        else:
            additions = {HEAD: files[HEAD]}
            for name, expected in files.items():
                if name == HEAD:
                    continue
                existing = fetch(api, name, parent, work, missing=True)
                if existing is None:
                    additions[name] = expected
                else:
                    check(existing == expected)  # Never replace corrupt historical objects.
            # A 409 must re-read/recompute, never retry a stale head on a new parent.
            try:
                result = api.create_commit(
                    repo_id=PUBLIC,
                    repo_type="dataset",
                    parent_commit=parent,
                    operations=[
                        CommitOperationAdd(path_in_repo=name, path_or_fileobj=value)
                        for name, value in sorted(additions.items())
                    ],
                    commit_message="Preserve bounded Tasman cycle metadata",
                )
                committed = revision(result.oid)
            except HfHubHTTPError as error:
                if error.response.status_code == 409 and attempt < 3:
                    continue
                raise
        # Exact revision readback also recovers commit-success/local-failure retries.
        check(len(files) <= 6 and sum(len(value) for value in files.values()) <= 6 * LIMIT)

        def verify_file(item: tuple[str, bytes], sha: str = committed) -> None:
            name, expected = item
            check(fetch(api, name, sha, work) == expected)

        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(verify_file, files.items()))
        result = {
            "record_type": "tasman_cycle_ledger_preservation",
            "status": "verified",
            "public_repository": PUBLIC,
            "public_revision": committed,
            "ledger_path": ledger_path,
            "ledger_sha256": digest,
            "ledger_semantic_sha256": ledger["ledger_sha256"],
            "source_run": observed["source_run"],
            "publication": observed["publication"],
            "receipt_sha256": hashes,
            "source_run_count": ledger["unique_source_run_count"],
            "three_cycle_gate_qualified": False,
            "historical_baseline_imported": False,
            "qualification_gaps": ledger["qualification_gaps"],
        }
        safe(work / "public/tasman-cycle-preservation.json").write_bytes(encode(result))
        return result
    raise ValueError("ledger compare-and-swap attempts exhausted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    work = None
    try:
        work = work_path(args.work)
        previous = safe(work / "public/tasman-cycle-preservation.json")
        if previous.exists():
            previous.rename(previous.with_name(f"tasman-cycle-prior-{uuid.uuid4()}.json"))
        preserve(HfApi(token=os.environ["HF_TOKEN"]), work)
    except Exception as error:
        result = {"status": "failed", "error_class": type(error).__name__[:128]}
        try:
            if work is None:
                raise ValueError("unsafe failure output root")
            path = safe(work / "public/tasman-cycle-preservation-failure.json")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encode(result))
        except Exception as secondary:
            result["local_record_error_class"] = type(secondary).__name__[:128]
        print(json.dumps(result))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
