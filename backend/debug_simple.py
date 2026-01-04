"""
Simple debug test without Unicode issues
"""
import asyncio
import json
import sys
import os
import traceback

# Add the backend app to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

async def debug_simple():
    try:
        print("Testing enhanced reasoning...")
        
        from app.services.gemini_service import gemini_service
        from app.utils.prompts_v2 import REASONING_SYSTEM_PROMPT
        
        # Test with a very simple prompt first
        simple_prompt = """
User asks: "Is MSG safe?"

You must respond with ONLY valid JSON in this exact format:
{
  "ai_insight_title": "Brief title",
  "quick_verdict": "One sentence answer",
  "why_this_matters": ["Reason 1", "Reason 2"],
  "trade_offs": {
    "positives": ["Good thing"],
    "negatives": ["Concern"]
  },
  "uncertainty": "What varies",
  "ai_advice": "One sentence advice"
}

Explain WHY MSG affects the body, not just what it is.
"""
        
        response = await gemini_service.generate_text(
            prompt=simple_prompt,
            system_instruction="You are a helpful assistant. Respond with valid JSON only.",
            temperature=0.3
        )
        
        print("Gemini Response:")
        print(response)
        print("\n" + "="*50)
        
        # Check if it's valid JSON
        try:
            parsed = json.loads(response)
            print("SUCCESS: Valid JSON response received")
            print("Enhanced reasoning is working!")
            
            # Check for mechanism words
            response_lower = response.lower()
            mechanism_words = ["because", "which", "causes", "leads to", "affects", "triggers"]
            found = [word for word in mechanism_words if word in response_lower]
            print(f"Mechanism words found: {found}")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON - {e}")
            print("This is why you're getting fallback responses")
            return False
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(debug_simple())
    if result:
        print("\nThe enhanced reasoning engine is working!")
        print("Try these test questions in your app:")
        print("1. 'Is MSG bad for health?'")
        print("2. 'Should I avoid palm oil?'") 
        print("3. 'Can I give my kid artificial colors?'")
    else:
        print("\nThere's an issue with JSON formatting from Gemini")