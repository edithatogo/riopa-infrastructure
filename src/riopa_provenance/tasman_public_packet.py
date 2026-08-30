"""Build a rights-bound Tasman layer packet without publishing or changing originals."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

from .hashing import sha256_bytes, sha256_json

SOURCE = "urn:riopa:source:tasman:geohub"
SERVICE = "https://gispublic.tasman.govt.nz/server/rest/services/OpenData/OpenData_Planning_TRMPLand_Zones/MapServer"
ITEM = "99868f57e0df486991a4785a1d3303d3"
RIGHTS_URL = f"https://www.arcgis.com/sharing/rest/content/items/{ITEM}"
ATTRIBUTION = "Tasman District Council (TDC)"
LICENCE_SHA256 = "8ef78b71e297f41a29d95c087d158594e6e980557064cd8a6c562b409c4d791c"
LICENCE_TEXT = "This data is distributed under"
MAX_BYTES = 512_000_000
MAX_FILES = 10000
_UUID = re.compile(r"urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
_SHA = re.compile(r"[0-9a-f]{64}")


def _read(root: Path, path: Path) -> bytes:
    if (
        ".." in path.parts
        or not path.resolve().is_relative_to(root)
        or any(p.is_symlink() for p in (path, *path.parents) if p.is_relative_to(root))
    ):
        raise ValueError("unsafe or symlinked input path")
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("missing or oversized input")
    return path.read_bytes()


def build_tasman_public_packet(
    store: Path, capture_set_path: Path, rights_capture_id: str, output: Path
) -> dict[str, Any]:
    """Prepare exactly the selected layer and reviewed standalone item metadata.

    The output carries no public repository revision or publication receipt.
    Existing mixed-source objects in the input store are deliberately not copied.
    """
    if store.is_symlink() or output.is_symlink() or capture_set_path.is_symlink():
        raise ValueError("symlinked root")
    root = store.absolute()
    target = output.absolute()
    if root.resolve() != root or target.resolve() != target:
        raise ValueError("root contains a symlink or traversal")
    if target.exists() or target.is_relative_to(root) or root.is_relative_to(target):
        raise ValueError("output must be fresh and disjoint")
    raw_set = _read(root, capture_set_path.absolute())
    capture_set = json.loads(raw_set)
    if (
        capture_set.get("record_type") != "arcgis_layer_capture_set"
        or capture_set.get("source_id") != SOURCE
        or capture_set.get("service_url") != SERVICE
        or not isinstance(capture_set.get("capture_set_id"), str)
        or not _UUID.fullmatch(capture_set["capture_set_id"])
        or type(capture_set.get("layer_id")) is not int
        or capture_set["layer_id"] != 3
        or capture_set.get("manifest_sha256")
        != sha256_json(capture_set, omit_keys={"manifest_sha256"})
    ):
        raise ValueError("capture set identity or integrity mismatch")
    counts, pages = capture_set.get("count_capture_ids"), capture_set.get("page_capture_ids")
    if not isinstance(counts, list) or len(counts) != 2 or not isinstance(pages, list) or not pages:
        raise ValueError("missing count/page closure")
    roles = [(capture_set.get("metadata_capture_id"), "metadata")]
    roles.extend((cid, "count") for cid in counts)
    if capture_set.get("object_ids_capture_id"):
        roles.append((capture_set["object_ids_capture_id"], "ids"))
    roles.extend((cid, "page") for cid in pages)
    roles.append((rights_capture_id, "rights"))
    if len(roles) > (MAX_FILES - 1) // 2:
        raise ValueError("capture budget exceeded")
    blobs = {"capture-set.json": raw_set}
    seen: set[str] = set()
    feature_ids: list[int] = []
    expected_count = capture_set.get("feature_count")
    if type(expected_count) is not int or expected_count < 0:
        raise ValueError("invalid feature count")
    rights_digest = ""
    observed: list[str] = []
    oid_field: str | None = None
    page_size = 0
    object_ids: list[int] | None = None
    field_names: set[str] = set()
    if capture_set.get("query") != {"where": "1=1", "out_fields": "*"}:
        raise ValueError("capture set must declare an unrestricted full-field query")
    for cid, role in roles:
        if not isinstance(cid, str) or not _UUID.fullmatch(cid) or cid in seen:
            raise ValueError("unsafe or duplicate capture identity")
        seen.add(cid)
        relative = f"captures/{cid.removeprefix('urn:uuid:')}.json"
        raw = _read(root, root / relative)
        record = json.loads(raw)
        obj = record["object"]
        digest = obj["sha256"]
        if not isinstance(digest, str) or not _SHA.fullmatch(digest):
            raise ValueError("unsafe object digest")
        storage = f"objects/sha256/{digest[:2]}/{digest}"
        if obj.get("storage_path") != storage:
            raise ValueError("object storage binding mismatch")
        body = _read(root, root / storage)
        if sha256_bytes(body) != digest or len(body) != obj["size_bytes"]:
            raise ValueError("object digest/size mismatch")
        if (
            record.get("capture_id") != cid
            or record.get("record_type") != "http_capture"
            or record.get("source_id") != SOURCE
            or record["response"]["status_code"] != 200
            or any(k.lower() == "content-range" for k in record["response"]["headers"])
        ):
            raise ValueError("capture identity or complete-response mismatch")
        payload = json.loads(body)
        if not isinstance(payload, dict) or "error" in payload:
            raise ValueError("malformed captured JSON")
        parsed_url = urlsplit(record["request"]["url"])
        request_url = parsed_url._replace(query="", fragment="").geturl()
        pairs = parse_qsl(parsed_url.query, keep_blank_values=True, strict_parsing=True)
        params = dict(pairs)
        if (
            len(params) != len(pairs)
            or parsed_url.fragment
            or record["request"].get("method") != "GET"
        ):
            raise ValueError("ambiguous request query or method")
        expected_url = RIGHTS_URL if role == "rights" else f"{SERVICE}/3"
        if role in ("count", "page", "ids"):
            expected_url += "/query"
        if request_url != expected_url:
            raise ValueError("capture request is not bound to selected layer/item")
        expected_params = {"f": "pjson" if role == "metadata" else "json"}
        if role in ("count", "ids", "page"):
            expected_params["where"] = "1=1"
        if role == "metadata":
            fields = payload.get("fields", [])
            if (
                not isinstance(fields, list)
                or not fields
                or any(
                    not isinstance(field, dict) or not isinstance(field.get("name"), str)
                    for field in fields
                )
            ):
                raise ValueError("invalid layer fields")
            field_names = {
                field["name"] for field in fields if field.get("type") != "esriFieldTypeGeometry"
            }
            candidates = [
                field.get("name") for field in fields if field.get("type") == "esriFieldTypeOID"
            ]
            oid_field = (
                payload.get("objectIdField")
                or payload.get("objectIdFieldName")
                or (candidates[0] if len(candidates) == 1 else None)
            )
            if oid_field != "OBJECTID" or capture_set.get("object_id_field") != oid_field:
                raise ValueError("unbound object ID field")
            maximum = payload.get("maxRecordCount") or 1000
            if type(maximum) is not int:
                raise ValueError("invalid server page size")
            page_size = min(max(maximum, 1), 10000)
            if capture_set.get("page_size") != page_size:
                raise ValueError("capture page size does not match metadata")
            pagination = payload.get("advancedQueryCapabilities", {}).get(
                "supportsPagination", True
            )
            strategy = "offset" if pagination else "object_ids"
            if capture_set.get("pagination_strategy") != strategy:
                raise ValueError("pagination strategy does not match metadata")
            if bool(capture_set.get("object_ids_capture_id")) != (strategy == "object_ids"):
                raise ValueError("unexpected object-ID inventory")
        elif role == "count":
            expected_params["returnCountOnly"] = "true"
        elif role == "ids":
            expected_params["returnIdsOnly"] = "true"
            raw_ids = payload.get("objectIds")
            if not isinstance(raw_ids, list) or any(type(v) is not int for v in raw_ids):
                raise ValueError("invalid object ID inventory")
            object_ids = sorted(raw_ids)
            if len(set(object_ids)) != expected_count or len(object_ids) != expected_count:
                raise ValueError("object ID inventory count mismatch")
        elif role == "page":
            expected_params.update(
                outFields="*",
                returnGeometry="true",
                returnExceededLimitFeatures="true",
                orderByFields=f"{oid_field} ASC",
            )
            if capture_set["pagination_strategy"] == "offset":
                expected_params.update(
                    resultOffset=str(len(feature_ids)), resultRecordCount=str(page_size)
                )
            else:
                if object_ids is None:
                    raise ValueError("missing object ID inventory")
                chunk = object_ids[len(feature_ids) : len(feature_ids) + page_size]
                if chunk:
                    expected_params["objectIds"] = ",".join(map(str, chunk))
                else:
                    expected_params["where"] = "1=0"
                    expected_params.pop("orderByFields")
            rows = payload.get("features")
            if not isinstance(rows, list) or len(rows) > page_size:
                raise ValueError("invalid feature page")
            if any(
                not isinstance(row, dict)
                or "geometry" not in row
                or not isinstance(row.get("attributes"), dict)
                or set(row["attributes"]) != field_names
                for row in rows
            ):
                raise ValueError("page omits declared fields or geometry")
            ids = [row["attributes"]["OBJECTID"] for row in rows]
            if ids != sorted(ids) or (feature_ids and ids and ids[0] <= feature_ids[-1]):
                raise ValueError("page object IDs are not strictly ordered")
            if (
                object_ids is not None
                and ids != object_ids[len(feature_ids) : len(feature_ids) + page_size]
            ):
                raise ValueError("object ID chunk mismatch")
        if params != expected_params:
            raise ValueError("request does not match full-layer query contract")
        if role == "rights":
            licence = payload.get("licenseInfo")
            if (
                request_url != RIGHTS_URL
                or payload.get("id") != ITEM
                or payload.get("url") != f"{SERVICE}/3"
                or payload.get("accessInformation") != ATTRIBUTION
                or not isinstance(licence, str)
                or sha256_bytes(licence.encode()) != LICENCE_SHA256
                or LICENCE_TEXT not in licence
                or "https://creativecommons.org/licenses/by/4.0/" not in licence
                or not any(s in record.get("endpoint_id", "") for s in ("licence", "license"))
            ):
                raise ValueError("standalone rights binding mismatch")
            rights_digest = digest
        elif role == "count" and (
            type(payload.get("count")) is not int or payload["count"] != expected_count
        ):
            raise ValueError("count mismatch")
        elif role == "page":
            for feature in payload.get("features", []):
                identity = feature["attributes"]["OBJECTID"]
                if type(identity) is not int:
                    raise ValueError("invalid feature identity")
                feature_ids.append(identity)
        observed.append(record["retrieved_at"])
        blobs[relative] = raw
        blobs[f"objects/sha256/{digest}"] = body
        if sum(map(len, blobs.values())) > MAX_BYTES:
            raise ValueError("packet byte budget exceeded")
    if len(feature_ids) != expected_count or len(set(feature_ids)) != expected_count:
        raise ValueError("feature identity/count reconciliation failed")
    manifest: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "riopa_public_source_archive_packet",
        "source_id": SOURCE,
        "capture_set_id": capture_set["capture_set_id"],
        "captured_at": max(observed),
        "publication_status": "public-rights-qualified",
        "publication_performed": False,
        "licence": "CC-BY-4.0",
        "attribution": ATTRIBUTION,
        "rights_capture_id": rights_capture_id,
        "rights_object_sha256": rights_digest,
        "rights_licence_text": LICENCE_TEXT,
        "non_claims": [
            "Prepared packet, not a public publication or preservation receipt.",
            "Valid time and operative legal status unknown; no atomic snapshot claimed.",
            "Rights metadata is separately observed, not backdated to layer capture.",
        ],
        "files": [
            {"path": name, "bytes": len(body), "sha256": sha256_bytes(body)}
            for name, body in sorted(blobs.items())
        ],
    }
    blobs["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    checksums = "".join(f"{sha256_bytes(body)}  {name}\n" for name, body in sorted(blobs.items()))
    blobs["checksums.sha256"] = checksums.encode()
    target.mkdir(parents=True)
    for name, body in blobs.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    return manifest
