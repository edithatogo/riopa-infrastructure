from __future__ import annotations

import json
import runpy
from pathlib import Path
from urllib.parse import quote

import httpx
import pytest

from riopa_provenance.capture import CaptureError, CapturePolicy, CaptureStore
from riopa_provenance.hashing import sha256_bytes, sha256_json

SCRIPT = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/capture_tasman_catalogue.py")
)


def test_catalogue_pages_reconcile_membership() -> None:
    pages = [
        {"start": 1, "total": 2, "nextStart": 2, "results": [{"id": "a" * 32}]},
        {"start": 2, "total": 2, "nextStart": -1, "results": [{"id": "b" * 32}]},
    ]
    assert len(SCRIPT["validate_catalogue_pages"](pages)) == 2


@pytest.mark.parametrize("change", ["duplicate", "total", "cursor", "boolean", "error", "id"])
def test_catalogue_rejects_inconsistent_pages(change: str) -> None:
    pages = [
        {"start": 1, "total": 2, "nextStart": 2, "results": [{"id": "a" * 32}]},
        {"start": 2, "total": 2, "nextStart": -1, "results": [{"id": "b" * 32}]},
    ]
    if change == "duplicate":
        pages[1]["results"] = [{"id": "a" * 32}]
    elif change == "total":
        pages[1]["total"] = 3
    elif change == "cursor":
        pages[0]["nextStart"] = 1
    elif change == "boolean":
        pages[0]["start"] = True
    elif change == "error":
        pages[1]["error"] = {"code": 400}
    else:
        pages[1]["results"] = [{"id": "../bad"}]
    with pytest.raises(ValueError):
        SCRIPT["validate_catalogue_pages"](pages)


def test_bounded_client_retries_and_accounts_all_attempts(tmp_path: Path) -> None:
    calls = 0
    delays = []

    def respond(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            503 if calls == 1 else 200, content=b"{}", headers={"Retry-After": "2"}
        )

    with httpx.Client(transport=httpx.MockTransport(respond)) as transport:
        client = SCRIPT["BoundedClient"](
            client=transport,
            store=CaptureStore(tmp_path),
            policy=CapturePolicy(allowed_hosts=frozenset({"www.arcgis.com"})),
            sleep=delays.append,
            max_total_bytes=10,
            max_requests=4,
        )
        client.capture("GET", "https://www.arcgis.com/", source_id="source", endpoint_id="endpoint")
        assert client.total_bytes == 4
        assert len(client.attempts) == 2
        assert delays == [2]
        assert list((tmp_path / "attempts").glob("*.json"))


@pytest.mark.parametrize("status,headers", [(206, {}), (200, {"Content-Range": "bytes 0-1/20"})])
def test_partial_http_is_never_accepted(
    tmp_path: Path, status: int, headers: dict[str, str]
) -> None:
    with httpx.Client(
        transport=httpx.MockTransport(
            lambda _: httpx.Response(status, content=b"{}", headers=headers)
        )
    ) as transport:
        client = SCRIPT["BoundedClient"](
            client=transport,
            store=CaptureStore(tmp_path),
            policy=CapturePolicy(allowed_hosts=frozenset({"www.arcgis.com"})),
        )
        with pytest.raises(CaptureError):
            client.capture(
                "GET", "https://www.arcgis.com/", source_id="source", endpoint_id="endpoint"
            )


def test_retained_budget_stops_retry(tmp_path: Path) -> None:
    with httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(503, content=b"busy"))
    ) as transport:
        client = SCRIPT["BoundedClient"](
            client=transport,
            store=CaptureStore(tmp_path),
            policy=CapturePolicy(allowed_hosts=frozenset({"www.arcgis.com"})),
            max_total_bytes=4,
        )
        with pytest.raises(CaptureError):
            client.capture(
                "GET", "https://www.arcgis.com/", source_id="source", endpoint_id="endpoint"
            )
        assert client.total_bytes == 4
        assert len(client.attempts) == 1


