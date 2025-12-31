from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class IntentConfidence(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class IntentProfile(BaseModel):
    """User intent profile inferred from conversation"""
    user_goal: Optional[str] = Field(None, description="Primary goal: weight_loss, health_check, allergy_safety, etc.")
    dietary_style: Optional[str] = Field(None, description="Dietary preference: vegetarian, keto, diabetic, etc.")
    allergy_risks: List[str] = Field(default_factory=list, description="Known or suspected allergies")
    audience: Optional[str] = Field(None, description="Target audience: self, kid, elderly, pregnant, athlete, etc.")
    top_concerns: List[str] = Field(default_factory=list, description="Main health concerns: sodium, sugar, preservatives, etc.")
    confidence: IntentConfidence = Field(IntentConfidence.medium, description="Confidence in intent inference")
    clarifying_question: Optional[str] = Field(None, description="Question to ask if more clarity needed")