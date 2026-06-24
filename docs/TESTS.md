# Testing Documentation

## Overview

The Healthcare AI Assistant includes a comprehensive test suite implemented using **Pytest**.

The tests validate the behavior of all major application layers:

* Agent Layer
* Embedding Layer
* LLM Layer
* RAG Layer

The goal of the test suite is to ensure that:

* Core business logic behaves correctly
* Edge cases are handled properly
* Components can be validated independently
* Future changes do not introduce regressions

---

# Testing Framework

## Pytest

The project uses:

```bash
pytest
```

Benefits:

* Simple test structure
* Fixtures
* Mocking support
* Fast execution
* Clear reporting

---

# Running Tests

## Run All Tests

From the project root:

```bash
pytest
```

---

## Verbose Output

```bash
pytest -v
```

---

## Run Specific Test File

### Agent Tests

```bash
pytest tests/test_agent.py
```

### Embedding Tests

```bash
pytest tests/test_embeddings.py
```

### LLM Tests

```bash
pytest tests/test_llm.py
```

### RAG Tests

```bash
pytest tests/test_rag.py
```

---

# Test Architecture

```text
tests/
│
├── test_agent.py
├── test_embeddings.py
├── test_llm.py
└── test_rag.py
```

Each file focuses on a specific application layer.

---

# Agent Layer Tests

File:

```text
tests/test_agent.py
```

Purpose:

Validate routing logic between:

* Appointment Tool
* RAG Pipeline

---

## Agent Router Coverage

### Appointment Detection

Verifies that appointment-related queries are correctly identified.

Example:

```text
I want to book a cardiology appointment
```

Expected:

```python
True
```

---

### Non-Appointment Detection

Verifies that informational healthcare questions are routed to the RAG system.

Example:

```text
What is HIPAA compliance?
```

Expected:

```python
False
```

---

### Tool Routing

Validates:

```python
process_question()
```

for appointment requests.

Expected:

```json
{
  "route": "tool"
}
```

---

### RAG Routing

Validates:

```python
process_question()
```

for knowledge-based questions.

Expected:

```json
{
  "route": "rag"
}
```

The LLM response is mocked to isolate routing behavior.

---

### Input Validation

Tests empty user input.

Expected:

```python
ValueError
```

---

### Query Classification

Validates:

```python
classify()
```

which determines whether a query should use:

* Tool
* RAG

---

## Appointment Tool Coverage

### Available Departments

Tests retrieval of available appointment departments.

---

### Department Matching

Validates successful department lookup.

Example:

```text
cardiology
```

---

### Unknown Department

Validates graceful handling of invalid departments.

Expected:

```python
available_slots == []
```

---

### Department Extraction

Tests keyword extraction from user queries.

Example:

```text
I need cardiology appointment
```

---

### Health Check

Verifies:

```python
health_check()
```

returns:

```json
{
  "status": "healthy"
}
```

and includes tool metadata.

---

# Embedding Layer Tests

File:

```text
tests/test_embeddings.py
```

Purpose:

Validate embedding generation and vector operations.

---

## Single Embedding Generation

Tests:

```python
generate_embedding()
```

Verifies:

* Output type
* Vector length
* Float values

---

## Batch Embedding Generation

Tests:

```python
generate_embeddings()
```

Verifies:

* Multiple vectors generated
* Correct output structure

---

## Empty Input Validation

Ensures invalid input is rejected.

Expected:

```python
ValueError
```

for:

```python
generate_embedding("")
```

---

## Empty Batch Validation

Ensures empty lists are rejected.

Expected:

```python
ValueError
```

for:

```python
generate_embeddings([])
```

---

## Embedding Dimension Validation

Tests:

```python
embedding_dimension()
```

Expected:

```python
384
```

This matches:

```text
all-MiniLM-L6-v2
```

embedding size.

---

## Cosine Similarity

Tests:

```python
cosine_similarity()
```

Verifies:

* Returns float
* Value remains between 0 and 1

---

## Health Check

Tests:

```python
health_check()
```

Verifies:

