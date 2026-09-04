"""Offline graph tests using Prototype / Representative Data only."""

import json
import unittest

from ai.relationship import RelationshipResult
from ai.relationship_graph import RelationshipGraph


class FakeRelationshipEngine:
    """Deterministic Phase 2 substitute used only by graph unit tests."""

    def __init__(self, related_pairs=(), strengths=None):
        self.related_pairs = {frozenset(pair) for pair in related_pairs}
        self.strengths = strengths or {}
        self.calls = []

    def compare(self, source_report, target_report):
        source_id = source_report["report_id"]
        target_id = target_report["report_id"]
        pair = frozenset((source_id, target_id))
        self.calls.append((source_id, target_id))
        is_related = pair in self.related_pairs
        strength = self.strengths.get(pair, 0.9 if is_related else 0.2)
        return RelationshipResult(
            source_report_id=source_id,
            target_report_id=target_id,
            semantic_similarity=0.8 if is_related else 0.1,
            hazard_match=1.0 if is_related else 0.0,
            activity_match=1.0 if is_related else 0.0,
            barrier_match=1.0 if is_related else 0.0,
            site_match=1.0 if is_related else 0.0,
            temporal_relation=0.9 if is_related else 0.1,
            relationship_strength=strength,
            is_related=is_related,
            evidence=[f"Prototype relationship: {source_id}-{target_id}"],
        )


def report(report_id):
    """Return Prototype / Representative Data, not operational report data."""

    return {"report_id": report_id, "narrative": f"Prototype report {report_id}"}


class RelationshipGraphTests(unittest.TestCase):
    def build_graph(self, related_pairs=(), reports=None, **engine_options):
        engine = FakeRelationshipEngine(related_pairs, **engine_options)
        graph = RelationshipGraph(engine)
        return graph.build(reports if reports is not None else []), engine

    def test_empty_report_list_creates_empty_graph(self):
        graph, engine = self.build_graph()

        self.assertEqual(graph.nodes, ())
        self.assertEqual(graph.edges, ())
        self.assertEqual(engine.calls, [])

    def test_one_report_creates_node_without_edges(self):
        graph, engine = self.build_graph(reports=[report("R001")])

        self.assertEqual(graph.nodes, ("R001",))
        self.assertEqual(graph.edges, ())
        self.assertEqual(engine.calls, [])

    def test_two_related_reports_create_one_edge(self):
        graph, _ = self.build_graph(
            [("R001", "R002")], [report("R001"), report("R002")]
        )

        self.assertEqual(len(graph.edges), 1)
        self.assertEqual(graph.neighbors("R001"), ["R002"])

    def test_two_unrelated_reports_do_not_create_default_edge(self):
        graph, _ = self.build_graph(reports=[report("R001"), report("R002")])

        self.assertEqual(graph.edges, ())
        self.assertEqual(graph.neighbors("R001"), [])

    def test_multiple_connected_reports_and_isolated_report(self):
        graph, _ = self.build_graph(
            [("R001", "R002"), ("R002", "R003"), ("R001", "R003")],
            [report(f"R00{index}") for index in range(1, 6)],
        )

        self.assertEqual(graph.neighbors("R002"), ["R001", "R003"])
        self.assertEqual(graph.neighbors("R004"), [])
        self.assertEqual(len(graph.edges), 3)

    def test_compares_each_unique_pair_once_without_self_or_reverse_edges(self):
        reports = [report(f"R00{index}") for index in range(1, 6)]
        graph, engine = self.build_graph(reports=reports)

        self.assertEqual(len(engine.calls), 10)
        self.assertTrue(all(first != second for first, second in engine.calls))
        self.assertEqual(len({frozenset(pair) for pair in engine.calls}), 10)
        self.assertEqual(graph.edges, ())

    def test_duplicate_report_ids_raise_value_error(self):
        graph = RelationshipGraph(FakeRelationshipEngine())

        with self.assertRaisesRegex(ValueError, "Duplicate report_id: R001"):
            graph.build([report("R001"), report("R001")])

    def test_malformed_reports_raise_clear_errors(self):
        graph = RelationshipGraph(FakeRelationshipEngine())

        with self.assertRaises(ValueError):
            graph.build(None)
        with self.assertRaises(TypeError):
            graph.build(["not a report"])
        with self.assertRaises(ValueError):
            graph.build([{"narrative": "missing ID"}])
        with self.assertRaisesRegex(ValueError, "surrounding whitespace"):
            graph.build([report(" R001 ")])

    def test_nodes_and_edges_are_deterministically_sorted(self):
        graph, _ = self.build_graph(
            [("R003", "R001"), ("R002", "R003")],
            [report("R003"), report("R001"), report("R002")],
        )

        self.assertEqual(graph.nodes, ("R001", "R002", "R003"))
        self.assertEqual(
            [(edge.source_report_id, edge.target_report_id) for edge in graph.edges],
            [("R001", "R003"), ("R002", "R003")],
        )

    def test_neighbors_raises_for_unknown_node(self):
        graph, _ = self.build_graph(reports=[report("R001")])

        with self.assertRaisesRegex(KeyError, "Unknown report ID: R999"):
            graph.neighbors("R999")

    def test_get_edge_supports_both_directions_and_missing_edge(self):
        graph, _ = self.build_graph(
            [("R001", "R002")], [report("R001"), report("R002"), report("R003")]
        )

        self.assertIs(graph.get_edge("R001", "R002"), graph.get_edge("R002", "R001"))
        self.assertIsNone(graph.get_edge("R001", "R003"))

    def test_include_unrelated_controls_retained_pair_results(self):
        reports = [report("R001"), report("R002"), report("R003")]
        related_pairs = [("R001", "R002")]
        default_graph, _ = self.build_graph(related_pairs, reports)
        all_graph = RelationshipGraph(FakeRelationshipEngine(related_pairs)).build(
            reports, include_unrelated=True
        )

        self.assertEqual(len(default_graph.edges), 1)
        self.assertEqual(len(all_graph.edges), 3)
        self.assertEqual(all_graph.neighbors("R003"), [])

    def test_edges_preserve_relationship_result_and_evidence(self):
        graph, _ = self.build_graph(
            [("R001", "R002")], [report("R001"), report("R002")]
        )

        edge = graph.get_edge("R001", "R002")
        self.assertEqual(edge.semantic_similarity, 0.8)
        self.assertEqual(edge.relationship_strength, 0.9)
        self.assertEqual(edge.evidence, ["Prototype relationship: R001-R002"])

    def test_to_dict_is_json_serializable_and_preserves_api_fields(self):
        graph, _ = self.build_graph(
            [("R001", "R002")], [report("R002"), report("R001")]
        )

        payload = graph.to_dict()
        self.assertEqual(payload["nodes"], [{"report_id": "R001"}, {"report_id": "R002"}])
        self.assertTrue(payload["edges"][0]["is_related"])
        self.assertIn("evidence", payload["edges"][0])
        json.dumps(payload)

    def test_graph_trusts_engine_decision_without_its_own_threshold(self):
        reports = [report("R001"), report("R002")]
        pair = frozenset(("R001", "R002"))
        graph, _ = self.build_graph(
            [("R001", "R002")], reports, strengths={pair: 0.1}
        )

        self.assertEqual(len(graph.edges), 1)
        self.assertEqual(graph.edges[0].relationship_strength, 0.1)


if __name__ == "__main__":
    unittest.main()
