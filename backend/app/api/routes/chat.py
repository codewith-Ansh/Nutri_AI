from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.request_models import ChatRequest
from app.services.gemini_service import gemini_service
from app.services.reasoning_service_v2 import ai_native_reasoning
from app.services.intent_service import ai_native_intent
from app.utils.session_manager import session_manager
from app.core.exceptions import NutriAIException
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

@router.options("/chat/stream")
async def chat_stream_options():
    """Handle CORS preflight for chat stream"""
    return {"message": "OK"}

@router.post("/chat/stream")
async def chat_stream_ai_native(request: ChatRequest):
    """AI-native streaming chat - reasoning-driven, context-aware"""
    try:
        # Get or create session
        session_id = request.session_id or session_manager.create_session()
        
        # Get conversation history and context
        history = session_manager.get_conversation_history(session_id)
        existing_context = session_manager.get_context(session_id)
        
        # Store user message
        session_manager.add_message(session_id, "user", request.message)
        
        # Softly infer context for this message
        inferred_context = await ai_native_intent.soft_infer_context(
            session_id=session_id,
            message=request.message,
            recent_history=history[-3:] if history else None,
            existing_context=existing_context
        )
        
        # Generate AI-native reasoning response
        reasoning_response = await ai_native_reasoning.analyze_from_text(
            user_input=request.message,
            inferred_context=inferred_context,
            conversation_history=history[-3:] if history else None
        )
        
        # Update session context
        session_manager.update_context(session_id, inferred_context)
        session_manager.add_message(session_id, "assistant", reasoning_response)
        
        async def generate_stream():
            # Stream the response naturally - no technical chunking
            words = reasoning_response.split()
            current_chunk = ""
            
            for i, word in enumerate(words):
                current_chunk += word + " "
                
                # Send chunks of 3-5 words for natural flow
                if (i + 1) % 4 == 0 or i == len(words) - 1:
                    data = {
                        "choices": [{
                            "delta": {
                                "content": current_chunk
                            }
                        }]
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                    current_chunk = ""
            
            # Send completion signal
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"AI-native chat stream error: {str(e)}")
        
        # Natural error response
        async def error_stream():
            error_msg = "I'm having trouble right now. Could you try asking again?"
            data = {
                "choices": [{
                    "delta": {
                        "content": error_msg
                    }
                }]
            }
            yield f"data: {json.dumps(data)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            error_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )