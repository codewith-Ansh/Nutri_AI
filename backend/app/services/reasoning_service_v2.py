import logging
import json
from typing import List, Optional, Dict, Any
from app.services.gemini_service import gemini_service
from app.utils.prompts_v2 import (
    REASONING_SYSTEM_PROMPT, 
    VISUAL_CONTEXT_PROMPT, 
    build_enhanced_system_prompt,
    MECHANISM_VALIDATION_EXAMPLES,
    CONTEXT_EMPHASIS_GUIDE
)
from app.core.exceptions import LLMServiceError
from app.data.curated_reasoning import get_curated_response

logger = logging.getLogger(__name__)

class EnhancedAIReasoningService:
    """Enhanced AI reasoning engine focused on mechanism-based decision support"""
    
    def __init__(self):
        self.gemini = gemini_service
        self.validation_examples = MECHANISM_VALIDATION_EXAMPLES
        self.context_guide = CONTEXT_EMPHASIS_GUIDE
    
    async def analyze_from_text(
        self,
        user_input: str,
        inferred_context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        language: str = "en"
    ) -> str:
        """Generate enhanced mechanism-based reasoning response from text input"""
        
        # First, check for curated responses (demo foods)
        curated_response = get_curated_response(user_input)
        if curated_response:
            logger.info(f"Using curated response for: {curated_response.get('_food', 'unknown')}")
            return json.dumps(curated_response, ensure_ascii=False)
        
        # Use detected language from context if no explicit language provided
        if language == "en" and inferred_context:
            detected_lang = inferred_context.get('detected_language', 'en')
            if detected_lang in ['hi', 'hinglish', 'gu']:
                language = detected_lang
                logger.info(f"Using detected language: {language}")
        
        # For Gujarati, always use enhanced Gujarati response
        if language == "gu":
            logger.info("Using enhanced Gujarati response for all food questions")
            return await self._generate_enhanced_gujarati_response(user_input, inferred_context)
        
        # Extract context for emphasis adjustment
        context_type = None
        if inferred_context:
            context_type = inferred_context.get('possible_context', None)
            logger.info(f"Applying context emphasis: {context_type}")
        
        # Use enhanced LLM reasoning with mechanism focus
        try:
            # Build enhanced context-aware prompt
            context_info = self._build_context_info(inferred_context)
            history_context = self._build_history_context(conversation_history)
            
            # Build enhanced prompt with mechanism requirements
            prompt = f"""
User question: "{user_input}"
{context_info}
{history_context}

CRITICAL REQUIREMENTS:
1. MECHANISM-LEVEL REASONING: Explain WHY each major claim happens (biological/behavioral cause), not just WHAT happens
2. SPECIFIC UNCERTAINTY: Reference exact variables, avoid generic "varies by person"
3. DEPTH WITHOUT LENGTH: One precise causal explanation over multiple shallow points
4. CONTEXT AWARENESS: {self._get_context_emphasis(context_type)}

Provide mechanism-based decision support following the enhanced reasoning requirements.

Examples of good mechanism reasoning:
- "MSG intensifies umami taste, which can override natural satiety signals and encourage overeating"
- "Palm oil raises LDL cholesterol by altering liver lipid regulation"
- "Sodium sensitivity varies due to genetic and kidney-response differences"

Avoid shallow statements like "contains additives" or "effects vary by person".
"""
            
            # Use enhanced system prompt with language and context awareness
            enhanced_system_prompt = build_enhanced_system_prompt(language, context_type)
            
            response = await self.gemini.generate_text(
                prompt=prompt,
                system_instruction=enhanced_system_prompt,
                temperature=0.3  # Lower temperature for more consistent reasoning
            )
            
            # Validate response quality
            validated_response = self._validate_response_quality(response.strip(), language)
            
            return validated_response
            
        except Exception as e:
            logger.error(f"Enhanced reasoning failed: {str(e)}")
            return self._generate_fallback_response(user_input, language)
    
    def _build_context_info(self, inferred_context: Optional[Dict[str, Any]]) -> str:
        """Build enhanced context information with emphasis guidance"""
        if not inferred_context:
            return ""
        
        likely_goal = inferred_context.get('likely_goal', '')
        possible_context = inferred_context.get('possible_context', '')
        soft_concerns = inferred_context.get('soft_concerns', [])
        hedge_language = inferred_context.get('hedge_language', '')
        confidence_level = inferred_context.get('confidence_level', '')
        
        return f"""
Inferred context for emphasis adjustment:
- Likely goal: {likely_goal}
- Possible context: {possible_context}
- Soft concerns: {', '.join(soft_concerns) if soft_concerns else 'none'}
- Confidence level: {confidence_level}
- Hedge approach: {hedge_language}
"""
    
    def _build_history_context(self, conversation_history: Optional[List[Dict[str, str]]]) -> str:
        """Build conversation history context"""
        if not conversation_history:
            return ""
        
        recent_msgs = conversation_history[-3:]  # Last 3 messages
        return "\nRecent conversation:\n" + "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')[:100]}..."
            for msg in recent_msgs
        ])
    
    def _get_context_emphasis(self, context_type: Optional[str]) -> str:
        """Get context-specific emphasis instructions"""
        if context_type == 'parent':
            return "Focus on child habit formation, taste conditioning, and long-term preference shaping when relevant."
        elif context_type == 'health_conscious':
            return "Emphasize biological mechanisms, cumulative exposure, and long-term health effects when relevant."
        elif context_type == 'quick_decision':
            return "Highlight the single most important risk or benefit first for quick decision-making."
        elif context_type == 'shopping':
            return "Briefly compare with similar alternatives when relevant for shopping decisions."
        else:
            return "Provide balanced mechanism-based reasoning for general decision support."
    
    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response from markdown code blocks"""
        response = response.strip()
        
        # Remove markdown code blocks
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        return response.strip()
    
    def _validate_response_quality(self, response: str, language: str) -> str:
        """Validate response meets enhanced reasoning requirements"""
        try:
            # Clean the response first
            cleaned_response = self._clean_json_response(response)
            
            # Parse JSON to ensure valid structure
            parsed = json.loads(cleaned_response)
            
            # Check required fields
            required_fields = ['ai_insight_title', 'quick_verdict', 'why_this_matters', 'trade_offs', 'uncertainty', 'ai_advice']
            missing_fields = [field for field in required_fields if field not in parsed]
            
            if missing_fields:
                logger.warning(f"Response missing required fields: {missing_fields}")
                return self._fix_missing_fields(parsed, missing_fields, language)
            
            # Validate trade_offs structure
            if 'trade_offs' in parsed and isinstance(parsed['trade_offs'], dict):
                if 'positives' not in parsed['trade_offs'] or 'negatives' not in parsed['trade_offs']:
                    logger.warning("Trade-offs missing positives or negatives")
                    parsed['trade_offs'] = {
                        'positives': parsed['trade_offs'].get('positives', ['Available for analysis']),
                        'negatives': parsed['trade_offs'].get('negatives', ['Limited information available'])
                    }
            
            # Quality checks for mechanism reasoning (basic validation)
            why_matters = parsed.get('why_this_matters', [])
            if isinstance(why_matters, list):
                shallow_indicators = ['contains', 'has', 'includes']
                for matter in why_matters:
                    if isinstance(matter, str) and any(indicator in matter.lower() for indicator in shallow_indicators):
                        if not any(mechanism in matter.lower() for mechanism in ['because', 'which', 'by', 'due to', 'causes', 'leads to']):
                            logger.info("Detected potentially shallow reasoning, but proceeding")
            
            return json.dumps(parsed, ensure_ascii=False)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {str(e)}")
            return self._generate_fallback_response("parsing error", language)
    
    def _fix_missing_fields(self, parsed: dict, missing_fields: List[str], language: str) -> str:
        """Fix response with missing required fields"""
        defaults = {
            'ai_insight_title': 'Food Analysis' if language == 'en' else ('खाद्य विश्लेषण' if language == 'hi' else 'Food Analysis'),
            'quick_verdict': 'Analysis completed' if language == 'en' else ('विश्लेषण पूरा' if language == 'hi' else 'Analysis complete'),
            'why_this_matters': ['Information processed for your decision'],
            'trade_offs': {'positives': ['Available for review'], 'negatives': ['Limited data available']},
            'uncertainty': 'Individual responses may vary',
            'ai_advice': 'Consider your personal health goals when making decisions'
        }
        
        for field in missing_fields:
            parsed[field] = defaults.get(field, 'Not available')
        
        return json.dumps(parsed, ensure_ascii=False)
    
    async def _generate_enhanced_gujarati_response(self, user_input: str, inferred_context: Optional[Dict[str, Any]] = None) -> str:
        """Generate comprehensive Gujarati response for all food-related questions"""
        try:
            # Build enhanced Gujarati prompt with strict language enforcement
            gujarati_prompt = f"""
