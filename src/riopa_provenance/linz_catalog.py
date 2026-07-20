"""Catalogue-complete LINZ Data Service discovery and planning primitives.

"Archive all LINZ datasets" is modelled as two separate completeness claims:

* catalogue completeness: every published catalogue entry is captured, versioned,
  classified, and assigned an explicit archival disposition; and
* payload completeness: every entry is either mirrored according to a supported
  strategy or carries a reviewed exception explaining why only metadata can be
  preserved or redistributed.

This distinction prevents large rasters, external catalogue items, restricted
records, or unsupported services from disappearing from coverage reports.
"""

from __future__ import annotations

import csv
import json
import re
import uuid
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

from .capture import CaptureError, CaptureResult, HttpCaptureClient, _atomic_write
from .hashing import sha256_file, sha256_json

_LINK_RE = re.compile(r'<(?P<url>[^>]+)>\s*;\s*rel="?(?P<rel>[^";,]+)"?', re.IGNORECASE)
_RANGE_RE = re.compile(r"^(?P<start>\d+)-(?P<end>\d+)/(?P<total>\d+|\*)$")


class LinzCatalogError(RuntimeError):
    """Raised when a catalogue snapshot cannot be proven complete."""


@dataclass(frozen=True)
class LinzCatalogSnapshot:
    """Content-bound catalogue snapshot artifacts."""

    snapshot_id: str
    source_id: str
    endpoint_id: str
    captured_at: str
    item_count: int
    page_count: int
    items_path: Path
    csv_path: Path
    manifest_path: Path
    capture_ids: tuple[str, ...]


@dataclass(frozen=True)
class LinzCatalogDiff:
    """Stable-ID comparison between two catalogue snapshots."""

    added: tuple[str, ...]
    removed: tuple[str, ...]
    changed: tuple[str, ...]
    unchanged: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "added": list(self.added),
            "removed": list(self.removed),
            "changed": list(self.changed),
            "unchanged": list(self.unchanged),
            "counts": {
                "added": len(self.added),
                "removed": len(self.removed),
                "changed": len(self.changed),
                "unchanged": len(self.unchanged),
            },
        }


def parse_link_header(value: str | None) -> dict[str, str]:
    """Parse the subset of RFC 8288 Link headers used for catalogue paging."""

    if not value:
        return {}
    return {
        match.group("rel").strip().lower(): match.group("url").strip()
        for match in _LINK_RE.finditer(value)
    }


def parse_resource_range(value: str | None) -> tuple[int, int, int | None] | None:
    """Parse Koordinates ``X-Resource-Range`` metadata."""

    if not value:
        return None
    match = _RANGE_RE.fullmatch(value.strip())
    if not match:
        raise LinzCatalogError(f"invalid X-Resource-Range header: {value!r}")
    total = match.group("total")
    return int(match.group("start")), int(match.group("end")), None if total == "*" else int(total)


def _capture_headers(result: CaptureResult) -> dict[str, str]:
    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    headers = metadata.get("response", {}).get("headers", {})
    if not isinstance(headers, dict):
        raise LinzCatalogError(f"capture has no response-header object: {result.capture_id}")
    return {str(key).lower(): str(value) for key, value in headers.items()}


def _item_type(item: Mapping[str, Any]) -> str:
    aliases = {
        "layer": "layer",
        "layers": "layer",
        "table": "table",
        "tables": "table",
        "set": "set",
        "sets": "set",
        "document": "document",
        "documents": "document",
        "source": "source",
        "sources": "source",
        "catalog-item": "catalog-item",
        "catalog-items": "catalog-item",
    }
    value = item.get("type")
    if isinstance(value, str) and value:
        return aliases.get(value.casefold(), value.casefold())
    url = str(item.get("url") or "")
    for candidate, normalised in aliases.items():
        if candidate.endswith("s") and f"/{candidate}/" in url:
            return normalised
    return "unknown"


