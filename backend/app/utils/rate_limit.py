import time
from typing import Dict
from fastapi import HTTPException
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.redis_client = None
        self.memory_buckets: Dict[str, Dict[str, float]] = {}
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
            self.redis_client.ping()
            logger.info("Redis rate limiter initialized successfully")
        except Exception as e:
            logger.warning(f"Redis unavailable, using in-memory rate limiter: {e}")
            self.redis_client = None
    
    def check_rate_limit(self, tool_name: str, max_per_minute: int = None):
        """Check if request is within rate limit, raise exception if exceeded"""
        if max_per_minute is None:
            max_per_minute = getattr(settings, 'OFF_RATE_LIMIT_PER_MINUTE', 60)
        
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        if self.redis_client:
            try:
                # Use Redis sorted set for sliding window
                key = f"rate_limit:{tool_name}"
                pipe = self.redis_client.pipeline()
                
                # Remove old entries
                pipe.zremrangebyscore(key, 0, window_start)
                # Count current requests
                pipe.zcard(key)
                # Add current request
                pipe.zadd(key, {str(current_time): current_time})
                # Set expiry
                pipe.expire(key, 60)
                
                results = pipe.execute()
                current_count = results[1]
                
                if current_count >= max_per_minute:
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded for {tool_name}. Max {max_per_minute} requests per minute."
                    )
                    
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise
                logger.error(f"Redis rate limit error: {e}")
                # Fall through to memory-based rate limiting
        
        # In-memory fallback
        if tool_name not in self.memory_buckets:
            self.memory_buckets[tool_name] = {'count': 0, 'window_start': current_time}
        
        bucket = self.memory_buckets[tool_name]
        
        # Reset window if needed
        if current_time - bucket['window_start'] >= 60:
            bucket['count'] = 0
            bucket['window_start'] = current_time
        
        if bucket['count'] >= max_per_minute:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded for {tool_name}. Max {max_per_minute} requests per minute."
            )
        
        bucket['count'] += 1

# Global rate limiter instance
rate_limiter = RateLimiter()