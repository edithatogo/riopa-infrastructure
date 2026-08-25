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
PlanningFeatureKind = Literal["zone", "overlay", "precinct", "designation"]


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


def build_provision_extraction_record(
    *,
    provision_id: str,
    source_ref: str,
    text_sha256: str,
    input_sha256: str,
    method: Literal["structured", "manual", "ai-assisted"],
    extracted_fields: Mapping[str, Any],
    uncertainty: str,
    tool_identity: str | None = None,
) -> dict[str, Any]:
    """Record a provenance-bearing extraction without interpreting legal meaning."""
    if not provision_id.strip() or not source_ref.strip() or not uncertainty.strip():
        raise ValueError("provision_id, source_ref and uncertainty must be non-empty")
    for field, digest in (("text_sha256", text_sha256), ("input_sha256", input_sha256)):
        if not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            raise ValueError(f"{field} must be a SHA-256 hex digest")
    if not extracted_fields:
        raise ValueError("extracted_fields must be non-empty")
    if method == "ai-assisted" and not tool_identity:
        raise ValueError("ai-assisted extraction requires tool_identity")
    return {
        "record_type": "planning-provision-extraction",
        "provision_id": provision_id,
        "source_ref": source_ref,
        "text_sha256": text_sha256.lower(),
        "input_sha256": input_sha256.lower(),
        "method": method,
        "tool_identity": tool_identity,
        "extracted_fields": dict(extracted_fields),
        "uncertainty": uncertainty,
        "review_status": "unreviewed",
        "promotion_allowed": False,
        "nonclaims": [
            (
                "The record preserves an extraction method and hashes; it is not a legal "
                "interpretation."
            ),
            "Unreviewed extraction does not establish operative status, authority or completeness.",
        ],
    }


def build_feature_provision_linkage(
    features: Sequence[Mapping[str, Any]],
    *,
    linkage_id: str,
    captured_at: str,
) -> dict[str, Any]:
    """Build a bounded feature-to-provision linkage packet.

    The packet records declared feature and provision references only. It does
    not fetch, interpret or assert the legal effect of a plan.
    """
    if not linkage_id.strip() or not captured_at.strip():
        raise ValueError("linkage_id and captured_at must be non-empty")
    if not features:
        raise ValueError("features must be non-empty")
    allowed_kinds = {"zone", "overlay", "precinct", "designation"}
    required = (
        "feature_id",
        "feature_kind",
        "feature_source_ref",
        "provision_version_id",
        "evidence",
        "confidence",
    )
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for feature in features:
        if not isinstance(feature, Mapping):
            raise ValueError("feature linkage records must be objects")
        missing = [field for field in required if field not in feature]
        if missing:
            raise ValueError(f"feature linkage record missing fields: {', '.join(missing)}")
        feature_id = feature["feature_id"]
        if not isinstance(feature_id, str) or not feature_id.strip() or feature_id in seen:
            raise ValueError("feature_id values must be unique non-empty strings")
        feature_kind = feature["feature_kind"]
        if feature_kind not in allowed_kinds:
            raise ValueError("feature_kind must be zone, overlay, precinct or designation")
        source_ref = feature["feature_source_ref"]
        provision_version_id = feature["provision_version_id"]
        if not isinstance(source_ref, str) or not source_ref.strip():
            raise ValueError("feature_source_ref must be a non-empty string")
        if not isinstance(provision_version_id, str) or not provision_version_id.strip():
            raise ValueError("provision_version_id must be a non-empty string")
        evidence = feature["evidence"]
        if not isinstance(evidence, Sequence) or isinstance(evidence, (str, bytes)) or not evidence:
            raise ValueError("feature linkage evidence must be a non-empty sequence")
        if any(not isinstance(item, str) or not item.strip() for item in evidence):
            raise ValueError("feature linkage evidence entries must be non-empty strings")
        confidence = feature["confidence"]
        if confidence not in {"unknown", "low", "medium", "high", "disputed"}:
            raise ValueError("feature linkage confidence is invalid")
        seen.add(feature_id)
        normalized.append(
            {
                "feature_id": feature_id,
                "feature_kind": feature_kind,
                "feature_source_ref": source_ref,
                "provision_version_id": provision_version_id,
                "evidence": sorted(set(evidence)),
                "confidence": confidence,
                "review_status": "unreviewed",
                "resolution": "declared-reference-only",
            }
        )
    normalized.sort(key=lambda item: str(item["feature_id"]))
    return {
        "record_type": "planning-feature-provision-linkage",
        "linkage_id": linkage_id,
        "captured_at": captured_at,
        "records": normalized,
        "records_sha256": sha256_json(normalized),
        "status": "bounded-unreviewed",
        "promotion_allowed": False,
        "nonclaims": [
            "Feature references do not establish zoning, legal or operative status.",
            "Unreviewed links do not establish completeness, authority or enforceability.",
        ],
    }


