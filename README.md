# Healthcare AI Assistant (RAG System with FastAPI + Ollama)

## 1. Project Overview

The Healthcare AI Assistant is a Retrieval-Augmented Generation (RAG) system designed to answer healthcare-related queries using a curated dataset of documents. It combines semantic search with a local LLM (Phi-3 via Ollama) and includes a lightweight agent for routing specific queries (e.g., appointment booking) to tools instead of the RAG pipeline.

The system is built to demonstrate:

* Document ingestion and chunking
* Embedding-based semantic search
* Vector database storage
* LLM-based response generation
* Tool/agent routing logic
* REST API exposure via FastAPI

---

# 2. Setup and Run Instructions

## 2.1 Prerequisites

* Python 3.10+
* Windows PowerShell (recommended)
* Ollama installed (for local LLM execution)

---

## 2.2 Clone Repository

```powershell
git clone <repository-url>
cd healthcare-ai-assistant
```

---

## 2.3 Create Virtual Environment

```powershell
python -m venv venv
```

---

## 2.4 Activate Environment

```powershell
.\venv\Scripts\Activate.ps1
```

If execution policy error occurs:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 2.5 Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 2.6 Install and Setup Ollama

Download:
[https://ollama.com/download/windows](https://ollama.com/download/windows)

Verify:

```powershell
ollama --version
```

Pull model:

```powershell
ollama pull phi3
```

---

## 2.7 Run the Application

### Terminal 1 – Start Ollama

```powershell
ollama serve
```

### Terminal 2 – Start FastAPI Server

```powershell
uvicorn app.main:app --reload
```

---

## 2.8 Access API Docs

```
http://127.0.0.1:8000/docs
```

---

# 3. Architecture Overview

## System Flow

```text
User Query
   ↓
FastAPI (/ask)
   ↓
Agent Router
   ├── Tool (Appointment queries)
   └── RAG Pipeline
          ↓
   Document Chunking
          ↓
   Embeddings (MiniLM)
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

# 4. API Endpoints

## 4.1 Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

---

## 4.2 Ingest Documents

```http
POST /ingest
```

Description:

* Loads documents from `/data`
* Splits into chunks
* Generates embeddings
* Stores in ChromaDB

Response:

```json
{
  "status": "success",
  "documents_processed": 6,
  "chunks_created": 15
}
```

---

## 4.3 Ask Question

```http
POST /ask
```

Request:

```json
{
  "question": "Can patients request medication refills through telehealth?"
}
```

### RAG Response

```json
{
  "route": "rag",
  "answer": "Patients can request medication refills during telehealth visits...",
  "sources": ["telehealth.txt"]
}
```

### Tool Response

```json
{
  "route": "tool",
  "result": {
    "department": "Cardiology",
    "available_slots": ["10:00 AM", "2:00 PM"]
  }
}
```

---

# 5. Sample Questions and Expected Behavior

## RAG-based Questions

* Can patients request medication refills through telehealth?
* What is HIPAA compliance?
* What are discharge policies?

Expected:

* Context-based answer from documents

---

## Out-of-domain Questions

* What is the parking fee?
* What is hospital cafeteria menu?

Expected:

* "I could not find this information in the provided documents."

---

## Tool-based Questions

* Can I book a cardiology appointment?
* Show available appointment slots

Expected:

* Direct tool response with slots

---

# 6. Dataset Details

The `/data` directory contains domain-specific healthcare documents:

| File                  | Description                   |
| --------------------- | ----------------------------- |
| telehealth.txt        | Telehealth policies and usage |
| medication_refill.txt | Prescription refill rules     |
| hipaa.txt             | Privacy and compliance rules  |
| insurance.txt         | Insurance handling policies   |
| discharge.txt         | Hospital discharge guidelines |
| appointments.txt      | Appointment scheduling data   |

These documents form the knowledge base for the RAG system.

---

# 7. Docker Setup

## Build Image

```bash
docker build -t healthcare-ai .
```

## Run Container

```bash
docker-compose up
```

The container exposes the FastAPI service.

---

# 8. System Components Explanation

## 8.1 LLM Used

* Model: Phi-3
* Runtime: Ollama (local inference)
* Purpose: Final response generation

---

## 8.2 Embedding Model

* Model: all-MiniLM-L6-v2
* Library: SentenceTransformers
* Purpose: Convert text into vector embeddings for semantic search

---

## 8.3 Vector Database

* Tool: ChromaDB
* Purpose:

  * Store embeddings
  * Enable similarity search over documents

---

## 8.4 Prompting Strategy

* Strict context grounding
* No hallucination allowed
* No medical diagnosis or treatment advice
* Forced fallback response when context is missing

---

## 8.5 Agent / Tool Workflow

* Rule-based keyword detection
* Routes query to:

  * RAG pipeline OR
  * Appointment tool

Keywords:

* book
* appointment
* slot
* schedule
* availability

---

## 8.6 Limitations

* No real-time medical data integration
* Rule-based (not ML-based) agent
* No long-term memory or conversation history
* Retrieval quality depends on chunking strategy
* No authentication or user management

---

## 8.7 Future Improvements

* Hybrid search (BM25 + vector search)
* Re-ranking model for better retrieval accuracy
* Memory-enabled conversations
* LangGraph or CrewAI-based agent system
* JWT authentication layer
* Cloud deployment (AWS/Azure/GCP)

---

# End of README


