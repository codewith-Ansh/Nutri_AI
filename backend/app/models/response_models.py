from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AnalysisResponse(BaseModel):
    """Response model for ingredient analysis"""
    success: bool
    session_id: str
    analysis: str
    ingredients: List[str]
    ingredient_count: int
    extracted_text: Optional[str] = None
    # New optional fields for reasoning v2
    intent: Optional[Dict[str, Any]] = None
    structured_findings: Optional[Dict[str, Any]] = None
    uncertainty: Optional[List[str]] = None

class ChatResponse(BaseModel):
    """Response model for chat interactions"""
    success: bool
    session_id: str
    response: str
    message_count: Optional[int] = None
    # New optional fields for reasoning v2
    intent: Optional[Dict[str, Any]] = None
    structured_findings: Optional[Dict[str, Any]] = None
    uncertainty: Optional[List[str]] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