@pytest.mark.parametrize("broken", [False, True, "malformed-capabilities"])
def test_whole_capture_binds_catalogue_layer_and_failure_receipt(
    tmp_path: Path, broken: bool | str
) -> None:
    item = {
        "id": SCRIPT["ITEM_ID"],
        "url": SCRIPT["SERVICE"] + "/3",
        "accessInformation": "Tasman District Council (TDC)",
        "title": "Zones",
        "licenseInfo": "https://creativecommons.org/licenses/by/4.0/",
    }
    site = {
        "site": {
            "item": {"id": SCRIPT["SITE_ID"]},
            "data": {
                "catalogV2": {
                    "scopes": {
                        "item": {"filters": [{"predicates": [{"group": list(SCRIPT["GROUPS"])}]}]}
                    }
                }
            },
        }
    }

    def respond(request: httpx.Request) -> httpx.Response:
        if str(request.url) == SCRIPT["HUB"]:
            return httpx.Response(200, text='window.__SITE="' + quote(json.dumps(site)) + '"')
        if request.url.path.endswith("/search"):
            return httpx.Response(
                200, json={"start": 1, "nextStart": -1, "total": 1, "results": [item]}
            )
        if request.url.path.endswith("/data"):
            return httpx.Response(200, json={})
        if request.url.path.endswith("/3"):
            return httpx.Response(
                200,
                json={
                    "objectIdField": "OBJECTID",
                    "maxRecordCount": 100,
                    "advancedQueryCapabilities": None
                    if broken == "malformed-capabilities"
                    else {"supportsPagination": True},
                },
            )
        if request.url.path.endswith("/query"):
            if request.url.params.get("returnCountOnly"):
                return httpx.Response(200, json={"count": 1})
            if broken:
                return httpx.Response(200, json={"error": {"code": 400}})
            return httpx.Response(
                200, json={"features": [{"attributes": {"OBJECTID": 1}, "geometry": None}]}
            )
        return httpx.Response(200, text="official page")

    with httpx.Client(transport=httpx.MockTransport(respond)) as transport:
        client = SCRIPT["BoundedClient"](
            client=transport,
            store=CaptureStore(tmp_path),
            policy=CapturePolicy(allowed_hosts=SCRIPT["HOSTS"]),
        )
        receipt = SCRIPT["capture_tasman"](client)
    assert receipt["status"] == ("incomplete" if broken else "captured")
    assert receipt["catalogue_unique_items"] == 1
    assert list(tmp_path.glob("tasman-receipt-*.json"))
    if broken:
        assert receipt["failure"]["stage"] == "zones-layer"
    else:
        assert receipt["zones"]["feature_count"] == 1


def test_committed_live_receipt_and_registry_are_bound() -> None:
    root = Path(__file__).resolve().parents[1]
    receipt = json.loads((root / "docs/tasman-geohub-capture-20260830.json").read_text())
    registry = json.loads((root / "config/source-registry/tasman-geohub.json").read_text())
    assert receipt["source_id"] == registry["sources"][0]["source_id"] == SCRIPT["SOURCE_ID"]
    assert receipt["status"] == "captured"
    assert receipt["semantic_sha256"] == sha256_json(receipt, omit_keys={"semantic_sha256"})
    assert receipt["producer_sha256"] == sha256_bytes(
        (root / "scripts/capture_tasman_catalogue.py").read_bytes()
    )
    groups = receipt["groups"]
    assert tuple(group["group_id"] for group in groups) == SCRIPT["GROUPS"]
    ids = {item for group in groups for item in group["item_ids"]}
    assert len(ids) == receipt["catalogue_unique_items"] == 114
    assert all(len(set(group["item_ids"])) == group["count"] for group in groups)
    assert receipt["selected_item"]["id"] == SCRIPT["ITEM_ID"] in ids
    assert receipt["zones"]["feature_count"] == 3655
    attempts = receipt["attempts"]
    assert len(attempts) == 12
    assert all(item["http_status"] == 200 for item in attempts)
    assert sum(item["bytes"] for item in attempts) == receipt["total_bytes"] == 24_899_154
    assert receipt["selected_item"]["public_payload_status"] == "not-published"
    review = json.loads(
        (root / "docs/tasman-geohub-offline-verification-20260830.json").read_text()
    )
    assert review["receipt_sha256"] == sha256_bytes((root / review["receipt"]).read_bytes())
    assert review["receipt_semantic_sha256"] == receipt["semantic_sha256"]
    assert review["verified"]["unique_object_ids"] == receipt["zones"]["feature_count"]
    assert review["producer_reconciliation"]["successor_arcgis_module_sha256"] == sha256_bytes(
        (root / "src/riopa_provenance/arcgis.py").read_bytes()
    )
