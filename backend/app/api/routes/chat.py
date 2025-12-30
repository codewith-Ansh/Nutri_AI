from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse
from app.services.reasoning_service import reasoning_service
from app.utils.session_manager import session_manager
from app.core.exceptions import NutriAIException, SessionNotFoundError
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Conversational ingredient analysis"""
    try:
        # Get session
        session = session_manager.get_session(request.session_id)
        if not session:
            raise SessionNotFoundError(f"Session {request.session_id} not found")
        
        # Get conversation history
        history = session_manager.get_conversation_history(request.session_id)
        
        # Generate response
        response = await reasoning_service.conversational_analysis(
            message=request.message,
            conversation_history=history
        )
        
        # Store in session
        session_manager.add_message(request.session_id, "user", request.message)
        session_manager.add_message(request.session_id, "assistant", response)
        
        logger.info(f"Chat response generated for session {request.session_id}")
        
        return ChatResponse(
            success=True,
            session_id=request.session_id,
            response=response,
            message_count=len(session["conversation_history"])
        )
    except NutriAIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming conversational ingredient analysis"""
    try:
        # Get session
        session = session_manager.get_session(request.session_id)
        if not session:
            # Create new session if not found
            request.session_id = session_manager.create_session()
        
        # Get conversation history
        history = session_manager.get_conversation_history(request.session_id)
        
        async def generate_stream():
            try:
                full_response = ""
                for chunk in reasoning_service.stream_conversational_analysis(
                    message=request.message,
                    conversation_history=history
                ):
                    full_response += chunk
                    # Format as SSE
                    yield f"data: {json.dumps({'choices': [{'delta': {'content': chunk}}]})}\n\n"
                
                # Store complete response in session
                session_manager.add_message(request.session_id, "user", request.message)
                session_manager.add_message(request.session_id, "assistant", full_response)
                
                # Send completion signal
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"Streaming error: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        logger.error(f"Chat stream error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/chat/{session_id}/history")
async def get_chat_history(session_id: str):
    """Get conversation history for a session"""
    try:
        history = session_manager.get_conversation_history(session_id)
        if history is None:
            raise SessionNotFoundError(f"Session {session_id} not found")
        
        return {
            "success": True,
            "session_id": session_id,
            "history": history,
            "message_count": len(history)
        }
    except NutriAIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Get history error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
