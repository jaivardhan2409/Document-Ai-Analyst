import redis
import json
from typing import Any, Optional
from app.config import settings

class CacheService:
    """Redis-based caching service"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 3600  # 1 hour
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear error: {e}")
            return 0

# Utility function to create cache keys
def get_search_cache_key(query: str, doc_ids: tuple, top_k: int) -> str:
    """Create cache key for search results"""
    doc_ids_str = "_".join(sorted(doc_ids)) if doc_ids else "all"
    return f"search:{query}:{doc_ids_str}:{top_k}"

def get_chat_cache_key(query: str, doc_ids: tuple) -> str:
    """Create cache key for chat results"""
    doc_ids_str = "_".join(sorted(doc_ids)) if doc_ids else "all"
    return f"chat:{query}:{doc_ids_str}"
