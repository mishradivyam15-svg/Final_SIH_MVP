"""Explainable pairwise relationships between structured safety reports.

This prototype combines sentence similarity with reported safety context. Its
weights and temporal decay are configurable heuristics, not validated models.
Missing structured values receive a neutral score and do not create evidence.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from math import exp
import re

from ai.embeddings import EmbeddingService


SafetyReport = Mapping[str, object]
CONTEXTUAL_FIELDS = (
    ("hazard", "hazard"),
    ("activity", "activity"),
    ("barrier failure", "barrier_failure"),
    ("site", "site"),
)


@dataclass(frozen=True)
class RelationshipConfig:
    """Interpretable prototype weights and decision settings."""

    semantic_weight: float = 0.30
    hazard_weight: float = 0.20
    activity_weight: float = 0.15
    barrier_weight: float = 0.15
    site_weight: float = 0.10
    temporal_weight: float = 0.10
    related_threshold: float = 0.55
    missing_value_score: float = 0.50
    temporal_decay_days: float = 30.0

    def __post_init__(self) -> None:
        weights = (
            self.semantic_weight,
            self.hazard_weight,
            self.activity_weight,
            self.barrier_weight,
            self.site_weight,
            self.temporal_weight,
        )
        if any(weight < 0 for weight in weights) or sum(weights) <= 0:
            raise ValueError("Relationship weights must be non-negative and non-zero.")
        if not 0 <= self.related_threshold <= 1:
            raise ValueError("related_threshold must be between 0 and 1.")
        if not 0 <= self.missing_value_score <= 1:
            raise ValueError("missing_value_score must be between 0 and 1.")
        if self.temporal_decay_days <= 0:
            raise ValueError("temporal_decay_days must be positive.")


@dataclass(frozen=True)
class RelationshipResult:
    """Inspectable relationship features and decision for a report pair."""

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
    evidence: list[str]

    def as_dict(self) -> dict[str, object]:
        """Return the JSON-compatible relationship API shape and decision."""

        return {
            "source_report_id": self.source_report_id,
            "target_report_id": self.target_report_id,
            "semantic_similarity": self.semantic_similarity,
            "hazard_match": self.hazard_match,
            "activity_match": self.activity_match,
            "barrier_match": self.barrier_match,
            "site_match": self.site_match,
            "temporal_relation": self.temporal_relation,
            "relationship_strength": self.relationship_strength,
            "is_related": self.is_related,
            "evidence": self.evidence,
        }


def normalize_signal(value: object) -> str | None:
    """Normalize text labels so case and minor formatting do not affect matches."""

    if not isinstance(value, str) or not value.strip():
        return None
    normalized = re.sub(r"[^a-z0-9]+", "_", value.casefold().strip())
    return normalized.strip("_") or None


def match_hazard(first: object, second: object, *, missing_score: float = 0.5) -> float:
    """Compare reported hazards using normalized categorical labels."""

    return _match_structured_value(first, second, missing_score=missing_score)


def match_activity(first: object, second: object, *, missing_score: float = 0.5) -> float:
    """Compare reported activities using normalized categorical labels."""

    return _match_structured_value(first, second, missing_score=missing_score)


def match_barrier_failure(
    first: object, second: object, *, missing_score: float = 0.5
) -> float:
    """Compare reported barrier failures using normalized categorical labels."""

    return _match_structured_value(first, second, missing_score=missing_score)


def match_site(first: object, second: object, *, missing_score: float = 0.5) -> float:
    """Compare reported sites using normalized categorical labels."""

    return _match_structured_value(first, second, missing_score=missing_score)


def temporal_relation(
    first: object, second: object, *, decay_days: float = 30.0, missing_score: float = 0.5
) -> float:
    """Score date proximity with deterministic exponential decay.

    The score is ``exp(-days_apart / decay_days)``. Missing or invalid dates
    are unknown rather than contradictory, so they receive ``missing_score``.
    """

    if decay_days <= 0:
        raise ValueError("decay_days must be positive.")
    first_date = _parse_date(first)
    second_date = _parse_date(second)
    if first_date is None or second_date is None:
        return _bounded(missing_score)
    days_apart = abs((first_date - second_date).days)
    return exp(-days_apart / decay_days)


class RelationshipEngine:
    """Compare two structured reports using semantic, context, and time signals."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        config: RelationshipConfig | None = None,
    ) -> None:
        self.embedding_service = embedding_service
        self.config = config or RelationshipConfig()

    def compare(
        self, source_report: SafetyReport, target_report: SafetyReport
    ) -> RelationshipResult:
        """Return feature scores, decision, and deterministic supporting evidence."""

        source_narrative = _text(source_report.get("narrative"))
        target_narrative = _text(target_report.get("narrative"))
        semantic_similarity = _bounded(
            self.embedding_service.cosine_similarity(
                self.embedding_service.embed_text(source_narrative),
                self.embedding_service.embed_text(target_narrative),
            )
        )
        hazard_match = match_hazard(
            source_report.get("hazard"),
            target_report.get("hazard"),
            missing_score=self.config.missing_value_score,
        )
        activity_match = match_activity(
            source_report.get("activity"),
            target_report.get("activity"),
            missing_score=self.config.missing_value_score,
        )
        barrier_match = match_barrier_failure(
            source_report.get("barrier_failure"),
            target_report.get("barrier_failure"),
            missing_score=self.config.missing_value_score,
        )
        site_match = match_site(
            source_report.get("site"),
            target_report.get("site"),
            missing_score=self.config.missing_value_score,
        )
        temporal_score = temporal_relation(
            source_report.get("timestamp"),
            target_report.get("timestamp"),
            decay_days=self.config.temporal_decay_days,
            missing_score=self.config.missing_value_score,
        )
        strength = self._relationship_strength(
            semantic_similarity,
            hazard_match,
            activity_match,
            barrier_match,
            site_match,
            temporal_score,
        )

        matching_context_fields = _matching_context_fields(
            source_report, target_report
        )
        conflicting_context_fields = _conflicting_context_fields(
            source_report, target_report
        )

        is_related = (
    strength >= self.config.related_threshold
    and bool(matching_context_fields)
    and len(conflicting_context_fields) < 2
)

        return RelationshipResult(
            source_report_id=_identifier(source_report.get("report_id")),
            target_report_id=_identifier(target_report.get("report_id")),
            semantic_similarity=semantic_similarity,
            hazard_match=hazard_match,
            activity_match=activity_match,
            barrier_match=barrier_match,
            site_match=site_match,
            temporal_relation=temporal_score,
            relationship_strength=strength,
            is_related=is_related,
            evidence=self._build_evidence(
                source_report,
                target_report,
                semantic_similarity,
                matching_context_fields,
            ),
        )
        
    def _relationship_strength(self, *scores: float) -> float:
        weights = (
            self.config.semantic_weight,
            self.config.hazard_weight,
            self.config.activity_weight,
            self.config.barrier_weight,
            self.config.site_weight,
            self.config.temporal_weight,
        )
        return _bounded(sum(weight * score for weight, score in zip(weights, scores)) / sum(weights))

    def _build_evidence(
        self,
        source_report: SafetyReport,
        target_report: SafetyReport,
        semantic_similarity: float,
        matching_context_fields: list[str],
    ) -> list[str]:
        evidence: list[str] = []
        if _text(source_report.get("narrative")) and _text(target_report.get("narrative")):
            label = "Low semantic similarity" if semantic_similarity < 0.30 else "Semantic similarity"
            evidence.append(f"{label}: {semantic_similarity:.2f}")
        for label, key in CONTEXTUAL_FIELDS:
            evidence.extend(
                _field_evidence(label, source_report.get(key), target_report.get(key))
            )

        unknown_context_fields = _unknown_context_fields(source_report, target_report)
        if len(unknown_context_fields) == len(CONTEXTUAL_FIELDS):
            evidence.append(
                "Contextual evidence insufficient: hazard, activity, barrier failure, "
                "and site are unknown."
            )
        elif unknown_context_fields:
            evidence.append(
                f"Unknown contextual fields: {', '.join(unknown_context_fields)}"
            )
        if not matching_context_fields and len(unknown_context_fields) != len(CONTEXTUAL_FIELDS):
            evidence.append("Contextual evidence insufficient: no known contextual match.")

        first_date = _parse_date(source_report.get("timestamp"))
        second_date = _parse_date(target_report.get("timestamp"))
        if first_date is not None and second_date is not None:
            days_apart = abs((first_date - second_date).days)
            evidence.append(f"Reports occurred {days_apart} days apart")
        else:
            evidence.append(
                "Temporal evidence unknown: one or both timestamps are missing or invalid"
            )
        return evidence


