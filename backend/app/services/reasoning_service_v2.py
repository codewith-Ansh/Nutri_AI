import logging
from typing import List, Optional, Dict, Any
from app.services.gemini_service import gemini_service
from app.utils.prompts_v2 import REASONING_SYSTEM_PROMPT, VISUAL_CONTEXT_PROMPT
from app.core.exceptions import LLMServiceError

logger = logging.getLogger(__name__)

class AINativeReasoningService:
    """AI-native reasoning service focused on decision support, not data analysis"""
    
    def __init__(self):
        self.gemini = gemini_service
    
    async def analyze_from_text(
        self,
        user_input: str,
        inferred_context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate reasoning-driven response from text input"""
        # First check if this is a common Indian food and provide immediate response
        food_item = user_input.lower().strip()
        # Only use fallback for very specific Indian foods to allow API to handle medical questions
        if any(term in food_item for term in ['parle g', 'parle-g', 'vadapav', 'vada pav', 'samosa']):
            return self._get_fallback_indian_food_response(food_item)
        
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
            
            # Enhanced prompt with better food recognition
            prompt = f"""
User question: "{user_input}"
{context_info}
{history_context}

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
                system_instruction=REASONING_SYSTEM_PROMPT,
                temperature=0.4
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Text reasoning failed: {str(e)}")
            # Always return fallback response for any error (including quota exceeded)
            fallback_response = self._get_fallback_indian_food_response(food_item)
            if fallback_response != "I'd be happy to help with information about this food. What specifically would you like to know?":
                return fallback_response
            # If no specific fallback, provide general helpful response
            return "I'm having some technical difficulties with the AI service right now. For common Indian foods like vadapav, samosa, Parle G, I can still help - just ask about them specifically!"
    
    async def analyze_from_image(
        self,
        image_data: bytes,
        inferred_context: Optional[Dict[str, Any]] = None
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
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Image loaded: {image.size} pixels")
            
            prompt = """
You are a food-label analysis assistant.

The image contains a nutrition label and ingredient list from an Indian packaged food.

Step 1: Extract all readable text from the image (ingredients + nutrition table).
Step 2: Clean and structure it clearly.
Step 3: Identify:
- High sugar
- Palm oil / trans fat
- Excess sodium
- Artificial additives
Step 4: Give a short health summary (3–4 lines).

If any text is unreadable, say so explicitly.

Also look for any barcode numbers (usually 8-13 digits) and include them if visible.
"""
            
            # Generate response with image
            logger.info("Calling Gemini Vision API")
            response = model.generate_content([prompt, image])
            
            result_text = response.text.strip()
            logger.info("Gemini Vision analysis completed successfully")
            
            # Check if barcode was detected and try to get product info
            barcode = self._extract_barcode_from_response(result_text)
            if barcode:
                logger.info(f"Barcode detected: {barcode}")
                product_info = await self._get_product_from_barcode(barcode)
                if product_info:
                    enhanced_result = f"{result_text}\n\n**Product Database Match:**\n{product_info}"
                    return enhanced_result
            
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
    
    def _get_fallback_indian_food_response(self, food_item: str) -> str:
        """Provide fallback responses for common Indian foods"""
        # Detect health conditions
        health_conditions = {
            'diabetes': ['diabetes', 'diabetic', 'blood sugar', 'sugar level'],
            'blood_pressure': ['blood pressure', 'hypertension', 'bp', 'high bp'],
            'cholesterol': ['cholesterol', 'high cholesterol', 'ldl', 'hdl'],
            'heart': ['heart disease', 'heart problem', 'cardiac'],
            'weight': ['weight loss', 'obesity', 'overweight', 'fat loss']
        }
        
        detected_condition = None
        for condition, terms in health_conditions.items():
            if any(term in food_item for term in terms):
                detected_condition = condition
                break
        
        # Log for debugging
        logger.info(f"Food item: {food_item}, Detected condition: {detected_condition}")
        
        # Samosa responses (moved to top for priority)
        if 'samosa' in food_item:
            if detected_condition == 'cholesterol':
                return "Samosas are deep-fried pastries with refined flour, which can raise bad cholesterol. The oil and trans fats aren't good for heart health. If you have high cholesterol, limit to very occasional consumption."
            elif detected_condition == 'diabetes':
                return "Samosas can spike blood sugar due to refined flour wrapper and potato filling. The deep-frying adds extra calories. If diabetic, have sparingly and check blood sugar after."
            elif detected_condition == 'blood_pressure':
                return "Samosas are high in sodium and deep-fried, which isn't ideal for blood pressure. The refined carbs and unhealthy fats can indirectly affect BP. Best avoided if you have hypertension."
            else:
                return "Samosas are deep-fried pastries with spiced filling. They're high in calories and refined carbs. Fine as an occasional snack but not regularly if you're health-conscious."
        
        # Vadapav responses
        elif 'vadapav' in food_item or 'vada pav' in food_item:
            if detected_condition == 'blood_pressure':
                return "With high blood pressure, vadapav isn't ideal since it's deep-fried (high in unhealthy fats) and often contains salt. The refined carbs can also affect blood pressure indirectly. If you want to have it occasionally, consider sharing one or having it as part of a meal with vegetables."
            elif detected_condition == 'diabetes':
                return "With diabetes, vadapav can spike blood sugar due to refined flour in the pav and fried potato. If you have it, pair with protein/fiber and monitor your levels. Better as an occasional treat."
            elif detected_condition == 'cholesterol':
                return "Vadapav is deep-fried which increases bad cholesterol. The oil used for frying and refined carbs aren't heart-friendly. If you have high cholesterol, it's best avoided or had very rarely."
            else:
                return "Vadapav is a Mumbai street food - a spiced potato fritter in a bread roll. It's deep-fried and carb-heavy, so quite caloric but filling and flavorful. Consider it an occasional treat if you're watching your diet."
        
        # Parle G responses
        elif 'parle g' in food_item or 'parle-g' in food_item:
            if detected_condition == 'diabetes':
                return "With diabetes, Parle G can cause blood sugar spikes since it contains refined flour and added sugar. If you want to have it, try 1-2 biscuits with a meal rather than alone, and monitor your blood sugar. Better to discuss portion sizes with your doctor."
            else:
                return "Parle G is a popular Indian glucose biscuit made with refined flour, sugar, and oil. It's a processed snack that gives quick energy but isn't very nutritious. Fine as an occasional treat with tea."
        
        # Other Indian foods
        elif 'bhel puri' in food_item or 'pani puri' in food_item:
            if detected_condition:
                return "Street chaat like bhel puri/pani puri often has high sodium, refined carbs, and hygiene concerns. If you have health conditions, it's better to have homemade versions with less salt and oil."
            else:
                return "Bhel puri and pani puri are popular street snacks with puffed rice, chutneys, and spices. They're relatively light but can be high in sodium. Enjoy occasionally from clean vendors."
        
        elif 'dosa' in food_item:
            if detected_condition == 'diabetes':
                return "Plain dosa is better for diabetes than other options since it's fermented and has some protein. But avoid potato masala filling and coconut chutney. Pair with sambar for fiber."
            else:
                return "Dosa is a fermented crepe made from rice and lentils. It's relatively healthy, especially plain dosa. The fermentation adds probiotics and makes it easier to digest."
        
        elif 'maggi' in food_item or 'noodles' in food_item:
            if detected_condition:
                return "Instant noodles like Maggi are high in sodium, preservatives, and refined carbs. Not ideal for any health condition. If you must have it, use less masala and add vegetables."
            else:
                return "Maggi and instant noodles are processed foods high in sodium and preservatives. They're convenient but not nutritious. Better as an occasional quick meal."
        
        # Generic food responses for common queries
        elif any(word in food_item for word in ['biscuit', 'cookie']):
            if detected_condition == 'diabetes':
                return "Most biscuits contain refined flour and sugar which can spike blood sugar. Look for sugar-free or whole grain options, and limit portion sizes."
            else:
                return "Most biscuits are made with refined flour, sugar, and oil. They're high in calories and low in nutrients. Fine as occasional treats."
        
        elif any(word in food_item for word in ['rice', 'biryani', 'pulao']):
            if detected_condition == 'diabetes':
                return "White rice can raise blood sugar quickly. Brown rice is better. For biryani/pulao, watch portions and pair with protein and vegetables."
            else:
                return "Rice is a staple carbohydrate. White rice digests quickly, brown rice has more fiber. Portion control is key for weight management."
        
        elif any(word in food_item for word in ['roti', 'chapati', 'bread']):
            if detected_condition == 'diabetes':
                return "Whole wheat roti is better than white bread for blood sugar control. Limit to 1-2 rotis per meal and pair with vegetables and protein."
            else:
                return "Whole wheat roti/chapati is healthier than white bread. It provides fiber and complex carbs. Good as part of balanced meals."
        
        elif 'dal' in food_item:
            return "Dal (lentils) is excellent - high in protein, fiber, and nutrients. Good for all health conditions. Just watch the oil/ghee used in preparation."
        
        elif any(word in food_item for word in ['healthy', 'nutrition', 'diet']):
            return "For healthy eating, focus on whole foods: vegetables, fruits, whole grains, lean proteins, and legumes. Limit processed foods, excess sugar, and unhealthy fats."
        
        else:
            return "I can help with information about Indian foods like vadapav, samosa, Parle G, dosa, rice, roti, and general nutrition questions. What would you like to know?"
    
    
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