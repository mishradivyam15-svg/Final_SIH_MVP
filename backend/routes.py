"""
API routes for the SIF Precursor backend.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.schemas import (
    AnalysisResponse,
    ReportInput,
    SafetyReport,
)
from backend.pipeline import run_extraction, run_full_analysis


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
# Full analysis (Extraction v1 + future AI-2)
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
    Accept a raw safety / near-miss report, run the full analysis
    pipeline, and return the structured result.

    Pipeline steps:
        1. Preprocessing (text normalization)
        2. Extraction v1 (rule-based safety signal extraction)
        3. (Future) AI-2 relationship / precursor analysis

    Steps 1-2 are active.  Step 3 returns empty results until the
    AI-2 implementation is integrated.
    """
    try:
        result = run_full_analysis(
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
            detail=f"Pipeline error: {exc}",
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
    only (no relationship / precursor analysis).

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
