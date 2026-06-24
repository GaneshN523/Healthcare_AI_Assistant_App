"""
Tests for Embedding Utilities

Covers:
- Single embedding generation
- Batch embedding generation
- Embedding dimension check
- Cosine similarity
- Health check
- Edge cases (empty input handling)
"""

import pytest

from app.embeddings import (
    generate_embedding,
    generate_embeddings,
    embedding_dimension,
    cosine_similarity,
    health_check,
)


# -----------------------------
# Test: Single Embedding
# -----------------------------
def test_generate_embedding():
    text = "Patient can request medication refill via telehealth."

    vector = generate_embedding(text)

    assert isinstance(vector, list)
    assert len(vector) > 0
    assert all(isinstance(x, float) for x in vector)


# -----------------------------
# Test: Batch Embeddings
# -----------------------------
def test_generate_embeddings():
    texts = [
        "Telehealth allows remote consultation.",
        "HIPAA ensures patient privacy.",
        "Insurance covers hospital expenses."
    ]

    vectors = generate_embeddings(texts)

    assert isinstance(vectors, list)
    assert len(vectors) == 3
    assert all(isinstance(v, list) for v in vectors)
    assert len(vectors[0]) > 0


# -----------------------------
# Test: Empty Input (Single)
# -----------------------------
def test_generate_embedding_empty():
    with pytest.raises(ValueError):
        generate_embedding("")


# -----------------------------
# Test: Empty Input (Batch)
# -----------------------------
def test_generate_embeddings_empty():
    with pytest.raises(ValueError):
        generate_embeddings([])


# -----------------------------
# Test: Embedding Dimension
# -----------------------------
def test_embedding_dimension():
    dim = embedding_dimension()

    assert isinstance(dim, int)
    assert dim > 0
    assert dim == 384  # all-MiniLM-L6-v2 expected dimension


# -----------------------------
# Test: Cosine Similarity
# -----------------------------
def test_cosine_similarity():
    v1 = generate_embedding("healthcare telehealth system")
    v2 = generate_embedding("telehealth healthcare system")

    score = cosine_similarity(v1, v2)

    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


# -----------------------------
# Test: Health Check
# -----------------------------
def test_health_check():
    result = health_check()

    assert isinstance(result, dict)
    assert "status" in result
    assert result["model"] is not None
    assert result["dimension"] == 384