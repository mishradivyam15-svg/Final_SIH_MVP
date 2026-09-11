"""
Pydantic schemas for the SIF Precursor backend.

These schemas match the actual AI-1 and AI-2 contracts.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


# -----------------------------------------------------------------
# Input: single raw report from frontend
# -----------------------------------------------------------------

class ReportInput(BaseModel):
    """Raw safety / near-miss report submitted by the frontend."""

    narrative: str = Field(
        ...,
        min_length=1,
        description="Free-text safety narrative.",
    )

    report_id: Optional[str] = Field(
        default=None,
        description="Optional report identifier.",
    )

    timestamp: Optional[str] = Field(
        default=None,
        description="ISO-8601 date or datetime string.",
    )

    site: Optional[str] = Field(
        default=None,
        description="Site / location of the event.",
    )

    source_type: Optional[str] = Field(
        default="incident",
        description="Type of safety report.",
    )


# -----------------------------------------------------------------
# Input: multiple reports for AI-2 analysis
# -----------------------------------------------------------------

class BatchReportInput(BaseModel):
    """Collection of reports used for cross-report AI-2 analysis."""

    reports: list[ReportInput] = Field(
        ...,
        min_length=2,
        description="At least two reports are required for relationship analysis.",
    )


# -----------------------------------------------------------------
# SafetyReport
# -----------------------------------------------------------------

class SafetyReport(BaseModel):
    """Structured safety report produced by the extraction pipeline."""

    report_id: Optional[str] = None
    timestamp: Optional[str] = None
    site: Optional[str] = None
    source_type: Optional[str] = None
    narrative: Optional[str] = None
    hazard: Optional[str] = None
    activity: Optional[str] = None
    equipment: Optional[str] = None
    barrier_failure: Optional[str] = None
    exposure: Optional[str] = None
    severity_potential: Optional[str] = None
    evidence: Optional[dict[str, Any]] = None
    hazard_confidence: Optional[float] = None
    exposure_confidence: Optional[float] = None
    extraction_method: Optional[str] = None


# -----------------------------------------------------------------
# AI-2 RelationshipResult
# -----------------------------------------------------------------

class RelationshipResult(BaseModel):
    """Actual pairwise relationship result produced by AI-2."""

    source_report_id: str
    target_report_id: str

    semantic_similarity: float
    hazard_match: float
    activity_match: float
    barrier_match: float
    site_match: float
    temporal_relation: float

    relationship_strength: float
    is_related: bool

    evidence: list[str] = Field(
        default_factory=list
    )


# -----------------------------------------------------------------
# AI-2 Precursor
# -----------------------------------------------------------------

class Precursor(BaseModel):
    """Prioritized precursor candidate produced by AI-2."""

    precursor_id: str
    title: str

    priority: str
    priority_score: float

    report_ids: list[str]

    common_hazard: Optional[str] = None
    common_barrier_failure: Optional[str] = None
    time_window: Optional[str] = None

    evidence: list[str] = Field(
        default_factory=list
    )

    review_status: str = "pending_review"


# -----------------------------------------------------------------
# Single-report analysis response
# -----------------------------------------------------------------

class AnalysisResponse(BaseModel):
    """Response returned by the single-report analysis endpoint."""

    safety_report: SafetyReport

    relationships: list[RelationshipResult] = Field(
        default_factory=list
    )

    precursors: list[Precursor] = Field(
        default_factory=list
    )

    pipeline_version: str = "extraction-v1+ai2"


# -----------------------------------------------------------------
# Batch AI-2 analysis response
# -----------------------------------------------------------------

class BatchAnalysisResponse(BaseModel):
    """Response containing extraction, relationships and precursors."""

    safety_reports: list[SafetyReport]

    relationships: list[RelationshipResult] = Field(
        default_factory=list
    )

    precursors: list[Precursor] = Field(
        default_factory=list
    )

    pipeline_version: str = "extraction-v1+ai2"