* Model availability
* Embedding dimension
* Service status

---

# LLM Layer Tests

File:

```text
tests/test_llm.py
```

Purpose:

Validate prompt construction and LLM workflow behavior.

---

## Prompt Construction

Tests:

```python
build_prompt()
```

Verifies:

* Question inclusion
* Context inclusion
* Proper prompt generation

---

## Empty Question Validation

Ensures:

```python
answer_question("")
```

raises:

```python
ValueError
```

---

## Knowledge Base Validation

Verifies that the system refuses to answer questions when the vector database has not been initialized.

Expected:

```python
RuntimeError
```

---

## RAG Pipeline Integration

Uses mocked retrieval results.

Verifies:

* Context usage
* Source propagation
* Confidence propagation
* Similarity score propagation

---

## Ollama Health Check

Tests successful connectivity to Ollama.

Expected:

```json
{
  "status": "healthy"
}
```

---

## Ollama Failure Handling

Simulates:

```text
Ollama unavailable
```

Expected:

```json
{
  "status": "unhealthy"
}
```

with error details.

---

## Direct Chat

Tests:

```python
direct_chat()
```

using mocked Ollama responses.

Verifies:

* Successful communication
* Response extraction

---

# RAG Layer Tests

File:

```text
tests/test_rag.py
```

Purpose:

Validate document processing, retrieval, and vector database behavior.

---

## Document Chunking

Tests:

```python
chunk_document()
```

Verifies:

* Chunks are generated
* Metadata exists
* Chunk identifiers are assigned

Each chunk should contain:

```json
{
  "text": "...",
  "document": "...",
  "chunk_id": 1
}
```

---

## Confidence Labeling

Tests conversion of similarity scores into labels.

Examples:

```text
0.95 → high
0.75 → medium/high
0.20 → low
```

---

## Knowledge Base Initialization

Tests:

```python
knowledge_base_initialized()
```

for:

### Empty Database

Expected:

```python
False
```

### Populated Database

Expected:

```python
True
```

---

## Knowledge Base Reset

Tests:

```python
reset_knowledge_base()
```

Verifies:

* Collection deletion
* Success response generation

---

## Retrieval Pipeline

Mocks:

* Embedding generation
* ChromaDB query

Verifies:

* Context generation
* Source extraction
* Confidence scoring
* Similarity score calculation

---

## Context Retrieval Wrapper

Tests:

```python
get_context_for_question()
```

Verifies:

* Context extraction
* Source extraction
* Confidence extraction

---

## Health Check

Tests:

```python
health_check()
```

Verifies:

* Vector store availability
* Document count reporting

---

## Document Loading Failure

Simulates:

```text
No documents found
```

Expected:

```python
FileNotFoundError
```

This ensures ingestion failures are properly reported.

---

# Mocking Strategy

The test suite heavily uses:

```python
monkeypatch
```

and:

```python
unittest.mock
```

to isolate components.

Benefits:

* No real Ollama calls
* No real embedding generation
* No external dependency requirements
* Faster execution
* Deterministic results

---

# Test Coverage Summary

| Layer                | Coverage |
| -------------------- | -------- |
| Agent Routing        | ✓        |
| Appointment Tool     | ✓        |
| Embedding Generation | ✓        |
| Embedding Similarity | ✓        |
| Prompt Construction  | ✓        |
| LLM Workflow         | ✓        |
| Ollama Health Checks | ✓        |
| Document Chunking    | ✓        |
| Retrieval Logic      | ✓        |
| Confidence Scoring   | ✓        |
| Vector Store Reset   | ✓        |
| Health Monitoring    | ✓        |
| Input Validation     | ✓        |
| Error Handling       | ✓        |

---

# Testing Philosophy

The test suite follows a layered testing approach:

1. Validate each component independently.
2. Mock external dependencies whenever possible.
3. Verify expected outputs and error conditions.
4. Ensure predictable behavior for future code changes.
5. Protect against regressions during development.

The tests are designed to provide confidence that the Healthcare AI Assistant behaves correctly across retrieval, generation, routing, and document-processing workflows.