User question: "{user_input}"

IMPORTANT: You MUST respond ONLY in Gujarati script (ગુજરાતી). Do NOT use English words or script anywhere in your response content.

Provide detailed analysis in Gujarati following this exact JSON structure:
{{
  "ai_insight_title": "Brief title in Gujarati only",
  "quick_verdict": "Detailed summary in Gujarati only - explain what this food is and its overall impact",
  "why_this_matters": [
    "Detailed explanation 1 in Gujarati with biological/nutritional reasoning",
    "Detailed explanation 2 in Gujarati with health mechanisms",
    "Detailed explanation 3 in Gujarati with practical implications"
  ],
  "trade_offs": {{
    "positives": [
      "Positive aspect 1 in Gujarati with detailed explanation",
      "Positive aspect 2 in Gujarati with health benefits",
      "Positive aspect 3 in Gujarati with nutritional value"
    ],
    "negatives": [
      "Concern 1 in Gujarati with detailed explanation",
      "Concern 2 in Gujarati with health implications"
    ]
  }},
  "uncertainty": "Detailed explanation in Gujarati about individual variations and factors",
  "ai_advice": "Comprehensive practical advice in Gujarati for making informed decisions"
}}

Remember: Every single word in the response values must be in Gujarati script. Be comprehensive and educational.
"""
            
            # Use Gemini with very strict Gujarati-only system instruction
            system_instruction = """You are a nutrition expert who responds ONLY in Gujarati script (ગુજરાતી). 
