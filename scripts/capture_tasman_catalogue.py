#!/usr/bin/env python3
"""Capture the named Tasman Hub catalogue and one complete planning-zones layer."""

from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import replace
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import httpx

from riopa_provenance.arcgis import ArcGISFeatureLayerArchiver
from riopa_provenance.capture import (
    CaptureError,
    CapturePolicy,
    CaptureResult,
    CaptureStore,
    HttpCaptureClient,
)
from riopa_provenance.hashing import sha256_bytes, sha256_json
from riopa_provenance.retry import RateLimiter, RateLimitPolicy, decide_retry

SOURCE_ID = "urn:riopa:source:tasman:geohub"
GROUPS = ("d082054cea30461f99bea1fb69a76ed5", "2e814c7362524afbac191cde905d6d44")
SITE_ID = "e47e7c3ff1254c4bb58d59e59b862c70"
ITEM_ID = "99868f57e0df486991a4785a1d3303d3"
TERMS_ID = "fe285ebaf93f4e2f81c6b77d614623c8"
HUB = "https://geohub.tasman.govt.nz/"
API = "https://www.arcgis.com/sharing/rest"
SERVICE = "https://gispublic.tasman.govt.nz/server/rest/services/OpenData/OpenData_Planning_TRMPLand_Zones/MapServer"
HOSTS = frozenset(
    {"www.tasman.govt.nz", "geohub.tasman.govt.nz", "www.arcgis.com", "gispublic.tasman.govt.nz"}
)


