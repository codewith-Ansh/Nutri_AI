import google.generativeai as genai
from app.config import settings
from app.core.exceptions import LLMServiceError
import logging
from typing import AsyncGenerator, Type
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
    
    async def generate_text(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful AI nutritionist assistant.",
        temperature: float = None,
        max_output_tokens: int = None
    ) -> str:
        """Generate text response from Gemini"""
        try:
            # Configure generation
            generation_config = genai.types.GenerationConfig(
                temperature=temperature or self.temperature,
                max_output_tokens=max_output_tokens or self.max_tokens,
            )
            
            # Create model with system instruction
            model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                system_instruction=system_instruction,
                generation_config=generation_config
            )
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {str(e)}")
            raise LLMServiceError(f"Failed to generate response: {str(e)}")
    
    def stream_text(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful AI nutritionist assistant.",
        temperature: float = None,
        max_output_tokens: int = None
    ):
        """Stream text response from Gemini"""
        try:
            # Configure generation
            generation_config = genai.types.GenerationConfig(
                temperature=temperature or self.temperature,
                max_output_tokens=max_output_tokens or self.max_tokens,
            )
            
            # Create model with system instruction
            model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                system_instruction=system_instruction,
                generation_config=generation_config
            )
            
            response = model.generate_content(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini streaming error: {str(e)}")
            raise LLMServiceError(f"Failed to stream response: {str(e)}")
    async def generate_json(
        self,
        prompt: str,
        response_schema: Type[BaseModel],
        system_instruction: str = "You are a helpful AI nutritionist assistant."
    ) -> BaseModel:
        """Generate structured JSON response using Gemini"""
        try:
            # Add JSON instruction to prompt
            json_prompt = f"{prompt}\n\nPlease respond with valid JSON only."
            
            response_text = await self.generate_text(json_prompt, system_instruction)
            
            # Parse JSON response into Pydantic model
            json_data = json.loads(response_text)
            return response_schema(**json_data)
        except Exception as e:
            logger.error(f"Gemini JSON generation error: {str(e)}")
            raise LLMServiceError(f"Failed to generate structured response: {str(e)}")
    
    async def generate_response(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful AI nutritionist assistant.",
        stream: bool = False
    ) -> str:
        """Generate response from Gemini (compatibility method)"""
        if stream:
            # For streaming, collect all chunks
            chunks = []
            for chunk in self.stream_text(prompt, system_prompt):
                chunks.append(chunk)
            return ''.join(chunks)
        else:
            return await self.generate_text(prompt, system_prompt)
    
    async def generate_with_context(
        self,
        prompt: str,
        conversation_history: list,
        system_prompt: str = "You are a helpful AI nutritionist assistant."
    ) -> str:
        """Generate response with conversation context"""
        try:
            # Build conversation context
            context_parts = []
            for msg in conversation_history:
                role = "user" if msg["role"] == "user" else "assistant"
                context_parts.append(f"{role}: {msg['content']}")
            
            full_prompt = f"Conversation history:\n" + "\n".join(context_parts) + f"\n\nuser: {prompt}"
            
            return await self.generate_text(full_prompt, system_prompt)
        except Exception as e:
            logger.error(f"Gemini context generation error: {str(e)}")
            raise LLMServiceError(f"Failed to generate contextual response: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """Validate that API key is configured"""
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
            raise LLMServiceError("Gemini API key not configured")
        return True
    
    async def generate_chat_response(
        self,
        message: str,
        conversation_history: list = None
    ) -> str:
        """Generate chat response with conversation context"""
        if conversation_history:
            return await self.generate_with_context(
                message, 
                conversation_history,
                "You are NutriAI, a helpful nutrition assistant. Provide accurate, helpful information about food, nutrition, and healthy eating."
            )
        else:
            return await self.generate_text(
                message,
                "You are NutriAI, a helpful nutrition assistant. Provide accurate, helpful information about food, nutrition, and healthy eating."
            )
    
    async def stream_chat_response(
        self,
        message: str,
        conversation_history: list = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat response with conversation context"""
        try:
            # Build context if provided
            if conversation_history:
                context_parts = []
                for msg in conversation_history:
                    role = "user" if msg["role"] == "user" else "assistant"
                    context_parts.append(f"{role}: {msg['content']}")
                
                full_prompt = f"Conversation history:\n" + "\n".join(context_parts) + f"\n\nuser: {message}"
            else:
                full_prompt = message
            
            # Stream response
            for chunk in self.stream_text(
                full_prompt,
                "You are NutriAI, a helpful nutrition assistant. Provide accurate, helpful information about food, nutrition, and healthy eating."
            ):
                yield chunk
        except Exception as e:
            logger.error(f"Chat streaming error: {str(e)}")
            raise LLMServiceError(f"Failed to stream chat response: {str(e)}")

# Singleton instance
gemini_service = GeminiService()
