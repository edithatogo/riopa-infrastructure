#!/usr/bin/env python3
"""Retain a bounded QLDC route-health snapshot, not a complete ePlan archive."""

from __future__ import annotations

import argparse
import json
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx

from riopa_provenance.capture import CaptureError, CapturePolicy, CaptureStore, HttpCaptureClient
from riopa_provenance.hashing import sha256_bytes, sha256_json
from riopa_provenance.retry import RateLimiter, RateLimitPolicy

SOURCE = "urn:riopa:source:qldc:eplan"
AUTHORITY = "https://www.qldc.govt.nz/your-council/district-plan/eplans"
ROUTES = {
    "operative-application": "https://districtplan.qldc.govt.nz/operative/",
    "proposed-application": "https://districtplan.qldc.govt.nz/proposed",
    "user-guide": "https://www.qldc.govt.nz/media/crfavxde/qldc_eplan_user-guide_mar24.pdf",
}


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        href = dict(attrs).get("href")
        if tag == "a" and href:
            self.urls.add(urljoin(AUTHORITY, href))


def qualify(client: HttpCaptureClient) -> dict[str, Any]:
    """One attempt per allowlisted route; HTTP denial never triggers a bypass/retry."""
    receipt: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "qldc_eplan_route_qualification",
        "source_id": SOURCE,
        "producer_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "status": "incomplete",
        "bounds": {"maximum_requests": 4, "per_response_bytes": client.policy.max_response_bytes},
        "routes": [],
        "non_claims": [
            "Application HTML is not a complete ePlan or an executable offline application.",
            "The guide is documentation, not plan provisions or spatial data.",
            "Route labels do not establish operative legal status or valid time.",
            "No public-payload publication, rights determination or preservation acceptance.",
            "HTTP denial describes this observation, not availability to all users.",
        ],
    }
    links: set[str] = set()
    for label, url in {"authority": AUTHORITY, **ROUTES}.items():
        row: dict[str, Any] = {"role": label, "url": url, "status": "not-attempted"}
        receipt["routes"].append(row)
        if label != "authority" and url not in links:
            row["status"] = "not-linked-by-authority"
            continue
        try:
            result = client.capture(
                "GET", url, source_id=SOURCE, endpoint_id=f"{SOURCE}:{label}", require_success=False
            )
            metadata = client.store.verify_capture_integrity(result.capture_id)
            row.update(
                capture_id=result.capture_id,
                sha256=result.object_sha256,
                bytes=result.size_bytes,
                http_status=result.status_code,
                retrieved_at=result.retrieved_at,
            )
            if result.status_code != 200:
                row["status"] = "http-denied" if result.status_code in (401, 403) else "http-error"
                continue
            if any(key.lower() == "content-range" for key in metadata["response"]["headers"]):
                row["status"] = "partial-response"
                continue
            payload = result.object_path.read_bytes()
            if label == "user-guide":
                row["status"] = "captured-guide" if payload.startswith(b"%PDF-") else "invalid-pdf"
            else:
                if "text/html" not in (result.media_type or "").lower():
                    raise ValueError("HTML response required")
                html = payload.decode("utf-8")
                row["status"] = "captured-authority" if label == "authority" else "captured-shell"
                if label == "authority":
                    parser = Links()
                    parser.feed(html)
                    links = parser.urls
        except (CaptureError, httpx.HTTPError, ValueError) as exc:
            row.update(status="capture-failed", failure_type=type(exc).__name__)
    receipt["total_retained_bytes"] = sum(row.get("bytes", 0) for row in receipt["routes"])
    receipt["status"] = (
        "routes-observed"
        if all(row["status"].startswith("captured-") for row in receipt["routes"])
        else "blocked-or-incomplete"
    )
    digest = sha256_json(receipt)
    receipt["semantic_sha256"] = digest
    payload = json.dumps(receipt, indent=2).encode() + b"\n"
    client.store.write_object(payload)
    output = client.store.root / f"qldc-routes-{digest}.json"
    if output.exists() and output.read_bytes() != payload:
        raise CaptureError("receipt collision")
    output.write_bytes(payload)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.store.resolve()
    if output.is_relative_to(root) and not output.is_relative_to(root / ".riopa-local"):
        parser.error("raw capture store must be outside Git or in .riopa-local")
    with httpx.Client(timeout=45, follow_redirects=False, trust_env=False) as transport:
        client = HttpCaptureClient(
            client=transport,
            store=CaptureStore(output),
            policy=CapturePolicy(
                allowed_hosts=frozenset({"www.qldc.govt.nz", "districtplan.qldc.govt.nz"}),
                max_response_bytes=8_000_000,
            ),
            rate_limiter=RateLimiter(RateLimitPolicy(requests_per_second=1)),
            sleep=time.sleep,
        )
        receipt = qualify(client)
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["status"] == "routes-observed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
