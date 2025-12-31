from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.tools.openfoodfacts_tool import openfoodfacts_tool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ProductResponse(BaseModel):
    found: bool
    barcode: str
    product_name: str = ""
    brands: str = ""
    ingredients: List[str] = []
    allergens: str = ""
    traces: str = ""
    nutriments: Dict[str, Any] = {}

class IngredientsResponse(BaseModel):
    found: bool
    barcode: str
    product_name: str = ""
    ingredients: List[str] = []

@router.get("/product/{barcode}", response_model=ProductResponse)
async def get_product(barcode: str):
    """Get normalized product info and extracted ingredient list"""
    try:
        # Fetch product from OpenFoodFacts
        product_data = await openfoodfacts_tool.fetch_product_by_barcode(barcode)
        
        if not product_data.get("found"):
            return ProductResponse(
                found=False,
                barcode=barcode
            )
        
        # Extract ingredients
        ingredients = openfoodfacts_tool.extract_ingredients_from_product(product_data)
        
        logger.info(f"Product lookup for {barcode}: {product_data.get('product_name', 'Unknown')}")
        
        return ProductResponse(
            found=True,
            barcode=barcode,
            product_name=product_data.get("product_name", ""),
            brands=product_data.get("brands", ""),
            ingredients=ingredients,
            allergens=product_data.get("allergens", ""),
            traces=product_data.get("traces", ""),
            nutriments=product_data.get("nutriments", {})
        )
        
    except Exception as e:
        logger.error(f"Product lookup error for {barcode}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch product")

@router.get("/product/{barcode}/ingredients", response_model=IngredientsResponse)
async def get_product_ingredients(barcode: str):
    """Get just ingredients list and product name"""
    try:
        # Fetch product from OpenFoodFacts
        product_data = await openfoodfacts_tool.fetch_product_by_barcode(barcode)
        
        if not product_data.get("found"):
            return IngredientsResponse(
                found=False,
                barcode=barcode
            )
        
        # Extract ingredients
        ingredients = openfoodfacts_tool.extract_ingredients_from_product(product_data)
        
        logger.info(f"Ingredients lookup for {barcode}: {len(ingredients)} ingredients")
        
        return IngredientsResponse(
            found=True,
            barcode=barcode,
            product_name=product_data.get("product_name", ""),
            ingredients=ingredients
        )
        
    except Exception as e:
        logger.error(f"Ingredients lookup error for {barcode}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch ingredients")