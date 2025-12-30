from app.services.gemini_service import gemini_service
from app.utils.prompts import PromptTemplates
from app.core.exceptions import LLMServiceError
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

class ReasoningService:
    def __init__(self):
        self.llm = gemini_service
        self.prompts = PromptTemplates()
    
    async def analyze_ingredients(self, ingredients: list[str], context: dict = None) -> dict:
        """Analyze ingredients and generate insights"""
        try:
            # Format ingredients for prompt
            ingredients_text = ", ".join(ingredients)
            
            # Get analysis prompt
            prompt = self.prompts.get_ingredient_analysis_prompt(ingredients_text)
            system_prompt = self.prompts.get_system_prompt()
            
            # Generate analysis
            analysis = await self.llm.generate_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            return {
                "success": True,
                "ingredients": ingredients,
                "analysis": analysis,
                "ingredient_count": len(ingredients)
            }
        except Exception as e:
            logger.error(f"Reasoning error: {str(e)}")
            raise LLMServiceError("Failed to analyze ingredients")
    
    async def analyze_text_input(self, text: str) -> dict:
        """Analyze raw text input"""
        try:
            prompt = self.prompts.get_text_analysis_prompt(text)
            system_prompt = self.prompts.get_system_prompt()
            
            analysis = await self.llm.generate_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            return {
                "success": True,
                "input_text": text,
                "analysis": analysis
            }
        except Exception as e:
            logger.error(f"Text analysis error: {str(e)}")
            raise LLMServiceError("Failed to analyze text")
    
    async def conversational_analysis(
        self,
        message: str,
        conversation_history: list
    ) -> str:
        """Generate conversational response with context"""
        try:
            system_prompt = self.prompts.get_conversational_system_prompt()
            
            response = await self.llm.generate_with_context(
                prompt=message,
                conversation_history=conversation_history,
                system_prompt=system_prompt
            )
            
            return response
        except Exception as e:
            logger.error(f"Conversational analysis error: {str(e)}")
            raise LLMServiceError("Failed to generate conversational response")
    
    def stream_conversational_analysis(
        self,
        message: str,
        conversation_history: list
    ):
        """Stream conversational response with context"""
        try:
            system_prompt = self.prompts.get_conversational_system_prompt()
            
            # Build conversation context
            context_parts = []
            for msg in conversation_history:
                role = "user" if msg["role"] == "user" else "assistant"
                context_parts.append(f"{role}: {msg['content']}")
            
            full_prompt = f"Conversation history:\n" + "\n".join(context_parts) + f"\n\nuser: {message}"
            
            for chunk in self.llm.stream_text(full_prompt, system_prompt):
                yield chunk
        except Exception as e:
            logger.error(f"Streaming conversational analysis error: {str(e)}")
            raise LLMServiceError("Failed to stream conversational response")

# Singleton instance
reasoning_service = ReasoningService()
