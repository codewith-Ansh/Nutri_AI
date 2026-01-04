#!/usr/bin/env python3
"""
Quick test to check if Gemini API is working
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.gemini_service import gemini_service

async def test_gemini():
    try:
        print("Testing Gemini API...")
        
        # Simple test
        response = await gemini_service.generate_text(
            prompt="What is pizza?",
            system_instruction="You are a helpful assistant. Answer in 1 sentence."
        )
        
        print(f"✅ API Working! Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ API Failed: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_gemini())
    if not result:
        print("\n🔧 Possible issues:")
        print("1. Check GEMINI_API_KEY in .env file")
        print("2. Verify internet connection")
        print("3. Check if API key has quota/permissions")