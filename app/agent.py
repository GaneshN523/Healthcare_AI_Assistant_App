"""
Agent Layer

Responsibilities:
- Route user requests
- Decide: Tool or RAG
- Handle appointment-related queries
- Forward knowledge questions to LLM/RAG
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List

from app.config import (
    APPOINTMENT_KEYWORDS,
    MOCK_APPOINTMENT_SLOTS,
)
from app.llm import llm_engine

logger = logging.getLogger(__name__)


class AppointmentTool:
    """
    Mock appointment scheduling tool.

    This satisfies the project requirement
    for an agent/tool workflow.
    """

    @staticmethod
    def check_available_slots(
        department: str | None = None
    ) -> Dict[str, Any]:
        """
        Return available appointment slots.

        If department is provided:
            return department slots

        Otherwise:
            return all slots
        """

        if department:

            for dept_name, slots in (
                MOCK_APPOINTMENT_SLOTS.items()
            ):

                if (
                    department.lower()
                    in dept_name.lower()
                ):
                    return {
                        "tool": "appointment_tool",
                        "department": dept_name,
                        "available_slots": slots,
                    }

            return {
                "tool": "appointment_tool",
                "department": department,
                "available_slots": [],
                "message": (
                    "No slots found for the requested "
                    "department."
                ),
            }

        return {
            "tool": "appointment_tool",
            "available_departments":
                MOCK_APPOINTMENT_SLOTS
        }

    @staticmethod
    def detect_department(
        question: str
    ) -> str | None:
        """
        Detect department from query.

        Very simple rule-based logic.
        """

        departments = (
            MOCK_APPOINTMENT_SLOTS.keys()
        )

        question_lower = (
            question.lower()
        )

        for department in departments:

            if (
                department.lower()
                in question_lower
            ):
                return department

        return None


class AgentRouter:
    """
    Main agent router.
    """

    def __init__(self) -> None:
        self.appointment_tool = (
            AppointmentTool()
        )

    # =====================================================
    # QUERY CLASSIFICATION
    # =====================================================

    @staticmethod
    def is_appointment_query(
        question: str
    ) -> bool:
        """
        Determine whether query should
        use appointment tool.
        """

        question_lower = (
            question.lower()
        )

        return any(
            keyword in question_lower
            for keyword in APPOINTMENT_KEYWORDS
        )

    # =====================================================
    # TOOL EXECUTION
    # =====================================================

    def handle_tool_request(
        self,
        question: str
    ) -> Dict[str, Any]:
        """
        Execute appointment tool.
        """

        department = (
            self.appointment_tool
            .detect_department(question)
        )

        result = (
            self.appointment_tool
            .check_available_slots(
                department
            )
        )

        logger.info(
            "Appointment tool invoked."
        )

        return {
            "route": "tool",
            "result": result,
        }

    # =====================================================
    # RAG EXECUTION
    # =====================================================

    def handle_rag_request(
        self,
        question: str
    ) -> Dict[str, Any]:
        """
        Forward request to RAG/LLM.
        """

        logger.info(
            "Routed to RAG system."
        )

        rag_response = (
            llm_engine.answer_question(
                question
            )
        )

        return {
            "route": "rag",
            **rag_response,
        }

    # =====================================================
    # MAIN ROUTER
    # =====================================================

    def process_question(
        self,
        question: str
    ) -> Dict[str, Any]:
        """
        Main entry point.

        Question
            ↓
        Appointment?
            ↓
         Yes      No
          ↓        ↓
        Tool      RAG
        """

        if not question:
            raise ValueError(
                "Question cannot be empty."
            )

        question = question.strip()

        if not question:
            raise ValueError(
                "Question cannot be empty."
            )

        logger.info(
            "Received question: %s",
            question
        )

        if self.is_appointment_query(
            question
        ):
            return self.handle_tool_request(
                question
            )

        return self.handle_rag_request(
            question
        )

    # =====================================================
    # DEBUG ROUTING
    # =====================================================

    def classify(
        self,
        question: str
    ) -> Dict[str, str]:
        """
        Useful for testing.
        """

        route = (
            "tool"
            if self.is_appointment_query(
                question
            )
            else "rag"
        )

        return {
            "question": question,
            "route": route,
        }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(
        self
    ) -> Dict[str, Any]:

        return {
            "status": "healthy",
            "appointment_departments":
                list(
                    MOCK_APPOINTMENT_SLOTS.keys()
                ),
            "appointment_keywords":
                APPOINTMENT_KEYWORDS,
        }


# =========================================================
# SINGLETON INSTANCE
# =========================================================

agent_router = AgentRouter()


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    test_questions: List[str] = [
        (
            "Can I book a cardiology "
            "appointment tomorrow?"
        ),
        (
            "Can a patient request a "
            "medication refill through "
            "telehealth?"
        ),
    ]

    for question in test_questions:

        print("\n" + "=" * 60)
        print("QUESTION:")
        print(question)

        try:

            result = (
                agent_router.process_question(
                    question
                )
            )

            print("\nRESULT:")
            print(result)

        except Exception as exc:

            print(
                f"\nERROR: {exc}"
            )