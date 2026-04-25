---
title: Document AI Analyst
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 8501
pinned: true
license: mit
short_description: Enterprise Agentic RAG — upload documents and chat with AI
---

# 🧠 Document AI Analyst — Enterprise Agentic RAG System

Upload complex PDFs, DOCX files, CSVs, or text documents and chat with an AI agent that provides accurate, cited insights powered by Retrieval-Augmented Generation.

## ✨ Features

- **Multi-Format Upload** — PDF, DOCX, TXT, CSV, and Markdown with smart chunking
- **Semantic Search** — High-precision vector retrieval using Google Gemini embeddings
- **Streaming Chat** — Real-time AI responses with inline source citations
- **Data Isolation** — Per-user knowledge bases and vector collections for complete privacy
- **Persistent Sessions** — Seamless authentication with secure JWT tokens
- **Premium UI** — Custom dark-themed Streamlit interface with glassmorphism and micro-animations

## 🏗️ Architecture

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit, Custom CSS Injection, SSE |
| **Backend** | FastAPI, SQLAlchemy, JWT Auth |
| **Embeddings** | Google Gemini (`gemini-embedding-001`) |
| **Vector Store** | ChromaDB (persistent, per-user collections) |
| **Database** | PostgreSQL (User metadata, Document tracking) |
| **LLM** | Google Gemini (`gemini-2.5-flash-lite`) |
| **Deployment** | Docker Compose multi-container orchestration |

## 🚀 Quick Start

1. Clone the repository and create your `.env` file:
   ```bash
   cp .env.example .env
   ```
2. Add your Gemini API Key to the `.env` file.
3. Start the application using Docker Compose:
   ```bash
   docker compose up -d --build
   ```
4. Access the UI at `http://localhost:8501`. Register an account, upload a document, and start chatting!

## 🔧 Local Development

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload
```

### Frontend
```bash
cd frontend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 📦 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key for LLM and embeddings |
| `POSTGRES_USER` | ✅ | PostgreSQL database user |
| `POSTGRES_PASSWORD` | ✅ | PostgreSQL database password |
| `POSTGRES_DB` | ✅ | PostgreSQL database name |
| `SECRET_KEY` | ✅ | JWT signing secret string |

## 🛠️ Tech Stack

Built with: FastAPI • Streamlit • ChromaDB • Google Gemini • PostgreSQL • Docker Compose
