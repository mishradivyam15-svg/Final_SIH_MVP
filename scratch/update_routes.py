import re

# 1. Update backend/app.py to include api_router
with open("backend/app.py", "r") as f:
    app_py = f.read()

if "api_router" not in app_py:
    app_py = app_py.replace("from backend.routes import router", "from backend.routes import router, api_router")
    app_py = app_py.replace("app.include_router(router)", "app.include_router(router)\n    app.include_router(api_router)")
    
    with open("backend/app.py", "w") as f:
        f.write(app_py)
    print("Updated app.py")

# 2. Update backend/routes.py
with open("backend/routes.py", "r") as f:
    routes_py = f.read()

# Add imports if missing
if "from backend.db" not in routes_py:
    imports = """from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from backend.db import (
    add_report, get_report, get_all_reports, update_analysis_results,
    get_dashboard_data, get_precursors, get_precursor, add_review_event,
    get_relationships_for_precursor, reports_db
)

api_router = APIRouter(prefix="/api")

class ReviewPayload(BaseModel):
    action: str
    note: Optional[str] = None
"""
    routes_py = routes_py.replace("router = APIRouter(prefix=\"/api/v1\")", imports + "\nrouter = APIRouter(prefix=\"/api/v1\")")

# Update analyze_report logic
old_analyze_body = """    try:
        result = run_full_analysis(
            narrative=report.narrative,
            report_id=report.report_id,
            timestamp=report.timestamp,
            site=report.site,
            source_type=report.source_type or "incident",
        )

        return result"""

new_analyze_body = """    try:
        if not report.report_id:
            import uuid
            report.report_id = str(uuid.uuid4())
            
        result = run_full_analysis(
            narrative=report.narrative,
            report_id=report.report_id,
            timestamp=report.timestamp,
            site=report.site,
            source_type=report.source_type or "incident",
        )

        # -----------------------------------------------------------------
        # Dynamic in-memory update for browse/detail endpoints
        # -----------------------------------------------------------------
        raw_report_dict = report.model_dump()
        add_report(raw_report_dict)
        
        # Also cache the extracted SafetyReport so GET /api/reports/:id has extraction info
        safety_rep_dict = result.safety_report.model_dump()
        reports_db[report.report_id].update(safety_rep_dict)
        
        all_raw = get_all_reports()
        if len(all_raw) >= 2:
            batch_result = run_batch_analysis(all_raw)
            update_analysis_results(
                batch_result["precursors"], 
                batch_result["relationships"]
            )
            result.relationships = batch_result["relationships"]
            result.precursors = batch_result["precursors"]

        return result"""

routes_py = routes_py.replace(old_analyze_body, new_analyze_body)

# Add new endpoints
new_endpoints = """
# -----------------------------------------------------------------
# Frontend Browse / Detail Endpoints (Mock Replacement)
# -----------------------------------------------------------------

@api_router.get("/dashboard")
def api_get_dashboard():
    return get_dashboard_data()

@api_router.get("/precursors")
def api_get_precursors(search: Optional[str] = None, priority: Optional[str] = None):
    # Simple filtering
    precursors = get_precursors()
    if priority and priority != "ALL":
        precursors = [p for p in precursors if p.get("priority") == priority]
    return precursors

@api_router.get("/precursors/{precursor_id}")
def api_get_precursor(precursor_id: str):
    p = get_precursor(precursor_id)
    if not p:
        raise HTTPException(status_code=404, detail="Precursor not found")
    return p

@api_router.get("/precursors/{precursor_id}/relationships")
def api_get_relationships(precursor_id: str):
    return get_relationships_for_precursor(precursor_id)

@api_router.get("/reports")
def api_get_reports_by_ids(ids: str):
    report_ids = [r.strip() for r in ids.split(",") if r.strip()]
    reports = []
    for rid in report_ids:
        r = get_report(rid)
        if r:
            reports.append(r)
    return reports

@api_router.get("/reports/{report_id}")
def api_get_report(report_id: str):
    r = get_report(report_id)
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    return r

@api_router.post("/precursors/{precursor_id}/review")
def api_submit_review(precursor_id: str, payload: ReviewPayload):
    p = get_precursor(precursor_id)
    if not p:
        raise HTTPException(status_code=404, detail="Precursor not found")
    return add_review_event(precursor_id, payload.action, payload.note or "")
"""

if "api_get_dashboard" not in routes_py:
    routes_py += new_endpoints

with open("backend/routes.py", "w") as f:
    f.write(routes_py)
print("Updated routes.py")
