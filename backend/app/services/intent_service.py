import json
import logging
from typing import Optional, List, Dict
from app.models.intent_models import IntentProfile, IntentConfidence
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

class IntentService:
    def __init__(self):
        self.client = GEMINI_CLIENT
    
    async def infer_intent(
        self,
        session_id: str,
        message: str,
        ingredients: Optional[List[str]] = None,
        recent_history: Optional[List[dict]] = None,
        existing_context: Optional[dict] = None
    ) -> IntentProfile:
        """Infer user intent from message and context"""
        try:
            # Format recent messages
            recent_msgs = ""
            if recent_history:
                recent_msgs = "\n".join([
                    f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                    for msg in recent_history[-3:]  # Last 3 messages
                ])
            
            # Format ingredients
            ingredients_str = ", ".join(ingredients) if ingredients else "none"
            
            # Format existing context
            context_str = json.dumps(existing_context) if existing_context else "none"
            
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
                system_instruction="You are an expert at inferring user intent from nutrition conversations."
            )
            
            # Parse JSON response
            try:
                intent_data = json.loads(response.strip())
                intent = IntentProfile(**intent_data)
                logger.info(f"Inferred intent for session {session_id}: {intent.user_goal}")
                return intent
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON parse failed, retrying with stricter prompt: {e}")
                # Retry with stricter prompt
                strict_prompt = prompt + "\n\nIMPORTANT: Return ONLY valid JSON. No explanations or markdown."
                response = await self.client.generate_text(strict_prompt)
                intent_data = json.loads(response.strip())
                return IntentProfile(**intent_data)
                
        except Exception as e:
            logger.error(f"Intent inference error: {str(e)}")
            # Return default intent on failure
            return IntentProfile(
                confidence=IntentConfidence.low,
                clarifying_question="Could you tell me more about what you're looking for?"
            )
    
    def merge_intent(self, old: IntentProfile, new: IntentProfile) -> IntentProfile:
        """Merge old and new intent profiles intelligently"""
        # Keep existing goal/dietary_style unless new has higher confidence
        user_goal = old.user_goal
        dietary_style = old.dietary_style
        
        if new.confidence.value == "high" or (new.confidence.value == "medium" and old.confidence.value == "low"):
            if new.user_goal:
                user_goal = new.user_goal
            if new.dietary_style:
                dietary_style = new.dietary_style
        
        # Merge lists uniquely
        allergy_risks = list(set(old.allergy_risks + new.allergy_risks))
        top_concerns = list(set(old.top_concerns + new.top_concerns))
        
        # Use new audience if specified
        audience = new.audience if new.audience else old.audience
        
        # Use highest confidence
        confidence = new.confidence if new.confidence.value == "high" else (
            old.confidence if old.confidence.value == "high" else new.confidence
        )
        
        # Keep clarifying question only if still needed
        clarifying_question = new.clarifying_question if confidence.value == "low" else None
        
        return IntentProfile(
            user_goal=user_goal,
            dietary_style=dietary_style,
            allergy_risks=allergy_risks,
            audience=audience,
            top_concerns=top_concerns,
            confidence=confidence,
            clarifying_question=clarifying_question
        )

# Singleton instance
intent_service = IntentService()