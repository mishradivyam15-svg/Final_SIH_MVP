"""
Pipeline bridge between the FastAPI backend and the AI pipeline.

Flow:
    Raw reports
        -> preprocessing
        -> ML inference (hazard + exposure)
        -> rule-based extraction (activity, equipment, barrier, evidence)
        -> merged SafetyReport
        -> RelationshipEngine
        -> RelationshipGraph
        -> ClusterEngine
        -> PrecursorEngine
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from ai.preprocessing import preprocess_report
from ai.extraction import extract_safety_signals
from ai.embeddings import EmbeddingService
from ai.relationship import RelationshipEngine
from ai.relationship_graph import RelationshipGraph
from ai.clustering import ClusterEngine
from ai.prioritization import PrecursorEngine
from ai.sif_classification import classify_sif

from backend.schemas import (
    AnalysisResponse,
    Precursor,
    RelationshipResult,
    SafetyReport,
)

logger = logging.getLogger(__name__)

# ── Lazy-loaded ML predictor (singleton) ───────────────────────
_predictor = None


def _get_predictor():
    """Load the ML model on first call (lazy init)."""
    global _predictor
    if _predictor is None:
        try:
            from ai.ml.inference import SafetySignalPredictor
            _predictor = SafetySignalPredictor(device="cpu")
            if _predictor.is_loaded:
                logger.info("ML safety-signal predictor loaded successfully")
            else:
                logger.warning(
                    "ML predictor created but checkpoint not found — "
                    "falling back to rule-based extraction only"
                )
        except Exception as exc:
            logger.warning(f"Failed to load ML predictor: {exc}")
            _predictor = None
    return _predictor


def run_extraction(
    narrative: str,
    report_id: str | None = None,
    timestamp: str | None = None,
    site: str | None = None,
    source_type: str = "incident",
) -> SafetyReport:
    """
    Run preprocessing + extraction on one report.

    Uses ML model for hazard/exposure prediction and rule-based
    extraction for activity, equipment, barrier_failure, and evidence.
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

    # Step 1: Preprocess
    preprocessed = preprocess_report(raw_report)

    # Step 2: Rule-based extraction (activity, equipment, barrier, evidence)
    rule_result = extract_safety_signals(preprocessed)

    # Step 3: ML prediction (hazard, exposure)
    predictor = _get_predictor()
    ml_result = None
    if predictor and predictor.is_loaded:
        try:
            ml_result = predictor.predict(preprocessed.get("narrative", ""))
        except Exception as exc:
            logger.warning(f"ML prediction failed: {exc}")

    # Step 4: Merge results — ML wins for hazard/exposure
    if ml_result and (ml_result.get("hazard") or ml_result.get("exposure")):
        hazard = ml_result["hazard"]
        exposure = ml_result["exposure"]
        hazard_confidence = ml_result["hazard_confidence"]
        exposure_confidence = ml_result["exposure_confidence"]
        extraction_method = "ml+rules"
    else:
        # Fallback to rule-based
        hazard = rule_result.get("hazard")
        exposure = rule_result.get("exposure")
        hazard_confidence = None
        exposure_confidence = None
        extraction_method = "rules"

    # Format hazard/exposure for display (replace underscores)
    if hazard:
        hazard = hazard.replace("_", " ").title()
    if exposure:
        exposure = exposure.replace("_", " ").title()

    # Format rule-based fields
    activity = rule_result.get("activity")
    if activity:
        activity = activity.replace("_", " ").title()
    equipment = rule_result.get("equipment")
    if equipment:
        equipment = equipment.replace("_", " ").title()
    barrier_failure = rule_result.get("barrier_failure")
    if barrier_failure:
        barrier_failure = barrier_failure.replace("_", " ").title()

    # SIF-potential + IOGP Life-Saving Rule tagging — a deterministic
    # classification derived from the final (ML-preferred) hazard and
    # exposure signals. See ai/sif_classification.py for the rationale.
    sif_result = classify_sif(hazard, exposure, barrier_failure)
    severity_potential = sif_result["severity_potential"]
    if severity_potential:
        severity_potential = severity_potential.replace("_", " ").title()

    return SafetyReport(
        report_id=report_id,
        timestamp=timestamp,
        site=site,
        source_type=source_type,
        narrative=preprocessed.get("narrative", narrative),
        hazard=hazard,
        activity=activity,
        equipment=equipment,
        barrier_failure=barrier_failure,
        exposure=exposure,
        severity_potential=severity_potential,
        sif_potential=sif_result["sif_potential"],
        iogp_life_saving_rule=sif_result["iogp_life_saving_rule"],
        evidence=rule_result.get("evidence"),
        hazard_confidence=hazard_confidence,
        exposure_confidence=exposure_confidence,
        extraction_method=extraction_method,
    )


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
        pipeline_version="ml-v1+extraction-v1+ai2",
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
        "pipeline_version": "ml-v1+extraction-v1+ai2",
    }