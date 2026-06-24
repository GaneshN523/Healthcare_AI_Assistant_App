# Model Details — Healthcare AI Assistant

This document explains the core AI components used in the Healthcare AI Assistant system, including the LLM, embedding model, vector database, prompting strategy, agent workflow, and system limitations.

---

# 1. Large Language Model (LLM)

## Model Used

* **Model Name:** Phi-3
* **Runtime:** Ollama (local inference server)
* **Type:** Lightweight instruction-tuned language model

---

## Why Phi-3

Phi-3 is selected because:

* It runs efficiently on local machines
* It provides strong reasoning for small-to-medium context tasks
* It supports instruction-following with structured prompts
* It avoids dependency on cloud APIs

---

## Role in System

The LLM is responsible for:

* Generating final answers
* Synthesizing retrieved context
* Formatting responses in natural language

---

## Input to LLM

```text id="llm_input_001"
System Prompt (rules)
+
Retrieved context (from ChromaDB)
+
User question
```

---

## Output

* Final natural language answer
* Optional refusal message if context is missing

Example fallback:

> I could not find this information in the provided documents.

---

# 2. Embedding Model

## Model Used

* **Model:** all-MiniLM-L6-v2
* **Library:** SentenceTransformers

---

## Purpose

The embedding model converts text into dense vector representations for semantic similarity search.

---

## How It Works

```text id="embed_flow_001"
Input Text
   ↓
Tokenization
   ↓
Transformer Encoding
   ↓
Dense Vector Representation
```

---

## Why This Model

* Lightweight and fast
* High-quality sentence-level embeddings
* Suitable for semantic search tasks
* Efficient for CPU-based execution

---

## Output Format

Each text chunk is converted into:

```json id="embed_vector_001"
[
  0.12,
  -0.03,
  0.98,
  ...
]
```

---

# 3. Vector Database

## Technology Used

* **Database:** ChromaDB
* **Type:** Persistent vector store

---

## Purpose

Stores:

* Embedded document chunks
* Metadata (source file, chunk ID)
* Enables similarity search for retrieval

---

## Stored Structure

```json id="vector_schema_001"
{
  "chunk_text": "Patients may request medication refills...",
  "embedding": [0.12, -0.45, ...],
  "metadata": {
    "document": "telehealth.txt",
    "chunk_id": 3
  }
}
```

---

## Retrieval Mechanism

```text id="retrieval_001"
Query → Embedding → Vector Search → Top-K Similar Chunks
```

---

## Why ChromaDB

* Lightweight and local
* Easy integration with Python
* Persistent storage support
* Efficient similarity search

---

# 4. Prompt Engineering Strategy

## Objective

Ensure the LLM:

* Uses only retrieved context
* Does not hallucinate
* Avoids medical advice generation
* Produces grounded responses

---

## System Prompt Rules

```text id="prompt_rules_001"
Use ONLY provided context.

If the answer is not found in the context, respond:
"I could not find this information in the provided documents."

Do not guess.
Do not invent facts.
Do not provide diagnosis.
Do not provide treatment advice.
```

---

## Prompt Structure

```text id="prompt_structure_001"
[System Rules]
+
[Retrieved Context]
+
[User Question]
```

---

## Key Design Principle

The system enforces **context grounding**, meaning:

> The LLM is not allowed to answer outside retrieved knowledge.

---

# 5. Agent / Tool Workflow

## Type

* Rule-based agent (keyword-driven)

---

## Purpose

Routes queries to:

* RAG pipeline (knowledge-based questions)
* Tool system (structured tasks like appointments)

---

## Trigger Keywords

```text id="agent_keywords_001"
appointment
book
schedule
slot
availability
```

---

## Decision Flow

```text id="agent_flow_001"
User Query
   ↓
Keyword Detection
   ↓
If match → Tool Execution
Else → RAG Pipeline
```

---

## Tool Example

### Input Query:

* "Can I book a cardiology appointment?"

### Output:

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

# 6. System Limitations

## 6.1 No Real-Time Data

* The system does not connect to live hospital databases

---

## 6.2 Rule-Based Agent

* Simple keyword matching
* No ML-based intent classification

---

## 6.3 No Memory Layer

* Each query is independent
* No conversation history maintained

---

## 6.4 Retrieval Dependency

* Output quality depends heavily on:

  * Chunking strategy
  * Embedding quality
  * Document coverage

---

## 6.5 No Authentication

* No user login or access control

---

## 6.6 Limited Medical Intelligence

* System is not a diagnostic tool
* Strictly informational only

---

# 7. Future Improvements

## 7.1 Retrieval Enhancements

* Hybrid search (BM25 + vector search)
* Re-ranking using cross-encoders

---

## 7.2 Agent Upgrades

* Replace rule-based logic with LLM-based planner
* Use frameworks like LangGraph or CrewAI

---

## 7.3 Memory Layer

* Add conversation memory for contextual continuity

---

## 7.4 Scalability Improvements

* Cloud-based vector database
* Distributed inference support

---

## 7.5 Security Enhancements

* JWT authentication
* Role-based access control

---

## 7.6 Observability

* Logging system
* Query tracing
* Performance metrics

