"""Offline tests using Prototype / Representative Data only."""

import unittest

import numpy as np

from ai.embeddings import EmbeddingService
from ai.relationship import (
    RelationshipConfig,
    RelationshipEngine,
    match_activity,
    match_barrier_failure,
    match_equipment,
    match_exposure,
    match_hazard,
    match_site,
    temporal_relation,
)


class PrototypeEmbeddingService:
    """Deterministic embedding substitute used only in relationship unit tests."""

    def embed_text(self, narrative):
        if narrative is None:
            return None

        text = narrative.casefold()

        if "restricted" in text or "controlled" in text or "same wording" in text:
            return np.array([1.0, 0.0, 0.0])

        if "electrical" in text or "energized" in text:
            return np.array([0.0, 1.0, 0.0])

        return np.array([0.0, 0.0, 1.0])

    @staticmethod
    def cosine_similarity(first, second):
        return EmbeddingService.cosine_similarity(first, second)


class FixedSimilarityEmbeddingService:
    """Offline backend that supplies a chosen semantic score for one test."""

    def __init__(self, similarity):
        self.similarity = similarity

    @staticmethod
    def embed_text(narrative):
        return narrative

    def cosine_similarity(self, first, second):
        return self.similarity


def report(**overrides):
    """Build Prototype / Representative Data, never operational report data."""

    base = {
        "report_id": "R001",
        "timestamp": "2026-01-10T09:00:00",
        "site": "Site-A",
        "source_type": "prototype",
        "narrative": "Worker entered a restricted maintenance area without authorization.",
        "hazard": "working_at_height",
        "activity": "maintenance",
        "equipment": "ladder",
        "barrier_failure": "fall_protection_missing",
        "exposure": "elevated work area",
        "severity_potential": 0.6,
    }

    base.update(overrides)
    return base


class RelationshipEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = RelationshipEngine(PrototypeEmbeddingService())

    def test_identical_reports_are_strongly_related(self):
        result = self.engine.compare(
            report(),
            report(report_id="R002"),
        )

        self.assertTrue(result.is_related)
        self.assertGreater(result.relationship_strength, 0.95)

    def test_differently_worded_related_reports_are_related(self):
        result = self.engine.compare(
            report(),
            report(
                report_id="R002",
                narrative=(
                    "Technician accessed the controlled maintenance "
                    "zone without clearance."
                ),
                timestamp="2026-01-12T09:00:00",
            ),
        )

        self.assertTrue(result.is_related)
        self.assertGreater(result.semantic_similarity, 0.99)

    def test_unrelated_reports_are_not_related(self):
        result = self.engine.compare(
            report(),
            report(
                report_id="R002",
                narrative=(
                    "Electrical maintenance was performed on "
                    "an energized panel."
                ),
                hazard="electrical_energy",
                activity="electrical_work",
                barrier_failure="lockout_missing",
                site="Site-B",
                timestamp="2026-07-10T09:00:00",
            ),
        )

        self.assertFalse(result.is_related)

    def test_hazard_matching_handles_same_and_different_values(self):
        self.assertEqual(
            match_hazard(
                "Working at Height",
                "working_at_height",
            ),
            1.0,
        )

        self.assertEqual(
            match_hazard(
                "working_at_height",
                "electrical_energy",
            ),
            0.0,
        )

    def test_activity_matching_handles_same_and_different_values(self):
        self.assertEqual(
            match_activity(
                "Maintenance",
                "maintenance",
            ),
            1.0,
        )

        self.assertEqual(
            match_activity(
                "maintenance",
                "lifting",
            ),
            0.0,
        )

    def test_same_activity_with_different_hazard_is_inspectable(self):
        result = self.engine.compare(
            report(),
            report(
                report_id="R002",
                hazard="electrical_energy",
            ),
        )

        self.assertEqual(result.activity_match, 1.0)
        self.assertEqual(result.hazard_match, 0.0)

        self.assertIn(
            "Different known hazards: "
            "working_at_height vs electrical_energy",
            result.evidence,
        )

    def test_barrier_matching_and_missing_value_are_safe(self):
        self.assertEqual(
            match_barrier_failure(
                "SOP violation",
                "sop_violation",
            ),
            1.0,
        )

        self.assertEqual(
            match_barrier_failure(
                "SOP violation",
                None,
            ),
            0.5,
        )

    def test_equipment_matching_supports_multi_label_values(self):
        self.assertEqual(
            match_equipment(
                "scissor_lift|crane|truck",
                "crane|truck",
            ),
            1.0,
        )

        self.assertEqual(
            match_equipment(
                "scissor_lift",
                "crane",
            ),
            0.0,
        )

        self.assertEqual(
            match_equipment(
                "scissor_lift|crane",
                None,
            ),
            0.5,
        )

    def test_exposure_matching_supports_multi_label_values(self):
        self.assertEqual(
            match_exposure(
                "struck_by|fall_from_height",
                "fall_from_height",
            ),
            1.0,
        )

        self.assertEqual(
            match_exposure(
                "struck_by",
                "electrical_exposure",
            ),
            0.0,
        )

        self.assertEqual(
            match_exposure(
                "struck_by",
                None,
            ),
            0.5,
        )

    def test_site_matching_handles_same_and_different_values(self):
        self.assertEqual(
            match_site(
                "Site-A",
                "site_a",
            ),
            1.0,
        )

        self.assertEqual(
            match_site(
                "Site-A",
                "Site-B",
            ),
            0.0,
        )

    def test_same_day_temporal_relation_is_strong(self):
        self.assertEqual(
            temporal_relation(
                "2026-01-10",
                "2026-01-10T22:00:00",
            ),
            1.0,
        )

    def test_distant_temporal_relation_is_weaker(self):
        self.assertLess(
            temporal_relation(
                "2026-01-10",
                "2026-07-10",
            ),
            0.01,
        )

    def test_missing_and_invalid_timestamps_are_neutral(self):
        self.assertEqual(
            temporal_relation(
                None,
                "2026-01-10",
            ),
            0.5,
        )

        self.assertEqual(
            temporal_relation(
                "not-a-date",
                "2026-01-10",
            ),
            0.5,
        )

    def test_relationship_strength_stays_in_range(self):
        result = self.engine.compare(
            report(
                narrative=None,
            ),
            report(
                report_id="R002",
                narrative=None,
            ),
        )

        self.assertGreaterEqual(
            result.relationship_strength,
            0.0,
        )

        self.assertLessEqual(
            result.relationship_strength,
            1.0,
        )

    def test_threshold_is_configurable(self):
        pair = report(
            report_id="R002",
            activity="lifting",
        )

        engine = RelationshipEngine(
            PrototypeEmbeddingService()
        )

        score = engine.compare(
            report(),
            pair,
        ).relationship_strength

        strict = RelationshipEngine(
            PrototypeEmbeddingService(),
            RelationshipConfig(
                related_threshold=min(
                    1.0,
                    score + 0.01,
                )
            ),
        )

        permissive = RelationshipEngine(
            PrototypeEmbeddingService(),
            RelationshipConfig(
                related_threshold=score,
            ),
        )

        self.assertFalse(
            strict.compare(
                report(),
                pair,
            ).is_related
        )

        self.assertTrue(
            permissive.compare(
                report(),
                pair,
            ).is_related
        )

    def test_evidence_is_generated_from_computed_fields(self):
        result = self.engine.compare(
            report(),
            report(report_id="R002"),
        )

        self.assertIn(
            "Semantic similarity: 1.00",
            result.evidence,
        )

        self.assertIn(
            "Same hazard: working_at_height",
            result.evidence,
        )

        self.assertIn(
            "Same equipment: ladder",
            result.evidence,
        )

        self.assertIn(
            "Reports occurred 0 days apart",
            result.evidence,
        )

    def test_missing_values_do_not_create_fabricated_evidence(self):
        result = self.engine.compare(
            report(
                barrier_failure=None,
                timestamp=None,
            ),
            report(
                report_id="R002",
                barrier_failure=None,
                timestamp=None,
            ),
        )

        self.assertFalse(
            any(
                "Same barrier" in item
                for item in result.evidence
            )
        )

        self.assertFalse(
            any(
                "Different known barrier" in item
                for item in result.evidence
            )
        )

        self.assertFalse(
            any(
                "days apart" in item
                for item in result.evidence
            )
        )

        self.assertIn(
            "Unknown contextual fields: barrier failure",
            result.evidence,
        )

        self.assertIn(
            "Temporal evidence unknown: one or both timestamps "
            "are missing or invalid",
            result.evidence,
        )

    def test_high_semantic_and_temporal_scores_need_contextual_evidence(self):
        result = self.engine.compare(
            report(),
            report(
                report_id="R002",
                narrative="Same wording shared by both reports.",
                hazard=None,
                activity=None,
                equipment=None,
                barrier_failure=None,
                exposure=None,
                site=None,
            ),
        )

        self.assertGreaterEqual(
            result.relationship_strength,
            self.engine.config.related_threshold,
        )
        self.assertFalse(result.is_related)
        self.assertIn(
            "Contextual evidence insufficient: no known safety-context match.",
            result.evidence,
        )

        self.assertFalse(
            result.is_related
        )

        self.assertIn(
            "Contextual evidence insufficient: hazard, activity, "
            "equipment, barrier failure, exposure, and site are unknown.",
            result.evidence,
        )

    def test_one_known_contextual_match_allows_related_decision(self):
        result = self.engine.compare(
            report(
                narrative="Same wording shared by both reports.",
                activity=None,
                equipment=None,
                barrier_failure=None,
                exposure=None,
                site=None,
            ),
            report(
                report_id="R002",
                narrative="Same wording shared by both reports.",
                activity=None,
                equipment=None,
                barrier_failure=None,
                exposure=None,
                site=None,
            ),
        )

        self.assertGreater(
            result.relationship_strength,
            0.70,
        )

        self.assertTrue(
            result.is_related
        )

        self.assertIn(
            "Same hazard: working_at_height",
            result.evidence,
        )

    def test_known_contextual_mismatch_cannot_be_overridden_by_unknowns(self):
        result = self.engine.compare(
            report(
                narrative="Same wording shared by both reports.",
            ),
            report(
                report_id="R002",
                narrative="Same wording shared by both reports.",
                hazard="electrical_energy",
                activity=None,
                equipment=None,
                barrier_failure=None,
                exposure=None,
                site=None,
            ),
        )

        self.assertAlmostEqual(
            result.relationship_strength,
            0.575,
        )

        self.assertFalse(
            result.is_related
        )

        self.assertIn(
            "Different known hazards: "
            "working_at_height vs electrical_energy",
            result.evidence,
        )

    def test_moderate_semantic_similarity_with_strong_context_is_related(self):
        engine = RelationshipEngine(
            FixedSimilarityEmbeddingService(0.5)
        )

        result = engine.compare(
            report(),
            report(report_id="R002"),
        )

        self.assertAlmostEqual(
            result.relationship_strength,
            0.875,
        )

        self.assertTrue(
            result.is_related
        )

    def test_exact_threshold_follows_greater_than_or_equal_rule(self):
        first = report()

        second = report(
            report_id="R002",
            narrative="Electrical work on an energized prototype panel.",
        )

        result = self.engine.compare(
            first,
            second,
        )

        threshold_engine = RelationshipEngine(
            PrototypeEmbeddingService(),
            RelationshipConfig(
                related_threshold=result.relationship_strength
            ),
        )

        threshold_result = threshold_engine.compare(
            first,
            second,
        )

        self.assertTrue(
            threshold_result.is_related
        )

    def test_as_dict_contains_the_complete_relationship_api(self):
        result = self.engine.compare(
            report(),
            report(report_id="R002"),
        )

        self.assertEqual(
            set(result.as_dict()),
            {
                "source_report_id",
                "target_report_id",
                "semantic_similarity",
                "hazard_match",
                "activity_match",
                "equipment_match",
                "barrier_match",
                "exposure_match",
                "site_match",
                "temporal_relation",
                "relationship_strength",
                "is_related",
                "evidence",
            },
        )

    def test_semantic_similarity_is_exposed_in_result(self):
        result = self.engine.compare(
            report(),
            report(report_id="R002"),
        )

        self.assertEqual(
            result.semantic_similarity,
            1.0,
        )

        self.assertEqual(
            result.as_dict()["semantic_similarity"],
            1.0,
        )

    def test_context_changes_a_superficial_semantic_match(self):
        result = self.engine.compare(
            report(
                narrative="Same wording describes a maintenance event.",
            ),
            report(
                report_id="R002",
                narrative="Same wording describes an electrical event.",
                hazard="electrical_energy",
                activity="electrical_work",
            ),
        )

        self.assertEqual(
            result.semantic_similarity,
            1.0,
        )

        self.assertFalse(
            result.is_related
        )

        self.assertIn(
            "Different known hazards: "
            "working_at_height vs electrical_energy",
            result.evidence,
        )


if __name__ == "__main__":
    unittest.main()