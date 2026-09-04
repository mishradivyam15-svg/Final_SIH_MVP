"""Sentence embedding helpers for safety-report narratives.

Missing or blank narratives produce ``None`` embeddings. Cosine comparisons
involving a missing or zero-vector embedding return ``0.0``.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

import numpy as np


class SentenceTransformerBackend(Protocol):
    """Minimum interface required from a Sentence Transformer backend."""

    def encode(
        self, sentences: Sequence[str], *, convert_to_numpy: bool = True
    ) -> np.ndarray:
        """Return one embedding vector for each supplied sentence."""


class EmbeddingService:
    """Create and compare sentence embeddings for safety-report narratives."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        backend: SentenceTransformerBackend | None = None,
    ) -> None:
        self.model_name = model_name
        self._backend = backend or self._load_backend(model_name)

    @staticmethod
    def _load_backend(model_name: str) -> SentenceTransformerBackend:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(model_name)

    def embed_text(self, narrative: str | None) -> np.ndarray | None:
        """Embed one narrative, returning ``None`` for missing or blank text."""

        return self.embed_batch([narrative])[0]

    def embed_batch(
        self, narratives: Sequence[str | None]
    ) -> list[np.ndarray | None]:
        """Embed narratives while preserving input order and missing values."""

        embeddings: list[np.ndarray | None] = [None] * len(narratives)
        valid_items = [
            (index, narrative.strip())
            for index, narrative in enumerate(narratives)
            if self._has_text(narrative)
        ]

        if not valid_items:
            return embeddings

        valid_indices, valid_narratives = zip(*valid_items)
        encoded = np.asarray(
            self._backend.encode(valid_narratives, convert_to_numpy=True), dtype=float
        )

        if encoded.ndim == 1:
            encoded = encoded.reshape(1, -1)
        if encoded.shape[0] != len(valid_indices):
            raise ValueError("Embedding backend returned an unexpected batch size.")

        for index, embedding in zip(valid_indices, encoded, strict=True):
            embeddings[index] = embedding

        return embeddings

    @staticmethod
    def cosine_similarity(
        first: np.ndarray | None, second: np.ndarray | None
    ) -> float:
        """Return cosine similarity, safely treating missing vectors as unrelated."""

        if first is None or second is None:
            return 0.0

        first_vector = np.asarray(first, dtype=float)
        second_vector = np.asarray(second, dtype=float)
        denominator = np.linalg.norm(first_vector) * np.linalg.norm(second_vector)

        if denominator == 0 or not np.isfinite(denominator):
            return 0.0

        similarity = float(np.dot(first_vector, second_vector) / denominator)
        return similarity if np.isfinite(similarity) else 0.0

    @staticmethod
    def _has_text(narrative: str | None) -> bool:
        return isinstance(narrative, str) and bool(narrative.strip())
