"""
RAG (Retrieval Augmented Generation)

Responsibilities:
- Load healthcare documents
- Chunk documents
- Generate embeddings
- Store chunks in ChromaDB
- Retrieve relevant chunks
- Return citations
- Calculate confidence score
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Dict, List, Tuple

import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIRECTORY,
    DATA_DIR,
    MIN_CONFIDENCE_HIGH,
    MIN_CONFIDENCE_MEDIUM,
    TOP_K_RESULTS,
    VECTOR_STORE_DIR,
)
from app.embeddings import generate_embedding

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Main RAG Engine
    """

    def __init__(self) -> None:

        self.client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

    # =====================================================
    # DOCUMENT LOADING
    # =====================================================

    def load_documents(self) -> List[Dict]:
        """
        Load all .txt documents from data directory.
        """

        documents = []

        txt_files = list(
            Path(DATA_DIR).glob("*.txt")
        )

        if not txt_files:
            raise FileNotFoundError(
                "No healthcare documents found in data directory."
            )

        for file_path in txt_files:

            try:
                content = file_path.read_text(
                    encoding="utf-8"
                )

                documents.append(
                    {
                        "document_name": file_path.name,
                        "content": content
                    }
                )

            except Exception as exc:
                logger.error(
                    "Failed reading %s: %s",
                    file_path.name,
                    exc
                )

        return documents

    # =====================================================
    # CHUNKING
    # =====================================================

    def chunk_document(
        self,
        document_name: str,
        content: str
    ) -> List[Dict]:
        """
        Convert document into chunks.
        """

        chunks = self.text_splitter.split_text(
            content
        )

        chunk_records = []

        for idx, chunk in enumerate(chunks):

            chunk_records.append(
                {
                    "chunk_id": idx,
                    "document": document_name,
                    "text": chunk
                }
            )

        return chunk_records

    # =====================================================
    # INGESTION
    # =====================================================

    def ingest_documents(self) -> Dict:
        """
        Full ingestion workflow.

        Documents
            ↓
        Chunk
            ↓
        Embed
            ↓
        Store
        """

        logger.info("Starting ingestion.")

        documents = self.load_documents()

        total_chunks = 0

        for document in documents:

            chunks = self.chunk_document(
                document["document_name"],
                document["content"]
            )

            total_chunks += len(chunks)

            ids = []
            embeddings = []
            metadatas = []
            texts = []

            for chunk in chunks:

                chunk_embedding = generate_embedding(
                    chunk["text"]
                )

                chunk_uuid = str(
                    uuid.uuid4()
                )

                ids.append(chunk_uuid)

                embeddings.append(
                    chunk_embedding
                )

                texts.append(
                    chunk["text"]
                )

                metadatas.append(
                    {
                        "document": chunk["document"],
                        "chunk_id": chunk["chunk_id"]
                    }
                )

            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )

            logger.info(
                "Stored %s chunks from %s",
                len(chunks),
                document["document_name"]
            )

        logger.info(
            "Ingestion complete. Documents=%s Chunks=%s",
            len(documents),
            total_chunks
        )

        return {
            "status": "success",
            "documents_processed": len(documents),
            "chunks_created": total_chunks
        }

    # =====================================================
    # COLLECTION STATUS
    # =====================================================

    def knowledge_base_initialized(self) -> bool:
        """
        Check if vector database contains documents.
        """

        try:
            count = self.collection.count()
            return count > 0

        except Exception:
            return False

    # =====================================================
    # CONFIDENCE
    # =====================================================

    @staticmethod
    def confidence_label(
        similarity_score: float
    ) -> str:

        if similarity_score >= MIN_CONFIDENCE_HIGH:
            return "high"

        if similarity_score >= MIN_CONFIDENCE_MEDIUM:
            return "medium"

        return "low"

    # =====================================================
    # RETRIEVAL
    # =====================================================

    def retrieve(
        self,
        question: str
    ) -> Dict:
        """
        Retrieve top matching chunks.
        """

        if not self.knowledge_base_initialized():
            raise RuntimeError(
                "Knowledge base not initialized."
            )

        query_embedding = generate_embedding(
            question
        )

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=TOP_K_RESULTS
        )

        retrieved_documents = (
            results.get("documents", [[]])[0]
        )

        retrieved_metadata = (
            results.get("metadatas", [[]])[0]
        )

        distances = (
            results.get("distances", [[]])[0]
        )

        context_chunks = []
        sources = []

        best_similarity = 0.0

        for text, metadata, distance in zip(
            retrieved_documents,
            retrieved_metadata,
            distances
        ):

            similarity = max(
                0.0,
                1 - float(distance)
            )

            best_similarity = max(
                best_similarity,
                similarity
            )

            context_chunks.append(text)

            sources.append(
                {
                    "document": metadata.get(
                        "document"
                    ),
                    "chunk_id": metadata.get(
                        "chunk_id"
                    ),
                    "chunk": text
                }
            )

        context = "\n\n".join(
            context_chunks
        )

        logger.info(
            "Retrieved %s chunks.",
            len(context_chunks)
        )

        return {
            "context": context,
            "sources": sources,
            "confidence": self.confidence_label(
                best_similarity
            ),
            "similarity_score": round(
                best_similarity,
                4
            )
        }

    # =====================================================
    # SEARCH + ANSWER PREPARATION
    # =====================================================

    def get_context_for_question(
        self,
        question: str
    ) -> Tuple[str, List[Dict], str]:
        """
        Convenience wrapper used by llm.py.
        """

        result = self.retrieve(
            question
        )

        return (
            result["context"],
            result["sources"],
            result["confidence"]
        )

    # =====================================================
    # RESET VECTOR DATABASE
    # =====================================================

    def reset_knowledge_base(self) -> Dict:
        """
        Delete all vectors.

        Useful during development/testing.
        """

        try:

            self.client.delete_collection(
                CHROMA_COLLECTION_NAME
            )

        except Exception:
            pass

        self.collection = (
            self.client.get_or_create_collection(
                name=CHROMA_COLLECTION_NAME
            )
        )

        logger.warning(
            "Knowledge base reset."
        )

        return {
            "status": "success",
            "message": "Knowledge base cleared."
        }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self) -> Dict:

        try:

            return {
                "status": "healthy",
                "documents_in_store":
                    self.collection.count()
            }

        except Exception as exc:

            return {
                "status": "unhealthy",
                "error": str(exc)
            }


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================

rag_engine = RAGEngine()


# ==========================================================
# STANDALONE TEST
# ==========================================================

if __name__ == "__main__":

    print(
        "Healthcare RAG Engine Test"
    )

    print(
        rag_engine.ingest_documents()
    )

    result = rag_engine.retrieve(
        "Can patients request medication refills through telehealth?"
    )

    print("\nConfidence:")
    print(result["confidence"])

    print("\nSources:")
    print(result["sources"])

    print("\nContext Preview:")
    print(result["context"][:500])