def _match_structured_value(first: object, second: object, *, missing_score: float) -> float:
    first_normalized = normalize_signal(first)
    second_normalized = normalize_signal(second)
    if first_normalized is None or second_normalized is None:
        return _bounded(missing_score)
    return 1.0 if first_normalized == second_normalized else 0.0


def _field_evidence(label: str, first: object, second: object) -> list[str]:
    first_normalized = normalize_signal(first)
    second_normalized = normalize_signal(second)
    if first_normalized is None or second_normalized is None:
        return []
    if first_normalized == second_normalized:
        return [f"Same {label}: {first_normalized}"]
    plural_label = "activities" if label == "activity" else f"{label}s"
    return [f"Different known {plural_label}: {first_normalized} vs {second_normalized}"]


def _matching_context_fields(
    source_report: SafetyReport, target_report: SafetyReport
) -> list[str]:
    """Return known contextual labels that match in both reports.

    This prototype decision heuristic prevents unknown fields from acting as
    positive relationship evidence. It is not a scientifically validated rule.
    """

    return [
        label
        for label, key in CONTEXTUAL_FIELDS
        if normalize_signal(source_report.get(key))
        == normalize_signal(target_report.get(key))
        and normalize_signal(source_report.get(key)) is not None
    ]

def _conflicting_context_fields(
    source_report: SafetyReport, target_report: SafetyReport
) -> list[str]:
    """Return contextual labels known to contradict between two reports."""

    return [
        label
        for label, key in CONTEXTUAL_FIELDS
        if (
            normalize_signal(source_report.get(key)) is not None
            and normalize_signal(target_report.get(key)) is not None
            and normalize_signal(source_report.get(key))
            != normalize_signal(target_report.get(key))
        )
    ]


def _unknown_context_fields(
    source_report: SafetyReport, target_report: SafetyReport
) -> list[str]:
    """Return contextual labels missing from either report."""

    return [
        label
        for label, key in CONTEXTUAL_FIELDS
        if normalize_signal(source_report.get(key)) is None
        or normalize_signal(target_report.get(key)) is None
    ]

def _parse_date(value: object) -> date | None:
    """Parse common safety-report date representations safely."""

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if not isinstance(value, str) or not value.strip():
        return None

    text = value.strip()

    for parser in (
        lambda value: datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).date(),
        lambda value: datetime.strptime(value, "%m/%d/%Y").date(),
        lambda value: datetime.strptime(value, "%m/%d/%y").date(),
    ):
        try:
            return parser(text)
        except ValueError:
            continue

    return None


def _text(value: object) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _identifier(value: object) -> str:
    """Convert a report identifier into a stable string representation."""

    if value is None:
        return ""

    if isinstance(value, bool):
        return ""

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(value)

    if isinstance(value, str):
        return value.strip()

    return str(value).strip()


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, value))
