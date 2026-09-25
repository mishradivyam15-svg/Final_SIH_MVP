"""
API routes for the SIF Precursor backend.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.schemas import (
    AnalysisResponse,
    BatchAnalysisResponse,
    BatchReportInput,
    ReportInput,
    SafetyReport,
)

from backend.pipeline import (
    run_batch_analysis,
    run_extraction,
    run_full_analysis,
)


from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from backend.db import (
    add_report, update_report, get_report, get_all_reports, update_analysis_results,
    get_dashboard_data, get_precursors, get_precursor, add_review_event,
    get_relationships_for_precursor
)

api_router = APIRouter(prefix="/api")

class ReviewPayload(BaseModel):
    action: str
    note: Optional[str] = None

router = APIRouter(prefix="/api/v1")


# -----------------------------------------------------------------
# Health check
# -----------------------------------------------------------------

@router.get(
    "/health",
    summary="Health check",
    tags=["system"],
)
def health_check():
    """Return a simple health-check response."""
    return {"status": "healthy"}


# -----------------------------------------------------------------
# Full analysis - single report
# -----------------------------------------------------------------

@router.post(
    "/reports/analyze",
    response_model=AnalysisResponse,
    summary="Analyze a safety report (full pipeline)",
    tags=["reports"],
    status_code=status.HTTP_200_OK,
)
def analyze_report(report: ReportInput):
    """
    Accept a raw safety / near-miss report and run the full analysis
    pipeline.

    Pipeline steps:
        1. Preprocessing
        2. Extraction v1
        3. AI-2 integration interface

    Note:
        Relationship and precursor analysis requires multiple reports,
        so cross-report AI-2 results are handled by /reports/analyze-batch.
    """
    try:
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
        # Persist for browse/detail endpoints
        # -----------------------------------------------------------------
        raw_report_dict = report.model_dump()
        add_report(raw_report_dict)
        
        # Also cache the extracted SafetyReport so GET /api/reports/:id has extraction info
        safety_rep_dict = result.safety_report.model_dump()
        update_report(report.report_id, safety_rep_dict)
        
        all_raw = get_all_reports()
        if len(all_raw) >= 2:
            batch_result = run_batch_analysis(all_raw)
            update_analysis_results(
                batch_result["precursors"], 
                batch_result["relationships"]
            )
            result.relationships = batch_result["relationships"]
            result.precursors = batch_result["precursors"]

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline error: {exc}",
        ) from exc


# -----------------------------------------------------------------
# Batch analysis - AI-2 relationship and precursor analysis
# -----------------------------------------------------------------

@router.post(
    "/reports/analyze-batch",
    response_model=BatchAnalysisResponse,
    summary="Analyze multiple safety reports with AI-2",
    tags=["reports"],
    status_code=status.HTTP_200_OK,
)
def analyze_reports_batch(batch: BatchReportInput):
    """
    Accept multiple safety / near-miss reports and run the complete
    cross-report AI pipeline.

    Pipeline steps:
        1. Preprocessing
        2. Extraction v1
        3. Relationship detection
        4. Relationship graph construction
        5. Precursor grouping
        6. Precursor prioritization

    Returns:
        - Structured safety reports
        - Relationships between reports
        - Detected precursor groups
        - Pipeline version
    """
    try:
        result = run_batch_analysis(
            [report.model_dump() for report in batch.reports]
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch analysis error: {exc}",
        ) from exc


# -----------------------------------------------------------------
# Extraction only
# -----------------------------------------------------------------

@router.post(
    "/reports/extract",
    response_model=SafetyReport,
    summary="Extract safety signals (extraction only)",
    tags=["reports"],
    status_code=status.HTTP_200_OK,
)
def extract_report(report: ReportInput):
    """
    Accept a raw safety / near-miss report and run Extraction v1
    only.

    Returns the structured SafetyReport.
    """
    try:
        result = run_extraction(
            narrative=report.narrative,
            report_id=report.report_id,
            timestamp=report.timestamp,
            site=report.site,
            source_type=report.source_type or "incident",
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction error: {exc}",
        ) from exc


# -----------------------------------------------------------------
# Schema introspection endpoints
# -----------------------------------------------------------------

@router.get(
    "/schema/safety-report",
    summary="SafetyReport JSON schema",
    tags=["schema"],
)
def get_safety_report_schema():
    """Return the SafetyReport JSON schema for frontend reference."""
    return SafetyReport.model_json_schema()


@router.get(
    "/schema/analysis-response",
    summary="AnalysisResponse JSON schema",
    tags=["schema"],
)
def get_analysis_response_schema():
    """Return the full AnalysisResponse JSON schema."""
    return AnalysisResponse.model_json_schema()


@router.get(
    "/schema/batch-analysis-response",
    summary="BatchAnalysisResponse JSON schema",
    tags=["schema"],
)
def get_batch_analysis_response_schema():
    """Return the BatchAnalysisResponse JSON schema."""
    return BatchAnalysisResponse.model_json_schema()
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
def api_get_reports_by_ids(ids: Optional[str] = None):
    """
    With `ids` (comma-separated): return just those reports, in order,
    skipping any that don't exist — used to hydrate a precursor's
    contributing reports.

    Without `ids`: return every report analyzed so far, most recent
    first — powers the "All Reports" browse page.
    """
    if not ids:
        reports = get_all_reports()
        return sorted(
            reports, key=lambda r: r.get("timestamp") or "", reverse=True
        )

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
