#!/usr/bin/env python3
"""
Test script for ingredient KB tool
Run: python test_kb.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_kb_tool():
    """Test KB tool functionality"""
    try:
        from app.tools.ingredient_kb_tool import ingredient_kb_tool
        
        print("Testing Ingredient KB Tool...")
        print("=" * 40)
        
        # Test 1: Lookup exact ingredient
        print("1. Testing exact lookup:")
        result = ingredient_kb_tool.lookup_ingredient("sodium benzoate")
        if result:
            print(f"✓ Found: {result['name']} - {result['why_it_matters']}")
        else:
            print("✗ Not found")
        
        # Test 2: Lookup by alias
        print("\n2. Testing alias lookup:")
        result = ingredient_kb_tool.lookup_ingredient("msg")
        if result:
            print(f"✓ Found: {result['name']} - {result['why_it_matters']}")
        else:
            print("✗ Not found")
        
        # Test 3: Search functionality
        print("\n3. Testing search:")
        results = ingredient_kb_tool.search_ingredients("dye", limit=3)
        print(f"✓ Found {len(results)} matches for 'dye':")
        for r in results:
            print(f"  - {r['name']}")
        
        # Test 4: Bulk lookup
        print("\n4. Testing bulk lookup:")
        ingredients = ["aspartame", "msg", "unknown_ingredient", "palm oil"]
        results = ingredient_kb_tool.bulk_lookup(ingredients)
        print(f"✓ Found {len(results)}/{len(ingredients)} ingredients:")
        for r in results:
            print(f"  - {r['name']}")
        
        # Test 5: Stats
        print("\n5. KB Statistics:")
        stats = ingredient_kb_tool.get_stats()
        print(f"✓ Total ingredients: {stats['total_ingredients']}")
        print(f"✓ Categories: {list(stats['categories'].keys())}")
        
        print("\n" + "=" * 40)
        print("🎉 All KB tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ KB test failed: {e}")
        return False

if __name__ == "__main__":
    test_kb_tool()