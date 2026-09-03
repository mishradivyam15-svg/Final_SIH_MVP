"""Offline clustering tests using Prototype / Representative Data only."""

import json
import unittest

from ai.clustering import ClusterConfig, ClusterEngine
from ai.relationship import RelationshipResult
from ai.relationship_graph import RelationshipGraph


class FakeRelationshipEngine:
    """Deterministic relationship source used only for graph fixtures."""

    def __init__(self, related_pairs=()):
        self.related_pairs = {frozenset(pair) for pair in related_pairs}
        self.calls = []

    def compare(self, source_report, target_report):
        source_id = source_report["report_id"]
        target_id = target_report["report_id"]
        self.calls.append((source_id, target_id))
        is_related = frozenset((source_id, target_id)) in self.related_pairs
        return RelationshipResult(
            source_report_id=source_id,
            target_report_id=target_id,
            semantic_similarity=0.8 if is_related else 0.1,
            hazard_match=1.0 if is_related else 0.0,
            activity_match=1.0 if is_related else 0.0,
            barrier_match=1.0 if is_related else 0.0,
            site_match=1.0 if is_related else 0.0,
            temporal_relation=0.9 if is_related else 0.1,
            relationship_strength=0.9 if is_related else 0.2,
            is_related=is_related,
            evidence=[f"Prototype supporting relationship: {source_id}-{target_id}"],
        )


def report(report_id):
    """Return Prototype / Representative Data, never operational report data."""

    return {"report_id": report_id, "narrative": f"Prototype report {report_id}"}


def build_graph(report_ids, related_pairs=(), *, include_unrelated=False):
    engine = FakeRelationshipEngine(related_pairs)
    graph = RelationshipGraph(engine).build(
        [report(report_id) for report_id in report_ids],
        include_unrelated=include_unrelated,
    )
    return graph, engine


class ClusterEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = ClusterEngine()

    def test_empty_graph_has_no_groups_or_ungrouped_reports(self):
        graph, _ = build_graph([])

        result = self.engine.group(graph)

        self.assertEqual(result.groups, ())
        self.assertEqual(result.ungrouped_report_ids, ())

    def test_one_node_is_ungrouped(self):
        graph, _ = build_graph(["R001"])

        result = self.engine.group(graph)

        self.assertEqual(result.groups, ())
        self.assertEqual(result.ungrouped_report_ids, ("R001",))

    def test_two_related_reports_create_candidate_group(self):
        graph, _ = build_graph(["R001", "R002"], [("R001", "R002")])

        result = self.engine.group(graph)

        self.assertEqual(result.groups[0].precursor_id, "P001")
        self.assertEqual(result.groups[0].report_ids, ("R001", "R002"))

    def test_multiple_groups_and_isolated_reports_are_deterministic(self):
        graph, _ = build_graph(
            ["R005", "R003", "R001", "R004", "R002", "R006"],
            [("R001", "R002"), ("R003", "R004")],
        )

        result = self.engine.group(graph)

        self.assertEqual([group.precursor_id for group in result.groups], ["P001", "P002"])
        self.assertEqual(
            [group.report_ids for group in result.groups],
            [("R001", "R002"), ("R003", "R004")],
        )
        self.assertEqual(result.ungrouped_report_ids, ("R005", "R006"))

    def test_minimum_group_size_leaves_small_components_ungrouped(self):
        graph, _ = build_graph(
            ["R001", "R002", "R003"], [("R001", "R002"), ("R002", "R003")]
        )
        engine = ClusterEngine(ClusterConfig(min_group_size=3))

        result = engine.group(graph)

        self.assertEqual(result.groups[0].report_ids, ("R001", "R002", "R003"))
        small_graph, _ = build_graph(["R004", "R005"], [("R004", "R005")])
        self.assertEqual(engine.group(small_graph).ungrouped_report_ids, ("R004", "R005"))

    def test_reports_appear_in_at_most_one_group_without_duplicates(self):
        graph, _ = build_graph(
            ["R001", "R002", "R003"], [("R001", "R002"), ("R002", "R003")]
        )

        result = self.engine.group(graph)
        grouped_ids = [report_id for group in result.groups for report_id in group.report_ids]

        self.assertEqual(grouped_ids, ["R001", "R002", "R003"])
        self.assertEqual(len(grouped_ids), len(set(grouped_ids)))

    def test_chain_effect_forms_one_group_without_claiming_all_pairs_related(self):
        graph, _ = build_graph(
            ["R001", "R002", "R003"], [("R001", "R002"), ("R002", "R003")]
        )

        group = self.engine.group(graph).groups[0]

        self.assertEqual(group.report_ids, ("R001", "R002", "R003"))
        self.assertEqual(len(group.supporting_edges), 2)
        self.assertIsNone(graph.get_edge("R001", "R003"))

    def test_supporting_edges_preserve_relationship_evidence(self):
        graph, _ = build_graph(["R001", "R002"], [("R001", "R002")])

        group = self.engine.group(graph).groups[0]

        self.assertEqual(group.supporting_edges[0].evidence, ["Prototype supporting relationship: R001-R002"])

    def test_json_serialization_preserves_group_contract(self):
        graph, _ = build_graph(["R001", "R002"], [("R001", "R002")])

        payload = self.engine.group(graph).to_dict()

        self.assertEqual(payload["groups"][0]["precursor_id"], "P001")
        self.assertEqual(payload["groups"][0]["report_ids"], ["R001", "R002"])
        self.assertIn("supporting_edges", payload["groups"][0])
        json.dumps(payload)

    def test_malformed_graph_and_invalid_config_raise_clear_errors(self):
        with self.assertRaises(TypeError):
            self.engine.group(None)
        with self.assertRaises(ValueError):
            ClusterConfig(min_group_size=1)
        with self.assertRaises(ValueError):
            ClusterConfig(min_group_size=2.5)

    def test_grouping_does_not_recalculate_relationships_or_load_embeddings(self):
        graph, relationship_engine = build_graph(
            ["R001", "R002", "R003"], [("R001", "R002")]
        )
        comparison_count = len(relationship_engine.calls)

        self.engine.group(graph)

        self.assertEqual(len(relationship_engine.calls), comparison_count)

    def test_grouping_uses_only_meaningful_edges_when_graph_retains_all_pairs(self):
        graph, _ = build_graph(
            ["R001", "R002", "R003"],
            [("R001", "R002")],
            include_unrelated=True,
        )

        result = self.engine.group(graph)

        self.assertEqual(result.groups[0].report_ids, ("R001", "R002"))
        self.assertEqual(result.ungrouped_report_ids, ("R003",))


if __name__ == "__main__":
    unittest.main()
