from __future__ import annotations

import json
import runpy
from pathlib import Path

import httpx
import pytest

from riopa_provenance import tasman_public_packet as builder
from riopa_provenance.capture import CapturePolicy, CaptureStore, HttpCaptureClient
from riopa_provenance.hashing import sha256_bytes, sha256_file, sha256_json
from riopa_provenance.public_archive_spatial import (
    PublicArchiveDescriptor,
    PublicArchivePacketError,
    verify_public_archive_packet,
)


@pytest.fixture
def inputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path, str]:
    licence = "This data is distributed under https://creativecommons.org/licenses/by/4.0/"
    monkeypatch.setattr(builder, "LICENCE_SHA256", sha256_bytes(licence.encode()))
    payloads = [
        {
            "fields": [
                {"name": "OBJECTID", "type": "esriFieldTypeOID"},
                {"name": "Shape", "type": "esriFieldTypeGeometry"},
            ]
        },
        {"count": 1},
        {"count": 1},
        {"features": [{"attributes": {"OBJECTID": 1}, "geometry": None}]},
        {
            "id": builder.ITEM,
            "url": builder.SERVICE + "/3",
            "licenseInfo": licence,
            "accessInformation": builder.ATTRIBUTION,
        },
    ]
    store = CaptureStore(tmp_path / "store")
    captures = []
    with httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json=payloads.pop(0)))
    ) as http:
        client = HttpCaptureClient(
            client=http,
            store=store,
            policy=CapturePolicy(
                allowed_hosts=frozenset({"www.arcgis.com", "gispublic.tasman.govt.nz"})
            ),
        )
        for role in ("metadata", "count-before", "count-after", "page", "licence"):
            params = {"f": "pjson" if role == "metadata" else "json"}
            if role.startswith("count"):
                params.update(where="1=1", returnCountOnly="true")
            elif role == "page":
                params.update(
                    where="1=1",
                    outFields="*",
                    returnGeometry="true",
                    returnExceededLimitFeatures="true",
                    orderByFields="OBJECTID ASC",
                    resultOffset="0",
                    resultRecordCount="1000",
                )
            captures.append(
                client.capture(
                    "GET",
                    builder.RIGHTS_URL
                    if role == "licence"
                    else builder.SERVICE + "/3" + ("" if role == "metadata" else "/query"),
                    source_id=builder.SOURCE,
                    endpoint_id=f"{builder.SOURCE}:{role}",
                    params=params,
                )
            )
    capture_set = {
        "record_type": "arcgis_layer_capture_set",
        "schema_version": "1.1.0",
        "source_id": builder.SOURCE,
        "service_url": builder.SERVICE,
        "layer_id": 3,
        "capture_set_id": "urn:uuid:00000000-0000-4000-8000-000000000001",
        "metadata_capture_id": captures[0].capture_id,
        "count_capture_ids": [c.capture_id for c in captures[1:3]],
        "page_capture_ids": [captures[3].capture_id],
        "feature_count": 1,
        "query": {"where": "1=1", "out_fields": "*"},
        "object_id_field": "OBJECTID",
        "page_size": 1000,
        "pagination_strategy": "offset",
    }
    capture_set["manifest_sha256"] = sha256_json(capture_set)
    path = store.root / "capture-set.json"
    path.write_text(json.dumps(capture_set))
    return store.root, path, captures[-1].capture_id


def descriptor(output: Path, manifest: dict) -> PublicArchiveDescriptor:
    return PublicArchiveDescriptor(
        dataset_repository="owner/test",
        packet_revision="a" * 40,
        packet_path="snapshots/test",
        manifest_sha256=sha256_file(output / "manifest.json"),
        source_id=builder.SOURCE,
        licence="CC-BY-4.0",
        attribution=builder.ATTRIBUTION,
        rights_capture_id=manifest["rights_capture_id"],
        rights_object_sha256=manifest["rights_object_sha256"],
        rights_licence_text=builder.LICENCE_TEXT,
    )


def test_packet_preserves_originals_and_verifies(
    inputs: tuple[Path, Path, str], tmp_path: Path
) -> None:
    store, capture_set, rights = inputs
    (store / "unrelated-catalogue.json").write_text('{"mixed":true}')
    output = tmp_path / "packet"
    manifest = builder.build_tasman_public_packet(store, capture_set, rights, output)
    verify_public_archive_packet(output, descriptor=descriptor(output, manifest))
    assert (output / "capture-set.json").read_bytes() == capture_set.read_bytes()
    assert not (output / "unrelated-catalogue.json").exists()
    assert manifest["publication_performed"] is False
    second = tmp_path / "second"
    assert builder.build_tasman_public_packet(store, capture_set, rights, second) == manifest
    assert (output / "checksums.sha256").read_bytes() == (second / "checksums.sha256").read_bytes()
    (output / "extra.json").write_text("{}")
    with pytest.raises(PublicArchivePacketError):
        verify_public_archive_packet(output, descriptor=descriptor(output, manifest))


