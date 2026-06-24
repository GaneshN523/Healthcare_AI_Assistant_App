"""
Application Configuration

Centralized configuration for the Healthcare AI Assistant.

Modify values here instead of hardcoding them throughout
the application.
"""

from pathlib import Path


# =====================================================
# PROJECT PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
VECTOR_STORE_DIR = BASE_DIR / "vector_store"


# =====================================================
# EMBEDDING SETTINGS
# =====================================================

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

TOP_K_RESULTS = 3


# =====================================================
# CHROMADB SETTINGS
# =====================================================

CHROMA_COLLECTION_NAME = "healthcare_documents"

CHROMA_PERSIST_DIRECTORY = str(VECTOR_STORE_DIR)


# =====================================================
# OLLAMA SETTINGS
# =====================================================

OLLAMA_MODEL = "phi3"

# Default local Ollama endpoint
OLLAMA_HOST = "http://localhost:11434"


# =====================================================
# API SETTINGS
# =====================================================

API_TITLE = "Healthcare AI Assistant"

API_DESCRIPTION = """
Healthcare Retrieval-Augmented Generation (RAG) Assistant.

Features:
- Healthcare document ingestion
- Semantic search using embeddings
- ChromaDB vector storage
- Ollama-powered answer generation
- Citations and confidence scores
- Simple agent workflow
"""

API_VERSION = "1.0.0"


# =====================================================
# RETRIEVAL SETTINGS
# =====================================================

MIN_CONFIDENCE_HIGH = 0.80
MIN_CONFIDENCE_MEDIUM = 0.60


# =====================================================
# AGENT SETTINGS
# =====================================================

APPOINTMENT_KEYWORDS = [
    "appointment",
    "appointments",
    "schedule",
    "scheduled",
    "book",
    "booking",
    "availability",
    "available",
    "slot",
    "slots",
    "doctor availability",
    "consultation",
    "visit",
    "reserve",
]


# =====================================================
# PROMPT TEMPLATE
# =====================================================

RAG_PROMPT_TEMPLATE = """
You are a healthcare policy assistant.

You MUST answer using ONLY the information
present in the supplied context.

If the answer is not explicitly present,
respond exactly:

I could not find this information in the provided documents.

Never:
- Guess
- Infer missing facts
- Use outside knowledge
- Provide diagnosis
- Provide treatment recommendations

Context:
--------------------
{context}
--------------------

Question:
{question}

Answer:
"""


# =====================================================
# MOCK APPOINTMENT DATA
# =====================================================

MOCK_APPOINTMENT_SLOTS = {
    "Cardiology": [
        "10:00 AM",
        "2:00 PM",
    ],
    "Dermatology": [
        "11:00 AM",
        "3:00 PM",
    ],
    "Neurology": [
        "9:30 AM",
        "1:30 PM",
    ],
}


# =====================================================
# LOGGING
# =====================================================

LOG_LEVEL = "INFO"


# =====================================================
# STARTUP CHECKS
# =====================================================

def ensure_directories() -> None:
    """
    Create required directories if they don't exist.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)


# Create folders automatically at startup
ensure_directories()