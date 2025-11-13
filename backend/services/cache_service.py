# """
# cache_service.py
# -----------------
# Handles Redis caching for query responses.
# Caches both the query and its generated answer
# to reduce recomputation and speed up responses.
# """

# import redis
# import json
# from backend.core.utils import log_info, log_error
# from backend.core.config import settings

# # Initialize Redis connection
# try:
#     redis_client = redis.StrictRedis(
#         host="localhost",     # or settings.REDIS_HOST if in .env
#         port=6379,
#         db=0,
#         decode_responses=True
#     )
#     redis_client.ping()
#     log_info("✅ Connected to Redis cache successfully.")
# except Exception as e:
#     log_error(f"❌ Redis connection failed: {e}")
#     redis_client = None


# def get_cached_response(query: str):
#     """Fetch cached response from Redis."""
#     if not redis_client:
#         return None
#     try:
#         cached_value = redis_client.get(query)
#         if cached_value:
#             log_info(f"⚡ Cache hit for query: {query}")
#             return json.loads(cached_value)
#     except Exception as e:
#         log_error(f"Redis read error: {e}")
#     return None


# def set_cached_response(query: str, response: str, ttl_seconds: int = 3600):
#     """Store response in Redis cache with TTL."""
#     if not redis_client:
#         return
#     try:
#         redis_client.setex(query, ttl_seconds, json.dumps(response))
#         log_info(f"💾 Cached query for {ttl_seconds}s: {query}")
#     except Exception as e:
#         log_error(f"Redis write error: {e}")

# backend/services/cache.py
"""
cache.py
--------
Semantic caching service for RAG queries using Redis.
Handles similarity-based query matching to reduce redundant LLM calls.

Features:
- Semantic similarity matching using sentence embeddings
- Redis-based persistent storage with TTL
- Global cache across all users
- Automatic cache expiry
"""

import redis
import json
import hashlib
from typing import Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from backend.core.utils import log_info, log_error


