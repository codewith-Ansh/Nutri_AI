# FastAPI application entry point
# Configure middleware (CORS)
# Register all API routes
# Add exception handlers
# Enable startup/shutdown events



from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.core.exceptions import NutriAIException
from app.api.routes import health, analyze, chat, intent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NutriAI Backend",
    description="AI-Native Food Ingredient Insights API",
    version="1.0.0",
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(intent.router, prefix="/api", tags=["Intent"])

# Global exception handler
@app.exception_handler(NutriAIException)
async def nutriai_exception_handler(request: Request, exc: NutriAIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 NutriAI Backend starting up...")
    logger.info(f"📡 API running on {settings.API_HOST}:{settings.API_PORT}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("⛔ NutriAI Backend shutting down...")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to NutriAI Backend API",
        "version": "1.0.0",
        "status": "running"
    }
