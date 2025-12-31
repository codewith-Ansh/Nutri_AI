from fastapi import APIRouter, Query
from typing import List, Dict, Optional
from app.tools.ingredient_kb_tool import ingredient_kb_tool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/search")
async def search_kb(
    q: str = Query(..., description="Search query for ingredients"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results to return")
) -> Dict:
    """Search ingredient knowledge base"""
    try:
        results = ingredient_kb_tool.search_ingredients(q, limit)
        
        return {
            "success": True,
            "query": q,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"KB search error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "results": [],
            "count": 0
        }

@router.get("/lookup/{ingredient}")
async def lookup_ingredient(ingredient: str) -> Dict:
    """Lookup specific ingredient by name or alias"""
    try:
        result = ingredient_kb_tool.lookup_ingredient(ingredient)
        
        if result:
            return {
                "success": True,
                "ingredient": ingredient,
                "result": result
            }
        else:
            return {
                "success": False,
                "ingredient": ingredient,
                "result": None,
                "message": "Ingredient not found in KB"
            }
    except Exception as e:
        logger.error(f"KB lookup error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

@router.post("/bulk-lookup")
async def bulk_lookup_ingredients(ingredients: List[str]) -> Dict:
    """Lookup multiple ingredients at once"""
    try:
        results = ingredient_kb_tool.bulk_lookup(ingredients)
        
        return {
            "success": True,
            "input_count": len(ingredients),
            "found_count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"KB bulk lookup error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "results": []
        }

@router.get("/categories/{category}")
async def get_by_category(category: str) -> Dict:
    """Get all ingredients in a specific category"""
    try:
        results = ingredient_kb_tool.get_by_category(category)
        
        return {
            "success": True,
            "category": category,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"KB category search error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "results": []
        }

@router.get("/stats")
async def get_kb_stats() -> Dict:
    """Get knowledge base statistics"""
    try:
        stats = ingredient_kb_tool.get_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"KB stats error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }