"""Offline unit tests for the Phase 1 embedding service."""

import unittest

import numpy as np

from ai.embeddings import EmbeddingService


class FakeSentenceTransformer:
    """Deterministic backend used only by unit tests."""

    dimension = 3

    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def encode(self, sentences, *, convert_to_numpy=True):
        self.calls.append(list(sentences))
        vectors = []
        for sentence in sentences:
            lowered = sentence.lower()
            if "electrical" in lowered or "energized" in lowered:
                vectors.append([0.0, 1.0, 0.0])
            elif "maintenance" in lowered or "restricted" in lowered:
                vectors.append([1.0, 0.0, 0.0])
            else:
                vectors.append([0.0, 0.0, 1.0])
        return np.asarray(vectors)


class EmbeddingServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.backend = FakeSentenceTransformer()
        self.service = EmbeddingService(backend=self.backend)

    def test_initialization_uses_injected_backend(self) -> None:
        self.assertIs(self.service._backend, self.backend)
        self.assertEqual(self.service.model_name, "all-MiniLM-L6-v2")

    def test_embeds_one_narrative(self) -> None:
        embedding = self.service.embed_text("Restricted maintenance area access")

        self.assertIsNotNone(embedding)
        np.testing.assert_allclose(embedding, [1.0, 0.0, 0.0])

    def test_embeds_batch_with_expected_shape(self) -> None:
        embeddings = self.service.embed_batch(
            ["Restricted maintenance area", "Electrical maintenance"]
        )

        self.assertEqual(len(embeddings), 2)
        self.assertTrue(all(embedding.shape == (3,) for embedding in embeddings))

    def test_cosine_similarity_for_identical_text_is_high(self) -> None:
        first = self.service.embed_text("Restricted maintenance area")
        second = self.service.embed_text("Restricted maintenance area")

        self.assertGreater(self.service.cosine_similarity(first, second), 0.99)

    def test_clearly_unrelated_narratives_have_low_similarity(self) -> None:
        access = self.service.embed_text("Restricted maintenance area")
        electrical = self.service.embed_text("Electrical work on energized panel")

        self.assertLess(self.service.cosine_similarity(access, electrical), 0.1)

    def test_none_narrative_returns_no_embedding(self) -> None:
        self.assertIsNone(self.service.embed_text(None))

    def test_empty_narrative_returns_no_embedding(self) -> None:
        self.assertIsNone(self.service.embed_text(""))

    def test_whitespace_narrative_returns_no_embedding(self) -> None:
        self.assertIsNone(self.service.embed_text("   \t\n"))

    def test_mixed_batch_preserves_missing_values(self) -> None:
        embeddings = self.service.embed_batch([None, "Electrical maintenance", ""])

        self.assertIsNone(embeddings[0])
        self.assertIsNotNone(embeddings[1])
        self.assertIsNone(embeddings[2])

    def test_batch_order_is_preserved(self) -> None:
        embeddings = self.service.embed_batch(
            ["Electrical maintenance", None, "Restricted maintenance area"]
        )

        np.testing.assert_allclose(embeddings[0], [0.0, 1.0, 0.0])
        self.assertIsNone(embeddings[1])
        np.testing.assert_allclose(embeddings[2], [1.0, 0.0, 0.0])

    def test_missing_or_zero_vector_similarity_is_zero(self) -> None:
        embedding = self.service.embed_text("Restricted maintenance area")

        self.assertEqual(self.service.cosine_similarity(None, embedding), 0.0)
        self.assertEqual(
            self.service.cosine_similarity(np.zeros(3), np.zeros(3)), 0.0
        )


if __name__ == "__main__":
    unittest.main()
