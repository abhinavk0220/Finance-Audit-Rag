# Finance Audit RAG

A Retrieval-Augmented Generation (RAG) system for financial audits, SOX compliance, and SEC filings, leveraging **Azure OpenAI GPT models**, FAISS & Chroma vector stores, and a FastAPI backend. The project also supports a **Streamlit frontend** for interactive querying.

---

## 🏗️ Project Structure

finance-audit-rag/
│
├── .env # Environment variables
├── requirements.txt # Python dependencies
├── README.md
│
├── backend/ # FastAPI backend
│ ├── main.py # Entrypoint
│ ├── core/ # Core logic
│ │ ├── config.py # Environment + Azure setup
│ │ ├── rag_pipeline.py # Text → Embeddings → VectorStore
│ │ ├── retrievers.py # FAISS + Chroma EnsembleRetriever
│ │ ├── memory_tool.py # Chat memory & audit memory
│ │ └── utils.py # Helper functions
│ │
│ ├── routes/ # API endpoints
│ │ ├── ingest_routes.py # /ingest
│ │ └── query_routes.py # /query
│ │
│ ├── data/ # Data & vectorstores
│ │ ├── sox_docs/
│ │ ├── public_sec_docs/
│ │ ├── private_sec_docs/
│ │ └── vectorstores/
│ │ ├── faiss_store/
│ │ └── chroma_store/
│ │
│ ├── services/ # Optional background services
│ ├── tests/ # Unit & integration tests
│ └── logs/ # Log files
│
└── frontend/ # Streamlit dashboard
├── app.py
└── assets/


---

## ⚡ Features

- **RAG Pipeline:** Combines FAISS and Chroma vector stores with Azure OpenAI GPT models for accurate financial audit answers.
- **Multiple Data Sources:** Supports SOX regulations, public SEC filings, and confidential company documents.
- **Memory Support:** Keeps track of conversation history with custom memory tool.
- **FastAPI Backend:** Provides `/ingest` and `/query` endpoints for ingestion and querying.
- **Streamlit Frontend:** Interactive web dashboard for real-time queries.
- **Configurable via .env:** Easily set Azure API keys, deployment names, and vector store paths.

---

## 📝 Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone <repo_url>
cd finance-audit-rag
