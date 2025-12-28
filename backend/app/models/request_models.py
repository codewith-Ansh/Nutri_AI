from pydantic import BaseModel, Field, validator
from typing import Optional, List

class TextAnalysisRequest(BaseModel):
    """Request model for text-based ingredient analysis"""
    text: str = Field(..., min_length=1, description="Ingredient text to analyze")
    session_id: Optional[str] = Field(None, description="Session ID for conversation context")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()

class ChatRequest(BaseModel):
    """Request model for chat interactions"""
    message: str = Field(..., min_length=1, description="User message")
    session_id: str = Field(..., description="Session ID for maintaining context")
    context: Optional[dict] = Field(None, description="Additional context")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()

class ImageUploadMetadata(BaseModel):
    """Metadata for image upload"""
    session_id: Optional[str] = Field(None, description="Session ID")
    include_raw_text: bool = Field(False, description="Include raw OCR text in response")