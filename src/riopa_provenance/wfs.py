"""Faithful, deterministic WFS 2.0 feature-type archival."""

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
class WFSFeatureTypeArchive:
    capture_set_id: str
    source_id: str
    service_url: str
    type_name: str
    capabilities_capture: CaptureResult
    schema_capture: CaptureResult
    page_captures: tuple[CaptureResult, ...]
    feature_count: int
    manifest_path: Path


def validate_wfs_request_contract(service_url: str, type_name: str, version: str) -> None:
    """Reject unsafe or ambiguous WFS requests before network capture."""

    parsed = urlsplit(service_url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise CaptureError("WFS service URL must be an HTTPS URL without userinfo")
    if not type_name.strip() or any(char in type_name for char in "\r\n\x00"):
        raise CaptureError("WFS type_name must be a non-empty single-line value")
    if version != "2.0.0":
        raise ValueError("the hardened archiver currently supports WFS 2.0.0 only")


class WFSFeatureTypeArchiver:
    """Archive capabilities, schema, and complete GeoJSON feature pages."""

    def __init__(self, capture_client: HttpCaptureClient, *, max_pages: int = 100_000) -> None:
        if max_pages < 1:
            raise ValueError("max_pages must be positive")
        self.capture_client = capture_client
        self.max_pages = max_pages

    def archive_feature_type(
        self,
        *,
        source_id: str,
        endpoint_id: str,
        service_url: str,
        type_name: str,
        page_size: int = 1000,
        sort_by: str | None = None,
        id_property: str | None = None,
        srs_name: str | None = None,
        cql_filter: str | None = None,
        version: str = "2.0.0",
        request_params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        redact_values: Sequence[str] = (),
    ) -> WFSFeatureTypeArchive:
        validate_wfs_request_contract(service_url, type_name, version)
        if page_size < 1 or page_size > 100_000:
            raise ValueError("page_size must be between 1 and 100000")

        common = dict(request_params or {})
        persisted_service_url = redact_text(service_url, redact_values, replacement="REDACTED")
        capabilities_capture = self.capture_client.capture(
            "GET",
            service_url,
            source_id=source_id,
            endpoint_id=f"{endpoint_id}:get-capabilities",
            params={**common, "service": "WFS", "version": version, "request": "GetCapabilities"},
            headers=headers,
            redact_values=redact_values,
        )
        schema_capture = self.capture_client.capture(
            "GET",
            service_url,
            source_id=source_id,
            endpoint_id=f"{endpoint_id}:describe-feature-type",
            params={
                **common,
                "service": "WFS",
                "version": version,
                "request": "DescribeFeatureType",
                "typeNames": type_name,
            },
            headers=headers,
            redact_values=redact_values,
        )

        pages: list[CaptureResult] = []
        feature_count = 0
        start_index = 0
        seen_page_hashes: set[str] = set()
        seen_feature_ids: set[str] = set()
        declared_total: int | None = None
        for page_number in range(self.max_pages):
            params: dict[str, Any] = {
                **common,
                "service": "WFS",
                "version": version,
                "request": "GetFeature",
                "typeNames": type_name,
                "outputFormat": "application/json",
                "count": page_size,
                "startIndex": start_index,
            }
            if sort_by:
                params["sortBy"] = sort_by
            if srs_name:
                params["srsName"] = srs_name
            if cql_filter:
                params["CQL_FILTER"] = cql_filter
            capture, payload = self.capture_client.capture_json(
                "GET",
                service_url,
                source_id=source_id,
                endpoint_id=f"{endpoint_id}:get-feature-page-{page_number:06d}",
                params=params,
                headers=headers,
                redact_values=redact_values,
            )
            if not isinstance(payload, dict) or payload.get("type") != "FeatureCollection":
                raise CaptureError("WFS GetFeature response must be a GeoJSON FeatureCollection")
            features = payload.get("features")
            if not isinstance(features, list):
                raise CaptureError("WFS GeoJSON response has no features array")
            returned = len(features)
            if returned == page_size and not sort_by:
                raise CaptureError("multi-page WFS capture requires sort_by for stable pagination")
            if (
                returned == page_size
                and not id_property
                and any(feature.get("id") is None for feature in features)
            ):
                raise CaptureError(
                    "multi-page WFS capture requires GeoJSON feature IDs or id_property"
                )
            for feature in features:
                if not isinstance(feature, dict):
                    raise CaptureError("WFS features array contains a non-object value")
                feature_id = feature.get("id")
                if feature_id is None and id_property:
                    properties = feature.get("properties") or {}
                    feature_id = (
                        properties.get(id_property) if isinstance(properties, dict) else None
                    )
                if feature_id is not None:
                    rendered_id = str(feature_id)
                    if rendered_id in seen_feature_ids:
                        raise CaptureError(
                            f"duplicate WFS feature identity across pages: {rendered_id}"
                        )
                    seen_feature_ids.add(rendered_id)
            if capture.object_sha256 in seen_page_hashes and features:
                raise CaptureError(
                    "WFS returned a repeated non-empty page; startIndex may be ignored"
                )
            seen_page_hashes.add(capture.object_sha256)
            pages.append(capture)
            feature_count += returned
            number_matched = payload.get("numberMatched")
            if isinstance(number_matched, int):
                declared_total = number_matched
            elif isinstance(number_matched, str) and number_matched.isdigit():
                declared_total = int(number_matched)
            if declared_total is not None and feature_count > declared_total:
                raise CaptureError(
                    f"captured {feature_count} WFS features but numberMatched={declared_total}"
                )
            if returned < page_size or (
                declared_total is not None and feature_count == declared_total
            ):
                break
            start_index += returned
        else:
            raise CaptureError(f"WFS pagination exceeded max_pages={self.max_pages}")

        if declared_total is not None and feature_count != declared_total:
            raise CaptureError(
                f"captured {feature_count} WFS features but numberMatched={declared_total}"
            )
        capture_set_id = f"urn:uuid:{uuid.uuid4()}"
        manifest = {
            "schema_version": "1.0.0",
            "record_type": "wfs_feature_type_capture_set",
            "capture_set_id": capture_set_id,
            "source_id": source_id,
            "service_url": persisted_service_url,
            "version": version,
            "type_name": type_name,
            "capabilities_capture_id": capabilities_capture.capture_id,
            "schema_capture_id": schema_capture.capture_id,
            "page_capture_ids": [item.capture_id for item in pages],
            "feature_count": feature_count,
            "declared_feature_count": declared_total,
            "page_size": page_size,
            "sort_by": sort_by,
            "id_property": id_property,
            "srs_name": srs_name,
            "filter": cql_filter,
            "manifest_sha256": "",
        }
        manifest["manifest_sha256"] = sha256_json(manifest, omit_keys={"manifest_sha256"})
        safe_id = capture_set_id.removeprefix("urn:uuid:")
        manifest_path = self.capture_client.store.root / "capture-sets" / f"{safe_id}.json"
        _atomic_write(
            manifest_path,
            json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8") + b"\n",
        )
        return WFSFeatureTypeArchive(
            capture_set_id=capture_set_id,
            source_id=source_id,
            service_url=persisted_service_url,
            type_name=type_name,
            capabilities_capture=capabilities_capture,
            schema_capture=schema_capture,
            page_captures=tuple(pages),
            feature_count=feature_count,
            manifest_path=manifest_path,
        )