def _item_name(item: Mapping[str, Any]) -> str:
    for key in ("name", "title", "label"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return f"{_item_type(item)} {item.get('id', 'unknown')}"


def normalise_catalog_item(item: Mapping[str, Any]) -> dict[str, Any]:
    """Preserve a raw catalogue entry alongside stable analytical fields."""

    if "id" not in item:
        raise LinzCatalogError("catalogue entry has no id")
    item_type = _item_type(item)
    source_id = str(item["id"])
    raw = dict(item)
    raw_digest = sha256_json(raw)
    return {
        "schema_version": "1.0.0",
        "record_type": "linz_catalog_item",
        "catalog_item_id": f"urn:riopa:linz-catalog:{item_type}:{source_id}",
        "source_catalog_id": source_id,
        "item_type": item_type,
        "name": _item_name(item),
        "url": item.get("url"),
        "url_html": item.get("url_html"),
        "kind": item.get("kind"),
        "first_published_at": item.get("first_published_at"),
        "published_at": item.get("published_at"),
        "updated_at": item.get("updated_at"),
        "license": item.get("license"),
        "categories": item.get("categories") or [],
        "tags": item.get("tags") or [],
        "raw_sha256": raw_digest,
        "raw": raw,
    }


def _write_jsonl(path: Path, records: Sequence[Mapping[str, Any]]) -> None:
    payload = b"".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n"
        for record in records
    )
    _atomic_write(path, payload)


