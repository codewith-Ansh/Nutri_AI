import re
from typing import List
from app.core.exceptions import InvalidInputError
import logging

logger = logging.getLogger(__name__)

class TextProcessor:
    """Service for processing text-based ingredient input"""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text input"""
        # Remove extra whitespace
        text = " ".join(text.split())
        # Remove special characters but keep commas, parentheses, periods
        text = re.sub(r'[^\w\s,().-]', '', text)
        return text.strip()
    
    @staticmethod
    def extract_ingredients(text: str) -> List[str]:
        """Extract ingredient list from text"""
        try:
            # Normalize text
            normalized = TextProcessor.normalize_text(text)
            
            # Look for ingredient section
            # Common patterns: "Ingredients:", "Contains:", etc.
            ingredient_pattern = r'(?:ingredients?|contains?):?\s*(.*?)(?:nutrition|allergen|$)'
            match = re.search(ingredient_pattern, normalized, re.IGNORECASE | re.DOTALL)
            
            if match:
                ingredient_text = match.group(1)
            else:
                # If no pattern found, assume entire text is ingredients
                ingredient_text = normalized
            
            # Split by commas
            ingredients = [ing.strip() for ing in ingredient_text.split(',')]
            
            # Filter out empty or too short items
            ingredients = [ing for ing in ingredients if ing and len(ing) > 1]
            
            logger.info(f"Extracted {len(ingredients)} ingredients from text")
            return ingredients
        except Exception as e:
            logger.error(f"Error extracting ingredients: {str(e)}")
            raise InvalidInputError("Failed to extract ingredients from text")
    
    @staticmethod
    def validate_input(text: str) -> bool:
        """Validate text input"""
        if not text or not text.strip():
            raise InvalidInputError("Text input cannot be empty")
        
        if len(text) > 5000:  # Max length check
            raise InvalidInputError("Text input too long (max 5000 characters)")
        
        return True
    
    @staticmethod
    def clean_ingredient(ingredient: str) -> str:
        """Clean individual ingredient text"""
        # Remove percentages in parentheses
        ingredient = re.sub(r'\([^)]*%[^)]*\)', '', ingredient)
        # Remove numbers and periods at start
        ingredient = re.sub(r'^[\d.]+\s*', '', ingredient)
        # Clean whitespace
        ingredient = " ".join(ingredient.split())
        return ingredient.strip()

# Singleton instance
text_processor = TextProcessor()
