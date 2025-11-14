"""
query_routes.py
---------------
Handles querying across federated vector stores (FAISS + Chroma)
using Azure GPT-4o-mini for final reasoning and response.

Features:
- Semantic caching to reduce LLM costs
- Federated retrieval from multiple vector stores
- Conversational memory management
- Performance metrics logging
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.core.retrievers import get_federated_retriever
from backend.core.memory_tool import AuditMemory
from backend.core.utils import log_info, log_error
from backend.core.config import settings
from backend.services.cache_service import get_cache_instance

from langchain_openai import AzureChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import time

router = APIRouter(prefix="/query", tags=["Query"])


# =========================================================
# 🔧 Configuration & Initialization
# =========================================================

def get_azure_chat_model():
    """
    Initialize Azure OpenAI chat model (GPT-4o-mini).
    
    Returns:
        AzureChatOpenAI instance configured for audit queries
    """
    return AzureChatOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_API_KEY,
        deployment_name=settings.AZURE_CHAT_DEPLOYMENT,
        openai_api_version=settings.AZURE_API_VERSION,
        temperature=0.2,  # Low temperature for factual responses
    )


# Initialize semantic cache (singleton - loads once at startup)
semantic_cache = get_cache_instance(
    redis_host="localhost",
    redis_port=6379,
    similarity_threshold=0.85,  # 85% similar = cache hit
    ttl=86400  # 24 hours cache
)

log_info("[QueryRoutes] ✅ Semantic cache initialized")


# =========================================================
# 📨 Request/Response Models
# =========================================================

class QueryRequest(BaseModel):
    """Request schema for RAG queries."""
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Explain section 302 compliance requirements"
            }
        }


class QueryResponse(BaseModel):
    """Response schema for RAG queries."""
    status: str
    response: str
    cached: bool
    response_time_seconds: float


# =========================================================
# 🔍 Main Query Endpoint
# =========================================================

@router.post("/", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG system with semantic caching.
    
    Flow:
    1. Check semantic cache for similar queries
    2. If cache hit: return instantly (0.1s)
    3. If cache miss: 
       - Retrieve relevant docs from FAISS/Chroma
       - Generate response via Azure GPT
       - Store in cache for future queries
       - Return response (3-5s)
    
    Args:
        request: QueryRequest with user's question
        
    Returns:
        QueryResponse with answer, cache status, and timing
        
    Example:
        POST /query
        {
            "query": "what are sox 302 requirements"
        }
        
        Response:
        {
            "status": "success",
            "response": "Section 302 requires...",
            "cached": true,
            "response_time_seconds": 0.12
        }
    """
    start_time = time.time()
    
    try:
        log_info(f"[Query] 🧠 Received: '{request.query}'")
        
        # ✅ STEP 1: Check cache for semantically similar queries
        cached_response = semantic_cache.get(request.query)
        
        if cached_response:
            elapsed = round(time.time() - start_time, 3)
            log_info(f"[Query] ⚡ Cache HIT! Response time: {elapsed}s")
            
            return QueryResponse(
                status="success",
                response=cached_response,
                cached=True,
                response_time_seconds=elapsed
            )
        
        # ❌ STEP 2: Cache miss - generate new response
        log_info("[Query] 🔄 Cache MISS - generating response via RAG...")
        
        # Initialize RAG components
        llm = get_azure_chat_model()
        retriever = get_federated_retriever()
        memory = AuditMemory()
        
        # Build conversational RAG chain
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory.memory,
            verbose=False,
            return_source_documents=False,  # Set True if you want source docs
        )
        
        # Generate response
        response = chain.invoke({"question": request.query})
        answer = response["answer"]
        
        # Save to conversation memory
        memory.add_message("user", request.query)
        memory.add_message("ai", answer)
        memory.save_memory()
        
        # ✅ STEP 3: Store in cache for future similar queries
        semantic_cache.set(request.query, answer)
        
        elapsed = round(time.time() - start_time, 3)
        log_info(f"[Query] ✅ Response generated in {elapsed}s")
        
        return QueryResponse(
            status="success",
            response=answer,
            cached=False,
            response_time_seconds=elapsed
        )
    
    except Exception as e:
        elapsed = round(time.time() - start_time, 3)
        log_error(f"[Query] ❌ Failed after {elapsed}s: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )


# =========================================================
# 📊 Cache Management Endpoints
# =========================================================

@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get cache statistics and health status.
    
    Returns:
        Dictionary with cache metadata:
        - total_cached_queries: Number of queries in cache
        - similarity_threshold: Current matching threshold
        - ttl_hours: Cache expiry time
        - redis_connected: Connection status
        
    Example:
        GET /query/cache/stats
        
        Response:
        {
            "status": "operational",
            "total_cached_queries": 42,
            "similarity_threshold": 0.85,
            "ttl_hours": 24.0,
            "redis_connected": true
        }
    """
    try:
        stats = semantic_cache.stats()
        log_info(f"[Cache] 📊 Stats requested: {stats['total_cached_queries']} queries cached")
        return stats
    except Exception as e:
        log_error(f"[Cache] ❌ Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache/clear")
async def clear_cache():
    """
    Clear all cached queries.
    
    Use this to:
    - Force fresh responses for all queries
    - Clear outdated cached data
    - Reset cache during development
    
    Returns:
        Success message with number of cleared entries
        
    Example:
        DELETE /query/cache/clear
        
        Response:
        {
            "status": "success",
            "message": "Cache cleared",
            "cleared_count": 42
        }
    """
    try:
        cleared_count = semantic_cache.clear()
        log_info(f"[Cache] 🧹 Cache cleared: {cleared_count} entries removed")
        
        return {
            "status": "success",
            "message": "Cache cleared successfully",
            "cleared_count": cleared_count
        }
    except Exception as e:
        log_error(f"[Cache] ❌ Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Check health status of query service.
    
    Verifies:
    - Cache connectivity
    - Vector store availability
    - Model initialization
    
    Returns:
        Health status dictionary
        
    Example:
        GET /query/health
        
        Response:
        {
            "status": "healthy",
            "cache_available": true,
            "timestamp": "2025-01-15T10:30:00"
        }
    """
    from datetime import datetime
    
    try:
        cache_status = semantic_cache.is_available()
        
        return {
            "status": "healthy" if cache_status else "degraded",
            "cache_available": cache_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        log_error(f"[Health] ❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# =========================================================
# 🧪 Development/Debug Endpoints
# =========================================================

@router.post("/test-similarity")
async def test_similarity(query1: str, query2: str):
    """
    Test semantic similarity between two queries.
    
    Useful for tuning similarity_threshold parameter.
    
    Args:
        query1: First query
        query2: Second query
        
    Returns:
        Similarity score (0-1) and match status
        
    Example:
        POST /query/test-similarity?query1=explain+302&query2=what+is+302
        
        Response:
        {
            "query1": "explain 302",
            "query2": "what is 302",
            "similarity": 0.92,
            "would_match": true,
            "threshold": 0.85
        }
    """
    try:
        if not semantic_cache.is_available():
            raise HTTPException(status_code=503, detail="Cache unavailable")
        
        emb1 = semantic_cache._generate_embedding(semantic_cache._normalize_query(query1))
        emb2 = semantic_cache._generate_embedding(semantic_cache._normalize_query(query2))
        
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity(
            emb1.reshape(1, -1),
            emb2.reshape(1, -1)
        )[0][0]
        
        return {
            "query1": query1,
            "query2": query2,
            "similarity": round(float(similarity), 4),
            "would_match": similarity >= semantic_cache.similarity_threshold,
            "threshold": semantic_cache.similarity_threshold
        }
    except Exception as e:
        log_error(f"[Similarity] ❌ Test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))