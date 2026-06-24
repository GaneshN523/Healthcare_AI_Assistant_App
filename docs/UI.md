# User Interface Documentation

## Overview

The Healthcare AI Assistant includes a web-based user interface built using Streamlit.

The UI serves as a frontend layer that communicates directly with the FastAPI backend through REST API calls.

Responsibilities of the UI:

* User authentication
* Chat interaction
* Knowledge base management
* System monitoring
* Displaying AI-generated responses
* Displaying document sources and retrieval information

The UI itself does not perform:

* Embedding generation
* Vector search
* Retrieval
* LLM inference

All AI-related operations are delegated to the FastAPI backend.

---

# Architecture

## High-Level Flow

```text
User
  │
  ▼
Streamlit UI
  │
  │ HTTP Requests
  ▼
FastAPI Backend
  │
  ├── Agent Router
  ├── RAG Pipeline
  ├── ChromaDB
  └── Ollama (Phi3)
```

The Streamlit application acts purely as a client.

All business logic remains inside the FastAPI application.

---

# File Location

```text
ui/
└── stapp.py
```

Application startup command:

```bash
streamlit run ui/stapp.py
```

Default URL:

```text
http://localhost:8501
```

---

# Backend Communication

## API Configuration

The frontend communicates with FastAPI through:

```python
API_BASE_URL = "http://127.0.0.1:8000"
```

All requests are sent to endpoints under this base URL.

Examples:

```text
http://127.0.0.1:8000/ask
http://127.0.0.1:8000/ingest
http://127.0.0.1:8000/reset
http://127.0.0.1:8000/health
http://127.0.0.1:8000/auth/check
```

---

# Session State Management

The application uses Streamlit Session State to persist information between page reruns.

Stored values:

```python
authenticated
username
password
messages
```

Purpose:

## authenticated

Tracks login status.

```python
True / False
```

---

## username

Stores the authenticated username.

Used for API requests.

---

## password

Stores the authenticated password.

Used for HTTP Basic Authentication.

---

## messages

Stores conversation history.

Structure:

```python
[
    {
        "role": "user",
        "content": "Question"
    },
    {
        "role": "assistant",
        "content": "Answer"
    }
]
```

This allows previous messages to remain visible after Streamlit reruns.

---

# Authentication Workflow

## Login Screen

When the application starts:

```python
if not st.session_state.authenticated
```

the user is redirected to the login page.

Displayed fields:

* Username
* Password

---

## Credential Verification

The login button triggers:

```python
check_credentials()
```

which sends:

```http
GET /auth/check
```

using HTTP Basic Authentication.

Request:

```python
requests.get(
    "/auth/check",
    auth=(username, password)
)
```

---

## Successful Authentication

If the backend returns:

```text
200 OK
```

the UI:

```python
st.session_state.authenticated = True
```

and reloads the page.

---

## Failed Authentication

If authentication fails:

```text
401 Unauthorized
```

the UI displays:

```text
Invalid credentials.
```

and remains on the login page.

---

# Sidebar Components

The sidebar provides administrative controls and system monitoring.

---

## Logout

Clears:

```python
authenticated
username
password
messages
```

and returns the user to the login screen.

---

## Backend Health Monitoring

The sidebar continuously checks:

```http
GET /health
```

through:

```python
get_health()
```

The response displays:

* Backend status
* Embedding service status
* LLM status
* Vector store status
* Agent status

If unavailable:

```text
Backend Offline
```

is displayed.

---

# Knowledge Base Management

## Document Ingestion

Button:

```text
📥 Ingest Documents
```

Calls:

```http
POST /ingest
```

Authentication:

```text
Required
```

Purpose:

* Load healthcare documents
* Chunk documents
* Generate embeddings
* Store vectors in ChromaDB

Response is displayed directly in the UI.

---

# Knowledge Base Reset

Located in:

```text
Danger Zone
```

Safety mechanism:

```python
confirm_reset
```

requires explicit confirmation.

---

## Reset Operation

Calls:

```http
DELETE /reset
```

Purpose:

* Delete vector database contents
* Remove indexed embeddings
* Reset knowledge base

The backend response is displayed to the user.

---

# Chat Interface

## Main Chat Window

The central portion of the UI contains:

```python
st.chat_message()
```

components.

Messages are rendered from:

```python
st.session_state.messages
```

This recreates the conversation after each page rerun.

---

# User Query Flow

## Step 1

User enters a question:

```python
st.chat_input()
```

Example:

```text
Can patients request medication refills through telehealth?
```

---

## Step 2

Message is stored:

```python
messages.append(...)
```

and immediately rendered.

---

## Step 3

The UI sends:

```http
POST /ask
```

Request:

```json
{
    "question": "Can patients request medication refills through telehealth?"
}
```

Authentication:

```text
HTTP Basic Authentication
```

---

## Step 4

FastAPI processes the request.

Possible routes:

```text
RAG
Tool
```

---

## Step 5

The response is returned to Streamlit.

---

# RAG Response Handling

Example response:

```json
{
    "route": "rag",
    "answer": "...",
    "similarity_score": 0.87,
    "sources": [...]
}
```

Displayed elements:

## Answer

Rendered using:

```python
st.markdown()
```

---

## Similarity Score

Displayed as:

```text
Similarity Score: 0.8700
```

This indicates retrieval relevance.

---

## Sources

Displayed inside:

```python
st.expander()
```

Users can inspect supporting documents.

---

# Tool Response Handling

Example:

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

Displayed using:

```python
st.json()
```

No RAG-specific information is shown.

---

# Error Handling

All backend operations are wrapped in:

```python
try:
    ...
except Exception
```

This prevents UI crashes caused by:

* Backend downtime
* Connection failures
* Request timeouts
* Unexpected server errors

Errors are displayed directly to the user.

---

# Backend Endpoints Used

| Endpoint      | Method | Purpose               |
| ------------- | ------ | --------------------- |
| `/auth/check` | GET    | Verify credentials    |
| `/health`     | GET    | Backend health status |
| `/ask`        | POST   | Submit user questions |
| `/ingest`     | POST   | Build vector database |
| `/reset`      | DELETE | Reset knowledge base  |

---

# Security Model

Authentication method:

```text
HTTP Basic Authentication
```

Credentials are provided with every protected request.

Protected operations:

* Ask Question
* Ingest Documents
* Reset Knowledge Base

Benefits:

* Prevents unauthorized LLM usage
* Prevents unauthorized ingestion
* Prevents unauthorized vector database resets

---

# UI Features Summary

Implemented features:

* Login page
* HTTP Basic Authentication
* Chat interface
* Conversation history
* Health monitoring
* Knowledge base ingestion
* Knowledge base reset
* RAG answer visualization
* Similarity score display
* Source document display
* Error handling
* Logout functionality

The UI acts as a lightweight frontend layer while delegating all AI, retrieval, and document-processing responsibilities to the FastAPI backend.
