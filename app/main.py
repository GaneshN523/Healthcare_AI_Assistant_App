"""
FastAPI Application Entry Point

Endpoints:
- GET  /
- GET  /health
- POST /ingest
- POST /ask
- DELETE /reset
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.agent import agent_router
from app.config import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
)
from app.embeddings import health_check as embeddings_health
from app.llm import llm_engine
from app.rag import rag_engine


# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - "
        "%(name)s - "
        "%(levelname)s - "
        "%(message)s"
    ),
)

logger = logging.getLogger(__name__)


# =====================================================
# APPLICATION LIFECYCLE
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.

    Replaces deprecated:
    - @app.on_event("startup")
    - @app.on_event("shutdown")
    """

    # -----------------------------------------
    # STARTUP
    # -----------------------------------------

    logger.info(
        "Healthcare AI Assistant starting..."
    )

    try:

        rag_status = (
            rag_engine.health_check()
        )

        logger.info(
            "Vector Store Status: %s",
            rag_status
        )

    except Exception as exc:

        logger.error(
            "Startup check failed: %s",
            exc
        )

    yield

    # -----------------------------------------
    # SHUTDOWN
    # -----------------------------------------

    logger.info(
        "Healthcare AI Assistant shutting down..."
    )


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)


# =====================================================
# PYDANTIC MODELS
# =====================================================

class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="User question"
    )


class Source(BaseModel):
    document: Optional[str] = None
    chunk_id: Optional[int] = None
    chunk: Optional[str] = None


class AskResponse(BaseModel):
    route: str
    answer: Optional[str] = None
    confidence: Optional[str] = None
    similarity_score: Optional[float] = None
    sources: Optional[List[Source]] = None
    result: Optional[Dict[str, Any]] = None


# =====================================================
# ROOT
# =====================================================

@app.get("/")
def root() -> Dict[str, str]:

    return {
        "message": "Healthcare AI Assistant API",
        "version": API_VERSION,
    }


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
def health() -> Dict[str, Any]:
    """
    Verify application health.
    """

    return {
        "status": "healthy",
        "services": {
            "embeddings": embeddings_health(),
            "llm": llm_engine.health_check(),
            "vector_store": rag_engine.health_check(),
            "agent": agent_router.health_check(),
        },
    }


# =====================================================
# INGEST DOCUMENTS
# =====================================================

@app.post("/ingest")
def ingest_documents() -> Dict[str, Any]:
    """
    Read healthcare documents,
    chunk them,
    embed them,
    store them in ChromaDB.
    """

    try:

        logger.info(
            "Document ingestion started."
        )

        result = (
            rag_engine.ingest_documents()
        )

        logger.info(
            "Document ingestion completed."
        )

        return result

    except FileNotFoundError as exc:

        logger.exception(
            "Document directory issue."
        )

        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except Exception as exc:

        logger.exception(
            "Ingestion failed."
        )

        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {exc}"
        )


# =====================================================
# ASK QUESTION
# =====================================================

@app.post(
    "/ask",
    response_model=AskResponse
)
def ask(
    request: AskRequest
) -> Dict[str, Any]:
    """
    Main question answering endpoint.

    Routes:

    Appointment Query
        ↓
    Appointment Tool

    Knowledge Query
        ↓
    RAG
        ↓
    Phi-3
    """

    question = request.question.strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:

        logger.info(
            "Question received: %s",
            question
        )

        response = (
            agent_router.process_question(
                question
            )
        )

        logger.info(
            "Question processed successfully."
        )

        return response

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

    except Exception as exc:

        logger.exception(
            "Unexpected error."
        )

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {exc}"
        )


# =====================================================
# RESET VECTOR STORE
# =====================================================

@app.delete("/reset")
def reset_knowledge_base() -> Dict[str, Any]:
    """
    Development endpoint.

    Clears ChromaDB.
    """

    try:

        result = (
            rag_engine.reset_knowledge_base()
        )

        logger.warning(
            "Knowledge base reset."
        )

        return result

    except Exception as exc:

        logger.exception(
            "Reset failed."
        )

        raise HTTPException(
            status_code=500,
            detail=f"Reset failed: {exc}"
        )


# =====================================================
# LOCAL DEVELOPMENT
# =====================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