def build_rule_structure_record(
    provisions: Sequence[Mapping[str, Any]],
    *,
    structure_id: str,
    captured_at: str,
) -> dict[str, Any]:
    """Preserve rule hierarchy and exception references without interpretation."""
    if not structure_id.strip() or not captured_at.strip():
        raise ValueError("structure_id and captured_at must be non-empty")
    if not provisions:
        raise ValueError("provisions must be non-empty")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for provision in provisions:
        if not isinstance(provision, Mapping):
            raise ValueError("rule structure records must be objects")
        provision_id = provision.get("provision_id")
        if not isinstance(provision_id, str) or not provision_id.strip() or provision_id in seen:
            raise ValueError("provision_id values must be unique non-empty strings")
        parent = provision.get("parent_provision_id")
        if parent is not None and (not isinstance(parent, str) or not parent.strip()):
            raise ValueError("parent_provision_id must be a non-empty string when present")
        if parent == provision_id:
            raise ValueError("a provision cannot be its own parent")
        values = {
            name: provision.get(name, ())
            for name in ("exception_refs", "combined_with", "unresolved_reasons")
        }
        for name, entries in values.items():
            if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)):
                raise ValueError(f"{name} must be a sequence")
            if any(not isinstance(item, str) or not item.strip() for item in entries):
                raise ValueError(f"{name} entries must be non-empty strings")
        seen.add(provision_id)
        normalized.append(
            {
                "provision_id": provision_id,
                "parent_provision_id": parent,
                "exception_refs": sorted(set(values["exception_refs"])),
                "combined_with": sorted(set(values["combined_with"])),
                "unresolved_reasons": sorted(set(values["unresolved_reasons"])),
                "resolution_status": "unresolved"
                if values["unresolved_reasons"]
                else "declared-structure",
            }
        )
    normalized.sort(key=lambda item: str(item["provision_id"]))
    return {
        "record_type": "planning-rule-structure",
        "structure_id": structure_id,
        "captured_at": captured_at,
        "records": normalized,
        "records_sha256": sha256_json(normalized),
        "status": "bounded-structure-only",
        "promotion_allowed": False,
        "nonclaims": [
            "Hierarchy and exception references do not establish legal effect or precedence.",
            "Unresolved states are retained and are not treated as negative evidence.",
        ],
    }


