# """
# query_routes.py
# ----------------
# Handles querying across federated vector stores (FAISS + Chroma)
# using Azure GPT-4o-mini for final reasoning and response.
# """

# from logging import config
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from pytest import Config
# from backend.core.retrievers import get_federated_retriever
# from backend.core.memory_tool import AuditMemory
# from backend.core.utils import log_info, log_error
# # from backend.core.config import Config
# from backend.core.config import settings


# from langchain_openai import AzureChatOpenAI
# from langchain.chains import ConversationalRetrievalChain
# import time

# router = APIRouter(prefix="/query", tags=["Query"])

# # --------------------------
# # Request schema
# # --------------------------
# class QueryRequest(BaseModel):
#     query: str


# # --------------------------
# # Setup model + memory
# # --------------------------
# def get_azure_chat_model():
#     """Return GPT-4o-mini model from Azure OpenAI."""
#     return AzureChatOpenAI(
#         azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
#         api_key=settings.AZURE_API_KEY,
#         deployment_name=settings.AZURE_CHAT_DEPLOYMENT,
#         openai_api_version=settings.AZURE_API_VERSION,
#         temperature=0.2,
#     )


# # --------------------------
# # POST /query
# # --------------------------
# @router.post("/")
# async def query_rag(request: QueryRequest):
#     """
#     Query the federated retriever (FAISS + Chroma)
#     and get a response from Azure GPT-4o-mini.
#     """
#     start = time.time()
#     try:
#         log_info(f"🧠 Query received: {request.query}")

#         # Initialize components
#         llm = get_azure_chat_model()
#         retriever = get_federated_retriever()
#         memory = AuditMemory()

#         # Build RAG Chain
#         chain = ConversationalRetrievalChain.from_llm(
#             llm=llm,
#             retriever=retriever,
#             memory=memory.memory,
#             verbose=False,
#         )

#         # Generate answer
#         response = chain.invoke({"question": request.query})
#         answer = response["answer"]

#         # Log and save memory
#         memory.add_message("user", request.query)
#         memory.add_message("ai", answer)
#         memory.save_memory()

#         log_info(f"✅ Response generated in {round(time.time() - start, 2)}s")
#         return {"status": "success", "response": answer}

#     except Exception as e:
#         log_error(f"❌ Query failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

"""
query_routes.py
----------------
Handles querying across federated vector stores (FAISS + Chroma)
using Azure GPT-4o-mini for final reasoning and response.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
import redis  # 🧩 ADDED
import json   # 🧩 ADDED

from backend.core.retrievers import get_federated_retriever
from backend.core.memory_tool import AuditMemory
from backend.core.utils import log_info, log_error
from backend.core.config import settings
from backend.core.config import settings, get_azure_embeddings


from langchain_openai import AzureChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import time
from backend.core.cache_manager import SemanticCache




router = APIRouter(prefix="/query", tags=["Query"])

# =========================================================
# ⚙️ Redis Cache Setup (🧩 ADDED)
# =========================================================
try:
    redis_client = redis.StrictRedis(
        host="localhost",  # if running locally
        port=6379,
        db=0,
        decode_responses=True,
    )
    redis_client.ping()
    print("[cache] ✅ Redis connected successfully.")
except Exception as e:
    redis_client = None
    print(f"[cache] ⚠️ Redis connection failed: {e}")


# --------------------------
# Request schema
# --------------------------
class QueryRequest(BaseModel):
    query: str


# Initialize cache ONCE at module level (singleton)
semantic_cache = SemanticCache(
    redis_host="localhost",
    redis_port=6379,
    similarity_threshold=0.85,  # Tune this: higher = stricter matching
    ttl=86400  # 24 hours
)
# --------------------------
# Setup model + memory
# --------------------------
def get_azure_chat_model():
    """Return GPT-4o-mini model from Azure OpenAI."""
    return AzureChatOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_API_KEY,
        deployment_name=settings.AZURE_CHAT_DEPLOYMENT,
        openai_api_version=settings.AZURE_API_VERSION,
        temperature=0.2,
    )


# =========================================================
# POST /query
# --------------------------
# @router.post("/")
# async def query_rag(request: QueryRequest):
#     """
#     Query the federated retriever (FAISS + Chroma)
#     and get a response from Azure GPT-4o-mini.
#     """
#     start = time.time()
#     try:
#         log_info(f"🧠 Query received: {request.query}")

#         # Initialize components
#         llm = get_azure_chat_model()
#         retriever = get_federated_retriever()
#         memory = AuditMemory()

#         # Build RAG Chain
#         chain = ConversationalRetrievalChain.from_llm(
#             llm=llm,
#             retriever=retriever,
#             memory=memory.memory,
#             verbose=False,
#         )

#         # Generate answer
#         response = chain.invoke({"question": request.query})
#         answer = response["answer"]

#         # Log and save memory
#         memory.add_message("user", request.query)
#         memory.add_message("ai", answer)
#         memory.save_memory()

#         log_info(f"✅ Response generated in {round(time.time() - start, 2)}s")
#         return {"status": "success", "response": answer}

#     except Exception as e:
#         log_error(f"❌ Query failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
@router.post("/")
async def query_rag(request: QueryRequest):
    """
    Query with semantic caching.
    """
    start = time.time()
    query_text = request.query.strip().lower()  # 🧩 Normalize for caching key
    cache_key = f"query_cache:{query_text}"

    try:
        log_info(f"🧠 Query received: {request.query}")
        
        # ✅ CHECK CACHE FIRST
        cached_response = semantic_cache.get(request.query)
        if cached_response:
            log_info(f"⚡ Cache hit! Response time: {round(time.time() - start, 2)}s")
            return {
                "status": "success",
                "response": cached_response,
                "cached": True  # Let frontend know it's cached
            }
        
        # ❌ CACHE MISS - Generate new response
        log_info("🔄 Cache miss, generating response...")
        
        llm = get_azure_chat_model()
        retriever = get_federated_retriever()
        memory = AuditMemory()

        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory.memory,
            verbose=False,
        )

        response = chain.invoke({"question": request.query})
        answer = response["answer"]

        # Save to memory
        memory.add_message("user", request.query)
        memory.add_message("ai", answer)
        memory.save_memory()
        
        # ✅ STORE IN CACHE
        semantic_cache.set(request.query, answer)

        # =========================================================
        # 💾 Save to Redis cache (🧩 ADDED)
        # =========================================================
        if redis_client:
            redis_client.setex(cache_key, 3600, json.dumps(answer))  # 1 hour TTL
            print(f"[cache] 💾 Cached response for query: '{request.query}'")

        log_info(f"✅ Response generated in {round(time.time() - start, 2)}s")
        return {
            "status": "success",
            "response": answer,
            "cached": False
        }

    except Exception as e:
        log_error(f"❌ Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ✅ ADD CACHE MANAGEMENT ENDPOINTS
@router.get("/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    return semantic_cache.stats()


@router.delete("/cache/clear")
async def clear_cache():
    """Clear all cached queries."""
    semantic_cache.clear()
    return {"status": "success", "message": "Cache cleared"}
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

        # ✅ Use the imported function from config.py
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
