#!/bin/bash

# Start the Backend (FastAPI) in the background on port 8000
echo "Starting Backend..."
export PYTHONPATH=$PYTHONPATH:/app/backend
cd /app/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Wait a few seconds for backend to warm up
sleep 5

# Start the Frontend (Streamlit) in the foreground on port 7860
echo "Starting Frontend..."
cd /app/frontend && streamlit run app.py --server.port 7860 --server.address 0.0.0.0
