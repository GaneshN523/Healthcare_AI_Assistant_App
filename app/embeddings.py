"""
Embedding Utilities

Responsibilities:
- Load SentenceTransformer model once (singleton)
- Generate embeddings for text/chunks
- Generate embeddings in batches
- Normalize embeddings for cosine similarity
- Provide helper functions for ingestion and retrieval
"""

from __future__ import annotations

import logging
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """
    Singleton wrapper around SentenceTransformer.

    Prevents reloading the embedding model on every request.
    """

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self) -> SentenceTransformer:
        """
        Load embedding model if not already loaded.
        """
        if self._model is None:
            logger.info(
                "Loading embedding model: %s",
                EMBEDDING_MODEL
            )

            try:
                self._model = SentenceTransformer(
                    EMBEDDING_MODEL
                )

                logger.info(
                    "Embedding model loaded successfully."
                )

            except Exception as exc:
                logger.exception(
                    "Failed to load embedding model."
                )
                raise RuntimeError(
                    f"Unable to load embedding model: {exc}"
                ) from exc

        return self._model

    @property
    def model(self) -> SentenceTransformer:
        """
        Return loaded model.
        """
        return self.load_model()


# Global singleton
embedding_manager = EmbeddingManager()


def normalize_vector(
    vector: np.ndarray
) -> np.ndarray:
    """
    Normalize vector to unit length.

    Useful for cosine similarity retrieval.
    """

    norm = np.linalg.norm(vector)

    if norm == 0:
        return vector

    return vector / norm


def generate_embedding(
    text: str
) -> List[float]:
    """
    Generate embedding for a single text string.

    Returns:
        List[float]
    """

    if not text or not text.strip():
        raise ValueError(
            "Input text cannot be empty."
        )

    try:
        embedding = embedding_manager.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.tolist()

    except Exception as exc:
        logger.exception(
            "Error generating embedding."
        )
        raise RuntimeError(
            f"Embedding generation failed: {exc}"
        ) from exc


def generate_embeddings(
    texts: List[str]
) -> List[List[float]]:
    """
    Generate embeddings for multiple texts.

    Returns:
        List[List[float]]
    """

    if not texts:
        raise ValueError(
            "Text list cannot be empty."
        )

    cleaned_texts = [
        text.strip()
        for text in texts
        if text and text.strip()
    ]

    if not cleaned_texts:
        raise ValueError(
            "No valid texts provided."
        )

    try:
        embeddings = embedding_manager.model.encode(
            cleaned_texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embeddings.tolist()

    except Exception as exc:
        logger.exception(
            "Batch embedding generation failed."
        )

        raise RuntimeError(
            f"Unable to generate embeddings: {exc}"
        ) from exc


def embedding_dimension() -> int:
    """
    Return embedding dimension.

    all-MiniLM-L6-v2 -> 384

    Useful for validation/debugging.
    """

    sample = generate_embedding(
        "dimension check"
    )

    return len(sample)


def cosine_similarity(
    vector_a: List[float],
    vector_b: List[float]
) -> float:
    """
    Compute cosine similarity.

    Useful for testing/debugging.
    """

    a = np.array(vector_a)
    b = np.array(vector_b)

    denominator = (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(a, b) / denominator
    )


def health_check() -> dict:
    """
    Verify embedding model availability.

    Used by API health endpoint.
    """

    try:
        dimension = embedding_dimension()

        return {
            "status": "healthy",
            "model": EMBEDDING_MODEL,
            "dimension": dimension,
        }

    except Exception as exc:
        return {
            "status": "unhealthy",
            "model": EMBEDDING_MODEL,
            "error": str(exc),
        }


if __name__ == "__main__":
    """
    Quick standalone test.
    """

    sample_text = (
        "Can a patient request a medication refill "
        "through telehealth?"
    )

    vector = generate_embedding(
        sample_text
    )

    print(
        f"Embedding dimension: {len(vector)}"
    )

    print(
        f"First 10 values: {vector[:10]}"
    )

    print(
        health_check()
    )