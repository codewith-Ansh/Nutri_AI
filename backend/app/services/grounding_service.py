import logging
from typing import List, Optional, Dict, Any
from app.services.tool_router import tool_router
from app.services.gemini_service import gemini_service
from app.utils.json_guard import extract_and_parse_json

logger = logging.getLogger(__name__)

class GroundingService:
    def __init__(self):
        self.tool_router = tool_router
        self.gemini = gemini_service
    
    async def generate_grounded_response(
        self,
        ingredients: List[str],
        product_info: Optional[Dict] = None,
        intent_profile: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate grounded response using tools and Gemini reasoning
        
        Args:
            ingredients: List of ingredient names
            product_info: Optional product context (barcode, name, etc.)
            intent_profile: User intent data
            history: Recent conversation history
            
        Returns:
            Dict with narrative, structured_data, and grounded_context
        """
        try:
            # Step 1: Gather grounded context
            grounded_context = await self._build_grounded_context(
                ingredients, product_info, intent_profile
            )
            
            # Step 2: Generate final response with Gemini
            response = await self._generate_final_response(
                grounded_context, intent_profile, history
            )
            
            return {
                "narrative": response.get("narrative", ""),
                "structured_data": response.get("structured_data", {}),
                "grounded_context": grounded_context,
                "uncertainty": response.get("uncertainty", [])
            }
            
        except Exception as e:
            logger.error(f"Grounding service failed: {str(e)}")
            return {
                "narrative": "I'm having trouble analyzing this right now. Please try again.",
                "structured_data": {},
                "grounded_context": {},
                "uncertainty": ["Analysis system temporarily unavailable"]
            }
    
    async def _build_grounded_context(
        self,
        ingredients: List[str],
        product_info: Optional[Dict],
        intent_profile: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build grounded context from tools"""
        context = {
            "kb_matches": [],
            "product_data": None,
            "highlights": []
        }
        
        # Get KB matches for ingredients
        if ingredients:
            kb_result = await tool_router.run_tool(
                "ingredient_kb.bulk_lookup",
                {"ingredients": ingredients[:8]}  # Limit to prevent overload
            )
            
            if kb_result["ok"]:
                context["kb_matches"] = kb_result["data"]
                # Extract key highlights
                for match in kb_result["data"][:3]:  # Top 3 for highlights
                    context["highlights"].append({
                        "ingredient": match["name"],
                        "key_point": match["why_it_matters"],
                        "confidence": match["confidence"]
                    })
        
        # Fetch OpenFoodFacts data if barcode available
        if product_info and product_info.get("barcode"):
            off_result = await tool_router.run_tool(
                "openfoodfacts.fetch_product_by_barcode",
                {"barcode": product_info["barcode"]}
            )
            
            if off_result["ok"] and off_result["data"].get("found"):
                context["product_data"] = {
                    "name": off_result["data"].get("product_name", ""),
                    "brands": off_result["data"].get("brands", ""),
                    "allergens": off_result["data"].get("allergens", ""),
                    "traces": off_result["data"].get("traces", "")
                }
        
        return context
    
    async def _generate_final_response(
        self,
        grounded_context: Dict[str, Any],
        intent_profile: Optional[Dict[str, Any]],
        history: Optional[List[Dict[str, str]]]
    ) -> Dict[str, Any]:
        """Generate final narrative using Gemini with grounded context"""
        
        # Build focused prompt
        prompt = self._create_grounded_prompt(grounded_context, intent_profile, history)
        
        system_prompt = """You are a nutrition AI that provides concise, ranked insights.

CRITICAL RULES:
- Focus on what matters most for decision-making
- Include tradeoffs and uncertainty when relevant
- Do NOT dump entire datasets
- Prioritize actionable insights
- Keep responses concise but complete
- Always include uncertainty where evidence is limited

Return JSON with:
{
  "narrative": "2-3 sentence user-facing response",
  "structured_data": {
    "key_findings": ["top 2-3 decision-critical points"],
    "tradeoffs": ["honest tradeoff if any"],
    "recommendations": ["specific actionable step"]
  },
  "uncertainty": ["honest uncertainty notes"]
}"""
        
        try:
            response_text = await self.gemini.generate_text(
                prompt=prompt,
                system_instruction=system_prompt,
                temperature=0.3
            )
            
            return extract_and_parse_json(response_text)
            
        except Exception as e:
            logger.warning(f"Gemini response parsing failed: {e}")
            return {
                "narrative": "Analysis completed with limited structured output.",
                "structured_data": {"key_findings": ["Analysis available but formatting limited"]},
                "uncertainty": ["Response formatting issue"]
            }
    
    def _create_grounded_prompt(
        self,
        grounded_context: Dict[str, Any],
        intent_profile: Optional[Dict[str, Any]],
        history: Optional[List[Dict[str, str]]]
    ) -> str:
        """Create focused prompt with grounded context"""
        
        prompt_parts = ["Analyze with grounded context:"]
        
        # Add KB highlights
        if grounded_context.get("highlights"):
            prompt_parts.append("\nKB Insights:")
            for highlight in grounded_context["highlights"]:
                prompt_parts.append(f"- {highlight['ingredient']}: {highlight['key_point']} ({highlight['confidence']} confidence)")
        
        # Add product context if available
        if grounded_context.get("product_data"):
            product = grounded_context["product_data"]
            prompt_parts.append(f"\nProduct: {product.get('name', 'Unknown')} by {product.get('brands', 'Unknown')}")
            if product.get("allergens"):
                prompt_parts.append(f"Allergens: {product['allergens']}")
        
        # Add intent focus
        if intent_profile:
            focus_areas = []
            if intent_profile.get("user_goal"):
                focus_areas.append(f"Goal: {intent_profile['user_goal']}")
            if intent_profile.get("allergy_risks"):
                focus_areas.append(f"Allergy concerns: {', '.join(intent_profile['allergy_risks'][:2])}")
            if intent_profile.get("dietary_style"):
                focus_areas.append(f"Diet: {intent_profile['dietary_style']}")
            
            if focus_areas:
                prompt_parts.append(f"\nUser context: {' | '.join(focus_areas)}")
        
        # Add recent context
        if history:
            recent = [f"{msg.get('role', 'user')}: {msg.get('content', '')[:40]}..." 
                     for msg in history[-2:]]
            prompt_parts.append(f"\nRecent: {' | '.join(recent)}")
        
        prompt_parts.append("\nProvide focused analysis prioritizing what matters most for decision-making.")
        
        return "\n".join(prompt_parts)

# Singleton instance
grounding_service = GroundingService()