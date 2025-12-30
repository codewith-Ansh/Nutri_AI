from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "NutriAI Backend",
        "debug_mode": settings.DEBUG
    }

@router.get("/health/llm")
async def llm_health_check():
    """Check LLM service availability"""
    try:
        from app.services.gemini_service import gemini_service
        gemini_service.validate_api_key()
        return {
            "status": "healthy",
            "llm_service": "available",
            "model": settings.GEMINI_MODEL
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "llm_service": "unavailable",
            "error": str(e)
        }
