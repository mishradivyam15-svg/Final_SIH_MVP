"""Deterministic undirected graph of safety-report relationships.

The graph performs exactly one relationship comparison for every unique
report pair.

By default, only relationships already marked as ``is_related=True`` are
stored as graph edges. This keeps clustering deterministic and prevents
semantic similarity alone from creating precursor groups.

For debugging/demo purposes, ``include_unrelated=True`` can retain every
pairwise comparison. These unrelated edges are still NOT considered graph
neighbors and therefore cannot create clusters.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from itertools import combinations

from ai.relationship import (
    RelationshipEngine,
    RelationshipResult,
    SafetyReport,
)


class RelationshipGraph:
    """Build an undirected, deterministic graph from safety reports."""

    def __init__(
        self,
        relationship_engine: RelationshipEngine,
    ) -> None:
        if not isinstance(
            relationship_engine,
            RelationshipEngine,
        ):
            raise TypeError(
                "relationship_engine must be a RelationshipEngine."
            )

        self.relationship_engine = relationship_engine

        self._node_ids: tuple[str, ...] = ()

        self._edges: dict[
            tuple[str, str],
            RelationshipResult,
        ] = {}

        self._neighbors: dict[
            str,
            set[str],
        ] = {}

    @property
    def nodes(self) -> tuple[str, ...]:
        """Return report IDs in deterministic order."""

        return self._node_ids

    @property
    def edges(self) -> tuple[RelationshipResult, ...]:
        """Return retained relationship results in deterministic order."""

        return tuple(
            self._edges[key]
            for key in sorted(self._edges)
        )

    @property
    def related_edges(self) -> tuple[RelationshipResult, ...]:
        """Return only edges whose relationship decision is related."""

        return tuple(
            edge
            for edge in self.edges
            if edge.is_related
        )

    @property
    def edge_count(self) -> int:
        """Return the number of retained edges."""

        return len(self._edges)

    @property
    def related_edge_count(self) -> int:
        """Return the number of meaningful related edges."""

        return sum(
            1
            for edge in self._edges.values()
            if edge.is_related
        )

    def build(
        self,
        reports: Iterable[SafetyReport] | None,
        *,
        include_unrelated: bool = False,
    ) -> RelationshipGraph:
        """Build the graph from all unique report pairs.

        Every unique report pair is compared exactly once.

        When ``include_unrelated`` is False, only relationships where
        ``result.is_related`` is True are retained.

        When ``include_unrelated`` is True, every pairwise result is retained
        for inspection. However, unrelated results are never added to the
        neighbor graph and therefore cannot create precursor clusters.
        """

        normalized_reports = self._validate_reports(
            reports
        )

        self._node_ids = tuple(
            report_id
            for report_id, _ in normalized_reports
        )

        self._edges = {}

        self._neighbors = {
            report_id: set()
            for report_id in self._node_ids
        }

        for (
            (_, source_report),
            (_, target_report),
        ) in combinations(
            normalized_reports,
            2,
        ):
            result = self.relationship_engine.compare(
                source_report,
                target_report,
            )

            source_id = source_report["report_id"]
            target_id = target_report["report_id"]

            edge_key = self._edge_key(
                source_id,
                target_id,
            )

            if include_unrelated or result.is_related:
                self._edges[edge_key] = result

            if result.is_related:
                self._neighbors[
                    edge_key[0]
                ].add(edge_key[1])

                self._neighbors[
                    edge_key[1]
                ].add(edge_key[0])

        return self

    def neighbors(
        self,
        report_id: str,
    ) -> list[str]:
        """Return directly related report IDs.

        Raises:
            KeyError: if ``report_id`` is not present in the graph.
        """

        if report_id not in self._neighbors:
            raise KeyError(
                f"Unknown report ID: {report_id}"
            )

        return sorted(
            self._neighbors[report_id]
        )

    def degree(
        self,
        report_id: str,
    ) -> int:
        """Return the number of directly related reports."""

        return len(
            self.neighbors(report_id)
        )

    def get_edge(
        self,
        source_report_id: str,
        target_report_id: str,
    ) -> RelationshipResult | None:
        """Retrieve an undirected relationship result.

        Returns ``None`` when the pair was not retained.
        """

        if not isinstance(
            source_report_id,
            str,
        ):
            return None

        if not isinstance(
            target_report_id,
            str,
        ):
            return None

        if source_report_id == target_report_id:
            return None

        return self._edges.get(
            self._edge_key(
                source_report_id,
                target_report_id,
            )
        )

    def strongest_edges(
        self,
        limit: int = 5,
    ) -> tuple[RelationshipResult, ...]:
        """Return the strongest retained relationships.

        This is useful for inspecting why a dataset does or does not form
        meaningful precursor groups.
        """

        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or limit < 1
        ):
            raise ValueError(
                "limit must be a positive integer."
            )

        return tuple(
            sorted(
                self.edges,
                key=lambda edge: (
                    -edge.relationship_strength,
                    edge.source_report_id,
                    edge.target_report_id,
                ),
            )[:limit]
        )

    def to_dict(
        self,
    ) -> dict[str, list[dict[str, object]]]:
        """Return a JSON-serializable graph representation."""

        return {
            "nodes": [
                {
                    "report_id": report_id,
                }
                for report_id in self._node_ids
            ],
            "edges": [
                edge.as_dict()
                for edge in self.edges
            ],
        }

    @staticmethod
    def _validate_reports(
        reports: Iterable[SafetyReport] | None,
    ) -> list[tuple[str, SafetyReport]]:
        """Validate and deterministically order reports."""

        if reports is None:
            raise ValueError(
                "reports must be an iterable of structured "
                "safety reports."
            )

        validated_reports: list[
            tuple[str, SafetyReport]
        ] = []

        seen_ids: set[str] = set()

        for report in reports:
            if not isinstance(
                report,
                Mapping,
            ):
                raise TypeError(
                    "Each report must be a mapping."
                )

            report_id = report.get(
                "report_id"
            )

            if not isinstance(
                report_id,
                str,
            ):
                raise ValueError(
                    "Each report must contain a non-empty "
                    "report_id."
                )

            if not report_id.strip():
                raise ValueError(
                    "Each report must contain a non-empty "
                    "report_id."
                )

            if report_id != report_id.strip():
                raise ValueError(
                    "report_id must not contain surrounding "
                    "whitespace."
                )

            normalized_id = report_id.strip()

            if normalized_id in seen_ids:
                raise ValueError(
                    f"Duplicate report_id: {normalized_id}"
                )

            seen_ids.add(
                normalized_id
            )

            validated_reports.append(
                (
                    normalized_id,
                    report,
                )
            )

        validated_reports.sort(
            key=lambda item: item[0]
        )

        return validated_reports

    @staticmethod
    def _edge_key(
        first_report_id: str,
        second_report_id: str,
    ) -> tuple[str, str]:
        """Return a deterministic undirected edge key."""

        if first_report_id <= second_report_id:
            return (
                first_report_id,
                second_report_id,
            )

        return (
            second_report_id,
            first_report_id,
        )
        