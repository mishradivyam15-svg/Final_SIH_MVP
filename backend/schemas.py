"""
Pydantic v2 schemas for the SIF Precursor backend.

These models codify the existing SafetyReport contract from the frozen
ai/extraction.py module and define placeholder shapes for the future
RelationshipResult / Precursor interfaces.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


# -----------------------------------------------------------------
# Input schema — what the frontend sends
# -----------------------------------------------------------------

class ReportInput(BaseModel):
    """Raw safety / near-miss report submitted by the frontend."""

    narrative: str = Field(
        ...,
        min_length=1,
        description="Free-text safety narrative describing the incident.",
    )
    report_id: Optional[str] = Field(
        default=None,
        description=(
            "Optional client-supplied report identifier. "
            "If omitted the backend will generate one."
        ),
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="ISO-8601 date or datetime string of the event.",
    )
    site: Optional[str] = Field(
        default=None,
        description="Site / location where the event occurred.",
    )
    source_type: Optional[str] = Field(
        default="incident",
        description=(
            "Type of report source. "
            "Defaults to 'incident' if not provided."
        ),
    )


# -----------------------------------------------------------------
# SafetyReport — mirrors ai/extraction.py output exactly
# -----------------------------------------------------------------

class SafetyReport(BaseModel):
    """
    Structured safety report produced by the extraction pipeline.

    Field set matches the frozen Extraction v1 contract defined in
    ai/extraction.py and validated by
    ai/validate_safetyreport_fixture.py.
    """

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


# -----------------------------------------------------------------
# Precursor — placeholder contract for future AI-2 output
# -----------------------------------------------------------------

class Precursor(BaseModel):
    """
    Placeholder contract for a SIF precursor identified by the
    future AI-2 cross-report analysis pipeline.

    This model defines the expected shape only.  No AI-2 logic is
    implemented.
    """

    precursor_id: Optional[str] = None
    hazard: Optional[str] = None
    exposure: Optional[str] = None
    barrier_failure: Optional[str] = None
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1.",
    )
    supporting_report_ids: list[str] = Field(
        default_factory=list,
        description="IDs of reports that support this precursor.",
    )


# -----------------------------------------------------------------
# RelationshipResult — placeholder contract for AI-2 output
# -----------------------------------------------------------------

class RelationshipResult(BaseModel):
    """
    Placeholder contract for a cross-report relationship identified
    by the future AI-2 pipeline.

    This model defines the expected shape only.  No AI-2 logic is
    implemented.
    """

    source_report_id: Optional[str] = None
    related_report_ids: list[str] = Field(
        default_factory=list,
        description="IDs of related safety reports.",
    )
    relationship_type: Optional[str] = Field(
        default=None,
        description=(
            "Type of relationship (e.g. 'recurring_hazard', "
            "'common_barrier_failure')."
        ),
    )
    precursors: list[Precursor] = Field(
        default_factory=list,
        description="Precursors identified across the related reports.",
    )


# -----------------------------------------------------------------
# AnalysisResponse — top-level API response
# -----------------------------------------------------------------

class AnalysisResponse(BaseModel):
    """
    Top-level response returned by the /reports/analyze endpoint.

    Wraps the SafetyReport produced by Extraction v1 together with
    future relationship / precursor data from the AI-2 pipeline.
    """

    safety_report: SafetyReport
    relationships: list[RelationshipResult] = Field(
        default_factory=list,
        description=(
            "Cross-report relationships. Empty until the AI-2 "
            "pipeline is integrated."
        ),
    )
    precursors: list[Precursor] = Field(
        default_factory=list,
        description=(
            "Identified SIF precursors. Empty until the AI-2 "
            "pipeline is integrated."
        ),
    )
    pipeline_version: str = Field(
        default="extraction-v1",
        description="Version of the AI pipeline that produced this result.",
    )
