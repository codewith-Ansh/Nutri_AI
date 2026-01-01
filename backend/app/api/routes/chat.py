from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse
from app.services.gemini_service import gemini_service
from app.utils.session_manager import session_manager
from app.core.exceptions import NutriAIException
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse
from app.services.gemini_service import gemini_service
from app.services.intent_service import intent_service
from app.services.reasoning_service_v2 import reasoning_service_v2
from app.utils.session_manager import session_manager
from app.core.exceptions import NutriAIException
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the AI assistant using reasoning v2"""
    try:
        # Get or create session
        session_id = request.session_id or session_manager.create_session()
        
        # Get conversation history and context
        history = session_manager.get_conversation_history(session_id)
        context = session_manager.get_context(session_id)
        
        # Get or infer intent
        stored_intent = session_manager.get_intent(session_id)
        if not stored_intent:
            intent_profile = await intent_service.infer_intent(
                session_id=session_id,
                message=request.message,
                recent_history=history[-3:] if history else None,
                existing_context=context
            )
            session_manager.set_intent(session_id, intent_profile.dict())
        else:
            intent_profile = stored_intent
        
        # Check if message contains ingredients for reasoning analysis
        ingredients = context.get('recent_ingredients', [])
        product_info = context.get('product_info')  # Get product context if available
        
        if ingredients:
            # Use reasoning v2 for ingredient-related queries
            reasoning_result = await reasoning_service_v2.generate(
                ingredients=ingredients,
                intent_profile=intent_profile,
                recent_history=history[-3:] if history else None,
                product_info=product_info
            )
            response_text = reasoning_result.narrative
            
            # Store structured findings in context for potential UI use
            session_manager.update_context(session_id, {
                'last_reasoning_result': reasoning_result.dict()
            })
        else:
            # Use regular chat for non-ingredient queries
            response_text = await gemini_service.generate_chat_response(
                message=request.message,
                conversation_history=history
            )
        
        # Store messages in session
        session_manager.add_message(session_id, "user", request.message)
        session_manager.add_message(session_id, "assistant", response_text)
        
        logger.info(f"Chat response generated for session {session_id}")
        
        return ChatResponse(
            success=True,
            session_id=session_id,
            response=response_text,
            intent=intent_profile if isinstance(intent_profile, dict) else intent_profile.dict(),
            structured_findings=context.get('last_reasoning_result')
        )
    except NutriAIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.options("/chat/stream")
async def chat_stream_options():
    """Handle CORS preflight for chat stream"""
    return {"message": "OK"}

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat response from AI assistant"""
    try:
        # Get or create session
        session_id = request.session_id or session_manager.create_session()
        
        # Get conversation history
        history = session_manager.get_conversation_history(session_id)
        
        # Store user message
        session_manager.add_message(session_id, "user", request.message)
        
        async def generate_stream():
            full_response = ""
            async for chunk in gemini_service.stream_chat_response(
                message=request.message,
                conversation_history=history
            ):
                full_response += chunk
                # Format as SSE
                data = {
                    "choices": [{
                        "delta": {
                            "content": chunk
                        }
                    }]
                }
                yield f"data: {json.dumps(data)}\n\n"
            
            # Store complete response
            session_manager.add_message(session_id, "assistant", full_response)
            
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
        logger.error(f"Chat stream error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")