import logging
from typing import List, Optional, Dict, Any
from app.models.ai_output_models import ReasoningV2Result, Finding, Tradeoff, Recommendation
from app.services.gemini_service import gemini_service
from app.tools.ingredient_kb_tool import ingredient_kb_tool
from app.utils.json_guard import extract_and_parse_json, JSONExtractionError
from app.utils.prompts_v2 import REASONING_V2_SYSTEM_PROMPT
from app.core.exceptions import LLMServiceError

logger = logging.getLogger(__name__)

class ReasoningServiceV2:
    def __init__(self):
        self.gemini = gemini_service
    
    async def generate(
        self,
        ingredients: List[str],
        extracted_text: Optional[str] = None,
        intent_profile: Optional[Dict[str, Any]] = None,
        recent_history: Optional[List[Dict[str, str]]] = None
    ) -> ReasoningV2Result:
        """
        Generate structured reasoning analysis
        
        Args:
            ingredients: List of ingredient names
            extracted_text: Optional raw text from image/input
            intent_profile: User intent data
            recent_history: Recent conversation messages
            
        Returns:
            ReasoningV2Result with structured analysis
        """
        try:
            # Build context block
            context_block = self._build_context_block(
                ingredients, extracted_text, intent_profile, recent_history
            )
            
            # Create reasoning prompt
            prompt = self._create_reasoning_prompt(context_block, intent_profile)
            
            # Try to get structured response from Gemini
            try:
                response_text = await self.gemini.generate_text(
                    prompt=prompt,
                    system_instruction=REASONING_V2_SYSTEM_PROMPT,
                    temperature=0.3
                )
                
                # Extract and validate JSON
                json_data = extract_and_parse_json(response_text)
                result = self._parse_reasoning_result(json_data)
                
                logger.info(f"Generated reasoning v2 result with {len(result.findings)} findings")
                return result
                
            except (JSONExtractionError, Exception) as e:
                logger.warning(f"First attempt failed: {e}, retrying with stricter prompt")
                
                # Retry with stricter JSON prompt
                strict_prompt = prompt + "\n\nCRITICAL: Return ONLY valid JSON matching the exact schema. No explanations."
                response_text = await self.gemini.generate_text(
                    prompt=strict_prompt,
                    system_instruction=REASONING_V2_SYSTEM_PROMPT,
                    temperature=0.1
                )
                
                json_data = extract_and_parse_json(response_text)
                result = self._parse_reasoning_result(json_data)
                return result
                
        except Exception as e:
            logger.error(f"Reasoning v2 generation failed: {str(e)}")
            # Return fallback result
            return self._create_fallback_result(ingredients)
    
    def _build_context_block(
        self,
        ingredients: List[str],
        extracted_text: Optional[str],
        intent_profile: Optional[Dict[str, Any]],
        recent_history: Optional[List[Dict[str, str]]]
    ) -> str:
        """Build compact context block for reasoning"""
        context_parts = []
        
        # Ingredients with KB lookup
        if ingredients:
            context_parts.append(f"Ingredients ({len(ingredients)}): {', '.join(ingredients[:10])}")
            if len(ingredients) > 10:
                context_parts.append(f"... and {len(ingredients) - 10} more")
            
            # Add KB knowledge for key ingredients
            kb_matches = ingredient_kb_tool.bulk_lookup(ingredients[:5])  # Top 5 for context
            if kb_matches:
                kb_info = []
                for match in kb_matches:
                    kb_info.append(f"{match['name']}: {match['why_it_matters']} ({match['confidence']} confidence)")
                context_parts.append(f"KB Knowledge: {' | '.join(kb_info)}")
        
        # Intent context
        if intent_profile:
            intent_summary = []
            if intent_profile.get('user_goal'):
                intent_summary.append(f"Goal: {intent_profile['user_goal']}")
            if intent_profile.get('dietary_style'):
                intent_summary.append(f"Diet: {intent_profile['dietary_style']}")
            if intent_profile.get('allergy_risks'):
                intent_summary.append(f"Allergies: {', '.join(intent_profile['allergy_risks'][:3])}")
            if intent_profile.get('audience'):
                intent_summary.append(f"For: {intent_profile['audience']}")
            
            if intent_summary:
                context_parts.append(f"User context: {' | '.join(intent_summary)}")
        
        # Recent conversation
        if recent_history:
            recent_msgs = [f"{msg.get('role', 'user')}: {msg.get('content', '')[:50]}..." 
                          for msg in recent_history[-2:]]
            context_parts.append(f"Recent: {' | '.join(recent_msgs)}")
        
        return "\n".join(context_parts)
    
    def _create_reasoning_prompt(self, context_block: str, intent_profile: Optional[Dict[str, Any]]) -> str:
        """Create the reasoning prompt"""
        
        # Adapt focus based on intent
        focus_areas = []
        if intent_profile:
            if intent_profile.get('user_goal') == 'weight_loss':
                focus_areas.append("caloric density and satiety")
            elif intent_profile.get('user_goal') == 'allergy_safety':
                focus_areas.append("allergen identification and cross-contamination")
            elif intent_profile.get('dietary_style') in ['diabetic']:
                focus_areas.append("blood sugar impact and glycemic considerations")
            
            if intent_profile.get('allergy_risks'):
                focus_areas.append("allergy risk assessment")
        
        focus_instruction = f"Focus especially on: {', '.join(focus_areas)}" if focus_areas else ""
        
        return f"""
Analyze these ingredients with reasoning-driven output:

{context_block}

{focus_instruction}

Provide analysis as JSON matching this exact schema:
{{
  "overall_assessment": "Brief 1-2 sentence summary",
  "findings": [
    {{
      "ingredient": "specific ingredient name",
      "why_it_matters": "why this ingredient is decision-critical",
      "risk_level": "low|medium|high",
      "confidence": "low|medium|high", 
      "evidence_notes": "supporting evidence or null"
    }}
  ],
  "tradeoffs": [
    {{
      "topic": "area of consideration",
      "benefit": "positive aspect",
      "concern": "negative aspect"
    }}
  ],
  "recommendations": [
    {{
      "title": "short recommendation title",
      "action": "specific actionable step"
    }}
  ],
  "uncertainty": ["honest uncertainty note"],
  "narrative": "2-3 sentence final answer for user"
}}

Rules:
- Include only 2-4 most decision-critical findings
- Do not list every ingredient
- Include honest uncertainty where evidence is limited
- Focus on what matters most for decision-making
- Keep narrative concise and actionable
"""
    
    def _parse_reasoning_result(self, json_data: Dict[str, Any]) -> ReasoningV2Result:
        """Parse JSON data into ReasoningV2Result"""
        
        # Parse findings
        findings = []
        for f_data in json_data.get('findings', []):
            findings.append(Finding(
                ingredient=f_data['ingredient'],
                why_it_matters=f_data['why_it_matters'],
                risk_level=f_data['risk_level'],
                confidence=f_data['confidence'],
                evidence_notes=f_data.get('evidence_notes')
            ))
        
        # Parse tradeoffs
        tradeoffs = []
        for t_data in json_data.get('tradeoffs', []):
            tradeoffs.append(Tradeoff(
                topic=t_data['topic'],
                benefit=t_data['benefit'],
                concern=t_data['concern']
            ))
        
        # Parse recommendations
        recommendations = []
        for r_data in json_data.get('recommendations', []):
            recommendations.append(Recommendation(
                title=r_data['title'],
                action=r_data['action']
            ))
        
        return ReasoningV2Result(
            overall_assessment=json_data.get('overall_assessment', ''),
            findings=findings,
            tradeoffs=tradeoffs,
            recommendations=recommendations,
            uncertainty=json_data.get('uncertainty', []),
            narrative=json_data.get('narrative', '')
        )
    
    def _create_fallback_result(self, ingredients: List[str]) -> ReasoningV2Result:
        """Create fallback result when reasoning fails"""
        return ReasoningV2Result(
            overall_assessment="Analysis temporarily unavailable",
            findings=[],
            tradeoffs=[],
            recommendations=[Recommendation(
                title="Review ingredients manually",
                action="Check ingredient labels for any specific dietary concerns"
            )],
            uncertainty=["Analysis system temporarily unavailable"],
            narrative="I'm having trouble analyzing these ingredients right now. Please try again or review the ingredient list manually."
        )

# Singleton instance
reasoning_service_v2 = ReasoningServiceV2()