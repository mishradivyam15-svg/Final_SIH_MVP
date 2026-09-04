"""Evaluation utilities for the semantic-only baseline and proposed relationship engine.

This module evaluates pairwise relationship decisions against supplied human labels.
It does not create labels, predict fatalities, or claim that the metrics are validated
operational performance.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from ai.relationship import RelationshipEngine, SafetyReport


@dataclass(frozen=True)
class LabeledPair:
    """A pair of safety reports with a supplied ground-truth relationship label."""

    source_report_id: str
    target_report_id: str
    is_related: bool

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation."""
        return {
            "source_report_id": self.source_report_id,
            "target_report_id": self.target_report_id,
            "is_related": self.is_related,
        }


@dataclass(frozen=True)
class EvaluationMetrics:
    """Classification metrics calculated from supplied labels and predictions."""

    true_positive: int
    true_negative: int
    false_positive: int
    false_negative: int
    accuracy: float
    precision: float
    recall: float
    f1: float

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation."""
        return {
            "true_positive": self.true_positive,
            "true_negative": self.true_negative,
            "false_positive": self.false_positive,
            "false_negative": self.false_negative,
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
        }


@dataclass(frozen=True)
class EvaluationComparison:
    """Side-by-side evaluation of baseline and proposed relationship decisions."""

    baseline: EvaluationMetrics
    proposed: EvaluationMetrics
    baseline_threshold: float
    sample_count: int

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation."""
        return {
            "baseline": self.baseline.as_dict(),
            "proposed": self.proposed.as_dict(),
            "baseline_threshold": self.baseline_threshold,
            "sample_count": self.sample_count,
        }


class RelationshipEvaluator:
    """Compare a semantic-only baseline with the context-aware engine."""

    def __init__(
        self,
        relationship_engine: RelationshipEngine,
        baseline_threshold: float = 0.70,
    ) -> None:
        if not isinstance(relationship_engine, RelationshipEngine):
            raise TypeError("relationship_engine must be a RelationshipEngine.")

        if not 0.0 <= baseline_threshold <= 1.0:
            raise ValueError("baseline_threshold must be between 0 and 1.")

        self.relationship_engine = relationship_engine
        self.baseline_threshold = baseline_threshold

    def evaluate(
        self,
        labeled_pairs: Iterable[LabeledPair],
        reports_by_id: Mapping[str, SafetyReport],
    ) -> EvaluationComparison:
        """Evaluate baseline and proposed decisions against supplied labels."""

        pairs = tuple(labeled_pairs)

        baseline_predictions: list[bool] = []
        proposed_predictions: list[bool] = []
        labels: list[bool] = []

        for pair in pairs:
            if not isinstance(pair, LabeledPair):
                raise TypeError("Each evaluation item must be a LabeledPair.")

            source = _get_report(reports_by_id, pair.source_report_id)
            target = _get_report(reports_by_id, pair.target_report_id)

            result = self.relationship_engine.compare(source, target)

            baseline_predictions.append(
                result.semantic_similarity >= self.baseline_threshold
            )
            proposed_predictions.append(result.is_related)
            labels.append(pair.is_related)

        return EvaluationComparison(
            baseline=_calculate_metrics(labels, baseline_predictions),
            proposed=_calculate_metrics(labels, proposed_predictions),
            baseline_threshold=self.baseline_threshold,
            sample_count=len(pairs),
        )


def _get_report(
    reports_by_id: Mapping[str, SafetyReport],
    report_id: str,
) -> SafetyReport:
    """Retrieve a report and raise a clear error when it is unavailable."""

    if report_id not in reports_by_id:
        raise KeyError(f"Report ID {report_id!r} is missing from reports_by_id.")

    report = reports_by_id[report_id]

    if not isinstance(report, Mapping):
        raise TypeError(f"Report {report_id!r} must be a mapping.")

    return report


def _calculate_metrics(
    labels: list[bool],
    predictions: list[bool],
) -> EvaluationMetrics:
    """Calculate binary classification metrics without external dependencies."""

    if len(labels) != len(predictions):
        raise ValueError("labels and predictions must have the same length.")

    true_positive = sum(
        label and prediction
        for label, prediction in zip(labels, predictions)
    )
    true_negative = sum(
        not label and not prediction
        for label, prediction in zip(labels, predictions)
    )
    false_positive = sum(
        not label and prediction
        for label, prediction in zip(labels, predictions)
    )
    false_negative = sum(
        label and not prediction
        for label, prediction in zip(labels, predictions)
    )

    sample_count = len(labels)

    accuracy = (
        (true_positive + true_negative) / sample_count
        if sample_count
        else 0.0
    )

    precision_denominator = true_positive + false_positive
    precision = (
        true_positive / precision_denominator
        if precision_denominator
        else 0.0
    )

    recall_denominator = true_positive + false_negative
    recall = (
        true_positive / recall_denominator
        if recall_denominator
        else 0.0
    )

    f1_denominator = precision + recall
    f1 = (
        2.0 * precision * recall / f1_denominator
        if f1_denominator
        else 0.0
    )

    return EvaluationMetrics(
        true_positive=true_positive,
        true_negative=true_negative,
        false_positive=false_positive,
        false_negative=false_negative,
        accuracy=round(accuracy, 6),
        precision=round(precision, 6),
        recall=round(recall, 6),
        f1=round(f1, 6),
    )
