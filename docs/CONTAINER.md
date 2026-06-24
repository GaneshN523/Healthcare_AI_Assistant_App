# Containerization and CI/CD Setup

## Overview

This document describes the containerization approach implemented for the Healthcare AI Assistant project and the GitHub Actions workflow used to automatically build and publish Docker images.

---

# Project Architecture

The application consists of:

```text
User
  │
  ▼
Streamlit UI
  │
  ▼
FastAPI Backend
  │
  ▼
Ollama (Phi3 Model)
```

Components:

* Streamlit provides the user interface.
* FastAPI exposes backend APIs.
* Ollama serves the Phi3 language model.
* The application uses a Retrieval-Augmented Generation (RAG) pipeline built on local healthcare documents.

---

# Containerization Strategy

## Initial Considerations

Several deployment approaches were evaluated:

### Option 1: Run Ollama Inside Docker

Pros:

* Fully self-contained image

Cons:

* Large image size
* Increased complexity
* Model download required during image build
* Hardware-specific considerations

### Option 2: Keep Ollama on Host Machine

Pros:

* Smaller Docker image
* Faster builds
* Simpler deployment
* Existing local Ollama installation can be reused

This option was selected.

---

# Final Architecture

```text
Host Machine
│
├── Ollama
│    └── Phi3 Model
│
└── Docker Container
     ├── FastAPI
     └── Streamlit
```

The Docker container contains only the application code.

The language model remains outside the container.

---

# Configuration Changes

## Ollama Host Configuration

Originally:

```python
OLLAMA_HOST = "http://localhost:11434"
```

This would not work from inside a Docker container because:

```text
localhost inside a container refers to the container itself
```

The configuration was updated to use an environment variable:

```python
import os

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)
```

Benefits:

* Local development continues to work.
* Container deployments can specify a different host.
* No code changes are required across environments.

---

# Files Added

## 1. Dockerfile

Location:

```text
Dockerfile
```

Purpose:

* Defines how the Docker image is built.
* Installs Python dependencies.
* Copies project files into the image.
* Starts the application.

Implementation:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

EXPOSE 8000
EXPOSE 8501

CMD ["./start.sh"]
```

---

## 2. start.sh

Location:

```text
start.sh
```

Purpose:

A Docker container normally starts a single process.

Since the project contains:

* FastAPI
* Streamlit

both applications need to be started together.

Implementation:

```bash
#!/bin/sh

uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 &

streamlit run ui/stapp.py \
    --server.address 0.0.0.0 \
    --server.port 8501
```

Behavior:

* FastAPI runs in the background.
* Streamlit remains the primary process.

---

## 3. .dockerignore

Location:

```text
.dockerignore
```

Purpose:

Prevents unnecessary files from being included in the Docker build context.

Implementation:

```text
__pycache__/
*.pyc

.git/
.github/

tests/

.venv/
venv/

.env

*.db
```

Benefits:

* Smaller image size
* Faster builds
* Cleaner Docker images

---

## 4. GitHub Actions Workflow

Location:

```text
.github/workflows/docker-build.yml
```

Purpose:

Automates Docker image creation whenever code is pushed to the main branch.

Implementation:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches:
      - main

permissions:
  contents: read
  packages: write

jobs:
  docker:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build Image
        run: docker build -t ghcr.io/ganeshn523/healthcare-ai-assistant:latest .

      - name: Push Image
        run: docker push ghcr.io/ganeshn523/healthcare-ai-assistant:latest
```

---

# GitHub Authentication Issue Encountered

During workflow setup, pushes failed with:

```text
refusing to allow a Personal Access Token to create or update workflow
```

Cause:

The existing Personal Access Token did not include:

```text
workflow
```

permission.

Resolution:

A new Personal Access Token was created with:

```text
repo
workflow
write:packages
read:packages
```

The old credential was removed from Windows Credential Manager and replaced with the new token.

---

# GitHub Container Registry Issue Encountered

Initial workflow builds failed with:

```text
repository name must be lowercase
```

Cause:

Docker image names must be lowercase.

Repository owner:

```text
GaneshN523
```

contained uppercase characters.

Resolution:

The image name was changed to:

```text
ghcr.io/ganeshn523/healthcare-ai-assistant:latest
```

which satisfies Docker naming requirements.

---

# CI/CD Flow

Final automated workflow:

```text
Developer
    │
    ▼
git push origin main
    │
    ▼
GitHub Actions
    │
    ▼
Checkout Source Code
    │
    ▼
Docker Build
    │
    ▼
Publish Image to GHCR
```

No local Docker build is required.

---

# Result

The project now supports:

* Docker containerization
* FastAPI and Streamlit in a single container
* Automated image builds using GitHub Actions
* Publishing images to GitHub Container Registry (GHCR)
* Environment-based Ollama configuration
* Reproducible deployments across machines

The application source code remains lightweight while Ollama and the Phi3 model continue to run externally on the host machine.
