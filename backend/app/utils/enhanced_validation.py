"""
Enhanced AI Reasoning Validation Utility
Ensures responses meet the production-ready mechanism-based reasoning requirements
"""

import json
import re
import logging
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)

class EnhancedReasoningValidator:
    """Validates AI responses against enhanced reasoning requirements"""
    
    def __init__(self):
        # Mechanism indicators - words that suggest causal explanations
        self.mechanism_indicators = [
            'because', 'which', 'by', 'due to', 'causes', 'leads to', 'triggers',
            'disrupts', 'interferes', 'affects', 'alters', 'bypasses', 'overrides',
            'stimulates', 'inhibits', 'blocks', 'activates', 'suppresses'
        ]
        
        # Shallow statement indicators - words that suggest surface-level descriptions
        self.shallow_indicators = [
            'contains', 'has', 'includes', 'is made of', 'consists of'
        ]
        
        # Specific uncertainty indicators - words that suggest precise variables
        self.specific_uncertainty_indicators = [
            'varies', 'depends on', 'differs', 'ranges', 'individual', 'genetic',
            'enzyme', 'metabolism', 'sensitivity', 'tolerance', 'response'
        ]
        
        # Generic uncertainty phrases to avoid
        self.generic_uncertainty_phrases = [
            'effects vary by individual',
            'results may differ',
            'varies by person',
            'individual results vary',
            'may vary'
        ]
    
    def validate_response(self, response: str, language: str = "en") -> Dict[str, Any]:
        """
        Validate response against enhanced reasoning requirements
        
        Returns:
            Dict with validation results and suggestions
        """
        try:
            # Parse JSON response
            parsed = json.loads(response)
            
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'suggestions': [],
                'quality_score': 0,
                'mechanism_score': 0,
                'uncertainty_score': 0,
                'structure_score': 0
            }
            
            # Validate JSON structure
            structure_validation = self._validate_structure(parsed)
            validation_result.update(structure_validation)
            
            # Validate mechanism-level reasoning
            mechanism_validation = self._validate_mechanisms(parsed, language)
            validation_result['mechanism_score'] = mechanism_validation['score']
            validation_result['warnings'].extend(mechanism_validation['warnings'])
            validation_result['suggestions'].extend(mechanism_validation['suggestions'])
            
            # Validate uncertainty specificity
            uncertainty_validation = self._validate_uncertainty(parsed, language)
            validation_result['uncertainty_score'] = uncertainty_validation['score']
            validation_result['warnings'].extend(uncertainty_validation['warnings'])
            validation_result['suggestions'].extend(uncertainty_validation['suggestions'])
            
            # Calculate overall quality score
            validation_result['quality_score'] = (
                validation_result['structure_score'] * 0.3 +
                validation_result['mechanism_score'] * 0.4 +
                validation_result['uncertainty_score'] * 0.3
            )
            
            # Determine if response meets minimum quality threshold
            if validation_result['quality_score'] < 0.7:
                validation_result['is_valid'] = False
                validation_result['errors'].append("Response does not meet minimum quality threshold for enhanced reasoning")
            
            return validation_result
            
        except json.JSONDecodeError as e:
            return {
                'is_valid': False,
                'errors': [f"Invalid JSON structure: {str(e)}"],
                'warnings': [],
                'suggestions': ['Ensure response is valid JSON'],
                'quality_score': 0,
                'mechanism_score': 0,
                'uncertainty_score': 0,
                'structure_score': 0
            }
    
    def _validate_structure(self, parsed: Dict) -> Dict[str, Any]:
        """Validate JSON structure meets requirements"""
        required_fields = [
            'ai_insight_title', 'quick_verdict', 'why_this_matters', 
            'trade_offs', 'uncertainty', 'ai_advice'
        ]
        
        errors = []
        warnings = []
        score = 1.0
        
        # Check required fields
        missing_fields = [field for field in required_fields if field not in parsed]
        if missing_fields:
            errors.append(f"Missing required fields: {missing_fields}")
            score -= 0.2 * len(missing_fields)
        
        # Validate trade_offs structure
        if 'trade_offs' in parsed:
            if not isinstance(parsed['trade_offs'], dict):
                errors.append("trade_offs must be a dictionary")
                score -= 0.2
            else:
                if 'positives' not in parsed['trade_offs']:
                    errors.append("trade_offs missing 'positives' field")
                    score -= 0.1
                if 'negatives' not in parsed['trade_offs']:
                    errors.append("trade_offs missing 'negatives' field")
                    score -= 0.1
        
        # Check for forbidden additional fields
        allowed_fields = required_fields + ['barcode', '_source', '_food']
        extra_fields = [field for field in parsed.keys() if field not in allowed_fields]
        if extra_fields:
            warnings.append(f"Response contains additional fields not in specification: {extra_fields}")
        
        return {
            'structure_score': max(0, score),
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_mechanisms(self, parsed: Dict, language: str) -> Dict[str, Any]:
        """Validate mechanism-level reasoning quality"""
        warnings = []
        suggestions = []
        score = 0.0
        total_checks = 0
        
        # Check why_this_matters for mechanism explanations
        why_matters = parsed.get('why_this_matters', [])
        if isinstance(why_matters, list):
            for matter in why_matters:
                if isinstance(matter, str):
                    total_checks += 1
                    mechanism_score = self._score_mechanism_quality(matter, language)
                    score += mechanism_score
                    
                    if mechanism_score < 0.5:
                        suggestions.append(f"Improve mechanism explanation: '{matter[:50]}...' - explain WHY it happens")
        
        # Check trade_offs for mechanism explanations
        trade_offs = parsed.get('trade_offs', {})
        if isinstance(trade_offs, dict):
            for category in ['positives', 'negatives']:
                items = trade_offs.get(category, [])
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, str):
                            total_checks += 1
                            mechanism_score = self._score_mechanism_quality(item, language)
                            score += mechanism_score
                            
                            if mechanism_score < 0.5:
                                suggestions.append(f"Add mechanism to {category}: '{item[:30]}...' - explain the biological/behavioral cause")
        
        # Calculate average score
        final_score = score / total_checks if total_checks > 0 else 0
        
        if final_score < 0.6:
            warnings.append("Response lacks sufficient mechanism-level reasoning")
        
        return {
            'score': final_score,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    def _score_mechanism_quality(self, text: str, language: str) -> float:
        """Score the mechanism quality of a text snippet"""
        text_lower = text.lower()
        score = 0.0
        
        # Check for mechanism indicators
        mechanism_count = sum(1 for indicator in self.mechanism_indicators if indicator in text_lower)
        if mechanism_count > 0:
            score += 0.6  # Base score for having mechanism language
        
        # Penalty for shallow indicators without mechanisms
        shallow_count = sum(1 for indicator in self.shallow_indicators if indicator in text_lower)
        if shallow_count > 0 and mechanism_count == 0:
            score -= 0.3  # Penalty for shallow statements
        
        # Bonus for specific biological/behavioral terms
        biological_terms = [
            'cholesterol', 'glucose', 'insulin', 'metabolism', 'enzyme', 'hormone',
            'neurotransmitter', 'inflammation', 'oxidation', 'absorption', 'digestion',
            'liver', 'kidney', 'brain', 'gut', 'bacteria', 'microbiome'
        ]
        
        behavioral_terms = [
            'satiety', 'hunger', 'craving', 'habit', 'preference', 'conditioning',
            'overeating', 'appetite', 'satisfaction', 'reward'
        ]
        
        bio_count = sum(1 for term in biological_terms if term in text_lower)
        behav_count = sum(1 for term in behavioral_terms if term in text_lower)
        
        if bio_count > 0 or behav_count > 0:
            score += 0.3  # Bonus for specific scientific terms
        
        # Check for causal language patterns
        causal_patterns = [
            r'\b\w+\s+(causes?|leads? to|triggers?|results? in)\s+\w+',
            r'\bby\s+\w+ing\b',
            r'\bwhich\s+\w+s?\b',
            r'\bdue to\s+\w+'
        ]
        
        for pattern in causal_patterns:
            if re.search(pattern, text_lower):
                score += 0.1  # Small bonus for causal language patterns
        
        return min(1.0, score)  # Cap at 1.0
    
    def _validate_uncertainty(self, parsed: Dict, language: str) -> Dict[str, Any]:
        """Validate uncertainty specificity"""
        warnings = []
        suggestions = []
        score = 0.0
        
        uncertainty_text = parsed.get('uncertainty', '')
        if isinstance(uncertainty_text, str):
            uncertainty_lower = uncertainty_text.lower()
            
            # Check for generic uncertainty phrases (negative score)
            generic_found = any(phrase in uncertainty_lower for phrase in self.generic_uncertainty_phrases)
            if generic_found:
                score -= 0.5
                warnings.append("Uncertainty uses generic language instead of specific variables")
                suggestions.append("Replace generic uncertainty with specific variables (e.g., 'genetic differences', 'enzyme activity')")
            
            # Check for specific uncertainty indicators (positive score)
            specific_count = sum(1 for indicator in self.specific_uncertainty_indicators if indicator in uncertainty_lower)
            if specific_count > 0:
                score += 0.7
            
            # Check for quantitative uncertainty (bonus)
            quantitative_patterns = [
                r'\d+%', r'\d+-fold', r'\d+ times', r'\d+x', r'up to \d+',
                r'between \d+ and \d+', r'varies \d+'
            ]
            
            for pattern in quantitative_patterns:
                if re.search(pattern, uncertainty_lower):
                    score += 0.3
                    break
            
            # Check for biological specificity
            biological_uncertainty_terms = [
                'genetic', 'enzyme', 'metabolism', 'liver', 'kidney', 'gut',
                'microbiome', 'sensitivity', 'tolerance', 'response'
            ]
            
            bio_uncertainty_count = sum(1 for term in biological_uncertainty_terms if term in uncertainty_lower)
            if bio_uncertainty_count > 0:
                score += 0.2
        
        # Normalize score
        final_score = max(0, min(1.0, score))
        
        if final_score < 0.5:
            warnings.append("Uncertainty lacks specificity - should reference exact variables")
        
        return {
            'score': final_score,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    def generate_improvement_suggestions(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate specific improvement suggestions based on validation results"""
        suggestions = []
        
        if validation_result['mechanism_score'] < 0.6:
            suggestions.append("Add more mechanism-level explanations that explain WHY things happen, not just WHAT happens")
            suggestions.append("Use causal language like 'because', 'which leads to', 'by disrupting', 'due to'")
            suggestions.append("Include specific biological or behavioral processes")
        
        if validation_result['uncertainty_score'] < 0.5:
            suggestions.append("Replace generic uncertainty with specific variables")
            suggestions.append("Reference exact factors like 'genetic differences', 'enzyme activity', 'sensitivity levels'")
            suggestions.append("Include quantitative ranges when possible (e.g., 'varies 40-fold')")
        
        if validation_result['structure_score'] < 1.0:
            suggestions.append("Ensure all required JSON fields are present")
            suggestions.append("Verify trade_offs has both 'positives' and 'negatives' arrays")
        
        return suggestions + validation_result.get('suggestions', [])

# Singleton instance
enhanced_reasoning_validator = EnhancedReasoningValidator()