from __future__ import annotations

import hashlib
import json
import runpy
from pathlib import Path

import httpx
import pytest

from riopa_provenance.capture import CapturePolicy, CaptureStore, HttpCaptureClient
from riopa_provenance.hashing import sha256_json

SCRIPT = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/capture_npdc_map_documents.py")
)
HTML = (
    '<a href="/media/nav/unrelated.pdf">nav</a><h1>Volume 3 - Maps</h1>'
    '<a href="/media/test/a10.pdf">A10</a><a href="/media/test/a10.pdf">repeat</a>'
    '<a href="/media/test/b10.pdf">B10</a>'
    '<div class="footer"><a href="/media/footer/privacy.pdf">privacy</a></div>'
)


def test_document_inventory_is_scoped_and_deduplicated() -> None:
    assert SCRIPT["enumerate_documents"](HTML) == [
        "https://www.npdc.govt.nz/media/test/a10.pdf",
        "https://www.npdc.govt.nz/media/test/b10.pdf",
    ]


@pytest.mark.parametrize(
    "href",
    [
        "https://foreign.test/a.pdf",
        "http://www.npdc.govt.nz/a.pdf",
        "/media/test/a.pdf?token=secret",
        "/media/test/%2e%2e/a.pdf",
    ],
)
def test_unexpected_pdf_link_fails_closed(href: str) -> None:
    with pytest.raises(ValueError, match="unexpected"):
        SCRIPT["enumerate_documents"](f'<h1>Volume 3 - Maps</h1><a href="{href}">A</a>')


def test_missing_inventory_is_not_reported_complete() -> None:
    with pytest.raises(ValueError, match="missing"):
        SCRIPT["enumerate_documents"]("<h1>Changed website</h1>")


@pytest.mark.parametrize("maximum,status", [(1, "deferred-budget"), (2, "captured")])
def test_capture_preserves_bytes_and_explicit_dispositions(
    tmp_path: Path, maximum: int, status: str
) -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        body = b"%PDF-1.7\noriginal bytes" if request.url.path.endswith(".pdf") else HTML.encode()
        return httpx.Response(200, content=body)

    store = CaptureStore(tmp_path)
    with httpx.Client(transport=httpx.MockTransport(respond)) as transport:
        client = HttpCaptureClient(
            client=transport,
            store=store,
            policy=CapturePolicy(allowed_hosts=frozenset({"www.npdc.govt.nz"})),
        )
        receipt = SCRIPT["capture_maps"](client, max_documents=maximum)
    assert receipt["discovered_count"] == 2
    assert receipt["captured_count"] == maximum
    assert receipt["documents"][1]["status"] == status
    for item in receipt["documents"][:maximum]:
        store.verify_capture_integrity(item["capture_id"])
        assert store.object_path(item["sha256"]).read_bytes() == b"%PDF-1.7\noriginal bytes"
    assert receipt["semantic_sha256"] == sha256_json(receipt, omit_keys={"semantic_sha256"})


def test_http_error_is_preserved_but_not_counted_as_pdf(tmp_path: Path) -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith(".pdf"):
            return httpx.Response(404, content=b"not found")
        return httpx.Response(200, content=HTML.encode())

    with httpx.Client(transport=httpx.MockTransport(respond)) as transport:
        client = HttpCaptureClient(
            client=transport,
            store=CaptureStore(tmp_path),
            policy=CapturePolicy(allowed_hosts=frozenset({"www.npdc.govt.nz"})),
        )
        receipt = SCRIPT["capture_maps"](client)
    assert receipt["captured_count"] == 0
    assert all(item["status"] == "invalid-response" for item in receipt["documents"])
    assert all(item["http_status"] == 404 for item in receipt["documents"])


@pytest.mark.parametrize("status", [200, 206])
def test_partial_document_is_never_counted_complete(tmp_path: Path, status: int) -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith(".pdf"):
            return httpx.Response(
                status, content=b"%PDF-1.7", headers={"Content-Range": "bytes 0-7/999"}
            )
        return httpx.Response(200, content=HTML.encode())

    with httpx.Client(transport=httpx.MockTransport(respond)) as transport:
        client = HttpCaptureClient(
            client=transport,
            store=CaptureStore(tmp_path),
            policy=CapturePolicy(allowed_hosts=frozenset({"www.npdc.govt.nz"})),
        )
        receipt = SCRIPT["capture_maps"](client)
    assert receipt["captured_count"] == 0


def test_partial_index_produces_failure_evidence(tmp_path: Path) -> None:
    with httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(206, content=HTML.encode()))
    ) as transport:
        client = HttpCaptureClient(
            client=transport,
            store=CaptureStore(tmp_path),
            policy=CapturePolicy(allowed_hosts=frozenset({"www.npdc.govt.nz"})),
        )
        with pytest.raises(ValueError, match="partial index"):
            SCRIPT["capture_maps"](client)
        assert client.on_failure is None
        assert client.policy.max_response_bytes == 512 * 1024 * 1024
    assert len(list((tmp_path / "failures").glob("*.json"))) == 1


