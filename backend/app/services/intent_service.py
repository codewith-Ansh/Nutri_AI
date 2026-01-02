import json
import logging
from typing import Optional, List, Dict
from app.utils.prompts_v2 import INTENT_EXTRACTION_PROMPT_TEMPLATE
from app.core.exceptions import LLMServiceError

logger = logging.getLogger(__name__)

# Import existing gemini service if available, otherwise create minimal wrapper
try:
    from app.services.gemini_service import gemini_service
    GEMINI_CLIENT = gemini_service
except ImportError:
    # Fallback minimal Gemini client
    import google.generativeai as genai
    from app.config import settings
    
    class MinimalGeminiClient:
        def __init__(self):
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        async def generate_text(self, prompt: str, system_instruction: str = "") -> str:
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                raise LLMServiceError(f"Gemini error: {str(e)}")
    
    GEMINI_CLIENT = MinimalGeminiClient()

class AINativeIntentService:
    """AI-native intent service that softly infers context without forms or certainty"""
    
    def __init__(self):
        self.client = GEMINI_CLIENT
    
    async def soft_infer_context(
        self,
        session_id: str,
        message: str,
        recent_history: Optional[List[dict]] = None,
        existing_context: Optional[dict] = None
    ) -> Dict[str, any]:
        """Softly infer user context without being certain"""
        try:
            # Format recent messages
            recent_msgs = ""
            if recent_history:
                recent_msgs = "\n".join([
                    f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                    for msg in recent_history[-3:]  # Last 3 messages
                ])
            
            # Format existing context
            context_str = json.dumps(existing_context) if existing_context else "none"
            
            # Extract any ingredients mentioned (but don't focus on them)
            ingredients_mentioned = self._extract_mentioned_ingredients(message)
            ingredients_str = ", ".join(ingredients_mentioned) if ingredients_mentioned else "none"
            
            # Build prompt
            prompt = INTENT_EXTRACTION_PROMPT_TEMPLATE.format(
                current_message=message,
                recent_messages=recent_msgs,
                ingredients=ingredients_str,
                existing_context=context_str
            )
            
            # Call Gemini
            response = await self.client.generate_text(
                prompt=prompt,
                system_instruction="You softly infer user context. Be uncertain, use hedge language, make gentle guesses."
            )
            
            # Parse JSON response
            try:
                # Clean the response text
                response_clean = response.strip()
                if response_clean.startswith('```json'):
                    response_clean = response_clean.replace('```json', '').replace('```', '')
                
                context_data = json.loads(response_clean)
                logger.info(f"Softly inferred context for session {session_id}: {context_data.get('likely_goal', 'unclear')}")
                return context_data
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON parse failed: {e}")
                # Return default uncertain context
                return self._default_uncertain_context()
                
        except Exception as e:
            logger.error(f"Context inference error: {str(e)}")
            return self._default_uncertain_context()
    
    def _extract_mentioned_ingredients(self, message: str) -> List[str]:
        """Extract any ingredients mentioned in message (simple keyword matching)"""
        # Common ingredient keywords
        common_ingredients = [
            'sugar', 'salt', 'sodium', 'oil', 'flour', 'preservatives',
            'artificial', 'colors', 'flavors', 'palm oil', 'trans fat'
        ]
        
        # Indian food items that should be recognized
        indian_foods = [
            'vadapav', 'vada pav', 'parle g', 'parle-g', 'samosa', 'bhel puri',
            'pani puri', 'dosa', 'idli', 'upma', 'poha', 'maggi', 'kurkure'
        ]
        
        message_lower = message.lower()
        
        # Check for Indian foods first
        found_foods = [food for food in indian_foods if food in message_lower]
        if found_foods:
            return found_foods[:2]  # Return food items as "ingredients" for context
        
        # Then check for regular ingredients
        found = [ing for ing in common_ingredients if ing in message_lower]
        return found[:3]  # Max 3 to keep it simple
    
    def _default_uncertain_context(self) -> Dict[str, any]:
        """Return default uncertain context when inference fails"""
        return {
            "likely_goal": "curiosity",
            "possible_context": None,
            "soft_concerns": [],
            "confidence_level": "uncertain",
            "hedge_language": "I'm not sure what you're most interested in here"
        }
    
    def merge_context_gently(
        self, 
        old_context: Dict[str, any], 
        new_context: Dict[str, any]
    ) -> Dict[str, any]:
        """Gently merge contexts, preferring uncertainty over false confidence"""
        # Only update if new context is more confident
        old_confidence = old_context.get('confidence_level', 'uncertain')
        new_confidence = new_context.get('confidence_level', 'uncertain')
        
        confidence_order = {'uncertain': 0, 'somewhat_sure': 1, 'fairly_confident': 2}
        
        if confidence_order.get(new_confidence, 0) > confidence_order.get(old_confidence, 0):
            # Use new context but keep uncertainty language
            merged = new_context.copy()
            merged['hedge_language'] = new_context.get('hedge_language') or "I think this might be about..."
            return merged
        else:
            # Keep old context, maybe add new concerns
            merged = old_context.copy()
            old_concerns = set(old_context.get('soft_concerns', []))
            new_concerns = set(new_context.get('soft_concerns', []))
            merged['soft_concerns'] = list(old_concerns.union(new_concerns))[:3]  # Max 3
            return merged

# Singleton instance
ai_native_intent = AINativeIntentService()
