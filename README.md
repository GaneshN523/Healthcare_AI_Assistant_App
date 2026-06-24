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

## Authentication

The API uses **HTTP Basic Authentication** for sensitive operations.

### Credentials (Example Credentials)

```text
Username: admin
Password: admin123
```

### Protected Endpoints

| Method | Endpoint  | Authentication Required |
| ------ | --------- | ----------------------- |
| POST   | `/ask`    | Yes                     |
| POST   | `/ingest` | Yes                     |
| DELETE | `/reset`  | Yes                     |

### Public Endpoints

| Method | Endpoint  |
| ------ | --------- |
| GET    | `/`       |
| GET    | `/health` |

---

## 4.1 Root Endpoint

```http
GET /
```

### Response

```json
{
  "message": "Healthcare AI Assistant API",
  "version": "1.0.0"
}
```

---

## 4.2 Health Check

```http
GET /health
```

### Response

```json
{
  "status": "healthy"
}
```

---

## 4.3 Ingest Documents

```http
POST /ingest
```

**Authentication Required:** Yes

### Description

* Loads documents from `/data`
* Splits documents into chunks
* Generates embeddings
* Stores vectors in ChromaDB

### Response

```json
{
  "status": "success",
  "documents_processed": 6,
  "chunks_created": 15
}
```

---

## 4.4 Ask Question

```http
POST /ask
```

**Authentication Required:** Yes

### Request

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
  "sources": [
    {
      "document": "telehealth.txt"
    }
  ]
}
```

### Tool Response

```json
{
  "route": "tool",
  "result": {
    "department": "Cardiology",
    "available_slots": [
      "10:00 AM",
      "2:00 PM"
    ]
  }
}
```

---

## 4.5 Reset Knowledge Base

```http
DELETE /reset
```

**Authentication Required:** Yes

### Description

* Clears the ChromaDB vector database
* Removes indexed document embeddings
* Resets the knowledge base

### Response

```json
{
  "status": "success",
  "message": "Knowledge base reset successfully"
}
```

After reset, documents must be re-ingested using:

```http
POST /ingest
```

to rebuild the vector database.

---

## Swagger Authentication

Open:

```text
http://127.0.0.1:8000/docs
```

Click:

```text
Authorize
```

Enter:

```text
Username: admin
Password: admin123
```

Click:

```text
Authorize
```

You can now access protected endpoints directly from Swagger UI.

---

## Unauthorized Access Example

Response when credentials are missing or invalid:

```json
{
  "detail": "Not authenticated"
}
```

### Status Code

```text
401 Unauthorized
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
* Uses simple HTTP Basic Authentication
* No user database
* No role-based access control
* Credentials are hardcoded for demonstration purposes

---

## 8.7 Future Improvements

* Hybrid search (BM25 + vector search)
* Re-ranking model for better retrieval accuracy
* Memory-enabled conversations
* LangGraph or CrewAI-based agent system
* JWT authentication with access and refresh tokens
* Role-based authorization
* Database-backed user management
* OAuth2 integration
* Cloud deployment (AWS/Azure/GCP)

---

# 9. Security Features

## HTTP Basic Authentication

The application uses FastAPI's **HTTP Basic Authentication** to protect resource-intensive and administrative endpoints.

### Protected Endpoints

- `POST /ask`
- `POST /ingest`
- `DELETE /reset`

Authentication is validated before any expensive operations are executed.

### This Prevents

- Unauthorized LLM access
- Unauthorized vector database modifications
- Unauthorized knowledge base resets

### If Authentication Fails

- The request is immediately rejected
- No vector search is performed
- No ChromaDB operations occur
- No Ollama inference occurs

### Response

```json
{
  "detail": "Not authenticated"
}
```

### Status Code

```text
401 Unauthorized
```

# End of README


