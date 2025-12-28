import openai
from openai import AsyncOpenAI
from app.config import settings
from app.core.exceptions import LLMServiceError
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
    
    async def generate_response(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful AI nutritionist assistant.",
        stream: bool = False
    ) -> str:
        """Generate response from LLM"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            if stream:
                return await self._stream_response(messages)
            else:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM generation error: {str(e)}")
            raise LLMServiceError(f"Failed to generate response: {str(e)}")
    
    async def _stream_response(self, messages: list) -> AsyncGenerator[str, None]:
        """Stream response from LLM"""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"LLM streaming error: {str(e)}")
            raise LLMServiceError(f"Failed to stream response: {str(e)}")
    
    async def generate_with_context(
        self,
        prompt: str,
        conversation_history: list,
        system_prompt: str = "You are a helpful AI nutritionist assistant."
    ) -> str:
        """Generate response with conversation context"""
        try:
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM context generation error: {str(e)}")
            raise LLMServiceError(f"Failed to generate contextual response: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """Validate that API key is configured"""
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
            raise LLMServiceError("OpenAI API key not configured")
        return True

# Singleton instance
llm_service = LLMService()
