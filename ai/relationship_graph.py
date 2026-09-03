"""Deterministic undirected graph of meaningful safety-report relationships.

Graph construction performs N(N-1)/2 unique pair comparisons. By default, it
stores only relationships already marked related by ``RelationshipEngine``.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from itertools import combinations

from ai.relationship import RelationshipEngine, RelationshipResult, SafetyReport


class RelationshipGraph:
    """Build an undirected, inspectable graph from structured safety reports."""

    def __init__(self, relationship_engine: RelationshipEngine) -> None:
        self.relationship_engine = relationship_engine
        self._node_ids: tuple[str, ...] = ()
        self._edges: dict[tuple[str, str], RelationshipResult] = {}
        self._neighbors: dict[str, set[str]] = {}

    @property
    def nodes(self) -> tuple[str, ...]:
        """Return report IDs in deterministic order."""

        return self._node_ids

    @property
    def edges(self) -> tuple[RelationshipResult, ...]:
        """Return retained pairwise results in deterministic edge order."""

        return tuple(self._edges[key] for key in sorted(self._edges))

    def build(
        self, reports: Iterable[SafetyReport] | None, *, include_unrelated: bool = False
    ) -> RelationshipGraph:
        """Build the graph with one comparison for every unique report pair.

        ``include_unrelated=False`` retains only meaningful edges. When true,
        every pairwise result is retained for inspection, while ``neighbors``
        continues to return only directly related reports.
        """

        normalized_reports = self._validate_reports(reports)
        self._node_ids = tuple(report_id for report_id, _ in normalized_reports)
        self._edges = {}
        self._neighbors = {report_id: set() for report_id in self._node_ids}

        for (_, source_report), (_, target_report) in combinations(normalized_reports, 2):
            result = self.relationship_engine.compare(source_report, target_report)
            edge_key = self._edge_key(
                source_report["report_id"], target_report["report_id"]
            )
            if include_unrelated or result.is_related:
                self._edges[edge_key] = result
            if result.is_related:
                self._neighbors[edge_key[0]].add(edge_key[1])
                self._neighbors[edge_key[1]].add(edge_key[0])

        return self

    def neighbors(self, report_id: str) -> list[str]:
        """Return directly related report IDs, or raise ``KeyError`` if unknown."""

        if report_id not in self._neighbors:
            raise KeyError(f"Unknown report ID: {report_id}")
        return sorted(self._neighbors[report_id])

    def get_edge(
        self, source_report_id: str, target_report_id: str
    ) -> RelationshipResult | None:
        """Retrieve an undirected edge result, returning ``None`` when absent."""

        if not isinstance(source_report_id, str) or not isinstance(target_report_id, str):
            return None
        if source_report_id == target_report_id:
            return None
        return self._edges.get(self._edge_key(source_report_id, target_report_id))

    def to_dict(self) -> dict[str, list[dict[str, object]]]:
        """Return nodes and retained edges in a JSON-serializable form."""

        return {
            "nodes": [{"report_id": report_id} for report_id in self._node_ids],
            "edges": [edge.as_dict() for edge in self.edges],
        }

    @staticmethod
    def _validate_reports(
        reports: Iterable[SafetyReport] | None,
    ) -> list[tuple[str, SafetyReport]]:
        if reports is None:
            raise ValueError("reports must be an iterable of structured safety reports.")

        validated_reports: list[tuple[str, SafetyReport]] = []
        seen_ids: set[str] = set()
        for report in reports:
            if not isinstance(report, Mapping):
                raise TypeError("Each report must be a mapping.")
            report_id = report.get("report_id")
            if not isinstance(report_id, str) or not report_id.strip():
                raise ValueError("Each report must contain a non-empty report_id.")
            if report_id != report_id.strip():
                raise ValueError("report_id must not contain surrounding whitespace.")
            normalized_id = report_id.strip()
            if normalized_id in seen_ids:
                raise ValueError(f"Duplicate report_id: {normalized_id}")
            seen_ids.add(normalized_id)
            validated_reports.append((normalized_id, report))

        return sorted(validated_reports, key=lambda item: item[0])

    @staticmethod
    def _edge_key(first_report_id: str, second_report_id: str) -> tuple[str, str]:
        return tuple(sorted((first_report_id, second_report_id)))
