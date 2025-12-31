import json
import re
from typing import Any, Dict

class JSONExtractionError(Exception):
    """Raised when JSON extraction fails"""
    pass

def extract_and_parse_json(text: str) -> Dict[str, Any]:
    """
    Robustly extract and parse JSON from text response
    
    Args:
        text: Raw text that may contain JSON
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        JSONExtractionError: If JSON cannot be extracted or parsed
    """
    # Remove markdown code fences
    cleaned = re.sub(r'```json\s*', '', text)
    cleaned = re.sub(r'```\s*$', '', cleaned)
    cleaned = cleaned.strip()
    
    # Try direct parsing first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON object in text
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Try simple repair - remove trailing commas
    try:
        repaired = re.sub(r',\s*}', '}', cleaned)
        repaired = re.sub(r',\s*]', ']', repaired)
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass
    
    # Last attempt - extract between first { and last }
    try:
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            json_candidate = cleaned[start:end+1]
            # Remove trailing commas again
            json_candidate = re.sub(r',\s*}', '}', json_candidate)
            json_candidate = re.sub(r',\s*]', ']', json_candidate)
            return json.loads(json_candidate)
    except json.JSONDecodeError:
        pass
    
    raise JSONExtractionError(f"Could not extract valid JSON from text: {text[:200]}...")

def validate_json_structure(data: Dict[str, Any], required_fields: list) -> bool:
    """Validate that JSON has required fields"""
    return all(field in data for field in required_fields)