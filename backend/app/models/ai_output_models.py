from pydantic import BaseModel
from typing import List, Optional

class Finding(BaseModel):
    ingredient: str
    why_it_matters: str
    risk_level: str  # low/medium/high
    confidence: str  # low/medium/high
    evidence_notes: Optional[str] = None

class Tradeoff(BaseModel):
    topic: str
    benefit: str
    concern: str

class Recommendation(BaseModel):
    title: str
    action: str

class ReasoningV2Result(BaseModel):
    overall_assessment: str
    findings: List[Finding]
    tradeoffs: List[Tradeoff]
    recommendations: List[Recommendation]
    uncertainty: List[str]
    narrative: str  # short final answer for the user