class SemanticCache:
    """
    Redis-backed semantic cache for RAG responses.
    
    Uses sentence embeddings to match semantically similar queries,
    enabling cache hits for questions with different wording but same meaning.
    
    Example:
        "explain section 302" ≈ "what is section 302" → cache hit
    """
    
    def __init__(
        self, 
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_password: Optional[str] = None,
        similarity_threshold: float = 0.85,
        ttl: int = 86400,
        use_ssl: bool = False
    ):
        """
        Initialize semantic cache with Redis backend.
        
        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
            redis_password: Redis password (if required)
            similarity_threshold: Minimum cosine similarity for cache hit (0-1)
                                0.85 = 85% similar queries match
            ttl: Cache expiry time in seconds (default: 24 hours)
            use_ssl: Use SSL for Redis connection (required for Redis Cloud)
        """
        try:
            # Connect to Redis
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True,
                ssl=use_ssl,
                socket_connect_timeout=5
            )
            
            # Test connection
            self.redis_client.ping()
            log_info(f"[Cache] ✅ Connected to Redis at {redis_host}:{redis_port}")
            
        except redis.ConnectionError as e:
            log_error(f"[Cache] ❌ Redis connection failed: {e}")
            log_info("[Cache] ⚠️ Falling back to no-cache mode")
            self.redis_client = None
        
        self.similarity_threshold = similarity_threshold
        self.ttl = ttl
        
        # Load lightweight embedding model for semantic matching
        try:
            log_info("[Cache] 🔄 Loading sentence embedding model...")
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            log_info("[Cache] ✅ Embedding model loaded (all-MiniLM-L6-v2)")
        except Exception as e:
            log_error(f"[Cache] ❌ Failed to load embedding model: {e}")
            self.encoder = None
    
    def is_available(self) -> bool:
        """Check if cache is operational."""
        return self.redis_client is not None and self.encoder is not None
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate semantic embedding vector for text.
        
        Args:
            text: Input text to embed
            
        Returns:
            384-dimensional numpy array representing semantic meaning
        """
        if not self.encoder:
            return np.array([])
        return self.encoder.encode(text, convert_to_numpy=True)
    
    def _normalize_query(self, query: str) -> str:
        """
        Normalize query for consistent matching.
        
        Args:
            query: Raw user query
            
        Returns:
            Normalized query (lowercase, stripped whitespace)
        """
        return query.lower().strip()
    
    def get(self, query: str) -> Optional[str]:
        """
        Check cache for semantically similar query.
        
        Args:
            query: User's question
            
        Returns:
            Cached response if similarity > threshold, else None
            
        Example:
            >>> cache.get("explain section 302")
            "Section 302 requires CEO/CFO certification..."
            
            >>> cache.get("what is section 302")  # Similar query
            "Section 302 requires CEO/CFO certification..."  # Same cached response
        """
        if not self.is_available():
            log_info("[Cache] ⚠️ Cache unavailable, skipping lookup")
            return None
        
        try:
            query_norm = self._normalize_query(query)
            query_embedding = self._generate_embedding(query_norm)
            
            # Get all cached queries
            cached_keys = self.redis_client.keys("query:*")
            
            if not cached_keys:
                log_info(f"[Cache] ❌ MISS: '{query}' (empty cache)")
                return None
            
            # Find most similar cached query
            max_similarity = 0.0
            best_match_key = None
            best_match_query = None
            
            for key in cached_keys:
                try:
                    cached_data = json.loads(self.redis_client.get(key))
                    cached_embedding = np.array(cached_data["embedding"])
                    
                    # Calculate cosine similarity
                    similarity = cosine_similarity(
                        query_embedding.reshape(1, -1),
                        cached_embedding.reshape(1, -1)
                    )[0][0]
                    
                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_match_key = key
                        best_match_query = cached_data["query"]
                
                except Exception as e:
                    log_error(f"[Cache] ⚠️ Error checking key {key}: {e}")
                    continue
            
            # Return cached response if similarity exceeds threshold
            if max_similarity >= self.similarity_threshold:
                cached_data = json.loads(self.redis_client.get(best_match_key))
                response = cached_data["response"]
                
                log_info(
                    f"[Cache] ✅ HIT: '{query}' ≈ '{best_match_query}' "
                    f"(similarity: {max_similarity:.3f})"
                )
                return response
            
            log_info(
                f"[Cache] ❌ MISS: '{query}' "
                f"(best match: {max_similarity:.3f} < {self.similarity_threshold})"
            )
            return None
        
        except Exception as e:
            log_error(f"[Cache] ❌ Error during cache lookup: {e}")
            return None
    
    def set(self, query: str, response: str) -> bool:
        """
        Store query-response pair with semantic embedding.
        
        Args:
            query: User's question
            response: Generated answer from RAG system
            
        Returns:
            True if successfully cached, False otherwise
            
        Example:
            >>> cache.set("explain section 302", "Section 302 requires...")
            True
        """
        if not self.is_available():
            log_info("[Cache] ⚠️ Cache unavailable, skipping storage")
            return False
        
        try:
            query_norm = self._normalize_query(query)
            query_embedding = self._generate_embedding(query_norm)
            
            # Generate unique key using MD5 hash
            query_hash = hashlib.md5(query_norm.encode()).hexdigest()
            key = f"query:{query_hash}"
            
            # Build cache entry
            cache_data = {
                "query": query_norm,
                "response": response,
                "embedding": query_embedding.tolist()
            }
            
            # Store in Redis with TTL
            self.redis_client.setex(
                key,
                self.ttl,
                json.dumps(cache_data)
            )
            
            log_info(f"[Cache] 💾 Stored: '{query}' (expires in {self.ttl}s)")
            return True
        
        except Exception as e:
            log_error(f"[Cache] ❌ Error storing cache: {e}")
            return False
    
    def clear(self) -> int:
        """
        Clear all cached queries.
        
        Returns:
            Number of keys deleted
        """
        if not self.is_available():
            log_info("[Cache] ⚠️ Cache unavailable")
            return 0
        
        try:
            keys = self.redis_client.keys("query:*")
            count = len(keys)
            
            if keys:
                self.redis_client.delete(*keys)
                log_info(f"[Cache] 🧹 Cleared {count} cached queries")
            else:
                log_info("[Cache] 🧹 No cached queries to clear")
            
            return count
        
        except Exception as e:
            log_error(f"[Cache] ❌ Error clearing cache: {e}")
            return 0
    
    def stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache metadata
        """
        if not self.is_available():
            return {
                "status": "unavailable",
                "message": "Cache is not operational"
            }
        
        try:
            keys = self.redis_client.keys("query:*")
            return {
                "status": "operational",
                "total_cached_queries": len(keys),
                "similarity_threshold": self.similarity_threshold,
                "ttl_hours": round(self.ttl / 3600, 1),
                "redis_connected": True
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# Singleton instance - initialized once at module load
_cache_instance = None

def get_cache_instance(
    redis_host: str = "localhost",
    redis_port: int = 6379,
    redis_password: Optional[str] = None,
    similarity_threshold: float = 0.85,
    ttl: int = 86400,
    use_ssl: bool = False
) -> SemanticCache:
    """
    Get or create singleton cache instance.
    
    This ensures the embedding model is loaded only once across the application.
    
    Args:
        redis_host: Redis server hostname
        redis_port: Redis server port
        redis_password: Redis password (optional)
        similarity_threshold: Minimum similarity for cache hit (0-1)
        ttl: Cache expiry in seconds
        use_ssl: Use SSL for Redis connection
        
    Returns:
        SemanticCache instance
    """
    global _cache_instance
    
    if _cache_instance is None:
        log_info("[Cache] 🚀 Initializing semantic cache (first time)...")
        _cache_instance = SemanticCache(
            redis_host=redis_host,
            redis_port=redis_port,
            redis_password=redis_password,
            similarity_threshold=similarity_threshold,
            ttl=ttl,
            use_ssl=use_ssl
        )
    
    return _cache_instance


# Quick test
if __name__ == "__main__":
    print("=== Testing Semantic Cache ===\n")
    
    cache = get_cache_instance()
    
    if not cache.is_available():
        print("❌ Cache not available. Make sure Redis is running:")
        print("   docker run -d -p 6379:6379 redis:alpine")
        exit(1)
    
    # Test 1: Store original query
    print("Test 1: Storing query...")
    cache.set("explain section 302", "Section 302 requires CEO/CFO certification of financial statements.")
    
    # Test 2: Retrieve with different wording (should HIT)
    print("\nTest 2: Semantically similar queries...")
    result1 = cache.get("what is section 302")
    print(f"Result: {result1[:50]}..." if result1 else "MISS")
    
    result2 = cache.get("tell me about 302 compliance")
    print(f"Result: {result2[:50]}..." if result2 else "MISS")
    
    # Test 3: Different topic (should MISS)
    print("\nTest 3: Different topic...")
    result3 = cache.get("explain sox 404")
    print(f"Result: {result3}" if result3 else "MISS (expected)")
    
    # Test 4: Stats
    print("\nTest 4: Cache statistics...")
    print(json.dumps(cache.stats(), indent=2))
    
    print("\n✅ Tests complete!")