NEVER use English words or Roman script in your response content. 
All content must be in Gujarati script only. 
Provide detailed, educational responses about food and nutrition in Gujarati.
If you don't know the Gujarati word for something, describe it in Gujarati rather than using English."""
            
            response = await self.gemini.generate_text(
                prompt=gujarati_prompt,
                system_instruction=system_instruction,
                temperature=0.2  # Lower temperature for more consistent language adherence
            )
            
            # Clean and validate the response
            cleaned_response = self._clean_json_response(response.strip())
            
            # Try to parse and validate
            try:
                parsed = json.loads(cleaned_response)
                # Ensure all content is in Gujarati by checking for English characters
                if self._contains_english_content(parsed):
                    logger.warning("Generated response contains English, using fallback")
                    return self._generate_gujarati_fallback(user_input)
                return json.dumps(parsed, ensure_ascii=False)
            except json.JSONDecodeError:
                logger.warning("JSON parsing failed, using fallback")
                return self._generate_gujarati_fallback(user_input)
                
        except Exception as e:
            logger.error(f"Enhanced Gujarati response generation failed: {str(e)}")
            return self._generate_gujarati_fallback(user_input)
    
    def _contains_english_content(self, parsed_response: dict) -> bool:
        """Check if response contains English content"""
        import re
        english_pattern = re.compile(r'[a-zA-Z]{3,}')  # 3+ consecutive English letters
        
        def check_value(value):
            if isinstance(value, str):
                return bool(english_pattern.search(value))
            elif isinstance(value, list):
                return any(check_value(item) for item in value)
            elif isinstance(value, dict):
                return any(check_value(v) for v in value.values())
            return False
        
        # Check all content fields (skip JSON keys)
        content_fields = ['ai_insight_title', 'quick_verdict', 'why_this_matters', 'trade_offs', 'uncertainty', 'ai_advice']
        for field in content_fields:
            if field in parsed_response and check_value(parsed_response[field]):
                return True
        return False
    
    def _generate_gujarati_fallback(self, user_input: str) -> str:
        """Generate fallback Gujarati response for any food question"""
        # Create a comprehensive fallback response in Gujarati
        response = {
            "ai_insight_title": "ખોરાક વિશ્લેષણ",
            "quick_verdict": "આ ખોરાક વિશે વિસ્તૃત માહિતી આપવા માટે હું તૈયાર છું. દરેક ખોરાકમાં વિવિધ પોષક તત્વો, વિટામિન્સ અને મિનરલ્સ હોય છે જે આપણા સ્વાસ્થ્ય પર અલગ અલગ અસર કરે છે.",
            "why_this_matters": [
                "દરેક ખોરાકમાં પ્રોટીન, કાર્બોહાઇડ્રેટ, ફેટ, વિટામિન્સ અને મિનરલ્સ હોય છે જે શરીરની વિવિધ જરૂરિયાતો પૂરી કરે છે અને મેટાબોલિઝમ, એનર્જી પ્રોડક્શન અને સેલ્યુલર ફંક્શન્સ માટે જરૂરી છે",
                "ખોરાકની ગુણવત્તા, બનાવવાની પદ્ધતિ અને માત્રા આપણા પાચનતંત્ર, રોગપ્રતિકારક શક્તિ અને લાંબા ગાળાના સ્વાસ્થ્ય પર સીધી અસર કરે છે",
                "સંતુલિત આહાર લેવાથી શરીરમાં હોર્મોન્સનું સંતુલન જાળવાય છે, બ્લડ સુગર કંટ્રોલ રહે છે અને હૃદય, મગજ અને અન્ય અંગોનું સ્વાસ્થ્ય સારું રહે છે"
            ],
            "trade_offs": {
                "positives": [
                    "પોષક તત્વો પ્રાપ્ત થાય છે - શરીરની દૈનિક જરૂરિયાતો પૂરી કરવા માટે વિટામિન્સ, મિનરલ્સ અને એનર્જી મળે છે",
                    "સ્વાદ અને સંતૃપ્તિ - ખોરાક માત્ર પોષણ જ નહીં પરંતુ માનસિક સંતુષ્ટિ અને સાંસ્કૃતિક જોડાણ પણ આપે છે",
                    "સામાજિક અને પારિવારિક બંધન - ખોરાક આપણી સંસ્કૃતિ, પરંપરા અને પારિવારિક મૂલ્યોનો ભાગ છે"
                ],
                "negatives": [
                    "વધુ પડતું સેવન - કોઈ પણ ખોરાકનું અતિસેવન મોટાપા, ડાયાબિટીસ, હૃદયરોગ અને અન્ય સ્વાસ્થ્ય સમસ્યાઓનું કારણ બની શકે છે",
                    "પ્રોસેસિંગ અને એડિટિવ્સ - પેકેજ્ડ અને પ્રોસેસ્ડ ફૂડમાં પ્રિઝર્વેટિવ્સ, આર્ટિફિશિયલ કલર્સ અને ફ્લેવર્સ હોઈ શકે છે"
                ]
            },
            "uncertainty": "દરેક વ્યક્તિની ઉંમર, વજન, શારીરિક પ્રવૃત્તિ, આનુવંશિકતા, અને હાલની સ્વાસ્થ્યની સ્થિતિ અલગ હોવાથી ખોરાકની અસર અલગ અલગ હોઈ શકે છે. એલર્જી, ડાયાબિટીસ, હાઈ બીપી જેવી સ્થિતિઓ હોય તો વિશેષ સાવધાની જરૂરી છે.",
            "ai_advice": "સંયમ સાથે વૈવિધ્યપૂર્ણ આહાર લો, ઘરે બનાવેલા તાજા ખોરાકને પ્રાધાન્ય આપો, પૂરતું પાણી પીવો, નિયમિત વ્યાયામ કરો અને જો કોઈ ખાસ સ્વાસ્થ્ય સમસ્યા હોય તો ડૉક્ટર અથવા પોષણ વિશેષજ્ઞની સલાહ લો."
        }
        
        return json.dumps(response, ensure_ascii=False)
    
    def _generate_fallback_response(self, user_input: str, language: str) -> str:
        """Generate structured fallback response when main reasoning fails"""
        # Try curated response first
        curated_fallback = get_curated_response(user_input)
        if curated_fallback:
            logger.info("Using curated fallback due to reasoning error")
            return json.dumps(curated_fallback, ensure_ascii=False)
        
        # Generate language-appropriate fallback
        if language == 'hi':
            error_response = {
                "ai_insight_title": "अस्थायी सेवा समस्या",
                "quick_verdict": "मुझे अभी AI सेवा के साथ कुछ तकनीकी कठिनाइयाँ हो रही हैं।",
                "why_this_matters": [
                    "AI तर्क सेवा अस्थायी रूप से अनुपलब्ध है",
                    "आप सामान्य खाद्य पदार्थों के बारे में पूछ सकते हैं या थोड़ी देर बाद कोशिश कर सकते हैं"
                ],
                "trade_offs": {
                    "positives": ["सेवा में बाधा अस्थायी है"],
                    "negatives": ["इस समय विस्तृत विश्लेषण प्रदान नहीं कर सकता"]
                },
                "uncertainty": "सेवा जल्द ही बहाल हो जानी चाहिए। सामान्य भारतीय खाद्य पदार्थों के लिए, मैं अभी भी मदद कर सकता हूँ।",
                "ai_advice": "कृपया अपना प्रश्न फिर से पूछें, या समोसा, वड़ापाव, या पारले जी जैसे विशिष्ट खाद्य पदार्थों के बारे में पूछें।"
            }
        elif language == 'hinglish':
            error_response = {
                "ai_insight_title": "Temporary Service Issue",
                "quick_verdict": "Mujhe abhi AI service ke saath kuch technical difficulties ho rahi hain.",
                "why_this_matters": [
                    "AI reasoning service temporarily unavailable hai",
                    "Aap common foods ke baare mein pooch sakte hain ya thodi der baad try kar sakte hain"
                ],
                "trade_offs": {
                    "positives": ["Service interruption temporary hai"],
                    "negatives": ["Abhi detailed analysis provide nahi kar sakta"]
                },
                "uncertainty": "Service jaldi restore ho jaani chahiye. Common Indian foods ke liye, main abhi bhi help kar sakta hun.",
                "ai_advice": "Please apna question phir se try kariye, ya specific foods jaise samosa, vadapav, ya Parle G ke baare mein puchiye."
            }
        else:
            error_response = {
                "ai_insight_title": "Temporary Service Issue",
                "quick_verdict": "I'm having some technical difficulties with the AI service right now.",
                "why_this_matters": [
                    "The AI reasoning service is temporarily unavailable",
                    "You can try asking about common foods or try again in a moment"
                ],
                "trade_offs": {
                    "positives": ["Service interruption is temporary"],
                    "negatives": ["Cannot provide detailed analysis at the moment"]
                },
                "uncertainty": "Service should be restored shortly. For common Indian foods, I may still be able to help.",
                "ai_advice": "Please try your question again, or ask about specific foods like samosa, vadapav, or Parle G."
            }
        
        error_response["_source"] = "enhanced_fallback"
        return json.dumps(error_response, ensure_ascii=False)
    
    async def analyze_from_image(
        self,
        image_data: bytes,
        inferred_context: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> str:
        """Generate enhanced mechanism-based response from image with product recognition"""
        try:
            logger.info("Starting enhanced image analysis with Gemini Vision")
            
            # Use Gemini Vision to analyze the image
            import google.generativeai as genai
            from app.config import settings
            from PIL import Image
            import io
            
            # Configure Gemini with vision model
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Image loaded: {image.size} pixels")
            
            # Extract context for emphasis adjustment
            context_type = None
            if inferred_context:
                context_type = inferred_context.get('possible_context', None)
            
            # Use enhanced structured prompt for consistent JSON output with mechanism focus
            enhanced_prompt = VISUAL_CONTEXT_PROMPT
            
            # Add context-specific emphasis
            if context_type:
                enhanced_prompt += f"\n\nCONTEXT EMPHASIS: {self._get_context_emphasis(context_type)}"
            
            # Add mechanism requirements
            enhanced_prompt += """

CRITICAL REASONING REQUIREMENTS:
1. MECHANISM-LEVEL REASONING: Explain WHY ingredients matter (biological/behavioral cause), not just WHAT they are
2. SPECIFIC UNCERTAINTY: Reference exact variables, avoid generic "varies by person"
3. DEPTH WITHOUT LENGTH: One precise causal explanation over multiple shallow points

Examples of good mechanism reasoning:
- "High sodium triggers water retention by disrupting kidney filtration balance"
- "Trans fats interfere with cell membrane function, increasing inflammation markers"
- "Artificial sweeteners may disrupt gut bacteria balance, affecting glucose metabolism"

Avoid shallow statements like "contains preservatives" or "has artificial ingredients".
"""
            
            # Add language-specific instructions
            if language == "hi":
                enhanced_prompt += "\n\nCRITICAL LANGUAGE REQUIREMENT: You MUST respond in Hindi (Devanagari script). Translate ALL content to Hindi while keeping JSON field names in English. Preserve all mechanism-level reasoning depth."
            elif language == "hinglish":
                enhanced_prompt += "\n\nCRITICAL LANGUAGE REQUIREMENT: You MUST respond in Hinglish (Hindi written in English script). Translate ALL content to Hinglish while keeping JSON field names in English. Preserve all mechanism-level reasoning depth."
            else:
                enhanced_prompt += "\n\nRespond in English with full mechanism-based reasoning."
            
            # Generate response with image
            logger.info("Calling Gemini Vision API with enhanced reasoning")
            response = model.generate_content([enhanced_prompt, image])
            
            result_text = response.text.strip()
            # Clean md code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            logger.info("Enhanced Gemini Vision analysis completed successfully")
            
            # Validate response quality
            validated_response = self._validate_response_quality(result_text, language)
            
            return validated_response
            
        except Exception as e:
            logger.error(f"Enhanced Gemini Vision analysis failed: {str(e)}")
            # Try OCR fallback with enhanced reasoning
            return await self._enhanced_fallback_ocr_analysis(image_data, language)
    
    async def _enhanced_fallback_ocr_analysis(self, image_data: bytes, language: str) -> str:
        """Enhanced OCR-based analysis when vision API fails"""
        try:
            # Save image temporarily for OCR
            import tempfile
            import os
            from app.services.image_services import image_service
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(image_data)
                tmp_path = tmp_file.name
            
            try:
                # Extract text using OCR
                extracted_text = image_service.extract_text_ocr(tmp_path)
                
                if extracted_text:
                    # Enhanced analysis with mechanism focus
                    analysis_prompt = f"""
I extracted this text from a food product image:

{extracted_text}

CRITICAL REQUIREMENTS:
1. MECHANISM-LEVEL REASONING: Explain WHY ingredients matter (biological/behavioral cause)
2. SPECIFIC UNCERTAINTY: Reference exact variables, not generic "varies by person"
3. DEPTH WITHOUT LENGTH: One precise causal explanation over multiple shallow points

Provide enhanced mechanism-based analysis following the structured JSON format.

Examples of good reasoning:
- "Sodium benzoate preserves freshness but may trigger hyperactivity in sensitive children by affecting neurotransmitter balance"
- "High fructose corn syrup bypasses normal glucose regulation, leading to faster fat storage"

Avoid shallow statements like "contains preservatives" or "has artificial ingredients".
"""
                    
                    # Use enhanced system prompt
                    enhanced_system_prompt = build_enhanced_system_prompt(language)
                    
                    response = await self.gemini.generate_text(
                        prompt=analysis_prompt,
                        system_instruction=enhanced_system_prompt,
                        temperature=0.3
                    )
                    
                    return self._validate_response_quality(response.strip(), language)
                else:
                    return self._generate_fallback_response("OCR extraction failed", language)
            
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
        except Exception as e:
            logger.error(f"Enhanced fallback OCR analysis failed: {str(e)}")
            return self._generate_fallback_response("Image analysis failed", language)
    
    def _extract_barcode_from_response(self, response_text: str) -> str:
        """Extract barcode number from AI response"""
        import re
        # Look for patterns like barcode numbers (8-13 digits)
        patterns = [
            r'\b\d{13}\b',  # 13-digit EAN
            r'\b\d{12}\b',  # 12-digit UPC
            r'\b\d{8}\b',   # 8-digit EAN-8
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response_text)
            if matches:
                return matches[0]
        return None
    
    async def _get_product_from_barcode(self, barcode: str) -> str:
        """Get product information from OpenFoodFacts using barcode"""
        try:
            import aiohttp
            
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == 1:  # Product found
                            product = data.get('product', {})
                            
                            name = product.get('product_name', 'Unknown')
                            brand = product.get('brands', 'Unknown')
                            ingredients = product.get('ingredients_text', 'Not available')
                            
                            return f"**{name}** by {brand}\nIngredients: {ingredients[:200]}{'...' if len(ingredients) > 200 else ''}"
                        
            return None
        except Exception as e:
            logger.error(f"OpenFoodFacts lookup failed: {str(e)}")
            return None
    
    def _should_hedge_response(self, confidence_level: str) -> bool:
        """Determine if response should include more hedge language"""
        return confidence_level in ['uncertain', 'somewhat_sure']
    
    def _adapt_tone_for_context(self, context: str) -> str:
        """Adapt communication tone based on inferred context"""
        if context == 'parent':
            return "When choosing for kids, people often focus on..."
        elif context == 'health_conscious':
            return "If health is a priority, you might want to consider..."
        elif context == 'shopping':
            return "When you're deciding between options..."
        else:
            return "People usually think about..."

# Singleton instance with enhanced capabilities
enhanced_ai_reasoning = EnhancedAIReasoningService()

# Backward compatibility alias
ai_native_reasoning = enhanced_ai_reasoning