#!/usr/bin/env python3
"""
Test image analysis functionality
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.reasoning_service_v2 import ai_native_reasoning

async def test_image_analysis():
    try:
        print("Testing image analysis...")
        
        # Create a dummy image data (you can replace with actual image bytes)
        dummy_image = b"dummy_image_data"
        
        response = await ai_native_reasoning.analyze_from_image(
            image_data=dummy_image,
            inferred_context={"likely_goal": "product_identification"}
        )
        
        print(f"✅ Image Analysis Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Image Analysis Failed: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_image_analysis())
    if result:
        print("\n✅ Image analysis system is working!")
    else:
        print("\n❌ Image analysis needs fixing")