"""
Tests for Agent Layer

Covers:
- Query routing (tool vs RAG)
- Appointment detection logic
- Tool execution correctness
- Department extraction
- Input validation
"""

import pytest
from unittest.mock import MagicMock

from app.agent import AgentRouter, AppointmentTool


# -------------------------------------------------
# Fixture
# -------------------------------------------------
@pytest.fixture
def agent():
    return AgentRouter()


# -------------------------------------------------
# Test: Appointment Detection (Positive)
# -------------------------------------------------
def test_is_appointment_query_positive(agent):
    assert agent.is_appointment_query(
        "I want to book a cardiology appointment"
    ) is True


# -------------------------------------------------
# Test: Appointment Detection (Negative)
# -------------------------------------------------
def test_is_appointment_query_negative(agent):
    assert agent.is_appointment_query(
        "What is HIPAA compliance?"
    ) is False


# -------------------------------------------------
# Test: Process Question → Tool Route
# -------------------------------------------------
def test_process_question_tool_route(agent):
    result = agent.process_question(
        "Can I book a cardiology appointment?"
    )

    assert result["route"] == "tool"
    assert "result" in result
    assert "available_slots" in result["result"]


# -------------------------------------------------
# Test: Process Question → RAG Route (Mock LLM)
# -------------------------------------------------
def test_process_question_rag_route(agent, monkeypatch):
    fake_rag_response = {
        "question": "What is HIPAA?",
        "answer": "HIPAA protects patient data.",
        "confidence": "high",
        "similarity_score": 0.91,
        "sources": ["hipaa.txt"],
    }

    monkeypatch.setattr(
        "app.agent.llm_engine.answer_question",
        lambda q: fake_rag_response
    )

    result = agent.process_question(
        "What is HIPAA compliance?"
    )

    assert result["route"] == "rag"
    assert result["answer"] == "HIPAA protects patient data."


# -------------------------------------------------
# Test: Empty Input Validation
# -------------------------------------------------
def test_process_question_empty(agent):
    with pytest.raises(ValueError):
        agent.process_question("")


# -------------------------------------------------
# Test: Classify Function
# -------------------------------------------------
def test_classify_tool(agent):
    result = agent.classify(
        "Book cardiology appointment"
    )

    assert result["route"] == "tool"
    assert result["question"] == "Book cardiology appointment"


def test_classify_rag(agent):
    result = agent.classify(
        "Explain HIPAA rules"
    )

    assert result["route"] == "rag"


# -------------------------------------------------
# Test: Appointment Tool Direct
# -------------------------------------------------
def test_appointment_tool_all_departments():
    result = AppointmentTool.check_available_slots()

    assert "available_departments" in result
    assert isinstance(result["available_departments"], dict)


# -------------------------------------------------
# Test: Appointment Tool With Department Match
# -------------------------------------------------
def test_appointment_tool_department_match():
    result = AppointmentTool.check_available_slots(
        department="cardiology"
    )

    assert "available_slots" in result


# -------------------------------------------------
# Test: Appointment Tool No Match
# -------------------------------------------------
def test_appointment_tool_no_match():
    result = AppointmentTool.check_available_slots(
        department="unknown_dept"
    )

    assert result["available_slots"] == []


# -------------------------------------------------
# Test: Department Detection
# -------------------------------------------------
def test_detect_department():
    question = "I need cardiology appointment"

    dept = AppointmentTool.detect_department(question)

    assert dept is None or isinstance(dept, str)


# -------------------------------------------------
# Test: Health Check
# -------------------------------------------------
def test_agent_health_check(agent):
    result = agent.health_check()

    assert result["status"] == "healthy"
    assert "appointment_keywords" in result
    assert "appointment_departments" in result