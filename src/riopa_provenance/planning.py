"""Fail-closed identity and evidence contracts for planning-rule linkage."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

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
