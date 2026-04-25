# 🧠 Premium RAG AI Assistant

A full-stack, production-ready Retrieval-Augmented Generation (RAG) application with a premium dark-themed UI. Upload documents, organize them into separate knowledge bases, and chat with them using Google's Gemini LLM.

## ✨ Features

- **Multi-Document Knowledge Bases**: Create isolated collections for different contexts (e.g., "Resumes", "Research", "Notes").
- **Extended File Support**: Process PDF, TXT, DOCX, CSV, and Markdown files.
- **Streaming Responses**: Real-time, word-by-word LLM answers with a pulsing cursor effect.
- **Premium UI/UX**: Custom dark theme, glassmorphism elements, gradient accents, and micro-animations.
- **Persistent Sessions**: Stay logged in across browser refreshes (15-minute file-based persistence).
- **Source Citations**: View exactly which document chunks the AI used to formulate its answer, complete with relevance scores.

## 🏗️ Architecture

- **Frontend**: Streamlit (with custom CSS injection and SSE streaming)
- **Backend API**: FastAPI (Python 3.10)
- **Database (Relational)**: PostgreSQL (Users, Document Metadata, Collections)
- **Database (Vector)**: ChromaDB (Embeddings, Semantic Search)
- **Cache / Rate Limiting**: Redis
- **LLM & Embeddings**: Google Gemini (`gemini-2.5-flash-lite` & `gemini-embedding-001`)
- **Infrastructure**: Docker Compose (Containerized setup)

## 🚀 Quick Start

### 1. Prerequisites
- Docker and Docker Compose installed
- Google Gemini API Key

### 2. Environment Setup
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Edit `.env` and add your Gemini API Key and desired passwords.

### 3. Run the Application
```bash
docker compose up -d --build
```

### 4. Access the UI
Open your browser and navigate to:
`http://localhost:8501`

## 📂 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── routers/             # API endpoints (auth, documents, chat)
│   │   ├── services/            # Core logic (LLM, embeddings, extraction)
│   │   └── models/              # SQLAlchemy database models
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── .streamlit/
│   │   └── config.toml          # Native Streamlit dark theme config
│   ├── app.py                   # Streamlit UI & custom CSS
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml           # Multi-container orchestration
├── .env.example                 # Environment variables template
└── .gitignore
```

## 🔒 Security Note
This project uses hardcoded secrets in the `docker-compose.yml` for demonstration purposes. Before deploying to production, ensure all secrets are properly managed via the `.env` file and not committed to version control.
