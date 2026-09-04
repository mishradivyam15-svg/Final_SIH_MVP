"""Graph-based precursor candidate grouping for the prototype.

Connected components are used because ``RelationshipGraph`` already contains
context-aware relationships. This is a deterministic baseline, not semantic
clustering: a chain of related edges forms one group even when its endpoints
are not directly related. HDBSCAN can be evaluated later if larger prototype
data shows variable-density groups that graph connectivity cannot represent.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from ai.relationship import RelationshipResult
from ai.relationship_graph import RelationshipGraph


@dataclass(frozen=True)
class ClusterConfig:
    """Configuration for deterministic graph-based precursor grouping."""

    min_group_size: int = 2

    def __post_init__(self) -> None:
        if (
            isinstance(self.min_group_size, bool)
            or not isinstance(self.min_group_size, int)
            or self.min_group_size < 2
        ):
            raise ValueError("min_group_size must be an integer of at least 2.")


@dataclass(frozen=True)
class PrecursorGroup:
    """A candidate precursor pattern supported by meaningful graph edges."""

    precursor_id: str
    report_ids: tuple[str, ...]
    supporting_edges: tuple[RelationshipResult, ...]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable precursor-group representation."""

        return {
            "precursor_id": self.precursor_id,
            "report_ids": list(self.report_ids),
            "supporting_edges": [edge.as_dict() for edge in self.supporting_edges],
        }


@dataclass(frozen=True)
class GroupingResult:
    """Candidate precursor groups and reports not supported by a group."""

    groups: tuple[PrecursorGroup, ...]
    ungrouped_report_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable grouping result."""

        return {
            "groups": [group.as_dict() for group in self.groups],
            "ungrouped_report_ids": list(self.ungrouped_report_ids),
        }


class ClusterEngine:
    """Create precursor candidates from meaningful relationship graph edges."""

    def __init__(self, config: ClusterConfig | None = None) -> None:
        self.config = config or ClusterConfig()

    def group(self, graph: RelationshipGraph) -> GroupingResult:
        """Group meaningful-edge components without recalculating relationships."""

        if not isinstance(graph, RelationshipGraph):
            raise TypeError("graph must be a RelationshipGraph.")

        components = self._connected_components(graph)
        qualifying_components = [
            component
            for component in components
            if len(component) >= self.config.min_group_size
        ]
        qualifying_components.sort(key=lambda component: tuple(component))

        groups = tuple(
            PrecursorGroup(
                precursor_id=f"P{index:03d}",
                report_ids=tuple(component),
                supporting_edges=self._supporting_edges(graph, component),
            )
            for index, component in enumerate(qualifying_components, start=1)
        )
        grouped_report_ids = {
            report_id for group in groups for report_id in group.report_ids
        }
        ungrouped_report_ids = tuple(
            report_id for report_id in graph.nodes if report_id not in grouped_report_ids
        )
        return GroupingResult(groups=groups, ungrouped_report_ids=ungrouped_report_ids)

    @staticmethod
    def _connected_components(graph: RelationshipGraph) -> list[list[str]]:
        unvisited = set(graph.nodes)
        components: list[list[str]] = []

        for start_id in graph.nodes:
            if start_id not in unvisited:
                continue
            component: list[str] = []
            pending = [start_id]
            unvisited.remove(start_id)
            while pending:
                report_id = pending.pop()
                component.append(report_id)
                for neighbor_id in graph.neighbors(report_id):
                    if neighbor_id in unvisited:
                        unvisited.remove(neighbor_id)
                        pending.append(neighbor_id)
            components.append(sorted(component))

        return components

    @staticmethod
    def _supporting_edges(
        graph: RelationshipGraph, report_ids: list[str]
    ) -> tuple[RelationshipResult, ...]:
        edges: list[RelationshipResult] = []
        for source_id, target_id in combinations(report_ids, 2):
            edge = graph.get_edge(source_id, target_id)
            if edge is not None and edge.is_related:
                edges.append(edge)
        return tuple(edges)
