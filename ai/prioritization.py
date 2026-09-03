"""Deterministic precursor summaries and prototype HSE review prioritization.

Scores prioritize recurring precursor patterns for HSE review. They are
transparent prototype heuristics, not predictions of fatalities or accidents.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isclose, isfinite
from statistics import mean
from typing import Literal

from ai.clustering import GroupingResult, PrecursorGroup
from ai.relationship import SafetyReport, normalize_signal


@dataclass(frozen=True)
class PriorityConfig:
    """Configurable prototype weights, recurrence reference, and review bands."""

    bfs_weight: float = 0.30
    rf_weight: float = 0.25
    ssc_weight: float = 0.15
    tp_weight: float = 0.15
    ahe_weight: float = 0.15
    recurrence_reference_count: int = 5
    high_threshold: float = 70.0
    medium_threshold: float = 40.0

    def __post_init__(self) -> None:
        weights = (
            self.bfs_weight,
            self.rf_weight,
            self.ssc_weight,
            self.tp_weight,
            self.ahe_weight,
        )
        if any(weight < 0 for weight in weights) or not isclose(sum(weights), 1.0):
            raise ValueError("Priority weights must be non-negative and sum to 1.")
        if (
            isinstance(self.recurrence_reference_count, bool)
            or not isinstance(self.recurrence_reference_count, int)
            or self.recurrence_reference_count <= 0
        ):
            raise ValueError("recurrence_reference_count must be a positive integer.")
        if not 0 <= self.medium_threshold <= self.high_threshold <= 100:
            raise ValueError("Priority thresholds must satisfy 0 <= medium <= high <= 100.")


@dataclass(frozen=True)
class Precursor:
    """Explainable candidate precursor prioritized for HSE review."""

    precursor_id: str
    title: str
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    priority_score: float
    report_ids: tuple[str, ...]
    common_hazard: str | None
    common_barrier_failure: str | None
    time_window: str | None
    evidence: tuple[str, ...]
    review_status: Literal["pending_review"] = "pending_review"

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation for future consumers."""

        return {
            "precursor_id": self.precursor_id,
            "title": self.title,
            "priority": self.priority,
            "priority_score": self.priority_score,
            "report_ids": list(self.report_ids),
            "common_hazard": self.common_hazard,
            "common_barrier_failure": self.common_barrier_failure,
            "time_window": self.time_window,
            "evidence": list(self.evidence),
            "review_status": self.review_status,
        }


class PrecursorEngine:
    """Summarize candidate groups without recalculating report relationships."""

    def __init__(self, config: PriorityConfig | None = None) -> None:
        self.config = config or PriorityConfig()

    def summarize(
        self, group: PrecursorGroup, reports_by_id: Mapping[str, SafetyReport]
    ) -> Precursor:
        """Create an interpretable precursor from one candidate group."""

        reports = self._reports_for_group(group, reports_by_id)
        report_ids = tuple(sorted(group.report_ids))
        common_hazard, hazard_count, hazard_evidence = _common_signal(
            reports, "hazard", "hazard"
        )
        common_barrier, barrier_count, barrier_evidence = _common_signal(
            reports, "barrier_failure", "barrier failure"
        )
        report_count = len(reports)
        supporting_edges = tuple(edge for edge in group.supporting_edges if edge.is_related)
        ssc = _mean_edge_value(supporting_edges, "semantic_similarity")
        temporal_proximity = _mean_edge_value(supporting_edges, "temporal_relation")
        bfs, severity_count, unavailable_severity_count = _barrier_failure_severity(reports)
        recurrence_frequency = min(
            report_count / self.config.recurrence_reference_count, 1.0
        )
        ahe = 0.0
        priority_score = 100 * (
            bfs * self.config.bfs_weight
            + recurrence_frequency * self.config.rf_weight
            + ssc * self.config.ssc_weight
            + temporal_proximity * self.config.tp_weight
            + ahe * self.config.ahe_weight
        )
        priority_score = round(priority_score, 2)
        priority = self._priority_label(priority_score)
        time_window, time_evidence = _time_window(reports)
        title = _title(common_hazard, common_barrier)

        evidence = [f"{report_count} reports form this candidate precursor group."]
        evidence.extend(hazard_evidence)
        evidence.extend(barrier_evidence)
        evidence.append(f"{len(supporting_edges)} supporting relationships connect this group.")
        for edge in supporting_edges:
            for edge_evidence in edge.evidence:
                evidence.append(
                    f"Supporting relationship {edge.source_report_id}-{edge.target_report_id}: {edge_evidence}"
                )
        evidence.append(
            f"Mean semantic similarity across {len(supporting_edges)} supporting relationships: {ssc:.2f}."
        )
        evidence.append(
            f"Mean temporal relationship across {len(supporting_edges)} supporting relationships: {temporal_proximity:.2f}."
        )
        evidence.append(
            f"BFS: {bfs:.2f} from {severity_count} valid severity_potential values; {unavailable_severity_count} unavailable."
        )
        evidence.append(
            f"RF: {recurrence_frequency:.2f} from {report_count} reports with reference count {self.config.recurrence_reference_count}."
        )
        evidence.append(
            "Activity/hazard exposure score unavailable because the current exposure representation does not define an ordinal severity mapping."
        )
        evidence.extend(time_evidence)
        evidence.append(f"Priority score: {priority_score:.2f}/100.")
        evidence.append(f"Priority: {priority}.")

        return Precursor(
            precursor_id=group.precursor_id,
            title=title,
            priority=priority,
            priority_score=priority_score,
            report_ids=report_ids,
            common_hazard=common_hazard,
            common_barrier_failure=common_barrier,
            time_window=time_window,
            evidence=tuple(evidence),
        )

    def summarize_all(
        self, grouping_result: GroupingResult, reports_by_id: Mapping[str, SafetyReport]
    ) -> tuple[Precursor, ...]:
        """Summarize groups in deterministic precursor-ID order."""

        if not isinstance(grouping_result, GroupingResult):
            raise TypeError("grouping_result must be a GroupingResult.")
        return tuple(
            self.summarize(group, reports_by_id)
            for group in sorted(grouping_result.groups, key=lambda item: item.precursor_id)
        )

    def _priority_label(self, score: float) -> Literal["HIGH", "MEDIUM", "LOW"]:
        if score >= self.config.high_threshold:
            return "HIGH"
        if score >= self.config.medium_threshold:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _reports_for_group(
        group: PrecursorGroup, reports_by_id: Mapping[str, SafetyReport]
    ) -> list[SafetyReport]:
        if not isinstance(group, PrecursorGroup):
            raise TypeError("group must be a PrecursorGroup.")
        if not isinstance(reports_by_id, Mapping):
            raise TypeError("reports_by_id must be a mapping.")
        if len(set(group.report_ids)) != len(group.report_ids):
            raise ValueError("A precursor group cannot contain duplicate report IDs.")
        missing_ids = sorted(set(group.report_ids) - set(reports_by_id))
        if missing_ids:
            raise KeyError(f"Missing reports for precursor group: {', '.join(missing_ids)}")
        return [reports_by_id[report_id] for report_id in sorted(group.report_ids)]


