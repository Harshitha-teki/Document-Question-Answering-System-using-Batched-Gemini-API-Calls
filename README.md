# 📄 Intelligent Document Q&A System (RAG)

A high-performance Retrieval-Augmented Generation (RAG) application utilizing **Gemini 2.5 Flash** to provide context-aware answers from uploaded documents.

## 🚀 Quick Start
1. **Clone the repo:** `git clone <your-repo-link>`
2. **Setup Env:** `cp .env.example .env` and add your `GEMINI_API_KEY`.
3. **Run:** `docker-compose up --build`

## 🛠️ Tech Stack
- **Backend:** FastAPI (Microservices Architecture)
- **Frontend:** Streamlit
- **LLM:** Google Gemini 2.5 Flash
- **DevOps:** Docker & Docker-Compose

## ✨ Core Features
- **Async Processing:** Status polling for large document ingestion.
- **Batched Retrieval:** Optimized Top-K context injection for accuracy.
- **Token Analytics:** Real-time tracking of prompt and completion tokens.