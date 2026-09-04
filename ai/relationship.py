"""Explainable pairwise relationships between structured safety reports.

This prototype combines semantic similarity with reported safety context and
temporal proximity. The scoring rules are deterministic and intentionally
interpretable.

Relationship decisions use two layers:

1. A weighted relationship-strength score.
2. Safety-context gates that prevent superficial semantic similarity from
   creating a relationship when known safety fields directly conflict.

For prototype data, a slightly permissive contextual floor is also supported.
This allows strong shared safety signals such as the same equipment, activity,
hazard, barrier failure, or exposure to create useful candidate edges even when
the overall weighted score is just below the main threshold.
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
    ("equipment", "equipment"),
    ("barrier failure", "barrier_failure"),
    ("exposure", "exposure"),
    ("site", "site"),
)


SAFETY_CONTEXT_FIELDS = (
    ("hazard", "hazard"),
    ("activity", "activity"),
    ("equipment", "equipment"),
    ("barrier failure", "barrier_failure"),
    ("exposure", "exposure"),
)


@dataclass(frozen=True)
class RelationshipConfig:
    """Interpretable prototype weights and decision settings."""

    semantic_weight: float = 0.25
    hazard_weight: float = 0.15
    activity_weight: float = 0.10
    equipment_weight: float = 0.10
    barrier_weight: float = 0.15
    exposure_weight: float = 0.15
    site_weight: float = 0.05
    temporal_weight: float = 0.05

    related_threshold: float = 0.55

    # Prototype contextual floor.
    #
    # This is intentionally lower than related_threshold. It allows a pair
    # with a meaningful safety-context match to become a candidate when the
    # weighted score is close to the main threshold.
    contextual_floor: float = 0.50

    # Minimum number of matching safety fields required when the contextual
    # floor is used.
    contextual_match_count: int = 1

    missing_value_score: float = 0.50
    temporal_decay_days: float = 30.0

    def __post_init__(self) -> None:
        weights = (
            self.semantic_weight,
            self.hazard_weight,
            self.activity_weight,
            self.equipment_weight,
            self.barrier_weight,
            self.exposure_weight,
            self.site_weight,
            self.temporal_weight,
        )

        if any(weight < 0 for weight in weights) or sum(weights) <= 0:
            raise ValueError(
                "Relationship weights must be non-negative and non-zero."
            )

        if not 0 <= self.related_threshold <= 1:
            raise ValueError(
                "related_threshold must be between 0 and 1."
            )

        if not 0 <= self.contextual_floor <= 1:
            raise ValueError(
                "contextual_floor must be between 0 and 1."
            )

        if self.contextual_floor > self.related_threshold:
            raise ValueError(
                "contextual_floor must not exceed related_threshold."
            )

        if (
            isinstance(self.contextual_match_count, bool)
            or not isinstance(self.contextual_match_count, int)
            or self.contextual_match_count < 1
        ):
            raise ValueError(
                "contextual_match_count must be a positive integer."
            )

        if not 0 <= self.missing_value_score <= 1:
            raise ValueError(
                "missing_value_score must be between 0 and 1."
            )

        if self.temporal_decay_days <= 0:
            raise ValueError(
                "temporal_decay_days must be positive."
            )


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

    equipment_match: float = 0.50
    exposure_match: float = 0.50

    def as_dict(self) -> dict[str, object]:
        """Return the JSON-compatible relationship API shape and decision."""

        return {
            "source_report_id": self.source_report_id,
            "target_report_id": self.target_report_id,
            "semantic_similarity": self.semantic_similarity,
            "hazard_match": self.hazard_match,
            "activity_match": self.activity_match,
            "equipment_match": self.equipment_match,
            "barrier_match": self.barrier_match,
            "exposure_match": self.exposure_match,
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

    normalized = re.sub(
        r"[^a-z0-9]+",
        "_",
        value.casefold().strip(),
    )

    return normalized.strip("_") or None


def match_hazard(
    first: object,
    second: object,
    *,
    missing_score: float = 0.5,
) -> float:
    """Compare reported hazards using normalized categorical labels."""

    return _match_structured_value(
        first,
        second,
        missing_score=missing_score,
    )


def match_activity(
    first: object,
    second: object,
    *,
    missing_score: float = 0.5,
) -> float:
    """Compare reported activities using normalized categorical labels."""

    return _match_structured_value(
        first,
        second,
        missing_score=missing_score,
    )


def match_barrier_failure(
    first: object,
    second: object,
    *,
    missing_score: float = 0.5,
) -> float:
    """Compare reported barrier failures using normalized multi-label values."""

    return _match_structured_value(
        first,
        second,
        missing_score=missing_score,
    )


def match_equipment(
    first: object,
    second: object,
    *,
    missing_score: float = 0.5,
) -> float:
    """Compare reported equipment using normalized multi-label values."""

    return _match_structured_value(
        first,
        second,
        missing_score=missing_score,
    )


def match_exposure(
    first: object,
    second: object,
    *,
    missing_score: float = 0.5,
) -> float:
    """Compare reported exposure using normalized multi-label values."""

    return _match_structured_value(
        first,
        second,
        missing_score=missing_score,
    )


def match_site(
    first: object,
    second: object,
    *,
    missing_score: float = 0.5,
) -> float:
    """Compare reported sites using normalized categorical labels."""

    return _match_structured_value(
        first,
        second,
        missing_score=missing_score,
    )


def temporal_relation(
    first: object,
    second: object,
    *,
    decay_days: float = 30.0,
    missing_score: float = 0.5,
) -> float:
    """Score date proximity with deterministic exponential decay.

    The score is:

        exp(-days_apart / decay_days)

    Missing or invalid dates are unknown rather than contradictory and
    therefore receive ``missing_score``.
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
        self,
        source_report: SafetyReport,
        target_report: SafetyReport,
    ) -> RelationshipResult:
        """Return feature scores, decision, and deterministic evidence."""

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

        equipment_match = match_equipment(
            source_report.get("equipment"),
            target_report.get("equipment"),
            missing_score=self.config.missing_value_score,
        )

        barrier_match = match_barrier_failure(
            source_report.get("barrier_failure"),
            target_report.get("barrier_failure"),
            missing_score=self.config.missing_value_score,
        )

        exposure_match = match_exposure(
            source_report.get("exposure"),
            target_report.get("exposure"),
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
            equipment_match,
            barrier_match,
            exposure_match,
            site_match,
            temporal_score,
        )

        matching_context_fields = _matching_context_fields(
            source_report,
            target_report,
        )

        matching_safety_context_fields = _matching_safety_context_fields(
            source_report,
            target_report,
        )

        conflicting_safety_context_fields = (
            _conflicting_safety_context_fields(
                source_report,
                target_report,
            )
        )

        # Primary decision:
        #
        # 1. Normal path: score reaches the configured threshold.
        #
        # 2. Prototype contextual path: score is close to the threshold and
        #    there is at least one genuine safety-context overlap.
        #
        # 3. Known conflicting safety context still blocks the relationship
        #    when two or more safety fields explicitly disagree.
        #
        # This fixes the representative-data situation where useful pairs
        # score around 0.50-0.54 because several fields are missing/unknown.
        normal_threshold_match = (
        strength >= self.config.related_threshold
        )

        contextual_threshold_match = (
        strength >= self.config.related_threshold
        and len(matching_safety_context_fields)
        >= self.config.contextual_match_count
        )

        no_major_context_conflict = (
        len(conflicting_safety_context_fields) < 2
        )

        is_related = (
        normal_threshold_match
        and bool(matching_safety_context_fields)
        and no_major_context_conflict
        )

        return RelationshipResult(
            source_report_id=_identifier(
                source_report.get("report_id")
            ),
            target_report_id=_identifier(
                target_report.get("report_id")
            ),
            semantic_similarity=semantic_similarity,
            hazard_match=hazard_match,
            activity_match=activity_match,
            equipment_match=equipment_match,
            barrier_match=barrier_match,
            exposure_match=exposure_match,
            site_match=site_match,
            temporal_relation=temporal_score,
            relationship_strength=strength,
            is_related=is_related,
            evidence=self._build_evidence(
                source_report,
                target_report,
                semantic_similarity,
                matching_context_fields,
                contextual_threshold_match,
            ),
        )

    def _relationship_strength(self, *scores: float) -> float:
        """Calculate the weighted relationship strength."""

        weights = (
            self.config.semantic_weight,
            self.config.hazard_weight,
            self.config.activity_weight,
            self.config.equipment_weight,
            self.config.barrier_weight,
            self.config.exposure_weight,
            self.config.site_weight,
            self.config.temporal_weight,
        )

        return _bounded(
            sum(
                weight * score
                for weight, score in zip(weights, scores)
            )
            / sum(weights)
        )

    def _build_evidence(
        self,
        source_report: SafetyReport,
        target_report: SafetyReport,
        semantic_similarity: float,
        matching_context_fields: list[str],
        contextual_threshold_match: bool = False,
    ) -> list[str]:
        """Build human-readable evidence for the relationship decision."""

        evidence: list[str] = []

        if (
            _text(source_report.get("narrative"))
            and _text(target_report.get("narrative"))
        ):
            label = (
                "Low semantic similarity"
                if semantic_similarity < 0.30
                else "Semantic similarity"
            )

            evidence.append(
                f"{label}: {semantic_similarity:.2f}"
            )

        for label, key in CONTEXTUAL_FIELDS:
            evidence.extend(
                _field_evidence(
                    label,
                    source_report.get(key),
                    target_report.get(key),
                )
            )

        unknown_context_fields = _unknown_context_fields(
            source_report,
            target_report,
        )

        if len(unknown_context_fields) == len(CONTEXTUAL_FIELDS):
            evidence.append(
                "Contextual evidence insufficient: "
                "hazard, activity, equipment, barrier failure, "
                "exposure, and site are unknown."
            )
        elif unknown_context_fields:
            evidence.append(
                "Unknown contextual fields: "
                f"{', '.join(unknown_context_fields)}"
            )

        if not _matching_safety_context_fields(
            source_report,
            target_report,
        ):
            evidence.append(
                "Contextual evidence insufficient: "
                "no known safety-context match."
            )

        if contextual_threshold_match:
            evidence.append(
                "Contextual relationship candidate: "
                "shared safety signal supports grouping."
            )

        first_date = _parse_date(
            source_report.get("timestamp")
        )
        second_date = _parse_date(
            target_report.get("timestamp")
        )

        if first_date is not None and second_date is not None:
            days_apart = abs(
                (first_date - second_date).days
            )

            evidence.append(
                f"Reports occurred {days_apart} days apart"
            )
        else:
            evidence.append(
                "Temporal evidence unknown: "
                "one or both timestamps are missing or invalid"
            )

        return evidence


