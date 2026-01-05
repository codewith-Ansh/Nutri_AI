from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.request_models import ChatRequest
from app.services.gemini_service import gemini_service
from app.services.reasoning_service_v2 import enhanced_ai_reasoning
from app.services.intent_service import ai_native_intent
from app.utils.session_manager import session_manager
from app.utils.followup_detector import should_use_food_context  # NEW
from app.core.exceptions import NutriAIException
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

def build_rolling_conversation_summary(history: List[dict]) -> str:
    """Build a rolling summary from the last 2 assistant messages for topic grounding"""
    try:
        # Get last 2 assistant messages
        assistant_messages = [msg for msg in history if msg.get('role') == 'assistant'][-2:]
        
        if not assistant_messages:
            return ""
        
        # Extract product name and key points from last responses
        product_name = "unknown product"
        key_points = []
        
        for msg in assistant_messages:
            content = msg.get('content', '')
            try:
                # Try to parse JSON response
                parsed = json.loads(content)
                
                # Extract product name from ai_insight_title
                title = parsed.get('ai_insight_title', '')
                if title and product_name == "unknown product":
                    product_name = title
                
                # Extract key concerns/points from trade_offs
                trade_offs = parsed.get('trade_offs', {})
                negatives = trade_offs.get('negatives', [])
                positives = trade_offs.get('positives', [])
                
                # Get top 2 concerns and 1 positive
                key_points.extend(negatives[:2])
                if positives:
                    key_points.append(positives[0])
                    
            except (json.JSONDecodeError, TypeError):
                # If not JSON, skip
                continue
        
        if product_name == "unknown product" and not key_points:
            return ""
        
        # Build summary string
        summary = f"""
Recent Conversation Summary:
- Product being discussed: {product_name}
- Key points already explained: {', '.join(key_points[:3]) if key_points else 'general food analysis'}
- User focus so far: health impact, consumption suitability
"""
        return summary.strip()
        
    except Exception as e:
        logger.error(f"Failed to build conversation summary: {str(e)}")
        return ""

@router.options("/chat/stream")
async def chat_stream_options():
    """Handle CORS preflight for chat stream"""
    return {"message": "OK"}

@router.post("/chat/stream")
async def chat_stream_ai_native(request: ChatRequest):
    """AI-native streaming chat - reasoning-driven, context-aware"""
    try:
        # Get or create session
        session_id = request.session_id or session_manager.create_session()
        
        # Get conversation history and context
        history = session_manager.get_conversation_history(session_id)
        existing_context = session_manager.get_context(session_id)
        
        # Store user message
        session_manager.add_message(session_id, "user", request.message)
        
        # NEW: Check if this is a follow-up question about previous food
        food_context = None
        stored_food_context = session_manager.get_food_context(session_id)
        has_new_image = hasattr(request, 'image') and request.image is not None
        
        # Clear food context if new image is uploaded
        if has_new_image:
            session_manager.clear_food_context(session_id)
            logger.info("Cleared food context due to new image in chat")
            stored_food_context = None
        
        if should_use_food_context(request.message, stored_food_context is not None, has_new_image):
            food_context = stored_food_context
            logger.info(f"Follow-up detected! Using food context: {food_context.get('product_name', 'unknown')}")
        
        # Softly infer context for this message
        inferred_context = await ai_native_intent.soft_infer_context(
            session_id=session_id,
            message=request.message,
            recent_history=history[-3:] if history else None,
            existing_context=existing_context
        )
        
        # NEW: Build rolling conversation summary for topic grounding
        conversation_summary = build_rolling_conversation_summary(history)
        if conversation_summary:
            logger.info(f"Built conversation summary for follow-up grounding")
        
        # Get UI-selected language (strict priority over auto-detection)
        selected_language = request.language or "en"
        logger.info(f"UI-selected language: {selected_language} (strict priority mode)")
        
        # Generate enhanced AI reasoning response with mechanism focus
        # NEW: Pass food_context, conversation_summary, and strict selected_language
        reasoning_response = await enhanced_ai_reasoning.analyze_from_text(
            user_input=request.message,
            inferred_context=inferred_context,
            conversation_history=history[-3:] if history else None,
            language=selected_language,  # UI-selected language (strict priority)
            food_context=food_context,  # Food context if follow-up
            conversation_summary=conversation_summary  # NEW: Rolling summary for topic grounding
        )
        
        # Update session context
        session_manager.update_context(session_id, inferred_context)
        session_manager.add_message(session_id, "assistant", reasoning_response)
        
        async def generate_stream():
            # Stream the response naturally - no technical chunking
            words = reasoning_response.split()
            current_chunk = ""
            
            for i, word in enumerate(words):
                current_chunk += word + " "
                
                # Send chunks of 3-5 words for natural flow
                if (i + 1) % 4 == 0 or i == len(words) - 1:
                    data = {
                        "choices": [{
                            "delta": {
                                "content": current_chunk
                            }
                        }]
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                    current_chunk = ""
            
            # Send completion signal
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"AI-native chat stream error: {str(e)}")
        
        # Natural error response
        async def error_stream():
            error_msg = "I'm having trouble right now. Could you try asking again?"
            data = {
                "choices": [{
                    "delta": {
                        "content": error_msg
                    }
                }]
            }
            yield f"data: {json.dumps(data)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            error_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )