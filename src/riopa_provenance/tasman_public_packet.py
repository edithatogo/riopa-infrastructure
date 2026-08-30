"""Build a rights-bound Tasman layer packet without publishing or changing originals."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

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
    roles.extend((cid, "page") for cid in pages)
    if capture_set.get("object_ids_capture_id"):
        roles.append((capture_set["object_ids_capture_id"], "ids"))
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
        request_url = record["request"]["url"].split("?", 1)[0]
        expected_url = RIGHTS_URL if role == "rights" else f"{SERVICE}/3"
        if role in ("count", "page", "ids"):
            expected_url += "/query"
        if request_url != expected_url:
            raise ValueError("capture request is not bound to selected layer/item")
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