@pytest.mark.parametrize(
    "bad",
    [
        "uuid",
        "symlink",
        "digest",
        "partial",
        "rights",
        "nested",
        "existing",
        "duplicate",
        "traversal",
        "count",
        "endpoint",
    ],
)
def test_rejects_invalid_inputs(inputs: tuple[Path, Path, str], tmp_path: Path, bad: str) -> None:
    store, capture_set, rights = inputs
    output = tmp_path / "packet"
    record_path = store / "captures" / f"{rights.removeprefix('urn:uuid:')}.json"
    record = json.loads(record_path.read_bytes())
    if bad == "uuid":
        rights = "urn:uuid:../../escape"
    elif bad == "symlink":
        link = tmp_path / "link"
        link.symlink_to(store, target_is_directory=True)
        store = link
    elif bad == "digest":
        record["object"]["sha256"] = "../escape"
    elif bad == "partial":
        record["response"]["headers"]["Content-Range"] = "bytes 0-1/20"
    elif bad == "rights":
        record["request"]["url"] = "https://www.arcgis.com/sharing/rest/search"
    elif bad == "nested":
        output = store / "nested"
    elif bad == "existing":
        output.mkdir()
    elif bad == "traversal":
        outside = tmp_path / "outside.json"
        outside.write_bytes(capture_set.read_bytes())
        capture_set = store / ".." / "outside.json"
    elif bad == "endpoint":
        value = json.loads(capture_set.read_bytes())
        endpoint_path = (
            store / "captures" / f"{value['metadata_capture_id'].removeprefix('urn:uuid:')}.json"
        )
        endpoint = json.loads(endpoint_path.read_bytes())
        endpoint["request"]["url"] = builder.SERVICE + "/4"
        endpoint_path.write_text(json.dumps(endpoint))
    else:
        value = json.loads(capture_set.read_bytes())
        if bad == "count":
            value["feature_count"] = 2
        else:
            value["page_capture_ids"] *= 2
        value["manifest_sha256"] = sha256_json(value, omit_keys={"manifest_sha256"})
        capture_set.write_text(json.dumps(value))
    record_path.write_text(json.dumps(record))
    with pytest.raises(ValueError):
        builder.build_tasman_public_packet(store, capture_set, rights, output)


def test_changed_rights_text_fails_with_resealed_object(
    inputs: tuple[Path, Path, str], tmp_path: Path
) -> None:
    store, capture_set, rights = inputs
    path = store / "captures" / f"{rights.removeprefix('urn:uuid:')}.json"
    record = json.loads(path.read_bytes())
    payload = json.loads((store / record["object"]["storage_path"]).read_bytes())
    payload["licenseInfo"] = "Not licensed. " + payload["licenseInfo"]
    body = json.dumps(payload).encode()
    digest = sha256_bytes(body)
    storage = f"objects/sha256/{digest[:2]}/{digest}"
    obj = store / storage
    obj.parent.mkdir(parents=True, exist_ok=True)
    obj.write_bytes(body)
    record["object"].update(sha256=digest, size_bytes=len(body), storage_path=storage)
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="rights binding"):
        builder.build_tasman_public_packet(store, capture_set, rights, tmp_path / "output")


def test_packet_budget_fails_before_output(
    inputs: tuple[Path, Path, str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(builder, "MAX_BYTES", 10)
    with pytest.raises(ValueError):
        builder.build_tasman_public_packet(*inputs, tmp_path / "output")
    assert not (tmp_path / "output").exists()


@pytest.mark.parametrize("tamper", [None, "source", "count", "rights_digest"])
def test_preparation_cli_binds_receipt_summary(
    inputs: tuple[Path, Path, str], tamper: str | None
) -> None:
    store, capture_set, rights = inputs
    receipt = {
        "source_id": "urn:riopa:source:wrong" if tamper == "source" else builder.SOURCE,
        "status": "captured",
        "zones": {
            "manifest_path": capture_set.name,
            "manifest_sha256": sha256_file(capture_set),
            "feature_count": 99 if tamper == "count" else 1,
        },
        "selected_item": {
            "rights_capture_id": rights,
            "rights_object_sha256": "0" * 64
            if tamper == "rights_digest"
            else json.loads(
                (store / "captures" / f"{rights.removeprefix('urn:uuid:')}.json").read_bytes()
            )["object"]["sha256"],
        },
    }
    digest = sha256_json(receipt)
    receipt["semantic_sha256"] = digest
    (store / f"tasman-receipt-{digest}.json").write_text(json.dumps(receipt))
    prepare = runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "scripts/prepare_tasman_public_packet.py")
    )["prepare"]
    public_summary = store.parent / "public/tasman-packet-preparation.json"
    if tamper:
        with pytest.raises(ValueError, match="summary differs"):
            prepare(store.parent)
        assert not public_summary.exists()
    else:
        report = prepare(store.parent)
        assert report["status"] == "prepared-not-published"
        assert report["feature_count"] == 1
        assert json.loads(public_summary.read_bytes()) == report


