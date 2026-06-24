"""
LLM Layer

Responsibilities:
- Connect to Ollama
- Build grounded RAG prompts
- Generate answers
- Prevent hallucinations
- Return citations and confidence
"""

from __future__ import annotations

import logging
from typing import Dict, Any

import ollama

from app.config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    RAG_PROMPT_TEMPLATE,
)
from app.rag import rag_engine

logger = logging.getLogger(__name__)


class LLMEngine:
    """
    Handles all interactions with Ollama.
    """

    def __init__(self) -> None:
        self.client = ollama.Client(
            host=OLLAMA_HOST
        )

    # =====================================================
    # PROMPT BUILDING
    # =====================================================

    @staticmethod
    def build_prompt(
        question: str,
        context: str
    ) -> str:
        """
        Build grounded RAG prompt.
        """

        return RAG_PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )

    # =====================================================
    # OLLAMA CALL
    # =====================================================

    def generate(
        self,
        prompt: str
    ) -> str:
        """
        Generate response from Ollama.
        """

        try:

            response = self.client.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    # lower temperature = less hallucination
                    "temperature": 0.1,
                    "top_p": 0.9,
                }
            )

            answer = (
                response["message"]["content"]
                .strip()
            )

            logger.info(
                "LLM response generated successfully."
            )

            return answer

        except Exception as exc:

            logger.exception(
                "Ollama generation failed."
            )

            raise RuntimeError(
                f"Unable to generate answer: {exc}"
            ) from exc

    # =====================================================
    # MAIN RAG PIPELINE
    # =====================================================

    def answer_question(
        self,
        question: str
    ) -> Dict[str, Any]:
        """
        Full RAG workflow.

        Question
            ↓
        Retrieve Chunks
            ↓
        Build Prompt
            ↓
        Phi-3
            ↓
        Answer
        """

        if not question or not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        if not rag_engine.knowledge_base_initialized():
            raise RuntimeError(
                "Knowledge base not initialized."
            )

        retrieval = rag_engine.retrieve(
            question
        )

        context = retrieval["context"]
        sources = retrieval["sources"]
        confidence = retrieval["confidence"]
        similarity_score = retrieval[
            "similarity_score"
        ]

        prompt = self.build_prompt(
            question=question,
            context=context
        )

        answer = self.generate(
            prompt
        )

        logger.info(
            "Question processed successfully."
        )

        return {
            "question": question,
            "answer": answer,
            "confidence": confidence,
            "similarity_score": similarity_score,
            "sources": sources,
        }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self) -> Dict[str, Any]:
        """
        Verify Ollama connectivity.
        """

        try:

            response = self.client.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ]
            )

            return {
                "status": "healthy",
                "model": OLLAMA_MODEL,
                "response_received": bool(
                    response
                ),
            }

        except Exception as exc:

            return {
                "status": "unhealthy",
                "model": OLLAMA_MODEL,
                "error": str(exc),
            }

    # =====================================================
    # DIRECT LLM TEST
    # =====================================================

    def direct_chat(
        self,
        message: str
    ) -> str:
        """
        Utility function for testing Ollama
        without retrieval.
        """

        try:

            response = self.client.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )

            return response[
                "message"
            ]["content"]

        except Exception as exc:

            raise RuntimeError(
                f"Ollama error: {exc}"
            ) from exc


# =========================================================
# SINGLETON INSTANCE
# =========================================================

llm_engine = LLMEngine()


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    print(
        "\n=== LLM HEALTH CHECK ==="
    )

    print(
        llm_engine.health_check()
    )

    try:

        response = (
            llm_engine.direct_chat(
                "What is telehealth?"
            )
        )

        print(
            "\n=== DIRECT TEST ==="
        )

        print(response)

    except Exception as exc:

        print(
            f"\nError: {exc}"
        )

llm_engine = LLMEngine()