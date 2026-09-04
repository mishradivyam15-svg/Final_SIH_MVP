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