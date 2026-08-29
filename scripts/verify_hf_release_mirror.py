#!/usr/bin/env python3
"""Verify the public Hugging Face mirror of a release without authentication."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "riopa-release-mirror-verifier/1"})
    try:
        with urlopen(request, timeout=30) as response:  # noqa: S310 - fixed HTTPS URL source
            return response.read()
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"mirror download failed for {url}: {exc}") from exc


def verify(receipt_path: Path, mirror_path: Path) -> dict[str, object]:
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    mirror = json.loads(mirror_path.read_text(encoding="utf-8"))
    source_hash = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    declared_source = mirror["source_publication_receipt"]["sha256"]
    if source_hash != declared_source:
        raise RuntimeError("historical publication receipt digest does not match mirror record")
    details = mirror["mirror"]
    repository = details["repository"]
    commit = details["commit"]
    prefix = details["path"].strip("/")
    assets = receipt["assets"]
    expected = {asset["name"]: asset["sha256"] for asset in assets}
    expected["release-metadata.json"] = details["release_metadata_sha256"]
    matches: list[str] = []
    for name, digest in expected.items():
        url = f"https://huggingface.co/datasets/{repository}/resolve/{commit}/{prefix}/{name}?download=true"
        payload = fetch_bytes(url)
        observed = hashlib.sha256(payload).hexdigest()
        if observed != digest:
            raise RuntimeError(f"digest mismatch for {name}: expected {digest}, got {observed}")
        matches.append(name)
    return {
        "schema_version": "1.0.0",
        "repository": repository,
        "commit": commit,
        "release": receipt["release"],
        "verified_files": matches,
        "verified_file_count": len(matches),
        "classification": "public-byte-mirror-verification",
        "non_claims": mirror["qualification"]["does_not_establish"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--receipt", type=Path, default=Path("docs/v0.4.0-release-publication-20260829.json")
    )
    parser.add_argument(
        "--mirror-record", type=Path, default=Path("docs/v0.4.0-release-mirror-20260829.json")
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = verify(args.receipt, args.mirror_record)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
