from app.services.llm_service import llm_service
from app.utils.prompts import PromptTemplates
from app.core.exceptions import LLMServiceError
import logging

logger = logging.getLogger(__name__)

class ReasoningService:
    def __init__(self):
        self.llm = llm_service
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

# Singleton instance
reasoning_service = ReasoningService()
