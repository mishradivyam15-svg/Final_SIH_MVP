"""
Pipeline bridge between the FastAPI backend and the AI pipeline.

Flow:
    Raw reports
        -> preprocessing
        -> extraction
        -> SafetyReport
        -> RelationshipEngine
        -> RelationshipGraph
        -> ClusterEngine
        -> PrecursorEngine
"""

from __future__ import annotations

import uuid
from typing import Any

from ai.preprocessing import preprocess_report
from ai.extraction import extract_safety_signals
from ai.embeddings import EmbeddingService
from ai.relationship import RelationshipEngine
from ai.relationship_graph import RelationshipGraph
from ai.clustering import ClusterEngine
from ai.prioritization import PrecursorEngine

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
    """Run preprocessing and Extraction v1 on one report."""

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
    safety_reports: list[SafetyReport],
) -> tuple[list[RelationshipResult], list[Precursor]]:
    """
    Run the complete AI-2 relationship and precursor pipeline.

    Steps:
        1. Create sentence embedding service.
        2. Compare every unique report pair.
        3. Build relationship graph.
        4. Group related reports into precursor candidates.
        5. Prioritize each precursor candidate.
    """

    if len(safety_reports) < 2:
        return [], []

    # Convert Pydantic models into dictionaries because the AI-2
    # modules operate on mapping-like SafetyReport objects.
    reports: list[dict[str, object]] = [
        report.model_dump() for report in safety_reports
    ]

    # Create the semantic embedding service.
    embedding_service = EmbeddingService()

    # Create the AI-2 relationship engine.
    relationship_engine = RelationshipEngine(
        embedding_service=embedding_service
    )

    # Build the relationship graph.
    graph = RelationshipGraph(
        relationship_engine=relationship_engine
    )

    graph.build(reports)

    # Return all retained relationship edges.
    relationships = [
        RelationshipResult(**edge.as_dict())
        for edge in graph.edges
    ]

    # Group related reports into precursor candidates.
    cluster_engine = ClusterEngine()
    grouping_result = cluster_engine.group(graph)

    # Map report IDs to reports for prioritization.
    reports_by_id = {
        str(report["report_id"]): report
        for report in reports
    }

    # Generate prioritized precursor summaries.
    precursor_engine = PrecursorEngine()

    precursor_results = precursor_engine.summarize_all(
        grouping_result,
        reports_by_id,
    )

    precursors = [
        Precursor(**precursor.as_dict())
        for precursor in precursor_results
    ]

    return relationships, precursors


def run_full_analysis(
    narrative: str,
    report_id: str | None = None,
    timestamp: str | None = None,
    site: str | None = None,
    source_type: str = "incident",
) -> AnalysisResponse:
    """
    Run extraction for a single report.

    AI-2 cross-report analysis requires multiple reports, so the
    single-report endpoint returns an extracted SafetyReport while
    batch analysis performs relationship/precursor detection.
    """

    safety_report = run_extraction(
        narrative=narrative,
        report_id=report_id,
        timestamp=timestamp,
        site=site,
        source_type=source_type,
    )

    return AnalysisResponse(
        safety_report=safety_report,
        relationships=[],
        precursors=[],
        pipeline_version="extraction-v1+ai2",
    )


def run_batch_analysis(
    reports: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Run extraction + AI-2 analysis for multiple raw reports.
    """

    safety_reports: list[SafetyReport] = []

    for report in reports:
        safety_report = run_extraction(
            narrative=report["narrative"],
            report_id=report.get("report_id"),
            timestamp=report.get("timestamp"),
            site=report.get("site"),
            source_type=report.get("source_type", "incident"),
        )

        safety_reports.append(safety_report)

    relationships, precursors = analyze_relationships(
        safety_reports
    )

    return {
        "safety_reports": [
            report.model_dump()
            for report in safety_reports
        ],
        "relationships": [
            relationship.model_dump()
            for relationship in relationships
        ],
        "precursors": [
            precursor.model_dump()
            for precursor in precursors
        ],
        "pipeline_version": "extraction-v1+ai2",
    }