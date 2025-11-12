# backend/core/rag_pipeline.py

import os
import glob
from typing import List, Optional

from chromadb import Embeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS, Chroma
from langchain.docstore.document import Document

from backend.core.config import (
    get_azure_embeddings,
    VECTORSTORE_TYPE,
    VECTORSTORE_PATH,
)

# =========================================================
# 📘 Document Loading
# =========================================================

def load_documents_from_folder(folder_path: str) -> List[Document]:
    """
    Loads all .txt files from the given folder as LangChain Documents.
    Each document is assigned metadata for source tracking.
    """
    docs = []
    for file_path in glob.glob(os.path.join(folder_path, "*.txt")):
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            loaded_docs = loader.load()
            for doc in loaded_docs:
                doc.metadata["source"] = os.path.basename(file_path)
            docs.extend(loaded_docs)
        except Exception as e:
            print(f"[load_documents_from_folder] ⚠️ Error loading {file_path}: {e}")
    return docs


# =========================================================
# ✂️ Text Splitting
# =========================================================

def split_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 150) -> List[Document]:
    """
    Splits documents into smaller overlapping chunks for better embedding.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", " "],
    )
    return splitter.split_documents(documents)


# =========================================================
# 🧠 Embedding + VectorStore Builder
# =========================================================

def build_vectorstore(docs: List[Document], persist_path: Optional[str] = None):
    """
    Embeds documents using Azure Embeddings and saves to either FAISS or Chroma.
    """
    print(f"[build_vectorstore] 🚀 Building vectorstore: {VECTORSTORE_TYPE}")
    embeddings = get_azure_embeddings()

    if VECTORSTORE_TYPE.lower() == "faiss":
        vectorstore = FAISS.from_documents(docs, embedding=embeddings)
        save_path = persist_path or os.path.join(VECTORSTORE_PATH, "faiss_store")
        os.makedirs(save_path, exist_ok=True)
        vectorstore.save_local(save_path)
        print(f"[build_vectorstore] 💾 FAISS index saved at: {save_path}")

    elif VECTORSTORE_TYPE.lower() == "chroma":
        persist_dir = persist_path or os.path.join(VECTORSTORE_PATH, "chroma_store")
        os.makedirs(persist_dir, exist_ok=True)
        vectorstore = Chroma.from_documents(
            docs,
            embedding=embeddings,
            persist_directory=persist_dir,
        )
        vectorstore.persist()
        print(f"[build_vectorstore] 💾 Chroma DB persisted at: {persist_dir}")

    else:
        raise ValueError(f"❌ Unsupported vectorstore type: {VECTORSTORE_TYPE}")

    print(f"[build_vectorstore] ✅ Vectorstore built successfully.")
    return vectorstore


# =========================================================
# 🔁 Combined Pipeline: Load → Split → Embed → Save
# =========================================================

def ingest_corpus(corpus_path: str, persist_path: Optional[str] = None):
    """
    Complete pipeline:
    - Load .txt files
    - Split into chunks
    - Embed + store
    """
    print(f"[ingest_corpus] 📂 Loading corpus from: {corpus_path}")

    raw_docs = load_documents_from_folder(corpus_path)
    if not raw_docs:
        print("[ingest_corpus] ⚠️ No documents found to ingest.")
        return None

    print(f"[ingest_corpus] 🧩 Loaded {len(raw_docs)} raw documents.")
    chunks = split_documents(raw_docs)
    print(f"[ingest_corpus] ✂️ Split into {len(chunks)} chunks.")

    vectorstore = build_vectorstore(chunks, persist_path=persist_path)
    print("[ingest_corpus] ✅ Ingestion pipeline completed successfully.")
    return vectorstore

# -------------------------------
# FAISS Store Creation
# -------------------------------
def create_faiss_store(documents: list, embeddings: Embeddings, store_path: str):
    """
    Create or update a FAISS vectorstore with documents and embeddings.
    """
    import os
    os.makedirs(store_path, exist_ok=True)

    vectorstore = FAISS.from_documents(documents, embeddings)
    faiss_file = os.path.join(store_path, "faiss_index")
    vectorstore.save_local(faiss_file)
    return vectorstore

# -------------------------------
# Chroma Store Creation
# -------------------------------
def create_chroma_store(documents: list, embeddings: Embeddings, store_path: str):
    """
    Create or update a Chroma vectorstore with documents and embeddings.
    """
    import os
    from langchain.vectorstores import Chroma

    os.makedirs(store_path, exist_ok=True)

    vectorstore = Chroma.from_documents(documents, embedding=embeddings, persist_directory=store_path)
    vectorstore.persist()
    return vectorstore



# =========================================================
# 🧪 Test (Run standalone)
# =========================================================

if __name__ == "__main__":
    test_path = "./backend/data/sox_docs"
    ingest_corpus(test_path)
