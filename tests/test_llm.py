"""
Tests for LLM Engine

Covers:
- Prompt building
- RAG pipeline flow
- Input validation
- Health check behavior
- Direct chat (mocked)
"""

import pytest
from unittest.mock import MagicMock

from app.llm import LLMEngine


# -------------------------------------------------
# Fixture: LLM Engine Instance
# -------------------------------------------------
@pytest.fixture
def llm():
    return LLMEngine()


# -------------------------------------------------
# Test: Prompt Building
# -------------------------------------------------
def test_build_prompt(llm):
    question = "What is telehealth?"
    context = "Telehealth allows remote consultation."

    prompt = llm.build_prompt(question, context)

    assert isinstance(prompt, str)
    assert question in prompt
    assert context in prompt


# -------------------------------------------------
# Test: Empty Question Validation
# -------------------------------------------------
def test_answer_question_empty_input(llm):
    with pytest.raises(ValueError):
        llm.answer_question("")


# -------------------------------------------------
# Test: Knowledge Base Not Initialized
# -------------------------------------------------
def test_answer_question_kb_not_initialized(llm, monkeypatch):
    monkeypatch.setattr(
        "app.llm.rag_engine.knowledge_base_initialized",
        lambda: False
    )

    with pytest.raises(RuntimeError):
        llm.answer_question("What is HIPAA?")


# -------------------------------------------------
# Mock RAG Engine Response
# -------------------------------------------------
def test_answer_question_flow(llm, monkeypatch):
    fake_retrieval = {
        "context": "HIPAA protects patient data.",
        "sources": ["hipaa.txt"],
        "confidence": 0.85,
        "similarity_score": 0.92,
    }

    monkeypatch.setattr(
        "app.llm.rag_engine.retrieve",
        lambda q: fake_retrieval
    )

    # Mock Ollama generate
    monkeypatch.setattr(
        llm,
        "generate",
        lambda prompt: "HIPAA ensures data privacy."
    )

    result = llm.answer_question("What is HIPAA?")

    assert isinstance(result, dict)
    assert result["question"] == "What is HIPAA?"
    assert "answer" in result
    assert result["sources"] == ["hipaa.txt"]
    assert result["confidence"] == 0.85
    assert result["similarity_score"] == 0.92


# -------------------------------------------------
# Test: Health Check (Mocked success)
# -------------------------------------------------
def test_health_check_success(llm, monkeypatch):
    fake_response = {
        "message": {"content": "Hello"}
    }

    monkeypatch.setattr(
        llm.client,
        "chat",
        lambda *args, **kwargs: fake_response
    )

    result = llm.health_check()

    assert result["status"] == "healthy"
    assert result["model"] is not None


# -------------------------------------------------
# Test: Health Check Failure
# -------------------------------------------------
def test_health_check_failure(llm, monkeypatch):
    def raise_error(*args, **kwargs):
        raise Exception("Ollama down")

    monkeypatch.setattr(
        llm.client,
        "chat",
        raise_error
    )

    result = llm.health_check()

    assert result["status"] == "unhealthy"
    assert "error" in result


# -------------------------------------------------
# Test: Direct Chat (Mocked)
# -------------------------------------------------
def test_direct_chat(llm, monkeypatch):
    monkeypatch.setattr(
        llm.client,
        "chat",
        lambda *args, **kwargs: {
            "message": {"content": "Telehealth is remote care."}
        }
    )

    response = llm.direct_chat("What is telehealth?")

    assert isinstance(response, str)
    assert "Telehealth" in response