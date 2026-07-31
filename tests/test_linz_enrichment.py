from __future__ import annotations

from riopa_provenance.linz_enrichment import build_service_queue


def test_service_queue_is_stable_and_explicit_about_owner_dispositions() -> None:
    items = [
        {
            "catalog_item_id": "urn:item:missing",
            "source_catalog_id": "missing",
            "item_type": "layer",
            "url": None,
        },
        {
            "catalog_item_id": "urn:item:table",
            "source_catalog_id": "table",
            "item_type": "table",
            "url": "https://data.linz.govt.nz/dataset/2/",
        },
        {
            "catalog_item_id": "urn:item:unknown",
            "source_catalog_id": "unknown",
            "item_type": "document",
            "url": "https://data.linz.govt.nz/dataset/3/",
        },
    ]
    jobs = build_service_queue(reversed(items))
    assert [job["catalog_item_id"] for job in jobs] == [
        "urn:item:missing",
        "urn:item:table",
        "urn:item:unknown",
    ]
    assert jobs[0]["disposition"] == "service-list-unavailable"
    assert jobs[0]["blocked_reason"]
    assert jobs[1]["disposition"] == "capture-service-list"
    assert jobs[1]["url"].endswith("/services/")
    assert jobs[2]["disposition"] == "not-a-service-owner"
    assert jobs[2]["url"] is None
    assert jobs == build_service_queue(items)
