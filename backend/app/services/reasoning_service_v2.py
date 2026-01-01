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
            
            prompt = f"""
User input: "{user_input}"
{context_info}
{history_context}

Provide a reasoning-driven response that:
1. Acknowledges the context (if this seems like a snack choice, shopping decision, etc.)
2. Explains WHY certain aspects matter for this decision
3. Presents trade-offs honestly (why people still buy this vs. concerns)
4. Acknowledges uncertainty where it exists
5. Helps the user think through the decision

Do NOT:
- List ingredients
- Give scores or percentages
- Make absolute statements
- Provide medical advice

Use natural, conversational language. Be a thinking partner, not an analyzer.
"""
            
            response = await self.gemini.generate_text(
                prompt=prompt,
                system_instruction=REASONING_SYSTEM_PROMPT,
                temperature=0.4
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Text reasoning failed: {str(e)}")
            return "I'm having trouble analyzing this right now. Could you tell me a bit more about what you're looking for?"
    
    async def analyze_from_image(
        self,
        image_data: bytes,
        inferred_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate reasoning-driven response from image with visual context inference"""
        try:
            # First, get visual context
            visual_prompt = VISUAL_CONTEXT_PROMPT + "\n\nAnalyze this food product image and provide the JSON response."
            
            # Note: This is a simplified approach. In a full implementation,
            # you'd use Gemini Vision API to analyze the actual image
            # For now, we'll infer context from any available metadata
            
            visual_context = {
                "visual_context": "This appears to be a packaged food product",
                "likely_intent": "quick_choice",
                "inferred_concerns": ["additives", "nutrition"],
                "hedge_language": "I might be wrong, but this looks like",
                "reasoning_focus": "convenience vs. health trade-offs"
            }
            
            # Build reasoning prompt based on visual context
            prompt = f"""
Based on the image analysis:
{visual_context['visual_context']}

Likely user intent: {visual_context['likely_intent']}
Possible concerns: {', '.join(visual_context['inferred_concerns'])}

Provide a response that:
1. References what you can see in the image ("This looks like...")
2. Acknowledges uncertainty about visual details
3. Focuses on decision-relevant aspects for this product type
4. Presents trade-offs people usually consider
5. Helps with the decision without being prescriptive

Use hedge language like "appears to be", "might be", "often".
Do NOT list ingredients or give technical analysis.
"""
            
            response = await self.gemini.generate_text(
                prompt=prompt,
                system_instruction=REASONING_SYSTEM_PROMPT,
                temperature=0.4
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Image reasoning failed: {str(e)}")
            return "I'm having trouble making out the details in this image. Could you try taking another photo with better lighting?"
    
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
