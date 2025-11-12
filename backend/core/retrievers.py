# backend/core/retrievers.py

import os
from langchain_community.vectorstores import FAISS, Chroma
from langchain.retrievers import EnsembleRetriever
from backend.core.config import get_azure_embeddings, VECTORSTORE_PATH


# =========================================================
# 🧠 Helper: Load Individual VectorStores
# =========================================================

def load_faiss_store(store_path: str):
    """
    Load FAISS vector store if available.
    """
    faiss_dir = os.path.join(store_path, "faiss_store", "faiss_index")
    print(f"[retrievers] Debug: VECTORSTORE_PATH={VECTORSTORE_PATH}")
    print(f"[retrievers] Debug: FAISS path={faiss_dir}")
    index_file = os.path.join(faiss_dir, "index.faiss")
    if not os.path.exists(index_file):
        # print("Hello")
        print("[retrievers] ⚠️ FAISS index file not found, skipping.")
        return None

    if not os.path.exists(faiss_dir):
        # print("Hello2")
        print("[retrievers] ⚠️ FAISS store not found, skipping.")
        return None

    try:
        embeddings = get_azure_embeddings()
        vectorstore = FAISS.load_local(
            faiss_dir,
            embeddings,
            allow_dangerous_deserialization=True,  # safe in dev mode
        )
        print(f"[retrievers] ✅ FAISS store loaded from: {faiss_dir}")
        return vectorstore.as_retriever(search_kwargs={"k": 4})
    except Exception as e:
        print(f"[retrievers] ❌ Failed to load FAISS store: {e}")
        return None



def load_chroma_store(store_path: str):
    """
    Load Chroma vector store if available.
    """
    chroma_dir = os.path.join(store_path, "chroma_store")
    print(f"[retrievers] Debug: Chroma path={chroma_dir}")
    if not os.path.exists(chroma_dir):
        print("[retrievers] ⚠️ Chroma store not found, skipping.")
        return None

    # Pick the first subfolder (the one created by Chroma ingestion)
    chroma_subfolders = [
        os.path.join(chroma_dir, d) for d in os.listdir(chroma_dir)
        if os.path.isdir(os.path.join(chroma_dir, d))
    ]
    if chroma_subfolders:
        persist_dir = chroma_subfolders[0]
    else:
        persist_dir = chroma_dir  # fallback

    try:
        embeddings = get_azure_embeddings()
        vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings,
        )
        print(f"[retrievers] ✅ Chroma store loaded from: {persist_dir}")
        return vectorstore.as_retriever(search_kwargs={"k": 4})
    except Exception as e:
        print(f"[retrievers] ❌ Failed to load Chroma store: {e}")
        return None



# =========================================================
# 🤝 Federated Retrieval: EnsembleRetriever
# =========================================================

def get_federated_retriever(faiss_weight: float = 0.6, chroma_weight: float = 0.4):
    """
    Combines FAISS + Chroma retrievers into a weighted EnsembleRetriever.
    If one store is missing, falls back to the other automatically.
    """
    print("[retrievers] 🔍 Initializing federated retriever...")
    

    faiss_retriever = load_faiss_store(VECTORSTORE_PATH)
    chroma_retriever = load_chroma_store(VECTORSTORE_PATH)

    retrievers = []
    weights = []

    if faiss_retriever:
        retrievers.append(faiss_retriever)
        weights.append(faiss_weight)
    if chroma_retriever:
        retrievers.append(chroma_retriever)
        weights.append(chroma_weight)

    if not retrievers:
        raise ValueError("❌ No available retrievers found (FAISS/Chroma missing).")

    if len(retrievers) == 1:
        print("[retrievers] ⚙️ Only one retriever available — using it directly.")
        return retrievers[0]

    print(f"[retrievers] 🤝 EnsembleRetriever combining {len(retrievers)} sources.")
    ensemble_retriever = EnsembleRetriever(
        retrievers=retrievers,
        weights=weights,
    )
    return ensemble_retriever


# =========================================================
# 🧪 Test (Run standalone)
# =========================================================

if __name__ == "__main__":
    retriever = get_federated_retriever()
    print("[retrievers] ✅ Federated retriever ready for queries.")
    results = retriever.get_relevant_documents("SOX compliance testing controls")
    print(f"[retrievers] Retrieved {len(results)} docs:")
    for r in results[:3]:
        print(f" - {r.metadata.get('source', 'unknown')} | {r.page_content[:80]}...")