def test_live_receipt_is_closed_and_bounded_metadata() -> None:
    root = Path(__file__).resolve().parents[1]
    receipt = json.loads((root / "docs/npdc-map-document-capture-20260830.json").read_text())
    registry = json.loads((root / "config/source-registry/npdc-map-documents.json").read_text())
    assert receipt["source_id"] == registry["sources"][0]["source_id"] == SCRIPT["SOURCE_ID"]
    assert receipt["index"]["url"] == SCRIPT["INDEX_URL"]
    assert receipt["semantic_sha256"] == sha256_json(receipt, omit_keys={"semantic_sha256"})
    documents = receipt["documents"]
    assert receipt["discovered_count"] == receipt["captured_count"] == len(documents) == 130
    assert len({item["url"] for item in documents}) == 130
    assert all(item["http_status"] == 200 and item["status"] == "captured" for item in documents)
    assert sum(item["bytes"] for item in documents) + receipt["index"]["bytes"] == 97_420_678
    assert receipt["total_bytes"] < receipt["bounds"]["max_total_bytes"]
    assert "raw PDFs retained locally" in receipt["publication"]
    reconciliation = json.loads(
        (root / "docs/npdc-map-producer-reconciliation-20260830.json").read_text()
    )
    assert (
        hashlib.sha256((root / reconciliation["historical_receipt"]).read_bytes()).hexdigest()
        == reconciliation["historical_receipt_sha256"]
    )
    assert reconciliation["historical_semantic_sha256"] == receipt["semantic_sha256"]
    assert all(field not in receipt for field in reconciliation["successor_fields"])


@pytest.mark.parametrize(
    "body",
    [
        b"\xff",
        b"<h1>Changed layout</h1>",
        b'<h1>Volume 3 - Maps</h1><a href="https://foreign.test/a.pdf">A</a>',
    ],
)
def test_index_parse_errors_persist_failure_evidence(tmp_path: Path, body: bytes) -> None:
    with httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, content=body))
    ) as transport:
        client = HttpCaptureClient(
            client=transport,
            store=CaptureStore(tmp_path),
            policy=CapturePolicy(allowed_hosts=frozenset({"www.npdc.govt.nz"})),
        )
        with pytest.raises(ValueError, match="index enumeration failed"):
            SCRIPT["capture_maps"](client)
        assert client.on_failure is None
    records = [json.loads(path.read_text()) for path in (tmp_path / "failures").glob("*.json")]
    assert records[0]["context"]["stage"] == "index-enumeration"
    assert records[0]["context"]["capture_id"]


@pytest.mark.parametrize("failure", ["http", "transport"])
def test_transient_failures_retry_and_account_for_all_retained_bytes(
    tmp_path: Path, failure: str
) -> None:
    count = 0
    delays = []

    def respond(request: httpx.Request) -> httpx.Response:
        nonlocal count
        if not request.url.path.endswith(".pdf"):
            return httpx.Response(200, content=HTML.encode())
        count += 1
        if count == 1:
            if failure == "transport":
                raise httpx.ConnectError("transient", request=request)
            return httpx.Response(429, content=b"busy", headers={"Retry-After": "2"})
        return httpx.Response(200, content=b"%PDF-1.7")

    with httpx.Client(transport=httpx.MockTransport(respond)) as transport:
        client = HttpCaptureClient(
            client=transport,
            store=CaptureStore(tmp_path),
            sleep=delays.append,
            policy=CapturePolicy(allowed_hosts=frozenset({"www.npdc.govt.nz"})),
        )
        receipt = SCRIPT["capture_maps"](client)
    assert receipt["captured_count"] == 2
    assert count == 3
    assert delays == ([2.0] if failure == "http" else [1.0])
    assert receipt["total_bytes"] == sum(item.get("bytes", 0) for item in receipt["attempts"])
    for item in receipt["attempts"]:
        if "capture_id" in item:
            client.store.verify_capture_integrity(item["capture_id"])


def test_oversize_document_records_failure_without_exceeding_retained_budget(
    tmp_path: Path,
) -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        body = b"%PDF-1.7\n" if request.url.path.endswith(".pdf") else HTML.encode()
        return httpx.Response(200, content=body)

    policy = CapturePolicy(allowed_hosts=frozenset({"www.npdc.govt.nz"}))
    with httpx.Client(transport=httpx.MockTransport(respond)) as transport:
        client = HttpCaptureClient(client=transport, store=CaptureStore(tmp_path), policy=policy)
        receipt = SCRIPT["capture_maps"](client, max_total_bytes=len(HTML.encode()) + 1)
        assert client.policy is policy
        assert client.on_failure is None
    assert receipt["captured_count"] == 0
    assert receipt["total_bytes"] == len(HTML.encode())
    assert all(item["status"] == "capture-failed" for item in receipt["documents"])
    assert receipt["documents"][0]["failures"][0]["category"] == "response-size"
    assert list((tmp_path / "failures").glob("*.json"))


@pytest.mark.parametrize("budget,expected_attempts", [(10000, 6), (len(HTML.encode()) + 4, 1)])
def test_retry_attempts_and_retained_budget_remain_bounded(
    tmp_path: Path, budget: int, expected_attempts: int
) -> None:
    count = 0

    def respond(request: httpx.Request) -> httpx.Response:
        nonlocal count
        if not request.url.path.endswith(".pdf"):
            return httpx.Response(200, content=HTML.encode())
        count += 1
        return httpx.Response(503, content=b"busy")

    with httpx.Client(transport=httpx.MockTransport(respond)) as transport:
        client = HttpCaptureClient(
            client=transport,
            store=CaptureStore(tmp_path),
            policy=CapturePolicy(allowed_hosts=frozenset({"www.npdc.govt.nz"})),
        )
        receipt = SCRIPT["capture_maps"](client, max_total_bytes=budget)
    assert count == expected_attempts
    assert receipt["captured_count"] == 0
    assert receipt["total_bytes"] <= budget
    assert receipt["total_bytes"] == len(HTML.encode()) + count * 4
