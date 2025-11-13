"""
ingest_routes.py
----------------
Handles ingestion of uploaded SOX & SEC documents into FAISS and Chroma vector stores.
Supports both folder-based ingestion and user-uploaded files.
"""

from fastapi import APIRouter, UploadFile, File, Form
from backend.core.utils import log_info, log_error, load_documents_from_dir
from backend.core.rag_pipeline import create_faiss_store, create_chroma_store
from backend.core.config import settings
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from pathlib import Path
import shutil

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
# Helpers
# --------------------------
def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def load_uploaded_document(file_path: str):
    """Load and split a single uploaded document."""
    ext = file_path.lower().split(".")[-1]
    if ext == "txt":
        loader = TextLoader(file_path, encoding="utf-8")
    elif ext == "pdf":
        loader = PyPDFLoader(file_path)
    else:
        loader = UnstructuredFileLoader(file_path)

    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(docs)

# --------------------------
# POST /ingest (existing folder ingestion)
# --------------------------
@router.post("/")
async def ingest_from_directories():
    """Ingests all pre-defined document directories into FAISS and Chroma."""
    try:
        log_info("🚀 Ingestion from directories started...")

        sox_docs = load_documents_from_dir("./backend/data/sox_docs")
        public_docs = load_documents_from_dir("./backend/data/public")
        private_docs = load_documents_from_dir("./backend/data/private")

        all_docs = sox_docs + public_docs + private_docs
        if not all_docs:
            return {"status": "warning", "message": "No documents found to ingest."}

        embeddings = get_azure_embeddings()
        faiss_path = "./backend/data/vectorstores/faiss_store"
        chroma_path = "./backend/data/vectorstores/chroma_store"

        if sox_docs or private_docs:
            create_faiss_store(sox_docs + private_docs, embeddings, faiss_path)
        if public_docs:
            create_chroma_store(public_docs, embeddings, chroma_path)

        log_info("✅ Folder ingestion completed successfully.")
        return {
            "status": "success",
            "faiss_docs": len(sox_docs) + len(private_docs),
            "chroma_docs": len(public_docs),
            "message": "Predefined documents ingested successfully."
        }

    except Exception as e:
        log_error(f"❌ Folder ingestion failed: {e}")
        return {"status": "error", "message": str(e)}

# --------------------------
# POST /ingest/upload (NEW)
# --------------------------
@router.post("/upload")
async def upload_and_ingest_document(
    files: list[UploadFile] = File(...),
    category: str = Form(...),  # "public" or "private"
):
    """
    Upload one or more documents and ingest them into FAISS or Chroma
    based on their category.
    """
    try:
        log_info(f"📥 Upload received for category: {category}")

        # Validate category
        if category not in ["public", "private"]:
            return {"status": "error", "message": "Category must be 'public' or 'private'."}

        upload_dir = f"./backend/data/{category}"  
        ensure_dir(upload_dir)

        saved_files = []
        for file in files:
            dest_path = os.path.join(upload_dir, file.filename)
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            saved_files.append(dest_path)

        log_info(f"📄 Saved {len(saved_files)} files.")

        # Load + split uploaded docs
        all_chunks = []
        for path in saved_files:
            chunks = load_uploaded_document(path)
            all_chunks.extend(chunks)

        embeddings = get_azure_embeddings()

        if category == "private":
            store_path = "./backend/data/vectorstores/faiss_store/faiss_index"
            create_faiss_store(all_chunks, embeddings, store_path)
            store_type = "FAISS"
        else:
            store_path = "./backend/data/vectorstores/chroma_store"
            create_chroma_store(all_chunks, embeddings, store_path)
            store_type = "Chroma"

        log_info(f"✅ Uploaded documents ingested into {store_type} successfully.")
        return {
            "status": "success",
            "category": category,
            "ingested_docs": len(saved_files),
            "message": f"Uploaded documents ingested into {store_type} store."
        }

    except Exception as e:
        log_error(f"❌ Upload ingestion failed: {e}")
        return {"status": "error", "message": str(e)}