class BoundedClient(HttpCaptureClient):
    """Bound every retained response and preserve retries before further I/O."""

    def __init__(
        self, *, max_total_bytes: int = 256_000_000, max_requests: int = 32, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        if (
            type(max_total_bytes) is not int
            or max_total_bytes < 1
            or type(max_requests) is not int
            or max_requests < 1
        ):
            raise ValueError("capture bounds must be positive integers")
        self.max_total_bytes = max_total_bytes
        self.max_requests = max_requests
        self.total_bytes = 0
        self.attempts: list[dict[str, Any]] = []
        self.per_response_limit = self.policy.max_response_bytes

    def capture(self, method: str, url: str, **kwargs: Any) -> CaptureResult:
        kwargs.pop("require_success", None)
        for attempt in range(1, 4):
            if len(self.attempts) >= self.max_requests or self.total_bytes >= self.max_total_bytes:
                raise CaptureError("capture request or retained-byte budget exhausted")
            self.policy = replace(
                self.policy,
                max_response_bytes=min(
                    self.per_response_limit, self.max_total_bytes - self.total_bytes
                ),
            )
            record: dict[str, Any] = {
                "sequence": len(self.attempts) + 1,
                "attempt": attempt,
                "endpoint_id": kwargs.get("endpoint_id"),
                "observed_at": self.store.clock().isoformat(),
            }
            result = None
            try:
                result = super().capture(method, url, require_success=False, **kwargs)
            except (httpx.HTTPError, CaptureError) as exc:
                record["failure_type"] = type(exc).__name__
                if isinstance(exc, httpx.TransportError):
                    decision = decide_retry(method=method, attempt=attempt)
                else:
                    raise
            else:
                self.total_bytes += result.size_bytes
                record.update(
                    capture_id=result.capture_id,
                    sha256=result.object_sha256,
                    bytes=result.size_bytes,
                    http_status=result.status_code,
                    retrieved_at=result.retrieved_at,
                )
                decision = decide_retry(
                    method=method,
                    attempt=attempt,
                    status_code=result.status_code,
                    retry_after=result.retry_after,
                    now=self.store.clock(),
                )
            finally:
                self.attempts.append(record)
                directory = self.store.root / "attempts"
                directory.mkdir(exist_ok=True)
                # Content addressing avoids overwriting earlier invocations in this store.
                payload = json.dumps(record, sort_keys=True).encode()
                digest, _ = self.store.write_object(payload)
                (directory / f"{digest}.json").write_bytes(payload)
            if decision.retry:
                self.sleep(decision.delay_seconds)
                continue
            if result is None:
                raise CaptureError("bounded transport attempts exhausted")
            metadata = self.store.verify_capture_integrity(result.capture_id)
            if result.status_code != 200 or any(
                key.lower() == "content-range" for key in metadata["response"]["headers"]
            ):
                raise CaptureError("complete HTTP 200 response required")
            return result
        raise AssertionError("retry loop must terminate")


def validate_catalogue_pages(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate a complete single-group traversal, not an atomic server snapshot."""
    if not pages:
        raise ValueError("empty catalogue traversal")
    expected_start, total = 1, pages[0].get("total")
    if type(total) is not int or not 0 <= total <= 500:
        raise ValueError("invalid or out-of-budget catalogue total")
    items: dict[str, dict[str, Any]] = {}
    for page in pages:
        if not isinstance(page, dict) or "error" in page:
            raise ValueError("catalogue API error or non-object response")
        if any(type(page.get(key)) is not int for key in ("start", "total", "nextStart")):
            raise ValueError("catalogue pagination requires integer fields")
        rows = page.get("results")
        if (
            page["start"] != expected_start
            or page["total"] != total
            or not isinstance(rows, list)
            or len(rows) > 100
        ):
            raise ValueError("catalogue page contract changed")
        for item in rows:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("id"), str)
                or not re.fullmatch(r"[0-9a-f]{32}", item["id"])
                or item["id"] in items
            ):
                raise ValueError("invalid or duplicate catalogue item")
            items[item["id"]] = item
        expected_start = page["nextStart"]
        if expected_start != -1 and (not rows or expected_start != page["start"] + len(rows)):
            raise ValueError("catalogue cursor did not advance exactly")
    if expected_start != -1 or len(items) != total:
        raise ValueError("catalogue traversal incomplete")
    return list(items.values())


def capture_tasman(client: BoundedClient) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "record_type": "tasman_catalogue_and_zones_capture",
        "source_id": SOURCE_ID,
        "producer_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "status": "incomplete",
        "groups": [],
        "bounds": {
            "max_requests": client.max_requests,
            "max_total_bytes": client.max_total_bytes,
            "max_response_bytes": client.per_response_limit,
            "max_pages_per_group": 5,
            "max_layer_pages": 4,
        },
        "byte_budget_scope": (
            "retained response bodies, including failed HTTP attempts; "
            "not wire or rejected overflow bytes"
        ),
        "non_claims": [
            "Catalogue traversal is not an atomic snapshot or full catalogue payload archival.",
            "Catalogue modified dates are not source currency or operative/valid dates.",
            "The zones layer is illustrative source geometry, not authoritative planning advice.",
            "No canonical materialisation, hosted cycle, public payload publication "
            "or external preservation is claimed.",
        ],
    }
    stage = "authority"

    def get_json(url: str, endpoint: str, **params: Any) -> dict[str, Any]:
        _, value = client.capture_json(
            "GET", url, source_id=SOURCE_ID, endpoint_id=f"{SOURCE_ID}:{endpoint}", params=params
        )
        if not isinstance(value, dict) or "error" in value:
            raise ValueError("expected a non-error JSON object")
        return value

    try:
        client.capture(
            "GET",
            "https://www.tasman.govt.nz/my-region/maps",
            source_id=SOURCE_ID,
            endpoint_id=f"{SOURCE_ID}:authority",
        )
        stage = "hub"
        home = client.capture("GET", HUB, source_id=SOURCE_ID, endpoint_id=f"{SOURCE_ID}:hub")
        match = re.search(r'window\.__SITE="([^"]+)"', home.object_path.read_text())
        if match is None:
            raise ValueError("Hub site configuration missing")
        site = json.loads(unquote(match.group(1)))["site"]
        predicates = site["data"]["catalogV2"]["scopes"]["item"]["filters"]
        expected = [{"predicates": [{"group": list(GROUPS)}]}]
        if site["item"]["id"] != SITE_ID or predicates != expected:
            raise ValueError("Hub identity or catalogue scope changed")
        receipt["site_id"] = SITE_ID
        stage = "terms"
        get_json(f"{API}/content/items/{TERMS_ID}/data", "hub-terms", f="json")
        client.capture(
            "GET",
            "https://www.tasman.govt.nz/my-council/about-us/terms-and-conditions/website-terms-of-use",
            source_id=SOURCE_ID,
            endpoint_id=f"{SOURCE_ID}:website-terms",
        )
        catalogue: dict[str, dict[str, Any]] = {}
        for group in GROUPS:
            stage = f"catalogue:{group}"
            pages = []
            cursor = 1
            for _ in range(5):
                page = get_json(
                    f"{API}/search",
                    stage,
                    f="json",
                    q=f"group:{group}",
                    num=100,
                    start=cursor,
                    sortField="title",
                    sortOrder="asc",
                )
                pages.append(page)
                next_start = page.get("nextStart")
                if next_start == -1:
                    break
                if type(next_start) is not int or next_start <= cursor:
                    raise ValueError("catalogue cursor did not advance")
                cursor = next_start
            items = validate_catalogue_pages(pages)
            receipt["groups"].append(
                {
                    "group_id": group,
                    "count": len(items),
                    "pages": len(pages),
                    "item_ids": sorted(item["id"] for item in items),
                }
            )
            for item in items:
                if item["id"] in catalogue and sha256_json(catalogue[item["id"]]) != sha256_json(
                    item
                ):
                    raise ValueError("shared catalogue item changed between group observations")
                catalogue[item["id"]] = item
        receipt["catalogue_unique_items"] = len(catalogue)
        stage = "selected-item"
        selected = catalogue[ITEM_ID]
        if (
            selected.get("url") != f"{SERVICE}/3"
            or selected.get("accessInformation") != "Tasman District Council (TDC)"
        ):
            raise ValueError("selected catalogue item binding changed")
        licence = selected.get("licenseInfo", "")
        if "https://creativecommons.org/licenses/by/4.0/" not in licence:
            raise ValueError("selected item licence changed")
        receipt["selected_item"] = {
            "id": ITEM_ID,
            "url": selected["url"],
            "title": selected["title"],
            "catalogue_modified": selected.get("modified"),
            "license_metadata_sha256": sha256_bytes(licence.encode()),
            "attribution": selected["accessInformation"],
            "licence_metadata_link": "https://creativecommons.org/licenses/by/4.0/",
            "rights_decision": "captured item metadata; no automatic publication approval",
            "public_payload_status": "not-published",
            "valid_time": None,
            "operative_status": "unresolved",
        }
        # Keep a standalone item receipt: publishing the entire catalogue page
        # would accidentally include unrelated, differently licensed items.
        stage = "selected-item-licence"
        rights_capture, rights_item = client.capture_json(
            "GET",
            f"{API}/content/items/{ITEM_ID}",
            source_id=SOURCE_ID,
            endpoint_id=f"{SOURCE_ID}:zones:licence",
            params={"f": "json"},
        )
        if not isinstance(rights_item, dict) or any(
            rights_item.get(key) != selected.get(key)
            for key in ("id", "url", "accessInformation", "licenseInfo")
        ):
            raise ValueError("standalone item rights differ from catalogue observation")
        receipt["selected_item"]["rights_capture_id"] = rights_capture.capture_id
        receipt["selected_item"]["rights_object_sha256"] = rights_capture.object_sha256
        stage = "zones-layer"
        archive = ArcGISFeatureLayerArchiver(client, max_pages=4).archive_layer(
            source_id=SOURCE_ID, endpoint_id=f"{SOURCE_ID}:zones", service_url=SERVICE, layer_id=3
        )
        receipt["zones"] = {
            "feature_count": archive.feature_count,
            "manifest_path": str(archive.manifest_path.relative_to(client.store.root)),
            "manifest_sha256": sha256_bytes(archive.manifest_path.read_bytes()),
        }
        receipt["status"] = "captured"
    except (CaptureError, httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError) as exc:
        receipt["failure"] = {"stage": stage, "type": type(exc).__name__}
    receipt["attempts"] = client.attempts
    receipt["total_bytes"] = client.total_bytes
    receipt["semantic_sha256"] = sha256_json(receipt)
    output = client.store.root / f"tasman-receipt-{receipt['semantic_sha256']}.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.store.resolve()
    if output.is_relative_to(root) and not output.is_relative_to(root / ".riopa-local"):
        parser.error("raw capture store must be outside Git or in .riopa-local")
    with httpx.Client(timeout=60, follow_redirects=False, trust_env=False) as transport:
        client = BoundedClient(
            client=transport,
            store=CaptureStore(output),
            policy=CapturePolicy(allowed_hosts=HOSTS, max_response_bytes=64_000_000),
            rate_limiter=RateLimiter(RateLimitPolicy(requests_per_second=1)),
            sleep=time.sleep,
        )
        receipt = capture_tasman(client)
    print(
        json.dumps(
            {
                key: receipt.get(key)
                for key in (
                    "status",
                    "catalogue_unique_items",
                    "zones",
                    "failure",
                    "total_bytes",
                    "semantic_sha256",
                )
            }
        )
    )
    return 0 if receipt["status"] == "captured" else 1


if __name__ == "__main__":
    raise SystemExit(main())