@pytest.mark.parametrize(
    "parameter,value",
    [
        ("outFields", "OBJECTID"),
        ("where", "OBJECTID=1"),
        ("resultOffset", "10"),
        ("returnGeometry", "false"),
        ("orderByFields", "OBJECTID DESC"),
        ("duplicate", "1"),
    ],
)
def test_rejects_partial_or_ambiguous_page_queries(
    inputs: tuple[Path, Path, str], tmp_path: Path, parameter: str, value: str
) -> None:
    from urllib.parse import parse_qsl, urlencode, urlsplit

    store, capture_set, rights = inputs
    cid = json.loads(capture_set.read_bytes())["page_capture_ids"][0]
    path = store / "captures" / f"{cid.removeprefix('urn:uuid:')}.json"
    record = json.loads(path.read_bytes())
    url = urlsplit(record["request"]["url"])
    params = dict(parse_qsl(url.query))
    if parameter == "duplicate":
        query = url.query + "&where=1%3D1"
    else:
        params[parameter] = value
        query = urlencode(params)
    record["request"]["url"] = url._replace(query=query).geturl()
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError):
        builder.build_tasman_public_packet(store, capture_set, rights, tmp_path / "output")


def replace_payload(store: Path, cid: str, payload: dict) -> None:
    path = store / "captures" / f"{cid.removeprefix('urn:uuid:')}.json"
    record = json.loads(path.read_bytes())
    body = json.dumps(payload).encode()
    digest = sha256_bytes(body)
    storage = f"objects/sha256/{digest[:2]}/{digest}"
    obj = store / storage
    obj.parent.mkdir(parents=True, exist_ok=True)
    obj.write_bytes(body)
    record["object"].update(sha256=digest, size_bytes=len(body), storage_path=storage)
    path.write_text(json.dumps(record))


@pytest.mark.parametrize(
    "field,value",
    [
        ("fields", None),
        ("fields", []),
        ("objectIdField", "BAD"),
        ("maxRecordCount", "bad"),
        ("maxRecordCount", 2),
        ("advancedQueryCapabilities", {"supportsPagination": False}),
    ],
)
def test_invalid_metadata_contract(
    inputs: tuple[Path, Path, str], tmp_path: Path, field: str, value: object
) -> None:
    store, path, rights = inputs
    cid = json.loads(path.read_bytes())["metadata_capture_id"]
    payload = {"fields": [{"name": "OBJECTID", "type": "esriFieldTypeOID"}], field: value}
    replace_payload(store, cid, payload)
    with pytest.raises(ValueError):
        builder.build_tasman_public_packet(store, path, rights, tmp_path / "output")


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_id", "wrong"),
        ("count_capture_ids", []),
        ("page_capture_ids", []),
        ("feature_count", -1),
        ("query", {}),
        ("object_ids_capture_id", "urn:uuid:00000000-0000-4000-8000-000000000088"),
    ],
)
def test_invalid_capture_set_contract(
    inputs: tuple[Path, Path, str], tmp_path: Path, field: str, value: object
) -> None:
    store, path, rights = inputs
    capture_set = json.loads(path.read_bytes())
    capture_set[field] = value
    capture_set["manifest_sha256"] = sha256_json(capture_set, omit_keys={"manifest_sha256"})
    path.write_text(json.dumps(capture_set))
    with pytest.raises(ValueError):
        builder.build_tasman_public_packet(store, path, rights, tmp_path / "output")


