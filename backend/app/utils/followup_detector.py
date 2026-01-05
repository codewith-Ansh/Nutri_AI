"""
Follow-up question detector for conversation context memory.
Detects when user is asking a follow-up question about previously analyzed food.
NOW SUPPORTS: English, Hindi, Gujarati, and Hinglish
"""

import re
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

# Pronouns that typically reference previous context (MULTILINGUAL)
REFERENCE_PRONOUNS_EN = ["this", "it", "that", "these", "those"]
REFERENCE_PRONOUNS_HI = ["yeh", "ye", "woh", "wo", "isko", "usko", "iski", "uski", "aapko"]  
REFERENCE_PRONOUNS_GU = ["aa", "e", "te", "shu", "shu che"]
REFERENCE_PRONOUNS_HINGLISH = ["ye", "this", "wo", "that", "isko", "usko"]

ALL_REFERENCE_PRONOUNS = (REFERENCE_PRONOUNS_EN + REFERENCE_PRONOUNS_HI + 
                          REFERENCE_PRONOUNS_GU + REFERENCE_PRONOUNS_HINGLISH)

# Keywords that indicate consumption/safety queries about food (MULTILINGUAL)
CONSUMPTION_QUERIES_EN = [
    "can i eat", "can we eat", "safe to eat", "okay to eat",
    "daily", "every day", "everyday",
    "safe for kids", "safe for children", "for kids", "for children",
    "for babies", "for toddlers",
    "diabetes", "diabetic", "high bp", "blood pressure", "heart",
    "pregnant", "pregnancy", "weight loss", "lose weight",
    "healthy", "good for me", "bad for me",
]

CONSUMPTION_QUERIES_HI = [
    "kya kha sakte", "kya le sakte", "safe hai", "theek hai",
    "roz", "daily", "har din", "bachchon ke liye", "bacchon ke liye",
    "diabetes", "bp", "pregnancy", "sehat", "health",
]

CONSUMPTION_QUERIES_GU = [
    "khaay shakay", "khavay", "safe che", "theek che",
    "daily", "har roj", "baalo mate", "bachcho mate",
    "diabetes", "bp", "pregnancy", "swasth", "health",
]

CONSUMPTION_QUERIES_HINGLISH = [
    "kha sakte hain", "le sakte", "safe hai kya",
    "roz kha sakte", "daily okay", "kids ke liye",
    "health ke liye", "diabetes mein"
]

ALL_CONSUMPTION_QUERIES = (CONSUMPTION_QUERIES_EN + CONSUMPTION_QUERIES_HI + 
                           CONSUMPTION_QUERIES_GU + CONSUMPTION_QUERIES_HINGLISH)

# Amount queries (MULTILINGUAL)
AMOUNT_QUERIES = [
    "how much", "how many", "portion", "serving", "quantity",
    "kitna", "kitni", "keto", "ket lu", "amount"
]

# Alternative queries (MULTILINGUAL)
ALTERNATIVE_QUERIES = [
    "instead", "alternative", "substitute", "replace", "better option",
    "uske jagah", "instead", "alternative", "badle mein"
]

# Question words that indicate follow-up (MULTILINGUAL)
FOLLOWUP_QUESTION_WORDS = [
    "what", "why", "how", "when", "should", "can",
    "kya", "kyun", "kaise", "kab", "chahiye",
    "shu", "kevi rite", "kyare"
]


def is_followup_question(message: str, has_new_image: bool = False) -> Tuple[bool, float, str]:
    """
    Detect if a message is a follow-up question about previously analyzed food.
    SUPPORTS: English, Hindi, Gujarati, Hinglish
    
    Args:
        message: User's message text
        has_new_image: Whether user uploaded a new image with this message
        
    Returns:
        Tuple of (is_followup, confidence, reason)
    """
    
    # If new image uploaded, definitely NOT a follow-up
    if has_new_image:
        return (False, 0.0, "New image uploaded")
    
    message_lower = message.lower().strip()
    word_count = len(message.split())
    
    # CRITICAL: Short messages are ALWAYS treated as follow-ups if context exists
    # This catches Hindi/Gujarati questions like "aapko kya chahiye?"
    if word_count <= 10:
        for pronoun in ALL_REFERENCE_PRONOUNS:
            if pronoun in message_lower:
                return (True, 0.95, f"Multilingual pronoun '{pronoun}' detected")
    
    # Consumption/safety queries with pronouns (HIGHEST CONFIDENCE)
    for query in ALL_CONSUMPTION_QUERIES:
        if query in message_lower:
            for pronoun in ALL_REFERENCE_PRONOUNS:
                if pronoun in message_lower:
                    return (True, 0.98, f"Consumption query '{query}' with pronoun")
            # Even without pronoun, consumption queries indicate follow-up
            return (True, 0.85, f"Consumption query '{query}'")
    
    # Amount queries
    for query in AMOUNT_QUERIES:
        if query in message_lower:
            return (True, 0.8, f"Amount query '{query}'")
    
    # Alternative queries
    for query in ALTERNATIVE_QUERIES:
        if query in message_lower:
            return (True, 0.9, f"Alternative query '{query}'")
    
    # Question words in short messages (likely follow-up)
    if word_count <= 8 and message_lower.strip().endswith('?'):
        for qword in FOLLOWUP_QUESTION_WORDS:
            if message_lower.startswith(qword):
                return (True, 0.75, f"Short question starting with '{qword}'")
    
    # Check for explicit NEW product name mention
    # Only if user explicitly mentions a different brand/product, treat as new query
    explicit_products = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', message)
    if explicit_products and len(explicit_products) > 0:
        # Exception: if it's just asking ABOUT a product (not analyzing it)
        asking_about = any(word in message_lower for word in ["about", "ke baare mein", "vishay", "regarding"])
        if not asking_about:
            return (False, 0.0, f"Different product mentioned: {explicit_products[0]}")
    
    # DEFAULT: If message is short and doesn't explicitly introduce new product, treat as follow-up
    if word_count <= 12 and not has_new_image:
        return (True, 0.65, "Short message, likely follow-up")
    
    return (False, 0.0, "Long message without follow-up indicators")


def should_use_food_context(message: str, has_food_context: bool, has_new_image: bool = False) -> bool:
    """
    Simplified check: should we inject food context into the prompt?
    AGGRESSIVE POLICY: Use context whenever it exists, unless explicitly reset
    
    Args:
        message: User's message
        has_food_context: Whether we have food context stored
        has_new_image: Whether user uploaded new image
        
    Returns:
        Boolean indicating whether to use stored food context
    """
    if not has_food_context:
        return False
    
    # If new image uploaded, clear previous context
    if has_new_image:
        return False
    
    is_followup, confidence, reason = is_followup_question(message, has_new_image)
    
    # LOWERED THRESHOLD: Use context if confidence >= 0.6 (was 0.7)
    # This ensures we almost ALWAYS use context when it exists
    use_context = is_followup and confidence >= 0.6
    
    if use_context:
        logger.info(f"USING FOOD CONTEXT: {reason} (confidence: {confidence:.2f})")
    else:
        logger.info(f"NOT using context: {reason} (confidence: {confidence:.2f})")
    
    return use_context