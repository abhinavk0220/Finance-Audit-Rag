# filename: backend/core/cache_manager.py
"""
cache_manager.py
----------------
Redis-based semantic caching for RAG queries.
Caches responses for semantically similar questions.
"""

import redis
import json
import hashlib
from typing import Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SemanticCache:
    def __init__(
        self, 
        redis_host: str = "localhost",
        redis_port: int = 6379,
        similarity_threshold: float = 0.85,  # 85% similar = same question
        ttl: int = 86400  # 24 hours cache
    ):
        """
        Initialize semantic cache with Redis backend.
        
        Args:
            similarity_threshold: 0.85 means "explain 302" ≈ "what is 302"
            ttl: Cache expiry in seconds (default 24h)
        """
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )
        self.similarity_threshold = similarity_threshold
        self.ttl = ttl
        
        # Load lightweight embedding model for semantic matching
        print("[Cache] 🔄 Loading embedding model...")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, 80MB model
        print("[Cache] ✅ Cache ready")
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate semantic embedding for query."""
        return self.encoder.encode(text, convert_to_numpy=True)
    
    def _normalize_query(self, query: str) -> str:
        """Basic normalization: lowercase, strip"""
        return query.lower().strip()
    
    def get(self, query: str) -> Optional[str]:
        """
        Check if semantically similar query exists in cache.
        Returns cached response if similarity > threshold.
        """
        query_norm = self._normalize_query(query)
        query_embedding = self._generate_embedding(query_norm)
        
        # Get all cached queries with their embeddings
        cached_keys = self.redis_client.keys("query:*")
        
        if not cached_keys:
            print(f"[Cache] ❌ MISS: '{query}' (empty cache)")
            return None
        
        # Find most similar cached query
        max_similarity = 0
        best_match_key = None
        
        for key in cached_keys:
            try:
                cached_data = json.loads(self.redis_client.get(key))
                cached_embedding = np.array(cached_data["embedding"])
                
                # Compute cosine similarity
                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1),
                    cached_embedding.reshape(1, -1)
                )[0][0]
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match_key = key
            
            except Exception as e:
                print(f"[Cache] ⚠️ Error checking {key}: {e}")
                continue
        
        # Return cached response if similarity exceeds threshold
        if max_similarity >= self.similarity_threshold:
            cached_data = json.loads(self.redis_client.get(best_match_key))
            cached_query = cached_data["query"]
            response = cached_data["response"]
            
            print(f"[Cache] ✅ HIT: '{query}' ≈ '{cached_query}' (similarity: {max_similarity:.2f})")
            return response
        
        print(f"[Cache] ❌ MISS: '{query}' (best similarity: {max_similarity:.2f})")
        return None
    
    def set(self, query: str, response: str):
        """
        Store query-response pair with semantic embedding.
        """
        query_norm = self._normalize_query(query)
        query_embedding = self._generate_embedding(query_norm)
        
        # Create unique key using hash
        query_hash = hashlib.md5(query_norm.encode()).hexdigest()
        key = f"query:{query_hash}"
        
        # Store with embedding for semantic search
        cache_data = {
            "query": query_norm,
            "response": response,
            "embedding": query_embedding.tolist()
        }
        
        self.redis_client.setex(
            key,
            self.ttl,
            json.dumps(cache_data)
        )
        print(f"[Cache] 💾 Stored: '{query}' (key: {key[:20]}...)")
    
    def clear(self):
        """Clear all cached queries."""
        keys = self.redis_client.keys("query:*")
        if keys:
            self.redis_client.delete(*keys)
            print(f"[Cache] 🧹 Cleared {len(keys)} cached queries")
    
    def stats(self) -> dict:
        """Get cache statistics."""
        keys = self.redis_client.keys("query:*")
        return {
            "total_cached_queries": len(keys),
            "similarity_threshold": self.similarity_threshold,
            "ttl_hours": self.ttl / 3600
        }


# Quick test
if __name__ == "__main__":
    cache = SemanticCache()
    
    # Test semantic matching
    cache.set("explain section 302", "Section 302 requires CEO/CFO certification...")
    
    # These should hit cache (semantically similar)
    print("\n--- Testing Semantic Similarity ---")
    print(cache.get("what is section 302"))  # Should HIT
    print(cache.get("tell me about 302 compliance"))  # Should HIT
    print(cache.get("explain sox 404"))  # Should MISS (different topic)