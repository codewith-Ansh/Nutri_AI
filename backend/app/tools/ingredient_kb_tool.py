import json
import os
from typing import Dict, List, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class IngredientKBTool:
    def __init__(self):
        self._kb_data = None
        self._name_index = None
        self._alias_index = None
    
    @property
    def kb_data(self) -> List[Dict]:
        """Lazy load KB data once"""
        if self._kb_data is None:
            self._load_kb()
        return self._kb_data
    
    @property
    def name_index(self) -> Dict[str, Dict]:
        """Lazy build name index"""
        if self._name_index is None:
            self._build_indexes()
        return self._name_index
    
    @property
    def alias_index(self) -> Dict[str, Dict]:
        """Lazy build alias index"""
        if self._alias_index is None:
            self._build_indexes()
        return self._alias_index
    
    def _load_kb(self):
        """Load KB from JSON file"""
        try:
            kb_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ingredient_kb_seed.json')
            with open(kb_path, 'r', encoding='utf-8') as f:
                self._kb_data = json.load(f)
            logger.info(f"Loaded {len(self._kb_data)} ingredients from KB")
        except Exception as e:
            logger.error(f"Failed to load ingredient KB: {e}")
            self._kb_data = []
    
    def _build_indexes(self):
        """Build search indexes for fast lookup"""
        self._name_index = {}
        self._alias_index = {}
        
        for item in self.kb_data:
            # Index by canonical name
            name_key = item['name'].lower().strip()
            self._name_index[name_key] = item
            
            # Index by aliases
            for alias in item.get('aliases', []):
                alias_key = alias.lower().strip()
                self._alias_index[alias_key] = item
    
    def lookup_ingredient(self, query: str) -> Optional[Dict]:
        """
        Lookup ingredient by exact name or alias match
        
        Args:
            query: ingredient name to search for
            
        Returns:
            ingredient dict or None if not found
        """
        if not query:
            return None
            
        query_clean = query.lower().strip()
        
        # Try exact name match first
        if query_clean in self.name_index:
            return self.name_index[query_clean]
        
        # Try alias match
        if query_clean in self.alias_index:
            return self.alias_index[query_clean]
        
        return None
    
    def search_ingredients(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search ingredients by partial name/alias match
        
        Args:
            query: search term
            limit: max results to return
            
        Returns:
            list of matching ingredient dicts
        """
        if not query:
            return []
        
        query_clean = query.lower().strip()
        matches = []
        
        # Search in names and aliases
        for item in self.kb_data:
            # Check name
            if query_clean in item['name'].lower():
                matches.append(item)
                continue
            
            # Check aliases
            for alias in item.get('aliases', []):
                if query_clean in alias.lower():
                    matches.append(item)
                    break
        
        return matches[:limit]
    
    def bulk_lookup(self, ingredients: List[str]) -> List[Dict]:
        """
        Lookup multiple ingredients at once
        
        Args:
            ingredients: list of ingredient names
            
        Returns:
            list of found ingredient dicts (may be shorter than input)
        """
        results = []
        for ingredient in ingredients:
            match = self.lookup_ingredient(ingredient)
            if match:
                results.append(match)
        return results
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Get all ingredients in a specific category"""
        return [item for item in self.kb_data if item.get('category', '').lower() == category.lower()]
    
    def get_stats(self) -> Dict:
        """Get KB statistics"""
        categories = {}
        confidence_levels = {}
        
        for item in self.kb_data:
            # Count categories
            cat = item.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
            
            # Count confidence levels
            conf = item.get('confidence', 'unknown')
            confidence_levels[conf] = confidence_levels.get(conf, 0) + 1
        
        return {
            'total_ingredients': len(self.kb_data),
            'categories': categories,
            'confidence_levels': confidence_levels
        }

# Singleton instance
ingredient_kb_tool = IngredientKBTool()