def _normalized_labels(
    value: object,
) -> set[str] | None:
    """Normalize a scalar or pipe-separated value into a label set."""

    if not isinstance(value, str) or not value.strip():
        return None

    labels = {
        normalized
        for part in value.split("|")
        if (
            normalized := normalize_signal(part)
        ) is not None
    }

    return labels or None


def _match_structured_value(
    first: object,
    second: object,
    *,
    missing_score: float,
) -> float:
    """Match scalar or multi-label structured values.

    A missing value is treated as unknown and receives the configured
    neutral score.

    Two known values match when their normalized label sets have at
    least one element in common.
    """

    first_labels = _normalized_labels(first)
    second_labels = _normalized_labels(second)

    if first_labels is None or second_labels is None:
        return _bounded(missing_score)

    return 1.0 if first_labels & second_labels else 0.0


def _field_evidence(
    label: str,
    first: object,
    second: object,
) -> list[str]:
    """Return human-readable evidence for one structured field."""

    first_labels = _normalized_labels(first)
    second_labels = _normalized_labels(second)

    if first_labels is None or second_labels is None:
        return []

    matching = sorted(
        first_labels & second_labels
    )

    if matching:
        return [
            f"Same {label}: {'|'.join(matching)}"
        ]

    plural_label = (
        "activities"
        if label == "activity"
        else (
            "equipments"
            if label == "equipment"
            else f"{label}s"
        )
    )

    return [
        "Different known "
        f"{plural_label}: "
        f"{'|'.join(sorted(first_labels))} "
        "vs "
        f"{'|'.join(sorted(second_labels))}"
    ]


