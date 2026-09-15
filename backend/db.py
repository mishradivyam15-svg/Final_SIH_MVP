from __future__ import annotations

import datetime
from typing import Any
import uuid

# In-memory storage for the current session.
reports_db: dict[str, dict] = {}
precursors_db: dict[str, dict] = {}
relationships_db: list[dict] = []
review_history_db: dict[str, list[dict]] = {}

def add_report(report: dict) -> None:
    report_id = report.get("report_id")
    if report_id:
        # Give it a date if missing so frontend displays it nicely
        if not report.get("timestamp") and not report.get("date"):
            report["timestamp"] = datetime.datetime.now().isoformat()
        reports_db[report_id] = report

def get_report(report_id: str) -> dict | None:
    return reports_db.get(report_id)

def get_all_reports() -> list[dict]:
    return list(reports_db.values())

def update_analysis_results(precursors: list[dict], relationships: list[dict]) -> None:
    global relationships_db
    relationships_db = relationships

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

        if pid in precursors_db:
            # Preserve existing review status/history
            frontend_p["status"] = precursors_db[pid].get("status", "OPEN")
            frontend_p["created_at"] = precursors_db[pid].get("created_at")
            frontend_p["review_history"] = review_history_db.get(pid, [])
        else:
            frontend_p["review_history"] = []

        precursors_db[pid] = frontend_p

def get_dashboard_data() -> dict:
    precursors = list(precursors_db.values())
    
    # Sort by risk score descending
    precursors.sort(key=lambda x: x.get("risk_score", 0), reverse=True)
    
    high_priority = [p for p in precursors if p.get("priority") == "HIGH"]
    review_queue = [p for p in precursors if p.get("status") in ("OPEN", "UNDER_INVESTIGATION")]
    
    top_precursor = high_priority[0] if high_priority else (precursors[0] if precursors else None)
    
    return {
        "overview": {
            "reports_analyzed": len(reports_db),
            "precursor_pattern_count": len(precursors_db),
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
    return list(precursors_db.values())

def get_precursor(precursor_id: str) -> dict | None:
    p = precursors_db.get(precursor_id)
    if p:
        p["review_history"] = review_history_db.get(precursor_id, [])
    return p

def add_review_event(precursor_id: str, action: str, note: str = "") -> dict:
    event = {
        "id": str(uuid.uuid4()),
        "action": action,
        "note": note,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    if precursor_id not in review_history_db:
        review_history_db[precursor_id] = []
    
    review_history_db[precursor_id].append(event)
    
    if precursor_id in precursors_db:
        if action == "CONFIRM":
            precursors_db[precursor_id]["status"] = "CONFIRMED"
        elif action == "DISMISS":
            precursors_db[precursor_id]["status"] = "DISMISSED"
        elif action == "INVESTIGATE":
            precursors_db[precursor_id]["status"] = "UNDER_INVESTIGATION"
            
        precursors_db[precursor_id]["updated_at"] = event["timestamp"]
        
    return event

def get_relationships_for_precursor(precursor_id: str) -> dict:
    p = precursors_db.get(precursor_id)
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
        r = reports_db.get(rid)
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
    for rel in relationships_db:
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
