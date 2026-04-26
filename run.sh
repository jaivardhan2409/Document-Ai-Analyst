#!/bin/bash

# Start the Backend (FastAPI) in the background
echo "Starting Backend on port 8000..."
export PYTHONPATH=$PYTHONPATH:/app/backend
cd /app/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Wait 10 seconds for backend and embedding models to load
echo "Waiting for backend to initialize..."
sleep 10

# Start the Frontend (Streamlit) using exec
echo "Starting Frontend on port 7860..."
cd /app/frontend && exec streamlit run app.py \
    --server.port 7860 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false