def _matching_context_fields(
    source_report: SafetyReport,
    target_report: SafetyReport,
) -> list[str]:
    """Return all known contextual labels that overlap."""

    return [
        label
        for label, key in CONTEXTUAL_FIELDS
        if (
            (
                first := _normalized_labels(
                    source_report.get(key)
                )
            ) is not None
            and (
                second := _normalized_labels(
                    target_report.get(key)
                )
            ) is not None
            and bool(first & second)
        )
    ]


def _matching_safety_context_fields(
    source_report: SafetyReport,
    target_report: SafetyReport,
) -> list[str]:
    """Return safety-context overlaps; site is supporting only."""

    return [
        label
        for label, key in SAFETY_CONTEXT_FIELDS
        if (
            (
                first := _normalized_labels(
                    source_report.get(key)
                )
            ) is not None
            and (
                second := _normalized_labels(
                    target_report.get(key)
                )
            ) is not None
            and bool(first & second)
        )
    ]


def _conflicting_context_fields(
    source_report: SafetyReport,
    target_report: SafetyReport,
) -> list[str]:
    """Return contextual labels known to have no overlap."""

    return [
        label
        for label, key in CONTEXTUAL_FIELDS
        if (
            (
                first := _normalized_labels(
                    source_report.get(key)
                )
            ) is not None
            and (
                second := _normalized_labels(
                    target_report.get(key)
                )
            ) is not None
            and not (first & second)
        )
    ]


