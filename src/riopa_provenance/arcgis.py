"""ArcGIS REST discovery and complete, fail-closed feature-layer archival."""

from __future__ import annotations

import json
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .capture import (
    CaptureError,
    CaptureResult,
    HttpCaptureClient,
    _atomic_write,
    redact_text,
)
from .hashing import sha256_json


@dataclass(frozen=True)
class ArcGISLayerArchive:
    capture_set_id: str
    source_id: str
    service_url: str
    layer_id: int
    metadata_capture: CaptureResult
    count_captures: tuple[CaptureResult, CaptureResult]
    object_ids_capture: CaptureResult | None
    page_captures: tuple[CaptureResult, ...]
    feature_count: int
    manifest_path: Path


def validate_arcgis_request_contract(
    service_url: str, layer_id: int, where: str, out_fields: str
) -> None:
    """Reject unsafe or ambiguous ArcGIS requests before network capture.

    This is a request-shape guard, not source or rights validation.  The
    capture client's allow-list and DNS policy remain authoritative for
    network access.
    """

    parsed = urlsplit(service_url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise CaptureError("ArcGIS service URL must be an HTTPS URL without userinfo")
    if layer_id < 0:
        raise CaptureError("ArcGIS layer_id must be non-negative")
    if not where.strip():
        raise CaptureError("ArcGIS where clause must not be empty")
    if not out_fields.strip():
        raise CaptureError("ArcGIS out_fields must not be empty")


def _effective_out_fields(out_fields: str, object_id_field: str | None) -> str:
    if not object_id_field or out_fields.strip() == "*":
        return out_fields
    fields = [item.strip() for item in out_fields.split(",") if item.strip()]
    if object_id_field.casefold() not in {item.casefold() for item in fields}:
        fields.append(object_id_field)
    return ",".join(fields)


def _feature_object_ids(features: list[Any], object_id_field: str) -> list[int]:
    values: list[int] = []
    for feature in features:
        if not isinstance(feature, dict) or not isinstance(feature.get("attributes"), dict):
            raise CaptureError("ArcGIS feature has no attributes object")
        value = feature["attributes"].get(object_id_field)
        if isinstance(value, bool) or not isinstance(value, int):
            raise CaptureError(
                f"ArcGIS feature has an invalid integer object ID in {object_id_field!r}"
            )
        values.append(value)
    return values


class ArcGISFeatureLayerArchiver:
    """Archive metadata and a count-reconciled complete query result.

    Offset pagination is used when the layer advertises support.  For older or
    non-paginable layers, the archiver first captures the complete object-ID
    set and then retrieves deterministic chunks.  Both strategies capture row
    counts before and after retrieval and fail if the source changes or the
    retrieved set is incomplete.
    """

    def __init__(self, capture_client: HttpCaptureClient, *, max_pages: int = 100_000) -> None:
        if max_pages < 1:
            raise ValueError("max_pages must be positive")
        self.capture_client = capture_client
        self.max_pages = max_pages

    def _capture_count(
        self,
        *,
        source_id: str,
        endpoint_id: str,
        query_url: str,
        common: Mapping[str, Any],
        where: str,
        headers: Mapping[str, str] | None,
        redact_values: Sequence[str],
    ) -> tuple[CaptureResult, int]:
        capture, payload = self.capture_client.capture_json(
            "GET",
            query_url,
            source_id=source_id,
            endpoint_id=endpoint_id,
            params={**common, "f": "json", "where": where, "returnCountOnly": "true"},
            headers=headers,
            redact_values=redact_values,
        )
        if not isinstance(payload, dict) or "error" in payload:
            raise CaptureError(f"ArcGIS count query failed: {payload}")
        count = payload.get("count")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise CaptureError("ArcGIS count query did not return a non-negative integer")
        return capture, count

    def _capture_page(
        self,
        *,
        source_id: str,
        endpoint_id: str,
        query_url: str,
        params: Mapping[str, Any],
        headers: Mapping[str, str] | None,
        redact_values: Sequence[str],
    ) -> tuple[CaptureResult, list[Any], bool]:
        capture, payload = self.capture_client.capture_json(
            "GET",
            query_url,
            source_id=source_id,
            endpoint_id=endpoint_id,
            params=params,
            headers=headers,
            redact_values=redact_values,
        )
        if not isinstance(payload, dict):
            raise CaptureError("ArcGIS query response must be a JSON object")
        if "error" in payload:
            raise CaptureError(f"ArcGIS query error: {payload['error']}")
        features = payload.get("features")
        if not isinstance(features, list):
            raise CaptureError("ArcGIS query response has no features array")
        return capture, features, bool(payload.get("exceededTransferLimit"))

    def archive_layer(
        self,
        *,
        source_id: str,
        endpoint_id: str,
        service_url: str,
        layer_id: int,
        where: str = "1=1",
        out_fields: str = "*",
        request_params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        redact_values: Sequence[str] = (),
    ) -> ArcGISLayerArchive:
        validate_arcgis_request_contract(service_url, layer_id, where, out_fields)
        base = service_url.rstrip("/")
        persisted_base = redact_text(base, redact_values, replacement="REDACTED")
        common = dict(request_params or {})
        layer_url = f"{base}/{layer_id}"
        query_url = f"{layer_url}/query"
        metadata_capture, metadata = self.capture_client.capture_json(
            "GET",
            layer_url,
            source_id=source_id,
            endpoint_id=f"{endpoint_id}:layer-metadata",
            params={**common, "f": "pjson"},
            headers=headers,
            redact_values=redact_values,
        )
        if not isinstance(metadata, dict):
            raise CaptureError("ArcGIS layer metadata response must be a JSON object")
        if "error" in metadata:
            raise CaptureError(f"ArcGIS metadata error: {metadata['error']}")

        raw_object_id = metadata.get("objectIdField") or metadata.get("objectIdFieldName")
        object_id_field = str(raw_object_id) if raw_object_id else None
        effective_out_fields = _effective_out_fields(out_fields, object_id_field)
        page_size = int(metadata.get("maxRecordCount") or 1000)
        page_size = min(max(page_size, 1), 10_000)
        supports_pagination = bool(
            metadata.get("advancedQueryCapabilities", {}).get("supportsPagination", True)
        )
        count_before_capture, count_before = self._capture_count(
            source_id=source_id,
            endpoint_id=f"{endpoint_id}:count-before",
            query_url=query_url,
            common=common,
            where=where,
            headers=headers,
            redact_values=redact_values,
        )

        pages: list[CaptureResult] = []
        feature_count = 0
        object_ids_capture: CaptureResult | None = None
        seen_ids: set[int] = set()
        if supports_pagination:
            pagination_strategy = "offset"
            offset = 0
            for page_number in range(self.max_pages):
                params: dict[str, Any] = {
                    **common,
                    "f": "json",
                    "where": where,
                    "outFields": effective_out_fields,
                    "returnGeometry": "true",
                    "resultOffset": offset,
                    "resultRecordCount": page_size,
                    "returnExceededLimitFeatures": "true",
                }
                if object_id_field:
                    params["orderByFields"] = f"{object_id_field} ASC"
                capture, features, exceeded = self._capture_page(
                    source_id=source_id,
                    endpoint_id=f"{endpoint_id}:query-page-{page_number:06d}",
                    query_url=query_url,
                    params=params,
                    headers=headers,
                    redact_values=redact_values,
                )
                pages.append(capture)
                returned = len(features)
                feature_count += returned
                if object_id_field:
                    page_ids = _feature_object_ids(features, object_id_field)
                    duplicates = seen_ids.intersection(page_ids)
                    if duplicates or len(page_ids) != len(set(page_ids)):
                        raise CaptureError("ArcGIS pagination returned duplicate object IDs")
                    seen_ids.update(page_ids)
                if returned == 0 and exceeded:
                    raise CaptureError(
                        "ArcGIS returned an empty page with exceededTransferLimit=true"
                    )
                if not exceeded and returned < page_size:
                    break
                if returned == 0:
                    break
                offset += returned
            else:
                raise CaptureError(f"ArcGIS pagination exceeded max_pages={self.max_pages}")
        else:
            pagination_strategy = "object_ids"
            if not object_id_field:
                raise CaptureError(
                    "non-paginable ArcGIS layer has no object ID field for deterministic chunking"
                )
            object_ids_capture, ids_payload = self.capture_client.capture_json(
                "GET",
                query_url,
                source_id=source_id,
                endpoint_id=f"{endpoint_id}:object-ids",
                params={
                    **common,
                    "f": "json",
                    "where": where,
                    "returnIdsOnly": "true",
                },
                headers=headers,
                redact_values=redact_values,
            )
            if not isinstance(ids_payload, dict) or "error" in ids_payload:
                raise CaptureError(f"ArcGIS object-ID query failed: {ids_payload}")
            raw_ids = ids_payload.get("objectIds")
            if not isinstance(raw_ids, list):
                raise CaptureError("ArcGIS object-ID query returned no objectIds array")
            if any(isinstance(item, bool) or not isinstance(item, int) for item in raw_ids):
                raise CaptureError("ArcGIS object-ID query returned a non-integer ID")
            object_ids = sorted(raw_ids)
            if len(object_ids) != len(set(object_ids)):
                raise CaptureError("ArcGIS object-ID query returned duplicate IDs")
            if len(object_ids) != count_before:
                raise CaptureError(
                    "ArcGIS object-ID count does not match count query; the result may be "
                    "truncated or changing"
                )
            if len(object_ids) >= 1_000_000:
                raise CaptureError(
                    "ArcGIS object-ID result reached the documented one-million-ID limit"
                )
            chunks = [
                object_ids[offset : offset + page_size]
                for offset in range(0, len(object_ids), page_size)
            ]
            if not chunks:
                chunks = [[]]
            for page_number, chunk in enumerate(chunks):
                params = {
                    **common,
                    "f": "json",
                    "where": "1=0" if not chunk else where,
                    "outFields": effective_out_fields,
                    "returnGeometry": "true",
                    "returnExceededLimitFeatures": "true",
                }
                if chunk:
                    params["objectIds"] = ",".join(str(item) for item in chunk)
                    params["orderByFields"] = f"{object_id_field} ASC"
                capture, features, exceeded = self._capture_page(
                    source_id=source_id,
                    endpoint_id=f"{endpoint_id}:object-id-page-{page_number:06d}",
                    query_url=query_url,
                    params=params,
                    headers=headers,
                    redact_values=redact_values,
                )
                if exceeded:
                    raise CaptureError("ArcGIS object-ID chunk still exceeded the transfer limit")
                returned_ids = _feature_object_ids(features, object_id_field)
                if returned_ids != chunk:
                    raise CaptureError(
                        "ArcGIS object-ID chunk did not return the exact requested ID sequence"
                    )
                pages.append(capture)
                feature_count += len(features)
                seen_ids.update(returned_ids)

        count_after_capture, count_after = self._capture_count(
            source_id=source_id,
            endpoint_id=f"{endpoint_id}:count-after",
            query_url=query_url,
            common=common,
            where=where,
            headers=headers,
            redact_values=redact_values,
        )
        if count_before != count_after:
            raise CaptureError(
                f"ArcGIS source count changed during capture: {count_before} to {count_after}"
            )
        if feature_count != count_before:
            raise CaptureError(
                f"ArcGIS capture is incomplete: captured={feature_count}, expected={count_before}"
            )
        if object_id_field and len(seen_ids) != feature_count:
            raise CaptureError("ArcGIS capture object-ID reconciliation failed")

        capture_set_id = f"urn:uuid:{uuid.uuid4()}"
        manifest = {
            "schema_version": "1.1.0",
            "record_type": "arcgis_layer_capture_set",
            "capture_set_id": capture_set_id,
            "source_id": source_id,
            "service_url": persisted_base,
            "layer_id": layer_id,
            "metadata_capture_id": metadata_capture.capture_id,
            "count_capture_ids": [
                count_before_capture.capture_id,
                count_after_capture.capture_id,
            ],
            "object_ids_capture_id": (
                object_ids_capture.capture_id if object_ids_capture is not None else None
            ),
            "page_capture_ids": [capture.capture_id for capture in pages],
            "feature_count": feature_count,
            "object_id_field": object_id_field,
            "page_size": page_size,
            "pagination_strategy": pagination_strategy,
            "query": {"where": where, "out_fields": effective_out_fields},
        }
        manifest["manifest_sha256"] = sha256_json(manifest)
        safe_id = capture_set_id.removeprefix("urn:uuid:")
        manifest_path = self.capture_client.store.root / "capture-sets" / f"{safe_id}.json"
        _atomic_write(
            manifest_path,
            json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8") + b"\n",
        )
        return ArcGISLayerArchive(
            capture_set_id=capture_set_id,
            source_id=source_id,
            service_url=persisted_base,
            layer_id=layer_id,
            metadata_capture=metadata_capture,
            count_captures=(count_before_capture, count_after_capture),
            object_ids_capture=object_ids_capture,
            page_captures=tuple(pages),
            feature_count=feature_count,
            manifest_path=manifest_path,
        )
