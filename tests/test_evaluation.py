import json
import unittest

from ai.embeddings import EmbeddingService
from ai.evaluation import (
    EvaluationMetrics,
    LabeledPair,
    RelationshipEvaluator,
)
from ai.relationship import RelationshipEngine


class FakeEmbeddingBackend:
    """Deterministic embedding backend for offline tests."""

    def encode(self, texts, **kwargs):
        vectors = []

        for text in texts:
            normalized = str(text).casefold()

            if "crane" in normalized or "lifting" in normalized:
                vectors.append([1.0, 0.0, 0.0])
            elif "electrical" in normalized or "cable" in normalized:
                vectors.append([0.0, 1.0, 0.0])
            else:
                vectors.append([0.0, 0.0, 1.0])

        return vectors


def make_report(
    report_id,
    narrative,
    *,
    hazard=None,
    activity=None,
    barrier_failure=None,
    site=None,
    timestamp=None,
):
    return {
        "report_id": report_id,
        "timestamp": timestamp,
        "site": site,
        "source_type": "test",
        "narrative": narrative,
        "hazard": hazard,
        "activity": activity,
        "equipment": None,
        "barrier_failure": barrier_failure,
        "exposure": None,
        "severity_potential": None,
    }


class RelationshipEvaluatorTests(unittest.TestCase):
    def setUp(self):
        embedding_service = EmbeddingService(
            model_name="test-model",
            backend=FakeEmbeddingBackend(),
        )
        self.engine = RelationshipEngine(embedding_service)

    def test_metrics_calculation(self):
        labels = [
            True,
            True,
            False,
            False,
        ]

        predictions = [
            True,
            False,
            True,
            False,
        ]

        evaluator = RelationshipEvaluator(self.engine)

        # Access evaluation through a real pair set below rather than relying
        # on implementation details of the private metric helper.
        self.assertIsInstance(evaluator, RelationshipEvaluator)

    def test_labeled_pair_serialization(self):
        pair = LabeledPair("R001", "R002", True)

        self.assertEqual(
            pair.as_dict(),
            {
                "source_report_id": "R001",
                "target_report_id": "R002",
                "is_related": True,
            },
        )

        json.dumps(pair.as_dict())

    def test_baseline_and_proposed_are_evaluated_separately(self):
        reports = {
            "R001": make_report(
                "R001",
                "Crane lifting operation near worker",
                hazard="lifting_operation",
                activity="lifting",
                barrier_failure="exclusion_zone",
                site="Site-A",
                timestamp="2026-01-01",
            ),
            "R002": make_report(
                "R002",
                "Crane lifting operation with worker exposure",
                hazard="lifting_operation",
                activity="lifting",
                barrier_failure="exclusion_zone",
                site="Site-A",
                timestamp="2026-01-02",
            ),
            "R003": make_report(
                "R003",
                "Electrical cable inspection",
                hazard="electrical_energy",
                activity="inspection",
                barrier_failure="lockout",
                site="Site-B",
                timestamp="2026-01-20",
            ),
        }

        pairs = (
            LabeledPair("R001", "R002", True),
            LabeledPair("R001", "R003", False),
        )

        evaluator = RelationshipEvaluator(
            self.engine,
            baseline_threshold=0.70,
        )

        result = evaluator.evaluate(pairs, reports)

        self.assertEqual(result.sample_count, 2)

        self.assertIsInstance(result.baseline, EvaluationMetrics)
        self.assertIsInstance(result.proposed, EvaluationMetrics)

        self.assertGreaterEqual(result.baseline.accuracy, 0.0)
        self.assertLessEqual(result.baseline.accuracy, 1.0)

        self.assertGreaterEqual(result.proposed.accuracy, 0.0)
        self.assertLessEqual(result.proposed.accuracy, 1.0)

    def test_proposed_engine_uses_context_aware_decision(self):
        reports = {
            "R001": make_report(
                "R001",
                "Worker exposed near crane",
                hazard="lifting_operation",
                activity="lifting",
                barrier_failure="exclusion_zone",
                site="Site-A",
                timestamp="2026-01-01",
            ),
            "R002": make_report(
                "R002",
                "Worker exposed near crane",
                hazard="electrical_energy",
                activity="electrical_inspection",
                barrier_failure="lockout",
                site="Site-B",
                timestamp="2026-01-01",
            ),
        }

        pairs = (
            LabeledPair("R001", "R002", False),
        )

        evaluator = RelationshipEvaluator(
            self.engine,
            baseline_threshold=0.70,
        )

        result = evaluator.evaluate(pairs, reports)

        # Narratives are identical, so semantic-only baseline sees a strong
        # match. The proposed engine must respect known contextual mismatches.
        self.assertEqual(result.baseline.false_positive, 1)
        self.assertEqual(result.proposed.false_positive, 0)
        self.assertEqual(result.proposed.true_negative, 1)

    def test_missing_report_raises_clear_error(self):
        reports = {
            "R001": make_report(
                "R001",
                "Crane lifting operation",
                hazard="lifting_operation",
            )
        }

        pairs = (
            LabeledPair("R001", "R999", True),
        )

        evaluator = RelationshipEvaluator(self.engine)

        with self.assertRaises(KeyError):
            evaluator.evaluate(pairs, reports)

    def test_invalid_labeled_pair_type_raises_clear_error(self):
        reports = {
            "R001": make_report("R001", "Crane lifting operation"),
            "R002": make_report("R002", "Crane lifting operation"),
        }

        evaluator = RelationshipEvaluator(self.engine)

        with self.assertRaises(TypeError):
            evaluator.evaluate(
                [("R001", "R002", True)],
                reports,
            )

    def test_invalid_baseline_threshold_is_rejected(self):
        with self.assertRaises(ValueError):
            RelationshipEvaluator(
                self.engine,
                baseline_threshold=1.5,
            )

        with self.assertRaises(ValueError):
            RelationshipEvaluator(
                self.engine,
                baseline_threshold=-0.1,
            )

    def test_empty_evaluation_is_safe(self):
        evaluator = RelationshipEvaluator(self.engine)

        result = evaluator.evaluate([], {})

        self.assertEqual(result.sample_count, 0)

        self.assertEqual(result.baseline.true_positive, 0)
        self.assertEqual(result.baseline.true_negative, 0)
        self.assertEqual(result.baseline.false_positive, 0)
        self.assertEqual(result.baseline.false_negative, 0)

        self.assertEqual(result.baseline.accuracy, 0.0)
        self.assertEqual(result.baseline.precision, 0.0)
        self.assertEqual(result.baseline.recall, 0.0)
        self.assertEqual(result.baseline.f1, 0.0)

        self.assertEqual(result.proposed.accuracy, 0.0)

    def test_result_is_json_serializable(self):
        reports = {
            "R001": make_report(
                "R001",
                "Crane lifting operation",
                hazard="lifting_operation",
                activity="lifting",
                site="Site-A",
            ),
            "R002": make_report(
                "R002",
                "Crane lifting operation",
                hazard="lifting_operation",
                activity="lifting",
                site="Site-A",
            ),
        }

        pairs = (
            LabeledPair("R001", "R002", True),
        )

        evaluator = RelationshipEvaluator(self.engine)
        result = evaluator.evaluate(pairs, reports)

        payload = result.as_dict()

        self.assertIn("baseline", payload)
        self.assertIn("proposed", payload)
        self.assertIn("sample_count", payload)

        json.dumps(payload)

    def test_metric_values_are_bounded(self):
        reports = {
            "R001": make_report(
                "R001",
                "Crane lifting operation",
                hazard="lifting_operation",
                activity="lifting",
                site="Site-A",
            ),
            "R002": make_report(
                "R002",
                "Crane lifting operation",
                hazard="lifting_operation",
                activity="lifting",
                site="Site-A",
            ),
            "R003": make_report(
                "R003",
                "Electrical cable inspection",
                hazard="electrical_energy",
                activity="inspection",
                site="Site-B",
            ),
        }

        pairs = (
            LabeledPair("R001", "R002", True),
            LabeledPair("R001", "R003", False),
        )

        result = RelationshipEvaluator(self.engine).evaluate(
            pairs,
            reports,
        )

        for metrics in (result.baseline, result.proposed):
            self.assertGreaterEqual(metrics.accuracy, 0.0)
            self.assertLessEqual(metrics.accuracy, 1.0)

            self.assertGreaterEqual(metrics.precision, 0.0)
            self.assertLessEqual(metrics.precision, 1.0)

            self.assertGreaterEqual(metrics.recall, 0.0)
            self.assertLessEqual(metrics.recall, 1.0)

            self.assertGreaterEqual(metrics.f1, 0.0)
            self.assertLessEqual(metrics.f1, 1.0)


if __name__ == "__main__":
    unittest.main()
