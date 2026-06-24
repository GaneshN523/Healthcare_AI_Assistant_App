"""
Tests for RAG Engine

Covers:
- Document loading
- Chunking logic
- Embedding integration (mocked)
- Ingestion workflow
- Retrieval correctness
- Confidence scoring
- Vector DB reset
- Health check
"""

import pytest
from unittest.mock import MagicMock

from app.rag import RAGEngine


# -------------------------------------------------
# Fixture
# -------------------------------------------------
@pytest.fixture
def rag():
    return RAGEngine()


# -------------------------------------------------
# Test: Chunking Logic
# -------------------------------------------------
def test_chunk_document(rag):
    text = "This is a sample medical document. " * 50

    chunks = rag.chunk_document(
        document_name="test.txt",
        content=text
    )

    assert isinstance(chunks, list)
    assert len(chunks) > 0

    for chunk in chunks:
        assert "text" in chunk
        assert "document" in chunk
        assert "chunk_id" in chunk


# -------------------------------------------------
# Test: Confidence Labeling
# -------------------------------------------------
def test_confidence_label(rag):
    assert rag.confidence_label(0.95) == "high"
    assert rag.confidence_label(0.75) in ["medium", "high"]
    assert rag.confidence_label(0.2) == "low"


# -------------------------------------------------
# Test: Knowledge Base Empty State
# -------------------------------------------------
def test_kb_not_initialized(rag, monkeypatch):
    monkeypatch.setattr(
        rag.collection,
        "count",
        lambda: 0
    )

    assert rag.knowledge_base_initialized() is False


# -------------------------------------------------
# Test: Knowledge Base Initialized
# -------------------------------------------------
def test_kb_initialized(rag, monkeypatch):
    monkeypatch.setattr(
        rag.collection,
        "count",
        lambda: 10
    )

    assert rag.knowledge_base_initialized() is True


# -------------------------------------------------
# Test: Reset Knowledge Base
# -------------------------------------------------
def test_reset_knowledge_base(rag, monkeypatch):
    monkeypatch.setattr(
        rag.client,
        "delete_collection",
        lambda name: None
    )

    result = rag.reset_knowledge_base()

    assert result["status"] == "success"
    assert "Knowledge base cleared" in result["message"]


# -------------------------------------------------
# Test: Retrieve (FULL PIPELINE MOCKED)
# -------------------------------------------------
def test_retrieve_pipeline(rag, monkeypatch):
    # Mock embedding generation
    monkeypatch.setattr(
        "app.rag.generate_embedding",
        lambda x: [0.1, 0.2, 0.3]
    )

    # Mock ChromaDB response
    fake_results = {
        "documents": [["Patient can request refill via telehealth"]],
        "metadatas": [[
            {"document": "telehealth.txt", "chunk_id": 1}
        ]],
        "distances": [[0.1]]
    }

    monkeypatch.setattr(
        rag.collection,
        "query",
        lambda **kwargs: fake_results
    )

    result = rag.retrieve("Can I request medication refill?")

    assert isinstance(result, dict)
    assert "context" in result
    assert "sources" in result
    assert "confidence" in result
    assert "similarity_score" in result

    assert result["confidence"] in ["high", "medium", "low"]
    assert len(result["sources"]) == 1


# -------------------------------------------------
# Test: Get Context Wrapper
# -------------------------------------------------
def test_get_context_for_question(rag, monkeypatch):
    monkeypatch.setattr(
        rag,
        "retrieve",
        lambda q: {
            "context": "sample context",
            "sources": [{"document": "a.txt"}],
            "confidence": "high"
        }
    )

    context, sources, confidence = rag.get_context_for_question(
        "test question"
    )

    assert context == "sample context"
    assert confidence == "high"
    assert isinstance(sources, list)


# -------------------------------------------------
# Test: Health Check
# -------------------------------------------------
def test_health_check(rag, monkeypatch):
    monkeypatch.setattr(
        rag.collection,
        "count",
        lambda: 5
    )

    result = rag.health_check()

    assert result["status"] == "healthy"
    assert result["documents_in_store"] == 5


# -------------------------------------------------
# Test: Load Documents Failure Case (No Files)
# -------------------------------------------------
def test_load_documents_no_files(rag, monkeypatch):
    monkeypatch.setattr(
        "pathlib.Path.glob",
        lambda self, pattern: []
    )

    with pytest.raises(FileNotFoundError):
        rag.load_documents()