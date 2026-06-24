# API Examples and Testing Guide

## Overview

This document demonstrates how to interact with the Healthcare AI Assistant APIs using Swagger UI, cURL, and Postman. It also includes actual test results obtained during system validation.

**Base URL**

```text
http://127.0.0.1:8000
```

---

# API Workflow

The recommended testing sequence is:

```text
1. Health Check
        ↓
2. Ingest Documents
        ↓
3. Ask Knowledge Question (RAG)
        ↓
4. Ask Appointment Question (Tool Routing)
        ↓
5. Ask Out-of-Scope Question
```

This validates the complete system end-to-end.

---

# 1. Health Check API

## Endpoint

```http
GET /health
```

## Purpose

Verifies the availability of:

* Embedding model
* LLM service
* Vector database
* Agent layer

## cURL Request

```bash
curl -X GET "http://127.0.0.1:8000/health"
```

## Response

```json
{
  "status": "healthy",
  "services": {
    "embeddings": {
      "status": "healthy",
      "model": "all-MiniLM-L6-v2",
      "dimension": 384
    },
    "llm": {
      "status": "healthy",
      "model": "phi3",
      "response_received": true
    },
    "vector_store": {
      "status": "healthy",
      "documents_in_store": 96
    },
    "agent": {
      "status": "healthy",
      "appointment_departments": [
        "Cardiology",
        "Dermatology",
        "Neurology"
      ],
      "appointment_keywords": [
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
        "reserve"
      ]
    }
  }
}
```

## Validation

Verified that:

* Embedding model loaded successfully.
* Ollama and Phi-3 were reachable.
* ChromaDB contained indexed documents.
* Agent routing system was available.

---

# 2. Document Ingestion API

## Endpoint

```http
POST /ingest
```

## Purpose

Processes all healthcare documents and stores embeddings in ChromaDB.

## Workflow

```text
Documents
    ↓
Chunking
    ↓
Embedding Generation
    ↓
Vector Storage
```

## cURL Request

```bash
curl -X POST "http://127.0.0.1:8000/ingest"
```

## Response

```json
{
  "status": "success",
  "documents_processed": 6,
  "chunks_created": 96
}
```

## Validation

Verified that:

* All six healthcare documents were loaded.
* Documents were split into chunks.
* Embeddings were generated successfully.
* Chunks were stored in ChromaDB.

---

# 3. RAG-Based Question Answering

## Endpoint

```http
POST /ask
```

## Purpose

Routes knowledge-related questions through the Retrieval-Augmented Generation pipeline.

## Request

```json
{
  "question": "Can patients request medication refills through telehealth?"
}
```

## cURL Request

```bash
curl -X POST \
"http://127.0.0.1:8000/ask" \
-H "Content-Type: application/json" \
-d '{
  "question": "Can patients request medication refills through telehealth?"
}'
```

## Response

```json
{
  "route": "rag",
  "answer": "Yes, patients can discuss and potentially request medication refills during telehealth visits; however, approval is subject to the provider's review based on various factors.",
  "confidence": "medium",
  "similarity_score": 0.6359,
  "sources": [
    {
      "document": "telehealth.txt",
      "chunk_id": 8
    },
    {
      "document": "telehealth.txt",
      "chunk_id": 12
    },
    {
      "document": "medication_refill.txt",
      "chunk_id": 11
    }
  ],
  "result": null
}
```

## Validation

Verified that:

* Agent selected the RAG route.
* Relevant chunks were retrieved from ChromaDB.
* Phi-3 generated an answer using retrieved context.
* Source citations were returned.
* Confidence score was calculated.

---

# 4. Agent Tool Routing Example

## Endpoint

```http
POST /ask
```

## Purpose

Demonstrates agent-based routing to a tool instead of the RAG system.

## Request

```json
{
  "question": "Can I book a cardiology appointment?"
}
```

## cURL Request

```bash
curl -X POST \
"http://127.0.0.1:8000/ask" \
-H "Content-Type: application/json" \
-d '{
  "question": "Can I book a cardiology appointment?"
}'
```

## Response

```json
{
  "route": "tool",
  "answer": null,
  "confidence": null,
  "similarity_score": null,
  "sources": null,
  "result": {
    "tool": "appointment_tool",
    "department": "Cardiology",
    "available_slots": [
      "10:00 AM",
      "2:00 PM"
    ]
  }
}
```

## Validation

Verified that:

* Agent detected appointment-related intent.
* No vector search was performed.
* No LLM call was required.
* Appointment tool returned available slots.

---

# 5. Out-of-Scope Query Handling

## Endpoint

```http
POST /ask
```

## Purpose

Verifies hallucination prevention and grounded answering.

## Request

```json
{
  "question": "Explain calculus and derivatives"
}
```

## cURL Request

```bash
curl -X POST \
"http://127.0.0.1:8000/ask" \
-H "Content-Type: application/json" \
-d '{
  "question": "Explain calculus and derivatives"
}'
```

## Response

```json
{
  "route": "rag",
  "answer": "I could not find this information in the provided documents.",
  "confidence": "low",
  "similarity_score": 0,
  "sources": [
    {
      "document": "insurance.txt",
      "chunk_id": 2
    },
    {
      "document": "insurance.txt",
      "chunk_id": 16
    },
    {
      "document": "medication_refill.txt",
      "chunk_id": 12
    }
  ],
  "result": null
}
```

## Validation

Verified that:

* Question was outside the healthcare dataset.
* Retrieval confidence was extremely low.
* The model followed prompt instructions.
* No hallucinated answer was generated.
* Grounded response policy was enforced successfully.

---

# Testing Through Swagger UI

## Open Swagger

```text
http://127.0.0.1:8000/docs
```

Available endpoints:

```text
GET    /health
POST   /ingest
POST   /ask
DELETE /reset
```

## Recommended Validation Sequence

```text
1. GET /health
2. POST /ingest
3. POST /ask (RAG Example)
4. POST /ask (Appointment Example)
5. POST /ask (Out-of-Scope Example)
```

---

# Postman Testing

## Health Check

Method:

```text
GET
```

URL:

```text
http://127.0.0.1:8000/health
```

---

## Ingestion

Method:

```text
POST
```

URL:

```text
http://127.0.0.1:8000/ingest
```

---

## Question Answering

Method:

```text
POST
```

URL:

```text
http://127.0.0.1:8000/ask
```

Headers:

```text
Content-Type: application/json
```

Body:

```json
{
  "question": "Can patients request medication refills through telehealth?"
}
```


