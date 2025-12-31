import httpx
import logging
from typing import Dict, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class OpenFoodFactsTool:
    def __init__(self):
        self.base_url = getattr(settings, 'OFF_BASE_URL', 'https://world.openfoodfacts.org')
        self.timeout = getattr(settings, 'OFF_TIMEOUT_SECONDS', 10)
    
    async def fetch_product_by_barcode(self, barcode: str) -> Dict:
        """Fetch product data from OpenFoodFacts by barcode"""
        try:
            url = f"{self.base_url}/api/v0/product/{barcode}.json"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('status') == 0:
                    logger.info(f"Product not found for barcode: {barcode}")
                    return {"found": False, "barcode": barcode}
                
                product = data.get('product', {})
                logger.info(f"Product found for barcode {barcode}: {product.get('product_name', 'Unknown')}")
                
                return {
                    "found": True,
                    "barcode": barcode,
                    "product_name": product.get('product_name', ''),
                    "brands": product.get('brands', ''),
                    "ingredients_text": product.get('ingredients_text', ''),
                    "allergens": product.get('allergens', ''),
                    "traces": product.get('traces', ''),
                    "nutriments": product.get('nutriments', {}),
                    "raw_product": product
                }
                
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching product {barcode}")
            return {"found": False, "barcode": barcode, "error": "timeout"}
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching product {barcode}: {e}")
            return {"found": False, "barcode": barcode, "error": "http_error"}
        except Exception as e:
            logger.error(f"Unexpected error fetching product {barcode}: {e}")
            return {"found": False, "barcode": barcode, "error": "unknown"}
    
    def extract_ingredients_from_product(self, product_json: Dict) -> List[str]:
        """Extract ingredients list from product JSON"""
        if not product_json.get("found"):
            return []
        
        ingredients_text = product_json.get("ingredients_text", "")
        if not ingredients_text:
            return []
        
        # Try to use existing text processor if available
        try:
            from app.services.text_processor import text_processor
            return text_processor.extract_ingredients(ingredients_text)
        except ImportError:
            # Fallback simple extraction
            ingredients = [ing.strip() for ing in ingredients_text.split(',')]
            return [ing for ing in ingredients if ing and len(ing) > 1]

# Singleton instance
openfoodfacts_tool = OpenFoodFactsTool()