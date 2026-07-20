"""Content-bound LINZ catalogue detail, service, and enrichment workflow."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from .capture import CaptureError, HttpCaptureClient, _atomic_write
from .hashing import sha256_file, sha256_json
from .linz_catalog import (
    LinzCatalogError,
    _write_catalog_csv,
    _write_jsonl,
    catalog_items_path,
    load_catalog_items,
    normalise_catalog_item,
    validate_detail_url,
)


@dataclass(frozen=True)
class LinzCatalogEnrichedSnapshot:
    snapshot_id: str
    item_count: int
    detail_count: int
    service_count: int
    items_path: Path
    manifest_path: Path


def build_service_queue(items: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Create deterministic service-list jobs for service-owning catalogue entries."""

    supported = {"layer", "table", "set", "catalog-item"}
    jobs: list[dict[str, Any]] = []
    for record in sorted(items, key=lambda item: str(item["catalog_item_id"])):
        item_type = str(record.get("item_type") or "unknown")
        source_url = record.get("url")
        if item_type not in supported:
            disposition = "not-a-service-owner"
            service_url = None
            blocked_reason = None
        elif not isinstance(source_url, str) or not source_url:
            disposition = "service-list-unavailable"
            service_url = None
            blocked_reason = "catalogue summary contains no owner URL"
        else:
            disposition = "capture-service-list"
            service_url = urljoin(source_url.rstrip("/") + "/", "services/")
            blocked_reason = None
        seed = {
            "catalog_item_id": record["catalog_item_id"],
            "service_url": service_url,
        }
        jobs.append(
            {
                "job_id": f"urn:riopa:linz-service-job:{sha256_json(seed)}",
                "catalog_item_id": record["catalog_item_id"],
                "source_catalog_id": record["source_catalog_id"],
                "item_type": item_type,
                "url": service_url,
                "disposition": disposition,
                "blocked_reason": blocked_reason,
            }
        )
    return jobs


class LinzCatalogServiceArchiver:
    """Archive service inventories with resumable, content-bound receipts."""

    def __init__(self, capture_client: HttpCaptureClient) -> None:
        self.capture_client = capture_client

    def archive_jobs(
        self,
        jobs: Iterable[Mapping[str, Any]],
        *,
        source_id: str,
        endpoint_id: str,
        output_dir: str | Path,
        expected_host: str = "data.linz.govt.nz",
        headers: Mapping[str, str] | None = None,
        redact_values: Sequence[str] = (),
        limit: int | None = None,
    ) -> list[Path]:
        output = Path(output_dir).resolve()
        output.mkdir(parents=True, exist_ok=True)
        selected = list(jobs)
        if limit is not None:
            if limit < 0:
                raise ValueError("limit must be non-negative")
            selected = selected[:limit]
        receipts: list[Path] = []
        for job in selected:
            if job.get("disposition") != "capture-service-list":
                continue
            job_id = str(job["job_id"])
            receipt_path = output / f"{job_id.rsplit(':', 1)[-1]}.json"
            if receipt_path.is_file():
                existing = _load_receipt(receipt_path, "service")
                receipts.append(receipt_path)
                if existing.get("job_id") != job_id:
                    raise LinzCatalogError(
                        f"existing service receipt belongs to another job: {receipt_path}"
                    )
                continue
            url = str(job["url"])
            validate_detail_url(url, expected_host=expected_host)
            result, payload = self.capture_client.capture_json(
                "GET",
                url,
                source_id=source_id,
                endpoint_id=f"{endpoint_id}:services:{job['source_catalog_id']}",
                headers=headers,
                redact_values=redact_values,
            )
            if not isinstance(payload, list) or any(
                not isinstance(entry, Mapping) for entry in payload
            ):
                raise CaptureError(
                    f"LINZ service inventory is not an object array: {result.capture_id}"
                )
            service_keys = sorted(
                {
                    str(entry.get("key"))
                    for entry in payload
                    if isinstance(entry.get("key"), str) and entry.get("key")
                }
            )
            receipt: dict[str, Any] = {
                "schema_version": "1.0.0",
                "record_type": "linz_catalog_service_capture",
                "job_id": job_id,
                "catalog_item_id": job["catalog_item_id"],
                "source_catalog_id": job["source_catalog_id"],
                "item_type": job["item_type"],
                "capture_id": result.capture_id,
                "captured_at": result.retrieved_at,
                "object_sha256": result.object_sha256,
                "size_bytes": result.size_bytes,
                "service_count": len(payload),
                "service_keys": service_keys,
                "service_sha256": sha256_json(payload),
                "receipt_sha256": "",
            }
            receipt["receipt_sha256"] = sha256_json(receipt, omit_keys={"receipt_sha256"})
            _atomic_write(
                receipt_path,
                json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
                + b"\n",
            )
            receipts.append(receipt_path)
        return receipts