def _write_catalog_csv(path: Path, records: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    fields = [
        "catalog_item_id",
        "source_catalog_id",
        "item_type",
        "kind",
        "name",
        "url",
        "url_html",
        "first_published_at",
        "published_at",
        "updated_at",
        "raw_sha256",
    ]
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow({key: record.get(key) for key in fields})
    temporary.replace(path)


def catalog_items_path(path: str | Path) -> Path:
    """Resolve the canonical JSONL payload from a JSONL path or snapshot manifest."""

    source = Path(path).resolve()
    if source.name.endswith("manifest.json"):
        manifest = json.loads(source.read_text(encoding="utf-8"))
        items = manifest.get("items") if isinstance(manifest, Mapping) else None
        reference = items.get("path") if isinstance(items, Mapping) else None
        if not isinstance(reference, str) or not reference:
            raise LinzCatalogError(f"catalogue snapshot has no items path: {source}")
        candidate = (source.parent / reference).resolve()
        try:
            candidate.relative_to(source.parent.resolve())
        except ValueError as exc:
            raise LinzCatalogError(
                f"catalogue items path escapes snapshot root: {reference}"
            ) from exc
        source = candidate
    if not source.is_file():
        raise LinzCatalogError(f"catalogue items file is missing: {source}")
    return source


def load_catalog_items(path: str | Path) -> list[dict[str, Any]]:
    """Load canonical catalogue items from JSONL or a snapshot manifest."""

    source = catalog_items_path(path)
    records: list[dict[str, Any]] = []
    for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise LinzCatalogError(f"catalogue JSONL line {number} is not an object")
        records.append(value)
    return records


class LinzCatalogArchiver:
    """Capture every published entry from a Koordinates catalogue endpoint."""

    def __init__(self, capture_client: HttpCaptureClient, *, max_pages: int = 100_000) -> None:
        if max_pages < 1:
            raise ValueError("max_pages must be positive")
        self.capture_client = capture_client
        self.max_pages = max_pages

    def archive(
        self,
        *,
        source_id: str,
        endpoint_id: str,
        catalog_url: str,
        output_dir: str | Path,
        query: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        redact_values: Sequence[str] = (),
    ) -> LinzCatalogSnapshot:
        """Capture a complete, de-duplicated catalogue snapshot.

        Pagination follows the server-provided ``Link: rel=page-next`` URL and checks
        ``X-Resource-Range`` when present.  Repeated pages, loops, inconsistent
        totals, duplicate stable IDs, and cross-host pagination fail closed.
        """

        output = Path(output_dir).resolve()
        output.mkdir(parents=True, exist_ok=True)
        original_host = (urlsplit(catalog_url).hostname or "").lower()
        current_url = catalog_url
        current_params: Mapping[str, Any] | None = {"sort": "name", **dict(query or {})}
        seen_urls: set[str] = set()
        seen_page_hashes: set[str] = set()
        captures: list[CaptureResult] = []
        records: list[dict[str, Any]] = []
        declared_total: int | None = None
        ranges: list[dict[str, int | None]] = []

        for page_index in range(1, self.max_pages + 1):
            if current_url in seen_urls:
                raise LinzCatalogError(f"catalogue pagination loop detected at {current_url}")
            seen_urls.add(current_url)
            result, payload = self.capture_client.capture_json(
                "GET",
                current_url,
                source_id=source_id,
                endpoint_id=f"{endpoint_id}:page:{page_index:06d}",
                params=current_params,
                headers=headers,
                redact_values=redact_values,
            )
            if not isinstance(payload, list):
                raise LinzCatalogError(
                    f"catalogue page {page_index} is not a JSON array: {result.capture_id}"
                )
            if result.object_sha256 in seen_page_hashes and payload:
                raise LinzCatalogError(f"repeated non-empty catalogue page at page {page_index}")
            seen_page_hashes.add(result.object_sha256)
            captures.append(result)
            page_records = [
                normalise_catalog_item(item) for item in payload if isinstance(item, dict)
            ]
            if len(page_records) != len(payload):
                raise LinzCatalogError(f"catalogue page {page_index} contains a non-object entry")
            records.extend(page_records)

            response_headers = _capture_headers(result)
            resource_range = parse_resource_range(
                response_headers.get("x-resource-range") or response_headers.get("x-resource_range")
            )
            if resource_range:
                start, end, total = resource_range
                if end - start != len(payload):
                    raise LinzCatalogError(
                        f"resource range {start}-{end} disagrees with {len(payload)} rows"
                    )
                if declared_total is not None and total is not None and total != declared_total:
                    raise LinzCatalogError(
                        f"catalogue total changed during capture: {declared_total} to {total}"
                    )
                if total is not None:
                    declared_total = total
                ranges.append({"start": start, "end": end, "total": total})

            links = parse_link_header(response_headers.get("link"))
            next_url = links.get("next") or links.get("page-next")
            if not next_url:
                break
            next_url = urljoin(current_url, next_url)
            if (urlsplit(next_url).hostname or "").lower() != original_host:
                raise LinzCatalogError(f"catalogue next link changes host: {next_url}")
            current_url = next_url
            current_params = None
        else:
            raise LinzCatalogError(f"catalogue pagination exceeded max_pages={self.max_pages}")

        by_id: dict[str, dict[str, Any]] = {}
        for record in records:
            identifier = str(record["catalog_item_id"])
            if identifier in by_id:
                raise LinzCatalogError(f"duplicate catalogue item identity: {identifier}")
            by_id[identifier] = record
        ordered = [by_id[key] for key in sorted(by_id)]
        if declared_total is not None and len(ordered) != declared_total:
            message = (
                "catalogue capture is incomplete: "
                f"observed={len(ordered)}, declared={declared_total}"
            )
            raise LinzCatalogError(message)

        snapshot_id = f"urn:uuid:{uuid.uuid4()}"
        safe_id = snapshot_id.removeprefix("urn:uuid:")
        items_path = output / f"linz-catalog-items-{safe_id}.jsonl"
        csv_path = output / f"linz-catalog-items-{safe_id}.csv"
        _write_jsonl(items_path, ordered)
        _write_catalog_csv(csv_path, ordered)
        counts = Counter(str(record.get("item_type") or "unknown") for record in ordered)
        captured_at = captures[0].retrieved_at if captures else ""
        effective_query = {"sort": "name", **dict(query or {})}
        filter_keys = sorted(key for key in effective_query if key != "sort")
        unfiltered_published_catalogue = not filter_keys
        manifest: dict[str, Any] = {
            "schema_version": "1.0.0",
            "record_type": "linz_catalog_snapshot",
            "snapshot_id": snapshot_id,
            "source_id": source_id,
            "endpoint_id": endpoint_id,
            "catalog_url": catalog_url,
            "captured_at": captured_at,
            "query": effective_query,
            "scope": {
                "catalogue_view": "published-version-of-each-visible-item",
                "visibility": "entries-visible-to-the-catalogue-request",
                "published_only": True,
                "unfiltered": unfiltered_published_catalogue,
                "filter_keys": filter_keys,
                "excluded_by_definition": [
                    "unpublished items",
                    "internal LINZ records not exposed through the catalogue",
                    "restricted entries not visible to the request identity",
                ],
            },
            "page_count": len(captures),
            "item_count": len(ordered),
            "declared_item_count": declared_total,
            "counts_by_type": dict(sorted(counts.items())),
            "pages": [
                {
                    "sequence": index,
                    "capture_id": capture.capture_id,
                    "object_sha256": capture.object_sha256,
                    "size_bytes": capture.size_bytes,
                }
                for index, capture in enumerate(captures, start=1)
            ],
            "resource_ranges": ranges,
            "items": {
                "path": items_path.name,
                "sha256": sha256_file(items_path),
                "size_bytes": items_path.stat().st_size,
                "format": "application/x-ndjson",
            },
            "csv": {
                "path": csv_path.name,
                "sha256": sha256_file(csv_path),
                "size_bytes": csv_path.stat().st_size,
                "format": "text/csv",
            },
            "completeness": {
                "catalogue_enumerated": True,
                "unfiltered_published_catalogue": unfiltered_published_catalogue,
                "every_entry_has_stable_identity": True,
                "payloads_archived": False,
                "claim": (
                    "complete enumeration of the published catalogue visible to the request; "
                    "payload archival tracked separately"
                    if unfiltered_published_catalogue
                    else (
                        "complete enumeration of a filtered catalogue result; "
                        "not a full-catalogue claim"
                    )
                ),
            },
            "manifest_sha256": "",
        }
        manifest["manifest_sha256"] = sha256_json(manifest, omit_keys={"manifest_sha256"})
        manifest_path = output / f"linz-catalog-snapshot-{safe_id}.manifest.json"
        _atomic_write(
            manifest_path,
            json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
            + b"\n",
        )
        return LinzCatalogSnapshot(
            snapshot_id=snapshot_id,
            source_id=source_id,
            endpoint_id=endpoint_id,
            captured_at=captured_at,
            item_count=len(ordered),
            page_count=len(captures),
            items_path=items_path,
            csv_path=csv_path,
            manifest_path=manifest_path,
            capture_ids=tuple(capture.capture_id for capture in captures),
        )


def diff_catalog_items(
    previous: Iterable[Mapping[str, Any]],
    current: Iterable[Mapping[str, Any]],
) -> LinzCatalogDiff:
    """Compare snapshots without treating retrieval timestamps as content changes."""

    left = {str(item["catalog_item_id"]): str(item["raw_sha256"]) for item in previous}
    right = {str(item["catalog_item_id"]): str(item["raw_sha256"]) for item in current}
    left_ids = set(left)
    right_ids = set(right)
    shared = left_ids & right_ids
    return LinzCatalogDiff(
        added=tuple(sorted(right_ids - left_ids)),
        removed=tuple(sorted(left_ids - right_ids)),
        changed=tuple(
            sorted(identifier for identifier in shared if left[identifier] != right[identifier])
        ),
        unchanged=tuple(
            sorted(identifier for identifier in shared if left[identifier] == right[identifier])
        ),
    )


def write_catalog_diff(
    previous_path: str | Path,
    current_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Write a content-bound catalogue change report."""

    previous = load_catalog_items(previous_path)
    current = load_catalog_items(current_path)
    report: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "linz_catalog_diff",
        "previous_sha256": sha256_file(catalog_items_path(previous_path)),
        "current_sha256": sha256_file(catalog_items_path(current_path)),
        **diff_catalog_items(previous, current).as_dict(),
        "report_sha256": "",
    }
    report["report_sha256"] = sha256_json(report, omit_keys={"report_sha256"})
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination


def build_detail_queue(
    items: Iterable[Mapping[str, Any]],
    *,
    shard_count: int = 1,
) -> list[dict[str, Any]]:
    """Create deterministic, resumable catalogue-detail jobs for every entry."""

    if shard_count < 1:
        raise ValueError("shard_count must be positive")
    jobs: list[dict[str, Any]] = []
    for record in sorted(items, key=lambda item: str(item["catalog_item_id"])):
        identifier = str(record["catalog_item_id"])
        source_url = record.get("url")
        if not isinstance(source_url, str) or not source_url:
            disposition = "metadata-summary-only"
            blocked_reason = "catalogue summary contains no detail URL"
        else:
            disposition = "capture-item-detail"
            blocked_reason = None
        digest = sha256_json({"catalog_item_id": identifier, "url": source_url})
        jobs.append(
            {
                "job_id": f"urn:riopa:linz-catalog-detail-job:{digest}",
                "catalog_item_id": identifier,
                "source_catalog_id": record["source_catalog_id"],
                "item_type": record["item_type"],
                "url": source_url,
                "shard": int(digest[:8], 16) % shard_count,
                "disposition": disposition,
                "blocked_reason": blocked_reason,
            }
        )
    return jobs


def validate_detail_url(url: str, *, expected_host: str) -> None:
    """Reject cross-host or credential-bearing detail URLs."""

    parsed = urlsplit(url)
    if parsed.scheme != "https":
        raise LinzCatalogError(f"catalogue detail URL must use HTTPS: {url}")
    if parsed.username or parsed.password:
        raise LinzCatalogError("catalogue detail URL contains authority credentials")
    if (parsed.hostname or "").lower() != expected_host.lower():
        raise LinzCatalogError(f"catalogue detail URL changes host: {url}")


class LinzCatalogDetailArchiver:
    """Capture item-detail records from a catalogue queue with resumable receipts."""

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
        """Capture detail jobs sequentially and skip valid existing receipts."""

        output = Path(output_dir).resolve()
        output.mkdir(parents=True, exist_ok=True)
        receipts: list[Path] = []
        selected = list(jobs)
        if limit is not None:
            if limit < 0:
                raise ValueError("limit must be non-negative")
            selected = selected[:limit]
        for job in selected:
            if job.get("disposition") != "capture-item-detail":
                continue
            job_id = str(job["job_id"])
            receipt_path = output / f"{job_id.rsplit(':', 1)[-1]}.json"
            if receipt_path.is_file():
                existing = json.loads(receipt_path.read_text(encoding="utf-8"))
                expected = sha256_json(existing, omit_keys={"receipt_sha256"})
                if existing.get("receipt_sha256") == expected:
                    receipts.append(receipt_path)
                    continue
                raise LinzCatalogError(f"existing detail receipt is corrupt: {receipt_path}")
            url = str(job["url"])
            validate_detail_url(url, expected_host=expected_host)
            result, payload = self.capture_client.capture_json(
                "GET",
                url,
                source_id=source_id,
                endpoint_id=f"{endpoint_id}:detail:{job['source_catalog_id']}",
                headers=headers,
                redact_values=redact_values,
            )
            if not isinstance(payload, dict):
                raise CaptureError(f"LINZ catalogue detail is not an object: {result.capture_id}")
            receipt: dict[str, Any] = {
                "schema_version": "1.0.0",
                "record_type": "linz_catalog_detail_capture",
                "job_id": job_id,
                "catalog_item_id": job["catalog_item_id"],
                "source_catalog_id": job["source_catalog_id"],
                "item_type": job["item_type"],
                "capture_id": result.capture_id,
                "captured_at": result.retrieved_at,
                "object_sha256": result.object_sha256,
                "size_bytes": result.size_bytes,
                "detail_sha256": sha256_json(payload),
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
