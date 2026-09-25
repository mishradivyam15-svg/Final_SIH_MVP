from __future__ import annotations

import datetime
import uuid

from backend.database import get_db

# Documents are stored with their natural id (report_id / precursor_id) as
# Mongo's _id, so upserts are a single indexed write with no extra unique
# index needed. Every read projects _id out — the original in-memory dicts
# never had that key, and callers (Pydantic schemas, the frontend
# normalizers) don't expect it.
_NO_ID = {"_id": 0}

# The relationship list is a single global snapshot (replaced wholesale on
# every analysis run, same as the old module-level list), so it lives in
# one fixed document rather than a full collection.
_RELATIONSHIPS_DOC_ID = "current"


def _reports():
    return get_db().reports


def _precursors():
    return get_db().precursors


def _relationships():
    return get_db().relationships


def _review_history():
    return get_db().review_history


def add_report(report: dict) -> None:
    report_id = report.get("report_id")
    if not report_id:
        return
    # Give it a date if missing so frontend displays it nicely
    if not report.get("timestamp") and not report.get("date"):
        report["timestamp"] = datetime.datetime.now().isoformat()
    doc = {**report, "_id": report_id}
    _reports().replace_one({"_id": report_id}, doc, upsert=True)


def update_report(report_id: str, updates: dict) -> None:
    """Merge fields into an already-stored report (e.g. extraction results
    computed after the initial submission)."""
    _reports().update_one({"_id": report_id}, {"$set": updates})


def get_report(report_id: str) -> dict | None:
    return _reports().find_one({"_id": report_id}, _NO_ID)


def get_all_reports() -> list[dict]:
    return list(_reports().find({}, _NO_ID))


def update_analysis_results(precursors: list[dict], relationships: list[dict]) -> None:
    _relationships().replace_one(
        {"_id": _RELATIONSHIPS_DOC_ID},
        {"_id": _RELATIONSHIPS_DOC_ID, "items": relationships},
        upsert=True,
    )

    precursor_coll = _precursors()

    # Update precursors while preserving review history
    for p in precursors:
        pid = p["precursor_id"]
        # AI-2 always creates new precursors with review_status
        # "pending_review" — translate that to the dashboard's "OPEN"
        # vocabulary. Without this, p.get("review_status", "OPEN") never
        # falls back to "OPEN" (the key is always present), so freshly
        # created precursors never matched the review-queue filter below.
        raw_status = p.get("review_status", "pending_review")
        # Convert schema names to frontend expected names
        frontend_p = {
            "precursor_id": pid,
            "title": p.get("title", "Untitled Precursor"),
            "priority": p.get("priority", "LOW"),
            "risk_score": p.get("priority_score", 0),
            "status": "OPEN" if raw_status == "pending_review" else raw_status,
            "hazard": p.get("common_hazard", "Unknown"),
            "barrier_failure": p.get("common_barrier_failure", "Unknown"),
            "iogp_life_saving_rule": p.get("common_iogp_life_saving_rule"),
            "sif_potential": p.get("sif_potential"),
            "report_ids": p.get("report_ids", []),
            "evidence": {
                "summary_points": p.get("evidence", [])
            },
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
        }

        existing = precursor_coll.find_one({"_id": pid}, _NO_ID)
        if existing:
            # Preserve existing review status/history
            frontend_p["status"] = existing.get("status", "OPEN")
            frontend_p["created_at"] = existing.get("created_at")
            history_doc = _review_history().find_one({"_id": pid}, _NO_ID)
            frontend_p["review_history"] = history_doc.get("events", []) if history_doc else []
        else:
            frontend_p["review_history"] = []

        precursor_coll.replace_one({"_id": pid}, {**frontend_p, "_id": pid}, upsert=True)


def get_dashboard_data() -> dict:
    precursors = list(_precursors().find({}, _NO_ID))

    # Sort by risk score descending
    precursors.sort(key=lambda x: x.get("risk_score", 0), reverse=True)

    high_priority = [p for p in precursors if p.get("priority") == "HIGH"]
    review_queue = [p for p in precursors if p.get("status") in ("OPEN", "UNDER_INVESTIGATION")]

    top_precursor = high_priority[0] if high_priority else (precursors[0] if precursors else None)

    return {
        "overview": {
            "reports_analyzed": _reports().count_documents({}),
            "precursor_pattern_count": _precursors().count_documents({}),
            "high_priority_count": len(high_priority),
            "review_queue_count": len(review_queue),
            "last_updated": datetime.datetime.now().isoformat(),
        },
        "top_precursor": top_precursor,
        "precursors": precursors,
        "review_queue": review_queue,
        "is_demo_data": False
    }


def get_precursors() -> list[dict]:
    return list(_precursors().find({}, _NO_ID))


def get_precursor(precursor_id: str) -> dict | None:
    p = _precursors().find_one({"_id": precursor_id}, _NO_ID)
    if p:
        history_doc = _review_history().find_one({"_id": precursor_id}, _NO_ID)
        p["review_history"] = history_doc.get("events", []) if history_doc else []
    return p


def add_review_event(precursor_id: str, action: str, note: str = "") -> dict:
    event = {
        "id": str(uuid.uuid4()),
        "action": action,
        "note": note,
        "timestamp": datetime.datetime.now().isoformat()
    }

    _review_history().update_one(
        {"_id": precursor_id},
        {"$push": {"events": event}, "$setOnInsert": {"_id": precursor_id}},
        upsert=True,
    )

    status_by_action = {
        "CONFIRM": "CONFIRMED",
        "DISMISS": "DISMISSED",
        "INVESTIGATE": "UNDER_INVESTIGATION",
    }
    new_status = status_by_action.get(action)
    if new_status:
        _precursors().update_one(
            {"_id": precursor_id},
            {"$set": {"status": new_status, "updated_at": event["timestamp"]}},
        )

    return event


def get_relationships_for_precursor(precursor_id: str) -> dict:
    p = _precursors().find_one({"_id": precursor_id}, _NO_ID)
    if not p:
        return {"nodes": [], "edges": []}

    report_ids = set(p.get("report_ids", []))
    nodes = []

    # Add precursor node
    nodes.append({
        "id": precursor_id,
        "type": "precursor",
        "label": p.get("title", "Precursor"),
    })

    # Add report nodes
    for rid in report_ids:
        r = _reports().find_one({"_id": rid}, _NO_ID)
        if r:
            nodes.append({
                "id": rid,
                "type": "report",
                "label": f"Report #{rid}",
            })

    edges = []

    # Connect precursor to reports
    for rid in report_ids:
        edges.append({
            "id": f"edge-{precursor_id}-{rid}",
            "source": precursor_id,
            "target": rid,
            "relationship": "part_of",
            "strength": 1.0
        })

    # Add relationships between reports in this precursor
    relationships_doc = _relationships().find_one({"_id": _RELATIONSHIPS_DOC_ID}, _NO_ID)
    relationships_list = relationships_doc.get("items", []) if relationships_doc else []
    for rel in relationships_list:
        src = rel.get("source_report_id")
        tgt = rel.get("target_report_id")
        if src in report_ids and tgt in report_ids:
            edges.append({
                "id": f"edge-{src}-{tgt}",
                "source": src,
                "target": tgt,
                "relationship": "semantic_similarity",
                "strength": rel.get("relationship_strength", 0.0)
            })

    return {"nodes": nodes, "edges": edges}
