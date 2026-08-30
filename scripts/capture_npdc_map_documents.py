#!/usr/bin/env python3
"""Capture a bounded NPDC PDF-map inventory using the faithful HTTP runtime."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import replace
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

import httpx

from riopa_provenance.capture import (
    CaptureError,
    CaptureFailure,
    CaptureFailureCategory,
    CapturePolicy,
    CaptureResult,
    CaptureStore,
    HttpCaptureClient,
)
from riopa_provenance.hashing import sha256_json
from riopa_provenance.retry import RateLimiter, RateLimitPolicy

SOURCE_ID = "urn:riopa:source:npdc:district-plan-2005-maps"
INDEX_URL = (
    "https://www.npdc.govt.nz/planning-our-future/district-plan/"
    "operative-district-plan-2005/volume-3-maps/"
)


class MapLinks(HTMLParser):
    """Enumerate only the named content region, excluding site navigation/footer."""

    def __init__(self) -> None:
        super().__init__()
        self.heading: list[str] | None = None
        self.active = False
        self.found = False
        self.urls: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "h1":
            self.heading = []
        if tag == "footer" or "footer" in (dict(attrs).get("class") or "").split():
            self.active = False
        href = dict(attrs).get("href")
        if tag != "a" or not self.active or not href:
            return
        parsed = urlsplit(urljoin(INDEX_URL, href))
        if not parsed.path.lower().endswith(".pdf"):
            return
        if (
            parsed.scheme != "https"
            or parsed.netloc != "www.npdc.govt.nz"
            or not parsed.path.startswith("/media/")
            or parsed.query
            or parsed.fragment
            or "%" in parsed.path
            or ".." in parsed.path.split("/")
        ):
            raise ValueError("unexpected PDF link in NPDC map content")
        self.urls.add(parsed.geturl())

    def handle_data(self, data: str) -> None:
        if self.heading is not None:
            self.heading.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1" and self.heading is not None:
            title = " ".join("".join(self.heading).split())
            self.active = title == "Volume 3 - Maps"
            self.found = self.found or self.active
            self.heading = None


def enumerate_documents(html: str) -> list[str]:
    parser = MapLinks()
    parser.feed(html)
    if not parser.found or not parser.urls:
        raise ValueError("NPDC map heading or document inventory missing")
    return sorted(parser.urls)


def complete_response(result: CaptureResult) -> bool:
    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    headers = metadata["response"]["headers"]
    return result.status_code == 200 and not any(key.lower() == "content-range" for key in headers)


def capture_maps(
    client: HttpCaptureClient, *, max_documents: int = 160, max_total_bytes: int = 128_000_000
) -> dict[str, Any]:
    original_policy, original_observer = client.policy, client.on_failure
    try:
        return _capture_maps(client, max_documents=max_documents, max_total_bytes=max_total_bytes)
    finally:
        client.policy, client.on_failure = original_policy, original_observer


def _capture_maps(
    client: HttpCaptureClient, *, max_documents: int, max_total_bytes: int
) -> dict[str, Any]:
    """Preserve bounded responses; record failures without claiming partial bytes are complete."""
    if not 1 <= max_documents <= 160 or max_total_bytes < 1:
        raise ValueError("invalid capture bounds")
    per_response_limit = client.policy.max_response_bytes
    failure_records: list[dict[str, Any]] = []
    previous_observer = client.on_failure

    def record_failure(failure: CaptureFailure) -> None:
        record = {
            "record_type": "npdc_capture_failure",
            "source_id": SOURCE_ID,
            "observed_at": client.store.clock().isoformat(),
            "category": failure.category.value,
            "status_code": failure.status_code,
            "retryable": failure.retryable,
        }
        digest, _ = client.store.write_object(json.dumps(record, sort_keys=True).encode())
        directory = client.store.root / "failures"
        directory.mkdir(exist_ok=True)
        (directory / f"{digest}.json").write_text(json.dumps(record, indent=2) + "\n")
        failure_records.append({**record, "object_sha256": digest})
        if previous_observer is not None:
            previous_observer(failure)

    client.on_failure = record_failure
    client.policy = replace(
        client.policy, max_response_bytes=min(per_response_limit, max_total_bytes)
    )
    index = client.capture("GET", INDEX_URL, source_id=SOURCE_ID, endpoint_id=f"{SOURCE_ID}:index")
    if not complete_response(index):
        record_failure(
            CaptureFailure(
                CaptureFailureCategory.MALFORMED_RESPONSE,
                "partial index",
                status_code=index.status_code,
            )
        )
        client.on_failure = previous_observer
        raise ValueError("partial index response cannot establish document inventory")
    urls = enumerate_documents(index.object_path.read_text(encoding="utf-8"))
    total = index.size_bytes
    documents = []
    for position, url in enumerate(urls):
        item: dict[str, Any] = {"url": url, "status": "deferred-budget"}
        if position < max_documents and total < max_total_bytes:
            first_failure = len(failure_records)
            client.policy = replace(
                client.policy, max_response_bytes=min(per_response_limit, max_total_bytes - total)
            )
            try:
                result = client.capture(
                    "GET",
                    url,
                    source_id=SOURCE_ID,
                    endpoint_id=f"{SOURCE_ID}:document",
                    require_success=False,
                )
                total += result.size_bytes
                with result.object_path.open("rb") as handle:
                    is_pdf = handle.read(5) == b"%PDF-"
                item.update(
                    status="captured"
                    if complete_response(result) and is_pdf
                    else "invalid-response",
                    capture_id=result.capture_id,
                    sha256=result.object_sha256,
                    bytes=result.size_bytes,
                    http_status=result.status_code,
                    retrieved_at=result.retrieved_at,
                )
            except (CaptureError, httpx.HTTPError) as exc:
                item.update(
                    status="capture-failed",
                    failure_type=type(exc).__name__,
                    failures=failure_records[first_failure:],
                )
        documents.append(item)
    receipt = {
        "schema_version": "1.0.0",
        "record_type": "npdc_map_document_capture",
        "source_id": SOURCE_ID,
        "index": {
            "url": INDEX_URL,
            "capture_id": index.capture_id,
            "sha256": index.object_sha256,
            "bytes": index.size_bytes,
            "retrieved_at": index.retrieved_at,
        },
        "documents": documents,
        "discovered_count": len(urls),
        "captured_count": sum(item["status"] == "captured" for item in documents),
        "total_bytes": total,
        "bounds": {"max_documents": max_documents, "max_total_bytes": max_total_bytes},
        "byte_budget_scope": "retained response bodies; not transferred or rejected overflow bytes",
        "publication": "metadata-only; raw PDFs retained locally pending exact rights disposition",
        "non_claims": [
            "Inventory completeness is limited to PDF links in this captured index content.",
            "The 2005 plan label does not establish present operative legal status.",
            "PDF documents are not vector features or canonical bitemporal spatial records.",
            "This capture is not a scheduled cycle or public payload preservation receipt.",
        ],
    }
    receipt["semantic_sha256"] = sha256_json(receipt)
    client.on_failure = previous_observer
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, required=True)
    parser.add_argument("--max-documents", type=int, default=160)
    args = parser.parse_args()
    repository = Path(__file__).resolve().parents[1]
    output = args.store.resolve()
    if output.is_relative_to(repository) and not output.is_relative_to(repository / ".riopa-local"):
        parser.error("raw capture store must be outside Git or under .riopa-local")
    with httpx.Client(timeout=45, follow_redirects=False) as transport:
        client = HttpCaptureClient(
            client=transport,
            store=CaptureStore(output),
            policy=CapturePolicy(
                allowed_hosts=frozenset({"www.npdc.govt.nz"}), max_response_bytes=32_000_000
            ),
            rate_limiter=RateLimiter(RateLimitPolicy(requests_per_second=1)),
            sleep=time.sleep,
        )
        receipt = capture_maps(client, max_documents=args.max_documents)
    receipt_path = output / f"receipt-{receipt['semantic_sha256']}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(receipt_path)
    print(f"Captured {receipt['captured_count']}/{receipt['discovered_count']} PDFs")
    return 0 if receipt["captured_count"] == receipt["discovered_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
