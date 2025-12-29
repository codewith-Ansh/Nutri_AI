from pydantic import BaseModel
from typing import Optional, List

class AnalysisResponse(BaseModel):
    """Response model for ingredient analysis"""
    success: bool
    session_id: str
    analysis: str
    ingredients: List[str]
    ingredient_count: int
    extracted_text: Optional[str] = None

class ChatResponse(BaseModel):
    """Response model for chat interactions"""
    success: bool
    session_id: str
    response: str
    message_count: int

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
