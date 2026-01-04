"""
Debug test to identify the exact issue
"""
import asyncio
import json
import sys
import os
import traceback

# Add the backend app to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

async def debug_enhanced_reasoning():
    try:
        print("Step 1: Testing imports...")
        
        # Test individual imports
        from app.utils.prompts_v2 import REASONING_SYSTEM_PROMPT, build_enhanced_system_prompt
        print("✓ Prompts imported successfully")
        
        from app.services.gemini_service import gemini_service
        print("✓ Gemini service imported successfully")
        
        from app.services.reasoning_service_v2 import enhanced_ai_reasoning
        print("✓ Enhanced reasoning service imported successfully")
        
        print("\nStep 2: Testing prompt building...")
        enhanced_prompt = build_enhanced_system_prompt("en", None)
        print(f"✓ Enhanced prompt built (length: {len(enhanced_prompt)})")
        
        print("\nStep 3: Testing direct Gemini call with enhanced prompt...")
        
        test_prompt = """
User question: "Is MSG safe?"

CRITICAL REQUIREMENTS:
1. MECHANISM-LEVEL REASONING: Explain WHY each major claim happens (biological/behavioral cause), not just WHAT happens
2. SPECIFIC UNCERTAINTY: Reference exact variables, avoid generic "varies by person"
3. DEPTH WITHOUT LENGTH: One precise causal explanation over multiple shallow points

Provide mechanism-based decision support following the enhanced reasoning requirements.
"""
        
        response = await gemini_service.generate_text(
            prompt=test_prompt,
            system_instruction=enhanced_prompt,
            temperature=0.3
        )
        
        print("Raw Gemini Response:")
        print(response)
        print("\n" + "="*50)
        
        # Try to parse as JSON
        try:
            parsed = json.loads(response)
            print("✓ Valid JSON response")
            print(json.dumps(parsed, indent=2))
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON: {e}")
            print("Response is not valid JSON, this is the issue!")
        
        return True
        
    except Exception as e:
        print(f"Error in step: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(debug_enhanced_reasoning())