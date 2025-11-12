"""
ingest_routes.py
----------------
Handles ingestion of SOX & SEC documents into FAISS and Chroma vector stores.
"""

from fastapi import APIRouter
from backend.core.utils import log_info, log_error, load_documents_from_dir
from backend.core.rag_pipeline import create_faiss_store, create_chroma_store
from backend.core.config import settings
from langchain_openai import AzureOpenAIEmbeddings
import os

router = APIRouter(prefix="/ingest", tags=["Ingest"])

# --------------------------
# Embedding Model Setup
# --------------------------

def get_azure_embeddings():
    return AzureOpenAIEmbeddings(
        model=settings.AZURE_EMBEDDING_DEPLOYMENT,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_API_KEY,
    )


# --------------------------
# POST /ingest Endpoint
# --------------------------

@router.post("/")
async def ingest_documents():
    """
    Ingests SOX, public SEC, and private SEC documents
    into FAISS and Chroma vector stores.
    """
    try:
        log_info("🚀 Ingestion started...")

        # Load documents
        sox_docs = load_documents_from_dir("./backend/data/sox_docs")
        public_docs = load_documents_from_dir("./backend/data/public_sec_docs")
        private_docs = load_documents_from_dir("./backend/data/private_sec_docs")

        # Combine docs for processing
        all_docs = sox_docs + public_docs + private_docs

        if not all_docs:
            return {"status": "warning", "message": "No documents found to ingest."}

        embeddings = get_azure_embeddings()

        # Create and persist stores
        faiss_path = "./backend/data/vectorstores/faiss_store"
        chroma_path = "./backend/data/vectorstores/chroma_store"

        if sox_docs or private_docs:
            create_faiss_store(sox_docs + private_docs, embeddings, faiss_path)
        if public_docs:
            create_chroma_store(public_docs, embeddings, chroma_path)

        log_info("✅ Ingestion completed successfully.")
        return {
            "status": "success",
            "faiss_docs": len(sox_docs) + len(private_docs),
            "chroma_docs": len(public_docs),
            "message": "Documents ingested into FAISS and Chroma successfully.",
        }

    except Exception as e:
        log_error(f"❌ Ingestion failed: {e}")
        return {"status": "error", "message": str(e)}
