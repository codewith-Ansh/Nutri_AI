import httpx
import hashlib
from typing import Optional, Dict, Any
from app.config import settings
from app.utils.cache import cache
from app.utils.rate_limit import rate_limiter
import logging

logger = logging.getLogger(__name__)

class OpenFoodFactsService:
    def __init__(self):
        self.base_url = settings.OFF_BASE_URL
        self.timeout = settings.OFF_TIMEOUT_SECONDS
    
    def _get_cache_key(self, barcode: str) -> str:
        """Generate cache key for product"""
        return f"off_product:{barcode}"
    
    async def get_product(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get product from OpenFoodFacts with caching and rate limiting"""
        # Check rate limit first
        rate_limiter.check_rate_limit("openfoodfacts", settings.OFF_RATE_LIMIT_PER_MINUTE)
        
        # Check cache first
        cache_key = self._get_cache_key(barcode)
        cached_result = cache.get_json(cache_key)
        if cached_result:
            logger.info(f"Cache hit for product {barcode}")
            return cached_result
        
        # Make API call
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/api/v0/product/{barcode}.json"
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    # Cache the result
                    cache.set_json(cache_key, data, settings.CACHE_TTL_SECONDS_DEFAULT)
                    logger.info(f"Fetched and cached product {barcode}")
                    return data
                else:
                    logger.warning(f"OpenFoodFacts API returned {response.status_code} for {barcode}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching product {barcode}: {e}")
            return None

# Global service instance
openfoodfacts_service = OpenFoodFactsService()