def _load_receipt(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LinzCatalogError(f"cannot load {label} receipt: {path}") from exc
    if not isinstance(value, dict):
        raise LinzCatalogError(f"{label} receipt root is not an object: {path}")
    expected = sha256_json(value, omit_keys={"receipt_sha256"})
    if value.get("receipt_sha256") != expected:
        raise LinzCatalogError(f"{label} receipt hash mismatch: {path}")
    return value


def _load_captured_json(
    receipt: Mapping[str, Any],
    *,
    store_root: Path,
    expected_collection: bool,
    label: str,
) -> Any:
    digest = receipt.get("object_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise LinzCatalogError(f"{label} receipt has no valid object digest")
    object_path = store_root / "objects" / "sha256" / digest[:2] / digest
    if not object_path.is_file():
        raise LinzCatalogError(f"{label} capture object is missing: {object_path}")
    if sha256_file(object_path) != digest:
        raise LinzCatalogError(f"{label} capture object hash mismatch: {object_path}")
    try:
        value = json.loads(object_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LinzCatalogError(f"{label} capture object is not JSON: {object_path}") from exc
    if expected_collection:
        if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
            raise LinzCatalogError(f"{label} capture object is not an object array")
    elif not isinstance(value, dict):
        raise LinzCatalogError(f"{label} capture object is not an object")
    expected_digest = receipt.get("service_sha256" if expected_collection else "detail_sha256")
    if expected_digest != sha256_json(value):
        raise LinzCatalogError(f"{label} semantic digest mismatch")
    return value


def _receipt_index(
    paths: Iterable[str | Path],
    *,
    record_type: str,
    label: str,
) -> dict[str, tuple[Path, dict[str, Any]]]:
    result: dict[str, tuple[Path, dict[str, Any]]] = {}
    for raw_path in paths:
        path = Path(raw_path).resolve()
        receipt = _load_receipt(path, label)
        if receipt.get("record_type") != record_type:
            raise LinzCatalogError(f"not a {label} receipt: {path}")
        item_id = str(receipt.get("catalog_item_id") or "")
        if not item_id:
            raise LinzCatalogError(f"{label} receipt has no catalogue item identity: {path}")
        if item_id in result:
            raise LinzCatalogError(f"duplicate {label} receipt for {item_id}")
        result[item_id] = (path, receipt)
    return result


def _receipt_paths(path: str | Path | None) -> list[Path]:
    if path is None:
        return []
    source = Path(path)
    if source.is_dir():
        return sorted(source.glob("*.json"))
    return [source]


def _detail_kind(payload: Mapping[str, Any]) -> Any:
    if payload.get("kind") is not None:
        return payload.get("kind")
    data = payload.get("data")
    return data.get("kind") if isinstance(data, Mapping) else None


def write_enriched_catalog_snapshot(
    catalog_snapshot_manifest: str | Path,
    detail_receipts: str | Path,
    capture_store_root: str | Path,
    output_dir: str | Path,
    *,
    service_receipts: str | Path | None = None,
    require_complete_details: bool = True,
    require_complete_services: bool = True,
) -> LinzCatalogEnrichedSnapshot:
    """Bind detail and service captures to every catalogue item.

    The output remains a catalogue record set rather than a payload archive. It
    is the authoritative capability-and-rights input to the all-items archive
    planner.
    """

    source_manifest_path = Path(catalog_snapshot_manifest).resolve()
    try:
        source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LinzCatalogError(
            f"cannot load source catalogue snapshot: {source_manifest_path}"
        ) from exc
    if (
        not isinstance(source_manifest, dict)
        or source_manifest.get("record_type") != "linz_catalog_snapshot"
    ):
        raise LinzCatalogError("enrichment source is not a LINZ catalogue snapshot")
    if source_manifest.get("manifest_sha256") != sha256_json(
        source_manifest, omit_keys={"manifest_sha256"}
    ):
        raise LinzCatalogError("source catalogue snapshot manifest hash mismatch")
    items_descriptor = source_manifest.get("items")
    if not isinstance(items_descriptor, Mapping):
        raise LinzCatalogError("source catalogue snapshot has no items descriptor")
    items_file = catalog_items_path(source_manifest_path)
    if items_descriptor.get("sha256") != sha256_file(items_file):
        raise LinzCatalogError("source catalogue item hash mismatch")
    if items_descriptor.get("size_bytes") != items_file.stat().st_size:
        raise LinzCatalogError("source catalogue item size mismatch")
    source_snapshot_id = str(source_manifest.get("snapshot_id") or "")
    source_completeness = source_manifest.get("completeness")
    source_unfiltered = bool(
        isinstance(source_completeness, Mapping)
        and source_completeness.get("unfiltered_published_catalogue") is True
    )
    items = load_catalog_items(items_file)
    store_root = Path(capture_store_root).resolve()
    detail_index = _receipt_index(
        _receipt_paths(detail_receipts),
        record_type="linz_catalog_detail_capture",
        label="detail",
    )
    service_index = _receipt_index(
        _receipt_paths(service_receipts),
        record_type="linz_catalog_service_capture",
        label="service",
    )
    item_ids = {str(item["catalog_item_id"]) for item in items}
    unknown_details = sorted(set(detail_index) - item_ids)
    unknown_services = sorted(set(service_index) - item_ids)
    if unknown_details or unknown_services:
        raise LinzCatalogError(
            "enrichment receipts reference unknown catalogue items: "
            f"details={unknown_details}, services={unknown_services}"
        )

    enriched: list[dict[str, Any]] = []
    missing_details: list[str] = []
    missing_services: list[str] = []
    service_owners = {"layer", "table", "set", "catalog-item"}
    for summary in sorted(items, key=lambda item: str(item["catalog_item_id"])):
        item_id = str(summary["catalog_item_id"])
        item_type = str(summary.get("item_type") or "unknown")
        detail_entry = detail_index.get(item_id)
        if detail_entry is None:
            missing_details.append(item_id)
            record = dict(summary)
            record["detail_status"] = "missing"
        else:
            detail_path, detail_receipt = detail_entry
            detail = _load_captured_json(
                detail_receipt,
                store_root=store_root,
                expected_collection=False,
                label="detail",
            )
            detail_id = detail.get("id")
            if detail_id is not None and str(detail_id) != str(summary["source_catalog_id"]):
                raise LinzCatalogError(f"detail identity mismatch for {item_id}")
            normalisable = dict(detail)
            normalisable.setdefault("id", summary["source_catalog_id"])
            normalisable.setdefault("type", item_type)
            normalisable.setdefault("url", summary.get("url"))
            normalised = normalise_catalog_item(normalisable)
            if normalised["catalog_item_id"] != item_id:
                raise LinzCatalogError(f"normalised detail identity mismatch for {item_id}")
            record = {
                **summary,
                **normalised,
                "kind": _detail_kind(detail) or summary.get("kind"),
                "catalog_summary": summary.get("raw"),
                "catalog_summary_sha256": summary.get("raw_sha256"),
                "detail_status": "captured",
                "detail_capture_id": detail_receipt["capture_id"],
                "detail_receipt_path": detail_path.as_posix(),
                "detail_receipt_sha256": detail_receipt["receipt_sha256"],
            }
        service_entry = service_index.get(item_id)
        if service_entry is None:
            if item_type in service_owners:
                missing_services.append(item_id)
            record["service_status"] = (
                "not-applicable" if item_type not in service_owners else "missing"
            )
            record["services"] = []
        else:
            service_path, service_receipt = service_entry
            services = _load_captured_json(
                service_receipt,
                store_root=store_root,
                expected_collection=True,
                label="service",
            )
            record["service_status"] = "captured"
            record["services"] = services
            record["service_capture_id"] = service_receipt["capture_id"]
            record["service_receipt_path"] = service_path.as_posix()
            record["service_receipt_sha256"] = service_receipt["receipt_sha256"]
        enriched.append(record)

    if require_complete_details and missing_details:
        raise LinzCatalogError(
            f"catalogue detail coverage is incomplete: {len(missing_details)} missing"
        )
    if require_complete_services and missing_services:
        raise LinzCatalogError(
            f"catalogue service coverage is incomplete: {len(missing_services)} missing"
        )

    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    seed = {
        "source_snapshot_id": source_snapshot_id,
        "items_sha256": sha256_file(items_file),
        "detail_receipts": sorted(
            receipt[1]["receipt_sha256"] for receipt in detail_index.values()
        ),
        "service_receipts": sorted(
            receipt[1]["receipt_sha256"] for receipt in service_index.values()
        ),
    }
    snapshot_id = f"urn:riopa:linz-enriched-catalog:{sha256_json(seed)}"
    safe_id = snapshot_id.rsplit(":", 1)[-1]
    enriched_path = output / f"linz-catalog-enriched-{safe_id}.jsonl"
    csv_path = output / f"linz-catalog-enriched-{safe_id}.csv"
    _write_jsonl(enriched_path, enriched)
    _write_catalog_csv(csv_path, enriched)
    manifest: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "linz_catalog_enriched_snapshot",
        "snapshot_id": snapshot_id,
        "source_snapshot_id": source_snapshot_id,
        "source_items": {
            "path": items_file.as_posix(),
            "sha256": sha256_file(items_file),
            "size_bytes": items_file.stat().st_size,
        },
        "items": {
            "path": enriched_path.name,
            "sha256": sha256_file(enriched_path),
            "size_bytes": enriched_path.stat().st_size,
            "format": "application/x-ndjson",
        },
        "csv": {
            "path": csv_path.name,
            "sha256": sha256_file(csv_path),
            "size_bytes": csv_path.stat().st_size,
            "format": "text/csv",
        },
        "item_count": len(enriched),
        "detail_coverage": {
            "captured": len(detail_index),
            "missing": len(missing_details),
            "complete": not missing_details,
        },
        "service_coverage": {
            "captured": len(service_index),
            "missing": len(missing_services),
            "complete": not missing_services,
        },
        "completeness": {
            "catalogue_enumerated": True,
            "unfiltered_published_catalogue": source_unfiltered,
            "details_captured": not missing_details,
            "services_captured": not missing_services,
            "payloads_archived": False,
            "claim": (
                "all entries in the unfiltered published catalogue visible to the "
                "request have content-bound detail and service dispositions; payload "
                "archival is tracked separately"
                if source_unfiltered
                else "the filtered catalogue subset has content-bound detail and "
                "service dispositions; this is not a full-catalogue claim"
            ),
        },
        "manifest_sha256": "",
    }
    manifest["manifest_sha256"] = sha256_json(manifest, omit_keys={"manifest_sha256"})
    manifest_path = output / f"linz-catalog-enriched-{safe_id}.manifest.json"
    _atomic_write(
        manifest_path,
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n",
    )
    return LinzCatalogEnrichedSnapshot(
        snapshot_id=snapshot_id,
        item_count=len(enriched),
        detail_count=len(detail_index),
        service_count=len(service_index),
        items_path=enriched_path,
        manifest_path=manifest_path,
    )
