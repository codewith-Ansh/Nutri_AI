import logging
import json
from typing import List, Optional, Dict, Any
from app.services.gemini_service import gemini_service
from app.utils.prompts_v2 import REASONING_SYSTEM_PROMPT, VISUAL_CONTEXT_PROMPT
from app.core.exceptions import LLMServiceError
from app.data.curated_reasoning import get_curated_response

logger = logging.getLogger(__name__)

class AINativeReasoningService:
    """AI-native reasoning service focused on decision support, not data analysis"""
    
    def __init__(self):
        self.gemini = gemini_service
    
    async def analyze_from_text(
        self,
        user_input: str,
        inferred_context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        language: str = "en"
    ) -> str:
        """Generate reasoning-driven response from text input"""
        
        # First, check for curated responses (demo foods)
        curated_response = get_curated_response(user_input)
        if curated_response:
            logger.info(f"Using curated response for: {curated_response.get('_food', 'unknown')}")
            return json.dumps(curated_response, ensure_ascii=False)
        
        # Use detected language from context if no explicit language provided
        if language == "en" and inferred_context:
            detected_lang = inferred_context.get('detected_language', 'en')
            if detected_lang in ['hi', 'hinglish']:
                language = detected_lang
                logger.info(f"Using detected language: {language}")
        
        # Otherwise, use LLM reasoning
        try:
            # Build context-aware prompt
            context_info = ""
            if inferred_context:
                likely_goal = inferred_context.get('likely_goal', '')
                possible_context = inferred_context.get('possible_context', '')
                soft_concerns = inferred_context.get('soft_concerns', [])
                hedge_language = inferred_context.get('hedge_language', '')
                
                context_info = f"""
Inferred context:
- Likely goal: {likely_goal}
- Possible context: {possible_context}
- Soft concerns: {', '.join(soft_concerns) if soft_concerns else 'none'}
- Hedge approach: {hedge_language}
"""
            
            # Build conversation context
            history_context = ""
            if conversation_history:
                recent_msgs = conversation_history[-3:]  # Last 3 messages
                history_context = "\nRecent conversation:\n" + "\n".join([
                    f"{msg.get('role', 'user')}: {msg.get('content', '')[:100]}..."
                    for msg in recent_msgs
                ])
            
            # Build language instruction
            language_instruction = ""
            if language == "hi":
                language_instruction = "\n\nCRITICAL LANGUAGE REQUIREMENT: You MUST respond in Hindi (Devanagari script). Translate ALL content to Hindi while keeping JSON field names in English. Example: 'quick_verdict': 'यह स्वादिष्ट है लेकिन रोज़ाना खाने के लिए उपयुक्त नहीं है।'"
            elif language == "hinglish":
                language_instruction = "\n\nCRITICAL LANGUAGE REQUIREMENT: You MUST respond in Hinglish (Hindi written in English script). Translate ALL content to Hinglish while keeping JSON field names in English. Example: 'quick_verdict': 'Ye tasty hai lekin daily khane ke liye ideal nahi hai.'"
            else:
                language_instruction = "\n\nRespond in English."
            
            # Enhanced prompt with better food recognition
            prompt = f"""
User question: "{user_input}"
{context_info}
{history_context}{language_instruction}

Provide a direct, focused answer to the user's specific question. Be concise and helpful.

For food questions:
- Answer what they asked specifically
- Keep responses under 3 sentences when possible
- Focus on the key point they want to know
- Don't add unnecessary background unless directly relevant

For Indian/regional foods like Parle G, vadapav, etc.:
- Give direct answers about what they are
- Address specific concerns (diabetes, health, etc.) if mentioned
- Be practical and actionable

Avoid:
- Long explanations about cultural significance unless asked
- Generic advice about "moderation" unless specifically relevant
- Asking follow-up questions unless the query is unclear

Be direct and helpful.
"""
            
            response = await self.gemini.generate_text(
                prompt=prompt,
                system_instruction=REASONING_SYSTEM_PROMPT + language_instruction,
                temperature=0.4
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Text reasoning failed: {str(e)}")
            # Try curated response as fallback
            curated_fallback = get_curated_response(user_input)
            if curated_fallback:
                logger.info("Using curated fallback due to LLM error")
                return json.dumps(curated_fallback, ensure_ascii=False)
            
            # Return structured error response if all else fails
            error_response = {
                "ai_insight_title": "Temporary Service Issue",
                "quick_verdict": "I'm having some technical difficulties with the AI service right now.",
                "why_this_matters": [
                    "The AI reasoning service is temporarily unavailable",
                    "You can try asking about common foods or try again in a moment"
                ],
                "trade_offs": {
                    "positives": ["Service interruption is temporary"],
                    "negatives": ["Cannot provide detailed analysis at the moment"]
                },
                "uncertainty": "Service should be restored shortly. For common Indian foods, I may still be able to help.",
                "ai_advice": "Please try your question again, or ask about specific foods like samosa, vadapav, or Parle G.",
                "_source": "error_fallback"
            }
            return json.dumps(error_response, ensure_ascii=False)
    
    async def analyze_from_image(
        self,
        image_data: bytes,
        inferred_context: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> str:
        """Generate reasoning-driven response from image with product recognition"""
        try:
            logger.info("Starting image analysis with Gemini Vision")
            
            # Use Gemini Vision to analyze the image
            import google.generativeai as genai
            from app.config import settings
            from PIL import Image
            import io
            
            # Configure Gemini with vision model
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Image loaded: {image.size} pixels")
            
            # Use structured prompt for consistent JSON output with language support
            prompt = VISUAL_CONTEXT_PROMPT
            if language == "hi":
                prompt += "\n\nCRITICAL LANGUAGE REQUIREMENT: You MUST respond in Hindi (Devanagari script). Translate ALL content to Hindi while keeping JSON field names in English."
            elif language == "hinglish":
                prompt += "\n\nCRITICAL LANGUAGE REQUIREMENT: You MUST respond in Hinglish (Hindi written in English script). Translate ALL content to Hinglish while keeping JSON field names in English."
            else:
                prompt += "\n\nRespond in English."
            
            # Generate response with image
            logger.info("Calling Gemini Vision API")
            response = model.generate_content([prompt, image])
            
            result_text = response.text.strip()
            # Clean md code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            logger.info("Gemini Vision analysis completed successfully")
            
            # Note: We skip the secondary barcode lookup to preserve the structured JSON format
            # The Vision API is powerful enough to read the label directly
            
            return result_text
            
        except Exception as e:
            logger.error(f"Gemini Vision analysis failed: {str(e)}")
            # Try OCR fallback
            return await self._fallback_ocr_analysis(image_data)
    
    async def _fallback_ocr_analysis(self, image_data: bytes) -> str:
        """Fallback OCR-based analysis when vision API fails"""
        try:
            # Save image temporarily for OCR
            import tempfile
            import os
            from app.services.image_services import image_service
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(image_data)
                tmp_path = tmp_file.name
            
            try:
                # Extract text using OCR
                extracted_text = image_service.extract_text_ocr(tmp_path)
                
                if extracted_text:
                    # Analyze the extracted text
                    analysis_prompt = f"""
I extracted this text from a food product image:

{extracted_text}

Please help identify:
1. What product this might be
2. Key ingredients mentioned
3. Any nutritional concerns
4. Brand or product name if visible

Provide a helpful analysis of this food product.
"""
                    
                    response = await self.gemini.generate_text(
                        prompt=analysis_prompt,
                        system_instruction="You are a helpful nutrition assistant. Analyze food products from text extracted from images.",
                        temperature=0.4
                    )
                    
                    return response.strip()
                else:
                    return "I couldn't extract clear text from this image. Try taking a clearer photo of the product label or ingredient list."
            
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
        except Exception as e:
            logger.error(f"Fallback OCR analysis failed: {str(e)}")
            return "I'm having trouble analyzing this image. Please try taking a clearer photo of the product package, focusing on the ingredient list or barcode area."
    
    def _extract_barcode_from_response(self, response_text: str) -> str:
        """Extract barcode number from AI response"""
        import re
        # Look for patterns like barcode numbers (8-13 digits)
        patterns = [
            r'\b\d{13}\b',  # 13-digit EAN
            r'\b\d{12}\b',  # 12-digit UPC
            r'\b\d{8}\b',   # 8-digit EAN-8
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response_text)
            if matches:
                return matches[0]
        return None
    
    async def _get_product_from_barcode(self, barcode: str) -> str:
        """Get product information from OpenFoodFacts using barcode"""
        try:
            import aiohttp
            
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == 1:  # Product found
                            product = data.get('product', {})
                            
                            name = product.get('product_name', 'Unknown')
                            brand = product.get('brands', 'Unknown')
                            ingredients = product.get('ingredients_text', 'Not available')
                            
                            return f"**{name}** by {brand}\nIngredients: {ingredients[:200]}{'...' if len(ingredients) > 200 else ''}"
                        
            return None
        except Exception as e:
            logger.error(f"OpenFoodFacts lookup failed: {str(e)}")
            return None
    
    def _should_hedge_response(self, confidence_level: str) -> bool:
        """Determine if response should include more hedge language"""
        return confidence_level in ['uncertain', 'somewhat_sure']
    
    def _adapt_tone_for_context(self, context: str) -> str:
        """Adapt communication tone based on inferred context"""
        if context == 'parent':
            return "When choosing for kids, people often focus on..."
        elif context == 'health_conscious':
            return "If health is a priority, you might want to consider..."
        elif context == 'shopping':
            return "When you're deciding between options..."
        else:
            return "People usually think about..."

# Singleton instance
ai_native_reasoning = AINativeReasoningService()