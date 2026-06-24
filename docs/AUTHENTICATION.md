# Why Authentication Was Added

The application performs operations that should not be publicly accessible:

## Ask Endpoint

The `/ask` endpoint:

* Queries the RAG pipeline
* Searches the vector database
* Communicates with the Phi-3 LLM
* Consumes CPU and memory resources

Authentication prevents unauthorized access.

---

## Ingest Endpoint

The `/ingest` endpoint:

* Reads healthcare documents
* Chunks documents
* Generates embeddings
* Rebuilds the ChromaDB vector store

This operation can be computationally expensive and should only be performed by authorized users.

---

## Reset Endpoint

The `/reset` endpoint:

* Deletes the vector database contents
* Clears the knowledge base

This endpoint is destructive and must be protected.

---

# Authentication Flow

The authentication process occurs before endpoint execution.

```text
Incoming Request
       |
       v
authenticate()
       |
       +---- Invalid Credentials
       |          |
       |          v
       |     Return 401
       |
       +---- Valid Credentials
                  |
                  v
          Execute Endpoint
```

If authentication fails:

* The endpoint function is never executed.
* No RAG retrieval occurs.
* No ChromaDB operations occur.
* No LLM inference occurs.

This prevents unnecessary processing and unauthorized access.

---

# Authentication Implementation

## auth.py

Create:

```text
app/auth.py
```

Implementation:

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

USERNAME = "admin"
PASSWORD = "admin123"


def authenticate(
    credentials: HTTPBasicCredentials = Depends(security)
):
    if (
        credentials.username != USERNAME
        or credentials.password != PASSWORD
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    return credentials.username
```

---

# Protecting Endpoints

## Ask Endpoint

```python
@app.post(
    "/ask",
    response_model=AskResponse
)
def ask(
    request: AskRequest,
    _: str = Depends(authenticate)
):
```

---

## Ingest Endpoint

```python
@app.post("/ingest")
def ingest_documents(
    _: str = Depends(authenticate)
):
```

---

## Reset Endpoint

```python
@app.delete("/reset")
def reset_knowledge_base(
    _: str = Depends(authenticate)
):
```

---

# Credentials

Current credentials:

```text
Username: admin
Password: admin123
```

> Note: These credentials are intended for demonstration and academic purposes only.

---

# Testing in Swagger UI

Start the application:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
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

You can now execute protected endpoints from Swagger UI.

---

# Testing with cURL

## Ask Endpoint

```bash
curl -X POST http://localhost:8000/ask \
-u admin:admin123 \
-H "Content-Type: application/json" \
-d "{\"question\":\"What is telehealth?\"}"
```

---

## Ingest Endpoint

```bash
curl -X POST http://localhost:8000/ingest \
-u admin:admin123
```

---

## Reset Endpoint

```bash
curl -X DELETE http://localhost:8000/reset \
-u admin:admin123
```

---

# Unauthorized Access Example

Request without authentication:

```http
POST /ask
```

Response:

```json
{
    "detail": "Not authenticated"
}
```

Status Code:

```text
401 Unauthorized
```

---

# Security Considerations

This implementation is intentionally simple and suitable for:

* Academic assignments
* Local development
* Demonstrations
* Proof-of-concept projects

For production systems, consider:

* OAuth2
* JWT tokens
* Password hashing
* User databases
* Role-based access control
* HTTPS enforcement

