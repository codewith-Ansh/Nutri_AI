from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.models.intent_models import IntentProfile
from app.services.intent_service import intent_service
from app.utils.session_manager import session_manager
from app.core.exceptions import NutriAIException
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class IntentInferRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    ingredients: Optional[List[str]] = None

class IntentInferResponse(BaseModel):
    success: bool
    session_id: str
    intent: IntentProfile

@router.post("/intent/infer", response_model=IntentInferResponse)
async def infer_intent(request: IntentInferRequest):
    """Infer user intent from message and context"""
    try:
        # Get or create session
        session_id = request.session_id or session_manager.create_session()
        
        # Get existing context and history
        existing_context = session_manager.get_context(session_id)
        recent_history = session_manager.get_conversation_history(session_id)
        
        # Infer intent
        new_intent = await intent_service.infer_intent(
            session_id=session_id,
            message=request.message,
            ingredients=request.ingredients,
            recent_history=recent_history,
            existing_context=existing_context
        )
        
        # Merge with existing intent if present
        existing_intent_data = existing_context.get("intent") if existing_context else None
        if existing_intent_data:
            try:
                existing_intent = IntentProfile(**existing_intent_data)
                merged_intent = intent_service.merge_intent(existing_intent, new_intent)
            except Exception:
                merged_intent = new_intent
        else:
            merged_intent = new_intent
        
        # Store in session context
        session_manager.update_context(session_id, {
            "intent": merged_intent.dict()
        })
        
        logger.info(f"Intent inferred for session {session_id}: {merged_intent.user_goal}")
        
        return IntentInferResponse(
            success=True,
            session_id=session_id,
            intent=merged_intent
        )
        
    except NutriAIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Intent inference error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to infer intent")

@router.get("/intent/{session_id}", response_model=IntentProfile)
async def get_intent(session_id: str):
    """Get stored intent for a session"""
    try:
        context = session_manager.get_context(session_id)
        if not context or "intent" not in context:
            raise HTTPException(status_code=404, detail="No intent found for session")
        
        intent_data = context["intent"]
        return IntentProfile(**intent_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get intent error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve intent")