@pytest.mark.parametrize(
    "rows",
    [
        None,
        [],
        [{"attributes": {"OBJECTID": 1}}],
        [{"attributes": {"OBJECTID": True}, "geometry": None}],
        [
            {"attributes": {"OBJECTID": 2}, "geometry": None},
            {"attributes": {"OBJECTID": 1}, "geometry": None},
        ],
    ],
)
def test_invalid_feature_page(inputs: tuple[Path, Path, str], tmp_path: Path, rows: object) -> None:
    store, path, rights = inputs
    cid = json.loads(path.read_bytes())["page_capture_ids"][0]
    replace_payload(store, cid, {"features": rows})
    with pytest.raises(ValueError):
        builder.build_tasman_public_packet(store, path, rights, tmp_path / "output")


@pytest.mark.parametrize("count", [0, 2])
@pytest.mark.parametrize("tamper", [None, "badids", "duplicateids", "wrongchunk"])
def test_actual_archiver_object_id_strategy(
    inputs: tuple[Path, Path, str], tmp_path: Path, count: int, tamper: str | None
) -> None:
    from riopa_provenance.arcgis import ArcGISFeatureLayerArchiver

    store, _, rights = inputs

    def respond(request: httpx.Request) -> httpx.Response:
        params = request.url.params
        if request.url.path.endswith("/3"):
            return httpx.Response(
                200,
                json={
                    "fields": [
                        {"name": "OBJECTID", "type": "esriFieldTypeOID"},
                        {"name": "Shape", "type": "esriFieldTypeGeometry"},
                    ],
                    "maxRecordCount": 1,
                    "advancedQueryCapabilities": {"supportsPagination": False},
                },
            )
        if params.get("returnCountOnly"):
            return httpx.Response(200, json={"count": count})
        if params.get("returnIdsOnly"):
            return httpx.Response(200, json={"objectIds": list(range(1, count + 1))})
        ids = [int(params["objectIds"])] if params.get("objectIds") else []
        return httpx.Response(
            200, json={"features": [{"attributes": {"OBJECTID": i}, "geometry": None} for i in ids]}
        )

    with httpx.Client(transport=httpx.MockTransport(respond)) as http:
        archive = ArcGISFeatureLayerArchiver(
            HttpCaptureClient(
                client=http,
                store=CaptureStore(store),
                policy=CapturePolicy(allowed_hosts=frozenset({"gispublic.tasman.govt.nz"})),
            )
        ).archive_layer(
            source_id=builder.SOURCE,
            endpoint_id=builder.SOURCE + ":zones",
            service_url=builder.SERVICE,
            layer_id=3,
        )
    output = tmp_path / "output"
    capture_set = json.loads(archive.manifest_path.read_bytes())
    if tamper:
        if tamper == "wrongchunk":
            cid = capture_set["page_capture_ids"][0]
            replace_payload(
                store, cid, {"features": [{"attributes": {"OBJECTID": 99}, "geometry": None}]}
            )
        else:
            cid = capture_set["object_ids_capture_id"]
            replace_payload(store, cid, {"objectIds": [True] if tamper == "badids" else [1, 1]})
        with pytest.raises(ValueError):
            builder.build_tasman_public_packet(store, archive.manifest_path, rights, output)
        return
    manifest = builder.build_tasman_public_packet(store, archive.manifest_path, rights, output)
    verify_public_archive_packet(output, descriptor=descriptor(output, manifest))


@pytest.mark.parametrize(
    "tamper", ["storage", "size", "jsonerror", "filebudget", "bytebudget", "ancestorlink"]
)
def test_extra_integrity_and_budget_guards(
    inputs: tuple[Path, Path, str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tamper: str
) -> None:
    store, capture_set, rights = inputs
    cid = json.loads(capture_set.read_bytes())["metadata_capture_id"]
    path = store / "captures" / f"{cid.removeprefix('urn:uuid:')}.json"
    record = json.loads(path.read_bytes())
    output = tmp_path / "output"
    if tamper == "storage":
        record["object"]["storage_path"] = "../outside"
    elif tamper == "size":
        record["object"]["size_bytes"] += 1
    elif tamper == "jsonerror":
        replace_payload(store, cid, {"error": {"code": 403}})
    elif tamper == "filebudget":
        monkeypatch.setattr(builder, "MAX_FILES", 2)
    elif tamper == "bytebudget":
        # Every individual input fits, but combined packet exceeds this budget.
        sizes = [p.stat().st_size for p in store.rglob("*") if p.is_file()]
        monkeypatch.setattr(builder, "MAX_BYTES", max(sizes) + 1)
    else:
        link = tmp_path / "alias"
        link.symlink_to(store, target_is_directory=True)
        output = link / "new-packet"
    if tamper in ("storage", "size"):
        path.write_text(json.dumps(record))
    with pytest.raises(ValueError):
        builder.build_tasman_public_packet(store, capture_set, rights, output)
