"""Fail-closed identity and evidence contracts for planning-rule linkage."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any, Literal

from .hashing import sha256_json

LegalStatus = Literal["draft", "proposed", "operative", "superseded", "unknown"]
LinkRelation = Literal["contains", "implements", "amends", "replaces", "crosswalk"]
Confidence = Literal["unknown", "low", "medium", "high", "disputed"]


@dataclass(frozen=True)
class PlanVersion:
    """Versioned plan identity; legal effect is always an explicit field."""

    plan_id: str
    version_id: str
    title: str
    source_ref: str
    legal_status: LegalStatus = "unknown"
    valid_from: str | None = None
    valid_to: str | None = None

    def __post_init__(self) -> None:
        if not all(
            value.strip() for value in (self.plan_id, self.version_id, self.title, self.source_ref)
        ):
            raise ValueError("plan identity fields must be non-empty")
        if self.valid_from is not None:
            date.fromisoformat(self.valid_from)
        if self.valid_to is not None:
            date.fromisoformat(self.valid_to)
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to must not precede valid_from")


@dataclass(frozen=True)
class ProvisionIdentity:
    """A provision anchor retained separately from its interpretation."""

    provision_id: str
    plan_version_id: str
    chapter: str
    citation: str
    text_ref: str

    def __post_init__(self) -> None:
        if not all(
            value.strip()
            for value in (
                self.provision_id,
                self.plan_version_id,
                self.chapter,
                self.citation,
                self.text_ref,
            )
        ):
            raise ValueError("provision identity fields must be non-empty")


@dataclass(frozen=True)
class PlanningLink:
    """Evidence-bearing link whose confidence never implies legal authority."""

    link_id: str
    source_ref: str
    target_ref: str
    relation: LinkRelation
    confidence: Confidence
    evidence: tuple[str, ...]
    uncertainty: str
    review_status: Literal["unreviewed", "panel-reviewed", "accepted", "rejected"] = "unreviewed"

    def __post_init__(self) -> None:
        if not all(
            value.strip()
            for value in (self.link_id, self.source_ref, self.target_ref, self.uncertainty)
        ):
            raise ValueError("planning link identity and uncertainty must be non-empty")
        if not self.evidence or any(not item.strip() for item in self.evidence):
            raise ValueError("planning links require non-empty evidence references")

    def as_dict(self) -> dict[str, object]:
        return {
            "link_id": self.link_id,
            "source_ref": self.source_ref,
            "target_ref": self.target_ref,
            "relation": self.relation,
            "confidence": self.confidence,
            "evidence": list(self.evidence),
            "uncertainty": self.uncertainty,
            "review_status": self.review_status,
            "promotion_allowed": False,
            "nonclaims": [
                "A planning link is not a legal interpretation or authority decision.",
                "Confidence does not establish completeness or operative status.",
            ],
        }


def build_plan_source_intake(
    records: Sequence[Mapping[str, Any]], *, intake_id: str, captured_at: str
) -> dict[str, Any]:
    """Preserve declared plan documents, structure and anchors before interpretation."""
    if not intake_id.strip() or not captured_at.strip():
        raise ValueError("intake_id and captured_at must be non-empty")
    if not records:
        raise ValueError("records must be non-empty")
    required = (
        "plan_id",
        "version_id",
        "source_ref",
        "locator",
        "document_sha256",
        "structure_sha256",
        "terms_status",
        "rights_status",
    )
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, Mapping):
            raise ValueError("plan source records must be objects")
        missing = [field for field in required if not isinstance(record.get(field), str)]
        if missing:
            raise ValueError(f"plan source record missing fields: {', '.join(missing)}")
        version_id = str(record["version_id"])
        if not version_id.strip() or version_id in seen:
            raise ValueError("plan source records require unique version_id values")
        for field in ("document_sha256", "structure_sha256"):
            digest = str(record[field])
            if not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
                raise ValueError(f"{field} must be a SHA-256 hex digest")
        seen.add(version_id)
        normalized.append(dict(record))
    normalized.sort(key=lambda item: str(item["version_id"]))
    return {
        "schema_version": "1.0.0",
        "record_type": "declared-plan-source-intake",
        "intake_id": intake_id,
        "captured_at": captured_at,
        "records": normalized,
        "records_sha256": sha256_json(normalized),
        "status": "archived-declared-candidate",
        "promotion_allowed": False,
        "nonclaims": [
            (
                "The intake preserves declared document and structure anchors; it does not "
                "contact or interpret a source."
            ),
            (
                "Hashes and rights fields do not establish legal status, completeness, "
                "authority or publication permission."
            ),
        ],
    }
