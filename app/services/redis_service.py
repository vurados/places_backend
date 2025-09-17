import json
import redis
from core.config import settings
from typing import Optional, Any

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
    
    async def get_cached_search(self, search_type: str, query: str, params: dict) -> Optional[Any]:
        cache_key = f"search:{search_type}:{query}:{json.dumps(params, sort_keys=True)}"
        cached = self.client.get(cache_key)
        if cached:
            return json.loads(cached)
        return None
    
    async def set_cached_search(self, search_type: str, query: str, params: dict, results: Any, ttl: int = 300):
        cache_key = f"search:{search_type}:{query}:{json.dumps(params, sort_keys=True)}"
        self.client.setex(cache_key, ttl, json.dumps(results))
    
    async def invalidate_search_cache(self, search_type: str = None, query: str = None):
        if search_type and query:
            pattern = f"search:{search_type}:{query}:*"
        elif search_type:
            pattern = f"search:{search_type}:*"
        else:
            pattern = "search:*"
        
        keys = self.client.keys(pattern)
        if keys:
            self.client.delete(*keys)

# Create global Redis client instance
redis_client = RedisClient()