def build_planning_concept_crosswalk(
    concepts: Sequence[Mapping[str, Any]],
    *,
    crosswalk_id: str,
    captured_at: str,
) -> dict[str, Any]:
    """Build a batch of original-to-canonical planning concept mappings."""
    if not crosswalk_id.strip() or not captured_at.strip():
        raise ValueError("crosswalk_id and captured_at must be non-empty")
    if not concepts:
        raise ValueError("concepts must be non-empty")
    from .canonical import build_crosswalk, validate_crosswalk_contract

    required = (
        "source_id",
        "source_label",
        "canonical_id",
        "method",
        "confidence",
        "reviewer",
        "valid_from",
    )
    records: list[dict[str, Any]] = []
    for concept in concepts:
        if not isinstance(concept, Mapping):
            raise ValueError("planning concept records must be objects")
        missing = [field for field in required if field not in concept]
        if missing:
            raise ValueError(f"planning concept record missing fields: {', '.join(missing)}")
        for field in required:
            if not isinstance(concept[field], str) or not concept[field].strip():
                raise ValueError(f"planning concept field must be a non-empty string: {field}")
        evidence = concept.get("evidence", [])
        if not isinstance(evidence, list) or any(
            not isinstance(item, str) or not item.strip() for item in evidence
        ):
            raise ValueError("planning concept evidence must be a list of non-empty strings")
        record = build_crosswalk(
            source_id=concept["source_id"],
            source_label=concept["source_label"],
            canonical_id=concept["canonical_id"],
            method=concept["method"],
            confidence=concept["confidence"],
            reviewer=concept["reviewer"],
            valid_from=concept["valid_from"],
            valid_to=concept.get("valid_to"),
            evidence=evidence,
        )
        errors = validate_crosswalk_contract(record)
        if errors:
            raise ValueError("invalid planning concept crosswalk: " + "; ".join(errors))
        records.append(record)
    records.sort(key=lambda item: str(item["mapping_id"]))
    return {
        "record_type": "planning-concept-crosswalk",
        "crosswalk_id": crosswalk_id,
        "captured_at": captured_at,
        "records": records,
        "records_sha256": sha256_json(records),
        "status": "bounded-unreviewed",
        "promotion_allowed": False,
        "nonclaims": [
            "Mappings preserve original assertions but do not establish semantic equivalence.",
            "Unreviewed crosswalks do not establish legal effect, completeness or authority.",
        ],
    }


def build_planning_feasibility_record(
    rules: Sequence[Mapping[str, Any]],
    *,
    query_id: str,
    feature_ref: str,
    captured_at: str,
) -> dict[str, Any]:
    """Return cited rule statuses without reducing them to legal advice."""
    if not query_id.strip() or not feature_ref.strip() or not captured_at.strip():
        raise ValueError("query_id, feature_ref and captured_at must be non-empty")
    if not rules:
        raise ValueError("rules must be non-empty")
    allowed_statuses = {"permitted", "discretionary", "prohibited", "unresolved"}
    allowed_confidence = {"unknown", "low", "medium", "high", "disputed"}
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for rule in rules:
        if not isinstance(rule, Mapping):
            raise ValueError("feasibility rules must be objects")
        required = ("provision_id", "status", "confidence", "evidence", "caveats")
        missing = [field for field in required if field not in rule]
        if missing:
            raise ValueError(f"feasibility rule missing fields: {', '.join(missing)}")
        provision_id = rule["provision_id"]
        if not isinstance(provision_id, str) or not provision_id.strip() or provision_id in seen:
            raise ValueError("provision_id values must be unique non-empty strings")
        status = rule["status"]
        if status not in allowed_statuses:
            raise ValueError("feasibility status is invalid")
        confidence = rule["confidence"]
        if confidence not in allowed_confidence:
            raise ValueError("feasibility confidence is invalid")
        for field in ("evidence", "caveats"):
            values = rule[field]
            if not isinstance(values, list) or any(
                not isinstance(item, str) or not item.strip() for item in values
            ):
                raise ValueError(f"feasibility {field} must be a list of non-empty strings")
        if not rule["evidence"]:
            raise ValueError("feasibility evidence must not be empty")
        seen.add(provision_id)
        normalized.append(
            {
                "provision_id": provision_id,
                "status": status,
                "confidence": confidence,
                "evidence": sorted(set(rule["evidence"])),
                "caveats": sorted(set(rule["caveats"])),
            }
        )
    normalized.sort(key=lambda item: str(item["provision_id"]))
    statuses = {str(item["status"]) for item in normalized}
    if "unresolved" in statuses or ("prohibited" in statuses and statuses - {"prohibited"}):
        decision_status = "unresolved"
    elif "prohibited" in statuses:
        decision_status = "prohibited"
    elif "discretionary" in statuses:
        decision_status = "discretionary"
    else:
        decision_status = "permitted"
    return {
        "record_type": "planning-feasibility-query",
        "query_id": query_id,
        "feature_ref": feature_ref,
        "captured_at": captured_at,
        "rules": normalized,
        "rules_sha256": sha256_json(normalized),
        "decision_status": decision_status,
        "authority_required": True,
        "status": "bounded-cited-reference",
        "promotion_allowed": False,
        "nonclaims": [
            "The status is a cited reference result, not legal advice or a consent decision.",
            "Conflicting or unresolved rules are not silently collapsed into permission.",
        ],
    }


