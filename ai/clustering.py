"""Graph-based precursor candidate grouping for the MVP.

The relationship layer decides whether two safety reports are related.
The clustering layer only groups those already-related reports.

For the prototype we use deterministic connected components:

    reports -> RelationshipGraph -> related edges -> connected components
            -> precursor groups

This means a chain such as:

    A <-> B <-> C

becomes one precursor group even if A and C do not have a direct
relationship edge.

This is intentionally deterministic and explainable. More advanced
clustering algorithms such as HDBSCAN can be evaluated later when the
prototype has a larger dataset.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from ai.relationship import RelationshipResult
from ai.relationship_graph import RelationshipGraph


@dataclass(frozen=True)
class ClusterConfig:
    """Configuration for precursor candidate grouping."""

    min_group_size: int = 2

    def __post_init__(self) -> None:
        if isinstance(self.min_group_size, bool):
            raise ValueError(
                "min_group_size must be an integer of at least 2."
            )

        if not isinstance(self.min_group_size, int):
            raise ValueError(
                "min_group_size must be an integer of at least 2."
            )

        if self.min_group_size < 2:
            raise ValueError(
                "min_group_size must be an integer of at least 2."
            )


@dataclass(frozen=True)
class PrecursorGroup:
    """A candidate precursor pattern supported by related report edges."""

    precursor_id: str
    report_ids: tuple[str, ...]
    supporting_edges: tuple[RelationshipResult, ...]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""

        return {
            "precursor_id": self.precursor_id,
            "report_ids": list(self.report_ids),
            "supporting_edges": [
                edge.as_dict()
                for edge in self.supporting_edges
            ],
        }


@dataclass(frozen=True)
class GroupingResult:
    """Result of grouping reports into precursor candidates."""

    groups: tuple[PrecursorGroup, ...]
    ungrouped_report_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""

        return {
            "groups": [
                group.as_dict()
                for group in self.groups
            ],
            "ungrouped_report_ids": list(
                self.ungrouped_report_ids
            ),
        }

    # Keep the existing API name used by the prototype.
    def to_dict(self) -> dict[str, object]:
        """Alias for as_dict()."""

        return self.as_dict()


class ClusterEngine:
    """Build deterministic precursor groups from a relationship graph."""

    def __init__(
        self,
        config: ClusterConfig | None = None,
    ) -> None:
        self.config = config or ClusterConfig()

    def group(
        self,
        graph: RelationshipGraph,
    ) -> GroupingResult:
        """Group related reports using connected components.

        Only relationships already present in RelationshipGraph are used.
        This method does not recalculate semantic similarity or contextual
        relationships.

        Reports belonging to a component smaller than min_group_size are
        returned as ungrouped reports.
        """

        if not isinstance(graph, RelationshipGraph):
            raise TypeError(
                "graph must be a RelationshipGraph."
            )

        components = self._connected_components(graph)

        qualifying_components = [
            component
            for component in components
            if len(component) >= self.config.min_group_size
        ]

        # Deterministic ordering is important for reproducible MVP output.
        qualifying_components.sort(
            key=lambda component: tuple(component)
        )

        groups: list[PrecursorGroup] = []

        for index, component in enumerate(
            qualifying_components,
            start=1,
        ):
            supporting_edges = self._supporting_edges(
                graph,
                component,
            )

            # A precursor group must have at least one actual
            # relationship edge supporting it.
            if not supporting_edges:
                continue

            groups.append(
                PrecursorGroup(
                    precursor_id=f"P{index:03d}",
                    report_ids=tuple(component),
                    supporting_edges=supporting_edges,
                )
            )

        groups_tuple = tuple(groups)

        grouped_report_ids = {
            report_id
            for group in groups_tuple
            for report_id in group.report_ids
        }

        ungrouped_report_ids = tuple(
            report_id
            for report_id in graph.nodes
            if report_id not in grouped_report_ids
        )

        return GroupingResult(
            groups=groups_tuple,
            ungrouped_report_ids=ungrouped_report_ids,
        )

    def cluster(
        self,
        graph: RelationshipGraph,
    ) -> GroupingResult:
        """Convenience alias for group().

        This makes the engine easier to consume from a backend/API layer
        without changing the primary group() interface.
        """

        return self.group(graph)

    @staticmethod
    def _connected_components(
        graph: RelationshipGraph,
    ) -> list[list[str]]:
        """Return deterministic connected components of the graph."""

        unvisited = set(graph.nodes)
        components: list[list[str]] = []

        for start_id in graph.nodes:
            if start_id not in unvisited:
                continue

            component: list[str] = []
            pending: list[str] = [start_id]

            unvisited.remove(start_id)

            while pending:
                report_id = pending.pop()
                component.append(report_id)

                neighbors = sorted(
                    graph.neighbors(report_id),
                    reverse=True,
                )

                for neighbor_id in neighbors:
                    if neighbor_id in unvisited:
                        unvisited.remove(neighbor_id)
                        pending.append(neighbor_id)

            component.sort()
            components.append(component)

        return components

    @staticmethod
    def _supporting_edges(
        graph: RelationshipGraph,
        report_ids: list[str],
    ) -> tuple[RelationshipResult, ...]:
        """Return all related edges inside a precursor component."""

        edges: list[RelationshipResult] = []

        for source_id, target_id in combinations(
            sorted(report_ids),
            2,
        ):
            edge = graph.get_edge(
                source_id,
                target_id,
            )

            if edge is None:
                continue

            if not edge.is_related:
                continue

            edges.append(edge)

        # Strongest supporting relationships first.
        edges.sort(
            key=lambda edge: (
                -edge.relationship_strength,
                edge.source_report_id,
                edge.target_report_id,
            )
        )

        return tuple(edges)
        