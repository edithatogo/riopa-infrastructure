from __future__ import annotations

import json
import runpy
from pathlib import Path

import httpx
import pytest

from riopa_provenance.capture import CapturePolicy, CaptureStore, HttpCaptureClient
from riopa_provenance.hashing import sha256_json

SCRIPT = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/qualify_qldc_eplan.py"))


@pytest.mark.parametrize(
    "scenario",
    ["ok", "403", "partial", "206", "bad-pdf", "missing-link", "transport", "redirect", "not-html"],
)
def test_bounded_snapshot_preserves_denials_and_never_promotes_shells(
    tmp_path: Path, scenario: str
) -> None:
    calls: list[str] = []

    def respond(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        calls.append(url)
        if url == SCRIPT["AUTHORITY"]:
            links = "".join(f'<a href="{u}">link</a>' for u in SCRIPT["ROUTES"].values())
            if scenario == "missing-link":
                links = '<a href="https://unapproved.example/data">unexpected</a>'
            return httpx.Response(200, text=links, headers={"Content-Type": "text/html"})
        if url.endswith(".pdf"):
            return httpx.Response(200, content=b"html" if scenario == "bad-pdf" else b"%PDF-1.7")
        if scenario == "transport":
            raise httpx.ConnectError("unreachable")
        if scenario == "redirect":
            return httpx.Response(302, headers={"Location": "https://unapproved.example/"})
        headers = {"Content-Type": "application/json" if scenario == "not-html" else "text/html"}
        if scenario == "partial":
            headers["Content-Range"] = "bytes 0-10/999"
        return httpx.Response(
            403 if scenario == "403" else 206 if scenario == "206" else 200,
            text="<html>application shell</html>",
            headers=headers,
        )

    store = CaptureStore(tmp_path)
    with httpx.Client(transport=httpx.MockTransport(respond)) as http:
        client = HttpCaptureClient(
            client=http,
            store=store,
            policy=CapturePolicy(
                allowed_hosts=frozenset({"www.qldc.govt.nz", "districtplan.qldc.govt.nz"}),
                max_response_bytes=8000,
            ),
        )
        receipt = SCRIPT["qualify"](client)
    assert len(calls) <= 4 and len(calls) == len(set(calls))
    assert all("unapproved" not in url for url in calls)
    assert receipt["status"] == ("routes-observed" if scenario == "ok" else "blocked-or-incomplete")
    assert len(receipt["non_claims"]) == 5
    for row in receipt["routes"]:
        if "capture_id" in row:
            store.verify_capture_integrity(row["capture_id"])
    assert receipt["total_retained_bytes"] == sum(r.get("bytes", 0) for r in receipt["routes"])
    digest = receipt.pop("semantic_sha256")
    assert sha256_json(receipt) == digest
    persisted = json.loads((tmp_path / f"qldc-routes-{digest}.json").read_text())
    assert persisted["semantic_sha256"] == digest
    if scenario == "403":
        assert [r["status"] for r in receipt["routes"]] == [
            "captured-authority",
            "http-denied",
            "http-denied",
            "captured-guide",
        ]


def test_bad_authority_prevents_all_downstream_requests(tmp_path: Path) -> None:
    with httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(403))) as http:
        receipt = SCRIPT["qualify"](
            HttpCaptureClient(
                client=http,
                store=CaptureStore(tmp_path),
                policy=CapturePolicy(allowed_hosts=frozenset({"www.qldc.govt.nz"})),
            )
        )
    assert receipt["routes"][0]["status"] == "http-denied"
    assert all(r["status"] == "not-linked-by-authority" for r in receipt["routes"][1:])
