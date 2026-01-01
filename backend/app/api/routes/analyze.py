from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.request_models import TextAnalysisRequest
from app.services.image_services import image_service
from app.services.reasoning_service_v2 import ai_native_reasoning
from app.services.intent_service import ai_native_intent
from app.utils.session_manager import session_manager
from app.core.exceptions import NutriAIException
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analyze/text")
async def analyze_text_ai_native(request: TextAnalysisRequest):
    """AI-native text analysis - reasoning-driven, not ingredient-focused"""
    try:
        # Get or create session
        session_id = request.session_id or session_manager.create_session()
        
        # Get conversation history for context
        history = session_manager.get_conversation_history(session_id)
        existing_context = session_manager.get_context(session_id)
        
        # Softly infer context (not rigid intent)
        inferred_context = await ai_native_intent.soft_infer_context(
            session_id=session_id,
            message=request.text,
            recent_history=history[-3:] if history else None,
            existing_context=existing_context
        )
        
        # Generate AI-native reasoning response
        reasoning_response = await ai_native_reasoning.analyze_from_text(
            user_input=request.text,
            inferred_context=inferred_context,
            conversation_history=history[-3:] if history else None
        )
        
        # Store context and conversation
        session_manager.update_context(session_id, inferred_context)
        session_manager.add_message(session_id, "user", request.text)
        session_manager.add_message(session_id, "assistant", reasoning_response)
        
        logger.info(f"AI-native text analysis completed for session {session_id}")
        
        # Return simple response - no structured data, no scores
        return {
            "success": True,
            "session_id": session_id,
            "analysis": reasoning_response
        }
        
    except NutriAIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Text analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="I'm having trouble right now. Could you try again?")

@router.post("/analyze/image")
async def analyze_image_ai_native(file: UploadFile = File(...)):
    """AI-native image analysis - visual context inference, not OCR-first"""
    try:
        # Read image data
        image_data = await file.read()
        
        # Create session
        session_id = session_manager.create_session()
        
        # Get existing context if any
        existing_context = session_manager.get_context(session_id)
        
        # Softly infer context from image (visual cues, not just text)
        inferred_context = await ai_native_intent.soft_infer_context(
            session_id=session_id,
            message=f"Uploaded image of food product",
            existing_context=existing_context
        )
        
        # Generate AI-native reasoning from image
        reasoning_response = await ai_native_reasoning.analyze_from_image(
            image_data=image_data,
            inferred_context=inferred_context
        )
        
        # Store context and conversation
        session_manager.update_context(session_id, inferred_context)
        session_manager.add_message(session_id, "user", "Shared a photo")
        session_manager.add_message(session_id, "assistant", reasoning_response)
        
        logger.info(f"AI-native image analysis completed for session {session_id}")
        
        # Return simple response - no technical metadata
        return {
            "success": True,
            "session_id": session_id,
            "analysis": reasoning_response
        }
        
    except NutriAIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="I couldn't analyze this image right now. Mind trying again?")