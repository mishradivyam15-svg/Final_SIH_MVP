"""
Pipeline bridge — thin integration layer between the FastAPI backend
and the frozen ai/ extraction code.

This is the ONLY module that imports from the ai/ package, creating a
clean seam for the backend.
"""

from __future__ import annotations

import uuid
from typing import Any

from ai.preprocessing import preprocess_report
from ai.extraction import extract_safety_signals

from backend.schemas import (
    AnalysisResponse,
    Precursor,
    RelationshipResult,
    SafetyReport,
)


def run_extraction(
    narrative: str,
    report_id: str | None = None,
    timestamp: str | None = None,
    site: str | None = None,
    source_type: str = "incident",
) -> SafetyReport:
    """
    Run the frozen Extraction v1 pipeline on a single report.

    Steps:
        1. Build the raw report dict expected by the ai/ code.
        2. Preprocess (normalize) the narrative.
        3. Extract safety signals.
        4. Return a typed SafetyReport.
    """

    if report_id is None:
        report_id = str(uuid.uuid4())

    raw_report: dict[str, Any] = {
        "report_id": report_id,
        "timestamp": timestamp,
        "site": site,
        "source_type": source_type,
        "narrative": narrative,
    }

    preprocessed = preprocess_report(raw_report)
    extracted = extract_safety_signals(preprocessed)

    return SafetyReport(**extracted)


def analyze_relationships(
    safety_report: SafetyReport,
) -> tuple[list[RelationshipResult], list[Precursor]]:
    """
    Placeholder for the future AI-2 cross-report relationship and
    precursor analysis pipeline.

    Returns empty lists until the AI-2 implementation is available.

    When the AI-2 team provides the implementation, only the body of
    this function needs to change — the API contract stays the same.
    """

    # ---------------------------------------------------------
    # AI-2 pipeline is not yet implemented.
    # Return empty results so the API shape is stable.
    # ---------------------------------------------------------
    return [], []


def run_full_analysis(
    narrative: str,
    report_id: str | None = None,
    timestamp: str | None = None,
    site: str | None = None,
    source_type: str = "incident",
) -> AnalysisResponse:
    """
    Run the complete analysis pipeline:

        1. Extraction v1  →  SafetyReport
        2. (Future) AI-2  →  Relationships + Precursors

    Returns an AnalysisResponse ready for JSON serialization.
    """

    safety_report = run_extraction(
        narrative=narrative,
        report_id=report_id,
        timestamp=timestamp,
        site=site,
        source_type=source_type,
    )

    relationships, precursors = analyze_relationships(safety_report)

    return AnalysisResponse(
        safety_report=safety_report,
        relationships=relationships,
        precursors=precursors,
        pipeline_version="extraction-v1",
    )
