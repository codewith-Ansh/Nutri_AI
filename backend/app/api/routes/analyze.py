from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.request_models import TextAnalysisRequest, ImageUploadMetadata
from app.models.response_models import AnalysisResponse
from app.services.image_service import image_service
from app.services.text_processor import text_processor
from app.services.reasoning_service import reasoning_service
from app.utils.session_manager import session_manager
from app.core.exceptions import NutriAIException
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analyze/text", response_model=AnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """Analyze ingredient text"""
    try:
        # Validate input
        text_processor.validate_input(request.text)
        
        # Extract ingredients
        ingredients = text_processor.extract_ingredients(request.text)
        
        # Get or create session
        session_id = request.session_id or session_manager.create_session()
        
        # Analyze ingredients
        analysis_result = await reasoning_service.analyze_ingredients(ingredients)
        
        # Store in session
        session_manager.add_message(session_id, "user", request.text)
        session_manager.add_message(session_id, "assistant", analysis_result["analysis"])
        
        logger.info(f"Text analysis completed for session {session_id}")
        
        return AnalysisResponse(
            success=True,
            session_id=session_id,
            analysis=analysis_result["analysis"],
            ingredients=ingredients,
            ingredient_count=len(ingredients)
        )
    except NutriAIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Text analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/analyze/image", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """Analyze ingredient image"""
    try:
        # Process image
        image_result = await image_service.process_image(file)
        
        if not image_result["success"] or not image_result["ingredients"]:
            raise HTTPException(
                status_code=400,
                detail="Could not extract ingredients from image"
            )
        
        # Create session
        session_id = session_manager.create_session()
        
        # Analyze extracted ingredients
        analysis_result = await reasoning_service.analyze_ingredients(
            image_result["ingredients"]
        )
        
        # Store in session
        session_manager.update_context(session_id, {
            "image_processed": True,
            "extracted_text": image_result["extracted_text"]
        })
        session_manager.add_message(
            session_id,
            "user",
            f"Uploaded image with {len(image_result['ingredients'])} ingredients"
        )
        session_manager.add_message(session_id, "assistant", analysis_result["analysis"])
        
        logger.info(f"Image analysis completed for session {session_id}")
        
        return AnalysisResponse(
            success=True,
            session_id=session_id,
            analysis=analysis_result["analysis"],
            ingredients=image_result["ingredients"],
            ingredient_count=len(image_result["ingredients"]),
            extracted_text=image_result["extracted_text"] if image_result else None
        )
    except NutriAIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
