from typing import List

def map_confidence_to_language(confidence: str) -> str:
    """Map confidence levels to human-readable language"""
    mapping = {
        "high": "Well-established",
        "medium": "Evidence suggests", 
        "low": "Unclear / limited evidence"
    }
    return mapping.get(confidence.lower(), "Unknown confidence")

def format_uncertainty_section(uncertainty_items: List[str]) -> str:
    """Format uncertainty items into a readable section"""
    if not uncertainty_items:
        return ""
    
    if len(uncertainty_items) == 1:
        return f"Uncertainty: {uncertainty_items[0]}"
    
    formatted_items = "\n".join([f"• {item}" for item in uncertainty_items])
    return f"Uncertainties:\n{formatted_items}"

def get_confidence_qualifier(confidence: str) -> str:
    """Get a qualifier phrase for confidence level"""
    qualifiers = {
        "high": "with high confidence",
        "medium": "with moderate confidence",
        "low": "with limited confidence"
    }
    return qualifiers.get(confidence.lower(), "")