def _common_signal(
    reports: list[SafetyReport], key: str, label: str
) -> tuple[str | None, int, list[str]]:
    values = [normalize_signal(report.get(key)) for report in reports]
    known_values = [value for value in values if value is not None]
    unknown_count = len(reports) - len(known_values)
    counts = Counter(known_values)
    if counts:
        value, count = counts.most_common(1)[0]
        has_tie = list(counts.values()).count(count) > 1
        if count > len(reports) / 2 and count >= 2 and not has_tie:
            evidence = [f"{count} of {len(reports)} reports share {label}: {value}."]
            if unknown_count:
                evidence.append(f"{unknown_count} reports have unknown {label} information.")
            return value, count, evidence

    if not known_values:
        return None, 0, [f"{label.capitalize()} information is unknown for all {len(reports)} reports."]
    evidence = [f"No common {label}: known values conflict."]
    if unknown_count:
        evidence.append(f"{unknown_count} reports have unknown {label} information.")
    return None, 0, evidence


def _mean_edge_value(edges: tuple, attribute: str) -> float:
    if not edges:
        return 0.0
    return float(mean(float(getattr(edge, attribute)) for edge in edges))


def _barrier_failure_severity(reports: list[SafetyReport]) -> tuple[float, int, int]:
    values: list[float] = []
    unavailable_count = 0
    for report in reports:
        if normalize_signal(report.get("barrier_failure")) is None:
            continue
        severity = _normalized_severity(report.get("severity_potential"))
        if severity is None:
            unavailable_count += 1
        else:
            values.append(severity)
    return (float(mean(values)) if values else 0.0, len(values), unavailable_count)


def _normalized_severity(value: object) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(numeric_value):
        return None
    return min(max(numeric_value, 0.0), 1.0)


def _time_window(reports: list[SafetyReport]) -> tuple[str | None, list[str]]:
    dates = [parsed for report in reports if (parsed := _parse_timestamp(report.get("timestamp"))) is not None]
    if not dates:
        return None, ["Time window unavailable because no valid report timestamps were provided."]
    earliest, latest = min(dates), max(dates)
    return (
        f"{earliest.isoformat()} to {latest.isoformat()}",
        [f"Reports span {earliest.isoformat()} to {latest.isoformat()} from {len(dates)} valid timestamps."],
    )


def _parse_timestamp(value: object):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        return parsed.astimezone(timezone.utc).date()
    return parsed.date()


def _title(hazard: str | None, barrier_failure: str | None) -> str:
    if hazard is not None and barrier_failure is not None:
        return f"Recurring {_display_label(hazard)} {_display_label(barrier_failure)}"
    if hazard is not None:
        return f"Recurring {_display_label(hazard)} Safety Pattern"
    if barrier_failure is not None:
        return f"Recurring {_display_label(barrier_failure)} Pattern"
    return "Recurring Safety Pattern"


def _display_label(value: str) -> str:
    return value.replace("_", " ").title()
