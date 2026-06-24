# Architecture Documentation — Healthcare AI Assistant

## 1. Overview

The Healthcare AI Assistant is built as a Retrieval-Augmented Generation (RAG) system combined with a lightweight agent-based routing layer. The system is designed to answer healthcare-related queries using internal documents while ensuring factual grounding and controlled tool execution for structured tasks such as appointment booking.

The architecture is modular, with clear separation between:

* Data ingestion
* Embedding generation
* Vector storage
* Retrieval pipeline
* LLM inference
* Tool-based agent routing
* API layer

---

# 2. High-Level Architecture

## System Flow

```text id="arch_flow_001"
User Query
    ↓
FastAPI (/ask endpoint)
    ↓
Agent Router
    ├── If appointment-related → Tool Execution Layer
    └── Else → RAG Pipeline
                    ↓
          Document Chunking (RAG)
                    ↓
          Embedding Model (MiniLM)
                    ↓
          Vector Database (ChromaDB)
                    ↓
          Similarity Search (Top-K retrieval)
                    ↓
          Context Construction
                    ↓
          Prompt Engineering Layer
                    ↓
          LLM (Phi-3 via Ollama)
                    ↓
          Final Response + Sources
```

---

# 3. Component-Level Architecture

## 3.1 API Layer (FastAPI)

**File:** `app/main.py`

Responsibilities:

* Exposes REST endpoints:

  * `/health`
  * `/ingest`
  * `/ask`
* Handles request validation
* Routes requests to agent or RAG pipeline
* Returns structured JSON responses

---

## 3.2 Agent Layer (Tool Routing)

**File:** `app/agent.py`

The agent acts as a decision layer that determines whether a query should be:

* Handled via RAG
* Routed to a tool (appointment system)

### Routing Logic

Keyword-based classification:

```text id="agent_logic_001"
appointment
book
schedule
slot
availability
```

### Behavior

| Query Type                  | Action       |
| --------------------------- | ------------ |
| Appointment-related         | Execute tool |
| General healthcare question | Use RAG      |

---

## 3.3 RAG Pipeline

**File:** `app/rag.py`

### Responsibilities:

* Load documents from `/data`
* Split text into chunks (500 tokens, overlap 50)
* Generate embeddings
* Store embeddings in ChromaDB
* Retrieve top-K relevant chunks

---

## 3.4 Embedding Layer

**File:** `app/embeddings.py`

### Model Used:

* all-MiniLM-L6-v2 (SentenceTransformers)

### Function:

Converts text into dense vector representations:

```text id="embedding_flow_001"
Text → Tokenization → Transformer Model → Vector Embedding
```

Supports:

* Single text embedding
* Batch embedding

---

## 3.5 Vector Database Layer

### Technology:

* ChromaDB

### Stored Data:

Each record contains:

```json id="vector_schema_001"
{
  "chunk_text": "...",
  "embedding": [...],
  "metadata": {
    "document": "telehealth.txt",
    "chunk_id": 1
  }
}
```

### Purpose:

* Enable semantic similarity search
* Retrieve contextually relevant chunks for LLM

---

## 3.6 Retrieval Process

### Steps:

```text id="retrieval_flow_001"
User Query
    ↓
Query Embedding
    ↓
Similarity Search in ChromaDB
    ↓
Top-K Relevant Chunks
    ↓
Context Aggregation
```

---

## 3.7 LLM Layer

**File:** `app/llm.py`

### Model:

* Phi-3 via Ollama

### Role:

* Generate final response using retrieved context

### Prompt Strategy:

Strict grounding rules:

* Use only provided context
* Do not hallucinate
* Do not provide medical diagnosis
* Do not provide treatment recommendations
* If context is missing:

> "I could not find this information in the provided documents."

---

## 3.8 Prompt Construction Flow

```text id="prompt_flow_001"
Retrieved Context
    +
User Question
    ↓
System Prompt (Rules)
    ↓
Final Prompt to Phi-3
    ↓
Generated Response
```

---

## 3.9 Tool Layer (Appointment System)

### Functionality:

Provides structured responses for scheduling queries.

### Example Output:

```json id="tool_output_001"
{
  "department": "Cardiology",
  "available_slots": [
    "10:00 AM",
    "2:00 PM"
  ]
}
```

---

# 4. End-to-End Data Flow

## RAG Flow

```text id="full_rag_flow"
User Question
    ↓
FastAPI
    ↓
Agent → RAG route
    ↓
Embedding Generation
    ↓
Vector Search (ChromaDB)
    ↓
Top-K Context Retrieval
    ↓
Prompt Construction
    ↓
Phi-3 (Ollama)
    ↓
Final Answer
```

---

## Tool Flow

```text id="full_tool_flow"
User Question
    ↓
FastAPI
    ↓
Agent detects appointment intent
    ↓
Tool execution
    ↓
Structured slot response
```

---

# 5. Design Principles

## 5.1 Modularity

Each component is independent:

* Embeddings
* Retrieval
* LLM
* Agent
* API

---

## 5.2 Separation of Concerns

* RAG handles unstructured queries
* Agent handles structured workflows
* LLM handles only generation

---

## 5.3 Factual Grounding

* Responses are strictly limited to retrieved context
* Hallucination prevention enforced via prompt design

---

## 5.4 Local-First Architecture

* Ollama runs locally
* No external API dependency for LLM
* ChromaDB runs locally

---

# 6. Key Strengths of Architecture

* Lightweight and modular design
* Fully local LLM execution
* Easy to extend with new tools
* Scalable RAG pipeline
* Clear separation between retrieval and generation

---

# 7. Limitations

* Rule-based agent (no ML classification)
* No conversation memory
* No re-ranking of retrieved results
* No authentication layer
* Static dataset (no real-time medical updates)

---

# 8. Future Improvements

* Add hybrid retrieval (BM25 + vector search)
* Add re-ranking model (cross-encoder)
* Replace rule-based agent with LLM-based planner
* Add conversation memory layer
* Introduce authentication (JWT)
* Deploy on cloud (AWS / Azure / GCP)
* Add streaming responses for LLM output

---

# End of Architecture Document


