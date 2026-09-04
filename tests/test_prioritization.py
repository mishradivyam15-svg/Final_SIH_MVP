"""Offline tests for prototype precursor aggregation and priority scoring."""

import json
import unittest

from ai.clustering import GroupingResult, PrecursorGroup
from ai.prioritization import PrecursorEngine, PriorityConfig
from ai.relationship import RelationshipResult


def edge(source, target, *, semantic=0.8, temporal=0.9, related=True):
    return RelationshipResult(
        source_report_id=source, target_report_id=target,
        semantic_similarity=semantic, hazard_match=1.0, activity_match=1.0,
        barrier_match=1.0, site_match=1.0, temporal_relation=temporal,
        relationship_strength=0.9, is_related=related,
        evidence=[f"Prototype supporting relationship: {source}-{target}"],
    )


def report(report_id, **overrides):
    data = {
        "report_id": report_id, "timestamp": "2026-01-10T09:00:00",
        "hazard": "working_at_height", "activity": "maintenance",
        "barrier_failure": "fall_protection_missing", "exposure": "fall_from_height",
        "severity_potential": 0.8,
    }
    data.update(overrides)
    return data


def group(report_ids=("R001", "R002", "R003"), edges=None, precursor_id="P001"):
    return PrecursorGroup(precursor_id, tuple(report_ids), tuple(edges or [edge("R001", "R002"), edge("R002", "R003")]))


class PrecursorEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = PrecursorEngine()
        self.reports = {identifier: report(identifier) for identifier in ("R001", "R002", "R003")}

    def test_basic_precursor_generation_and_pending_review(self):
        precursor = self.engine.summarize(group(), self.reports)
        self.assertEqual(precursor.precursor_id, "P001")
        self.assertEqual(precursor.review_status, "pending_review")
        self.assertEqual(precursor.common_hazard, "working_at_height")

    def test_strict_majority_requires_more_than_half_of_all_reports(self):
        reports = {"R001": report("R001"), "R002": report("R002"), "R003": report("R003", hazard="electrical_energy"), "R004": report("R004", hazard=None)}
        precursor = self.engine.summarize(group(tuple(reports), [edge("R001", "R002")]), reports)
        self.assertIsNone(precursor.common_hazard)
        self.assertIn("No common hazard: known values conflict.", precursor.evidence)

    def test_common_barrier_and_hazard_ties_are_not_common(self):
        reports = {"R001": report("R001"), "R002": report("R002", hazard="electrical_energy", barrier_failure="lockout_missing"), "R003": report("R003"), "R004": report("R004", hazard="electrical_energy", barrier_failure="lockout_missing")}
        precursor = self.engine.summarize(group(tuple(reports), [edge("R001", "R002")]), reports)
        self.assertIsNone(precursor.common_hazard)
        self.assertIsNone(precursor.common_barrier_failure)

    def test_missing_signal_information_is_explicit(self):
        reports = {"R001": report("R001", hazard=None, barrier_failure=None), "R002": report("R002", hazard=None, barrier_failure=None)}
        precursor = self.engine.summarize(group(tuple(reports), [edge("R001", "R002")]), reports)
        self.assertIn("Hazard information is unknown for all 2 reports.", precursor.evidence)
        self.assertIn("Barrier failure information is unknown for all 2 reports.", precursor.evidence)

    def test_rf_calculation_and_cap(self):
        precursor = self.engine.summarize(group(), self.reports)
        self.assertIn("RF: 0.60 from 3 reports with reference count 5.", precursor.evidence)
        reports = {f"R00{index}": report(f"R00{index}") for index in range(1, 7)}
        capped = self.engine.summarize(group(tuple(reports), [edge("R001", "R002")]), reports)
        self.assertIn("RF: 1.00 from 6 reports with reference count 5.", capped.evidence)

    def test_ssc_and_tp_are_means_of_supporting_edges(self):
        precursor = self.engine.summarize(group(edges=[edge("R001", "R002", semantic=0.6, temporal=0.4), edge("R002", "R003", semantic=0.8, temporal=1.0)]), self.reports)
        self.assertIn("Mean semantic similarity across 2 supporting relationships: 0.70.", precursor.evidence)
        self.assertIn("Mean temporal relationship across 2 supporting relationships: 0.70.", precursor.evidence)

    def test_bfs_uses_valid_barrier_severities_and_clamps_values(self):
        reports = {"R001": report("R001", severity_potential=1.5), "R002": report("R002", severity_potential=-2), "R003": report("R003", severity_potential="invalid")}
        precursor = self.engine.summarize(group(), reports)
        self.assertIn("BFS: 0.50 from 2 valid severity_potential values; 1 unavailable.", precursor.evidence)

    def test_bfs_ignores_reports_without_barrier_failure(self):
        reports = {"R001": report("R001", severity_potential=0.8), "R002": report("R002", barrier_failure=None, severity_potential=1.0), "R003": report("R003", barrier_failure=None, severity_potential=1.0)}
        precursor = self.engine.summarize(group(), reports)
        self.assertIn("BFS: 0.80 from 1 valid severity_potential values; 0 unavailable.", precursor.evidence)

    def test_ahe_is_explicitly_unavailable_and_contributes_zero(self):
        precursor = self.engine.summarize(group(), self.reports)
        self.assertIn("Activity/hazard exposure score unavailable because the current exposure representation does not define an ordinal severity mapping.", precursor.evidence)
        self.assertLessEqual(precursor.priority_score, 85.0)

    def test_priority_formula_and_configurable_weights(self):
        precursor = self.engine.summarize(group(), self.reports)
        self.assertEqual(precursor.priority_score, 64.5)
        engine = PrecursorEngine(PriorityConfig(bfs_weight=0.25, rf_weight=0.30, ssc_weight=0.15, tp_weight=0.15, ahe_weight=0.15))
        self.assertEqual(engine.summarize(group(), self.reports).priority_score, 63.5)

    def test_priority_label_boundaries(self):
        engine = PrecursorEngine(PriorityConfig(high_threshold=70, medium_threshold=40))
        self.assertEqual(engine._priority_label(70), "HIGH")
        self.assertEqual(engine._priority_label(40), "MEDIUM")
        self.assertEqual(engine._priority_label(39.99), "LOW")

    def test_invalid_configuration_is_rejected(self):
        with self.assertRaises(ValueError): PriorityConfig(recurrence_reference_count=0)
        with self.assertRaises(ValueError): PriorityConfig(bfs_weight=0.5)
        with self.assertRaises(ValueError): PriorityConfig(high_threshold=30, medium_threshold=40)

    def test_deterministic_and_generic_titles(self):
        self.assertEqual(self.engine.summarize(group(), self.reports).title, "Recurring Working At Height Fall Protection Missing")
        reports = {"R001": report("R001", hazard=None, barrier_failure=None), "R002": report("R002", hazard=None, barrier_failure=None)}
        self.assertEqual(self.engine.summarize(group(tuple(reports), [edge("R001", "R002")]), reports).title, "Recurring Safety Pattern")

    def test_time_windows_handle_valid_missing_invalid_and_timezone_aware_values(self):
        reports = {"R001": report("R001", timestamp="2026-01-10T00:30:00+05:30"), "R002": report("R002", timestamp="2026-01-09T20:00:00+00:00"), "R003": report("R003", timestamp="invalid")}
        precursor = self.engine.summarize(group(), reports)
        self.assertEqual(precursor.time_window, "2026-01-09 to 2026-01-09")
        reports = {"R001": report("R001", timestamp=None), "R002": report("R002", timestamp=""), "R003": report("R003", timestamp="invalid")}
        self.assertIsNone(self.engine.summarize(group(), reports).time_window)

    def test_chain_groups_use_only_supporting_edges_and_preserve_evidence(self):
        chain = group(edges=[edge("R001", "R002", semantic=0.6), edge("R002", "R003", semantic=0.8)])
        precursor = self.engine.summarize(chain, self.reports)
        self.assertIn("2 supporting relationships connect this group.", precursor.evidence)
        self.assertIn(
            "Supporting relationship R001-R002: Prototype supporting relationship: R001-R002",
            precursor.evidence,
        )
        self.assertNotIn("R001-R003", " ".join(precursor.evidence))

    def test_missing_report_ids_and_serialization(self):
        with self.assertRaisesRegex(KeyError, "Missing reports"):
            self.engine.summarize(group(), {"R001": report("R001")})
        payload = self.engine.summarize(group(), self.reports).as_dict()
        self.assertEqual(payload["report_ids"], ["R001", "R002", "R003"])
        json.dumps(payload)

    def test_summarize_all_is_deterministic(self):
        first = group(("R001", "R002"), [edge("R001", "R002")], "P002")
        second = group(("R002", "R003"), [edge("R002", "R003")], "P001")
        result = self.engine.summarize_all(GroupingResult((first, second), ()), self.reports)
        self.assertEqual([item.precursor_id for item in result], ["P001", "P002"])


if __name__ == "__main__":
    unittest.main()
