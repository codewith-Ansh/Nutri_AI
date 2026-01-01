from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.intent_service import ai_native_intent
from app.utils.session_manager import session_manager
from app.core.exceptions import NutriAIException
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class IntentInferRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class IntentInferResponse(BaseModel):
    success: bool
    session_id: str
    context: dict

@router.post("/intent/infer", response_model=IntentInferResponse)
async def infer_context(request: IntentInferRequest):
    """Softly infer user context (AI-native approach)"""
    try:
        # Get or create session
        session_id = request.session_id or session_manager.create_session()
        
        # Get existing context and history
        existing_context = session_manager.get_context(session_id)
        recent_history = session_manager.get_conversation_history(session_id)
        
        # Softly infer context
        inferred_context = await ai_native_intent.soft_infer_context(
            session_id=session_id,
            message=request.message,
            recent_history=recent_history,
            existing_context=existing_context
        )
        
        # Merge with existing context
        if existing_context:
            merged_context = ai_native_intent.merge_context_gently(existing_context, inferred_context)
        else:
            merged_context = inferred_context
        
        # Store in session
        session_manager.update_context(session_id, merged_context)
        
        logger.info(f"Context inferred for session {session_id}: {merged_context.get('likely_goal', 'unclear')}")
        
        return IntentInferResponse(
            success=True,
            session_id=session_id,
            context=merged_context
        )
        
    except Exception as e:
        logger.error(f"Context inference error: {str(e)}")
        return IntentInferResponse(
            success=False,
            session_id=session_id or "unknown",
            context={"likely_goal": "curiosity", "confidence_level": "uncertain"}
        )