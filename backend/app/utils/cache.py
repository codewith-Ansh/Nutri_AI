import json
import time
from typing import Optional, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Cache:
    def __init__(self):
        self.redis_client = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection with fallback to in-memory"""
        try:
            import redis
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis unavailable, using in-memory cache: {e}")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if self.redis_client:
            try:
                return self.redis_client.get(key)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
                return None
        else:
            # In-memory fallback
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                if entry['expires'] > time.time():
                    return entry['value']
                else:
                    del self.memory_cache[key]
            return None
    
    def set(self, key: str, value: str, ttl_seconds: int = None):
        """Set value in cache with TTL"""
        if ttl_seconds is None:
            ttl_seconds = getattr(settings, 'CACHE_TTL_SECONDS_DEFAULT', 300)
        
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl_seconds, value)
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        else:
            # In-memory fallback
            self.memory_cache[key] = {
                'value': value,
                'expires': time.time() + ttl_seconds
            }
    
    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get JSON value from cache"""
        value = self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    def set_json(self, key: str, value: Dict[str, Any], ttl_seconds: int = None):
        """Set JSON value in cache"""
        try:
            json_str = json.dumps(value)
            self.set(key, json_str, ttl_seconds)
        except (TypeError, ValueError) as e:
            logger.error(f"JSON serialization error: {e}")

# Global cache instance
cache = Cache()