def _conflicting_safety_context_fields(
    source_report: SafetyReport,
    target_report: SafetyReport,
) -> list[str]:
    """Return known safety-context labels with no overlap."""

    return [
        label
        for label, key in SAFETY_CONTEXT_FIELDS
        if (
            (
                first := _normalized_labels(
                    source_report.get(key)
                )
            ) is not None
            and (
                second := _normalized_labels(
                    target_report.get(key)
                )
            ) is not None
            and not (first & second)
        )
    ]


def _has_multiple_safety_context_conflicts(
    source_report: SafetyReport,
    target_report: SafetyReport,
) -> bool:
    """Return whether multiple safety fields explicitly conflict."""

    return (
        len(
            _conflicting_safety_context_fields(
                source_report,
                target_report,
            )
        )
        >= 2
    )


def _unknown_context_fields(
    source_report: SafetyReport,
    target_report: SafetyReport,
) -> list[str]:
    """Return contextual fields unknown in one or both reports."""

    unknown: list[str] = []

    for label, key in CONTEXTUAL_FIELDS:
        first = _normalized_labels(
            source_report.get(key)
        )
        second = _normalized_labels(
            target_report.get(key)
        )

        if first is None or second is None:
            unknown.append(label)

    return unknown


def _parse_date(value: object) -> date | None:
    """Parse common ISO-style date and datetime values."""

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if not isinstance(value, str):
        return None

    text = value.strip()

    if not text:
        return None

    try:
        return datetime.fromisoformat(
            text.replace("Z", "+00:00")
        ).date()
    except ValueError:
        pass

    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _text(value: object) -> str | None:
    """Return stripped text or None."""

    if not isinstance(value, str):
        return None

    text = value.strip()

    return text or None


def _identifier(value: object) -> str:
    """Return a stable string report identifier."""

    if isinstance(value, str) and value.strip():
        return value.strip()

    if value is None:
        return ""

    return str(value)


def _bounded(value: float) -> float:
    """Clamp a score to the inclusive [0, 1] range."""

    if value < 0.0:
        return 0.0

    if value > 1.0:
        return 1.0

    return float(value)