def build_planning_linkage_error_report(
    *,
    source_intake: Mapping[str, Any],
    structure: Mapping[str, Any],
    linkage: Mapping[str, Any],
    crosswalk: Mapping[str, Any],
    feasibility: Mapping[str, Any],
) -> dict[str, Any]:
    """Quantify unresolved references across one bounded planning packet.

    This report compares identifiers already present in caller-supplied packets;
    it never repairs, infers or promotes a planning link.  Missing references
    remain explicit so a later source-faithful review can resolve them.
    """

    packets = {
        "source_intake": (source_intake, "declared-plan-source-intake", "records"),
        "structure": (structure, "planning-rule-structure", "records"),
        "linkage": (linkage, "planning-feature-provision-linkage", "records"),
        "crosswalk": (crosswalk, "planning-concept-crosswalk", "records"),
        "feasibility": (feasibility, "planning-feasibility-query", "rules"),
    }
    for name, (packet, record_type, field) in packets.items():
        if packet.get("record_type") != record_type:
            raise ValueError(f"{name} has unexpected record_type")
        if not isinstance(packet.get(field), list):
            raise ValueError(f"{name}.{field} must be a list")

    source_versions = {
        str(item["version_id"])
        for item in source_intake["records"]
        if isinstance(item, Mapping) and isinstance(item.get("version_id"), str)
    }
    provision_ids = {
        str(item["provision_id"])
        for item in structure["records"]
        if isinstance(item, Mapping) and isinstance(item.get("provision_id"), str)
    }
    feature_ids = {
        str(item["feature_id"])
        for item in linkage["records"]
        if isinstance(item, Mapping) and isinstance(item.get("feature_id"), str)
    }
    missing_link_targets = sorted(
        str(item.get("provision_version_id"))
        for item in linkage["records"]
        if isinstance(item, Mapping) and item.get("provision_version_id") not in source_versions
    )
    unlinked_crosswalk_sources = sorted(
        str(
            item.get("source_assertion", {}).get("source_id")
            if isinstance(item.get("source_assertion"), Mapping)
            else None
        )
        for item in crosswalk["records"]
        if isinstance(item, Mapping)
        and (
            not isinstance(item.get("source_assertion"), Mapping)
            or item["source_assertion"].get("source_id") not in feature_ids
        )
    )
    missing_feasibility_provisions = sorted(
        str(item.get("provision_id"))
        for item in feasibility["rules"]
        if isinstance(item, Mapping) and item.get("provision_id") not in provision_ids
    )
    findings = {
        "missing_link_targets": missing_link_targets,
        "unlinked_crosswalk_sources": unlinked_crosswalk_sources,
        "missing_feasibility_provisions": missing_feasibility_provisions,
    }
    return {
        "record_type": "planning-linkage-error-report",
        "packet_record_counts": {
            name: len(packet[field]) for name, (packet, _, field) in packets.items()
        },
        "findings": findings,
        "finding_counts": {name: len(values) for name, values in findings.items()},
        "total_finding_count": sum(len(values) for values in findings.values()),
        "scope": "caller-supplied bounded planning packets",
        "status": "quantified-unresolved" if any(findings.values()) else "no-unresolved-references",
        "promotion_allowed": False,
        "nonclaims": [
            "The report quantifies identifier mismatches; it does not repair or infer links.",
            (
                "Zero findings in a synthetic packet do not establish council completeness "
                "or legal authority."
            ),
        ],
        "report_sha256": sha256_json(findings),
    }
