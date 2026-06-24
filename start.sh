#!/bin/sh

echo "Starting FastAPI..."

uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 &

echo "Starting Streamlit..."

streamlit run ui/stapp.py \
    --server.address 0.0.0.0 \
    --server.port 8501