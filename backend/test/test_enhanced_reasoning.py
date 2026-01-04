"""
Enhanced AI Reasoning Engine Test Suite
Tests the production-ready mechanism-based reasoning capabilities
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from app.services.reasoning_service_v2 import enhanced_ai_reasoning
from app.utils.enhanced_validation import enhanced_reasoning_validator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedReasoningTestSuite:
    """Comprehensive test suite for enhanced AI reasoning engine"""
    
    def __init__(self):
        self.test_cases = self._load_test_cases()
        self.results = []
    
    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """Load test cases covering various scenarios"""
        return [
            {
                "name": "MSG Mechanism Test",
                "input": "Is MSG bad for health?",
                "language": "en",
                "context": {"possible_context": "health_conscious"},
                "expected_mechanisms": ["umami", "satiety", "signals", "override"],
                "expected_uncertainty_specifics": ["sensitivity", "individual", "genetic"]
            },
            {
                "name": "Palm Oil Mechanism Test",
                "input": "What about palm oil in cookies?",
                "language": "en", 
                "context": {"possible_context": "parent"},
                "expected_mechanisms": ["saturated fat", "cholesterol", "liver", "regulation"],
                "expected_uncertainty_specifics": ["metabolism", "genetic", "response"]
            },
            {
                "name": "Hindi Language Preservation Test",
                "input": "क्या चीनी हानिकारक है?",
                "language": "hi",
                "context": {"possible_context": "health_conscious"},
                "expected_mechanisms": ["glucose", "insulin", "metabolism"],
                "expected_uncertainty_specifics": ["sensitivity", "diabetes", "individual"]
            },
            {
                "name": "Hinglish Language Preservation Test", 
                "input": "Artificial colors safe hain kya?",
                "language": "hinglish",
                "context": {"possible_context": "parent"},
                "expected_mechanisms": ["hyperactivity", "neurotransmitter", "children"],
                "expected_uncertainty_specifics": ["sensitive", "individual", "response"]
            },
            {
                "name": "Context Emphasis - Parent",
                "input": "Should I give my kid this snack?",
                "language": "en",
                "context": {"possible_context": "parent"},
                "expected_emphasis": ["habit", "preference", "conditioning", "long-term"],
                "expected_uncertainty_specifics": ["children", "development", "individual"]
            },
            {
                "name": "Context Emphasis - Shopping",
                "input": "Which cereal is better?",
                "language": "en", 
                "context": {"possible_context": "shopping"},
                "expected_emphasis": ["compared", "alternative", "similar"],
                "expected_uncertainty_specifics": ["preference", "goals", "individual"]
            },
            {
                "name": "Shallow Statement Detection",
                "input": "What's in this processed food?",
                "language": "en",
                "context": {"possible_context": "health_conscious"},
                "avoid_shallow": ["contains", "has", "includes"],
                "require_mechanisms": True
            }
        ]
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test cases and return comprehensive results"""
        logger.info("Starting Enhanced AI Reasoning Engine Test Suite")
        
        overall_results = {
            "total_tests": len(self.test_cases),
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "test_results": [],
            "summary": {}
        }
        
        for i, test_case in enumerate(self.test_cases, 1):
            logger.info(f"Running test {i}/{len(self.test_cases)}: {test_case['name']}")
            
            try:
                result = await self._run_single_test(test_case)
                overall_results["test_results"].append(result)
                
                if result["passed"]:
                    overall_results["passed"] += 1
                else:
                    overall_results["failed"] += 1
                
                if result["warnings"]:
                    overall_results["warnings"] += len(result["warnings"])
                    
            except Exception as e:
                logger.error(f"Test {test_case['name']} failed with exception: {str(e)}")
                overall_results["test_results"].append({
                    "test_name": test_case["name"],
                    "passed": False,
                    "error": str(e),
                    "warnings": [],
                    "suggestions": []
                })
                overall_results["failed"] += 1
        
        # Generate summary
        overall_results["summary"] = self._generate_summary(overall_results)
        
        logger.info(f"Test Suite Complete: {overall_results['passed']}/{overall_results['total_tests']} passed")
        return overall_results
    
    async def _run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case"""
        # Generate response using enhanced reasoning
        response = await enhanced_ai_reasoning.analyze_from_text(
            user_input=test_case["input"],
            inferred_context=test_case.get("context"),
            language=test_case["language"]
        )
        
        # Validate response
        validation_result = enhanced_reasoning_validator.validate_response(
            response, test_case["language"]
        )
        
        # Parse response for content analysis
        try:
            parsed_response = json.loads(response)
        except json.JSONDecodeError:
            return {
                "test_name": test_case["name"],
                "passed": False,
                "error": "Invalid JSON response",
                "validation_result": validation_result,
                "warnings": [],
                "suggestions": []
            }
        
        # Run specific test validations
        test_result = {
            "test_name": test_case["name"],
            "passed": True,
            "warnings": [],
            "suggestions": [],
            "validation_result": validation_result,
            "response": response
        }
        
        # Check mechanism requirements
        if "expected_mechanisms" in test_case:
            mechanism_check = self._check_mechanisms(parsed_response, test_case["expected_mechanisms"])
            if not mechanism_check["passed"]:
                test_result["passed"] = False
                test_result["warnings"].extend(mechanism_check["warnings"])
        
        # Check uncertainty specificity
        if "expected_uncertainty_specifics" in test_case:
            uncertainty_check = self._check_uncertainty_specifics(parsed_response, test_case["expected_uncertainty_specifics"])
            if not uncertainty_check["passed"]:
                test_result["warnings"].extend(uncertainty_check["warnings"])
        
        # Check context emphasis
        if "expected_emphasis" in test_case:
            emphasis_check = self._check_context_emphasis(parsed_response, test_case["expected_emphasis"])
            if not emphasis_check["passed"]:
                test_result["warnings"].extend(emphasis_check["warnings"])
        
        # Check for shallow statements
        if test_case.get("avoid_shallow"):
            shallow_check = self._check_shallow_avoidance(parsed_response, test_case["avoid_shallow"])
            if not shallow_check["passed"]:
                test_result["passed"] = False
                test_result["warnings"].extend(shallow_check["warnings"])
        
        # Check language preservation
        if test_case["language"] in ["hi", "hinglish"]:
            language_check = self._check_language_preservation(parsed_response, test_case["language"])
            if not language_check["passed"]:
                test_result["warnings"].extend(language_check["warnings"])
        
        # Overall validation check
        if not validation_result["is_valid"]:
            test_result["passed"] = False
            test_result["warnings"].extend(validation_result["errors"])
        
        return test_result
    
    def _check_mechanisms(self, response: Dict, expected_mechanisms: List[str]) -> Dict[str, Any]:
        """Check if response contains expected mechanism explanations"""
        response_text = json.dumps(response).lower()
        found_mechanisms = [mech for mech in expected_mechanisms if mech.lower() in response_text]
        
        return {
            "passed": len(found_mechanisms) >= len(expected_mechanisms) * 0.6,  # 60% threshold
            "warnings": [] if len(found_mechanisms) >= len(expected_mechanisms) * 0.6 else 
                       [f"Missing expected mechanisms: {set(expected_mechanisms) - set(found_mechanisms)}"]
        }
    
    def _check_uncertainty_specifics(self, response: Dict, expected_specifics: List[str]) -> Dict[str, Any]:
        """Check if uncertainty contains specific variables"""
        uncertainty_text = response.get("uncertainty", "").lower()
        found_specifics = [spec for spec in expected_specifics if spec.lower() in uncertainty_text]
        
        return {
            "passed": len(found_specifics) > 0,
            "warnings": [] if len(found_specifics) > 0 else 
                       [f"Uncertainty lacks specific variables. Expected one of: {expected_specifics}"]
        }
    
    def _check_context_emphasis(self, response: Dict, expected_emphasis: List[str]) -> Dict[str, Any]:
        """Check if response shows context-appropriate emphasis"""
        response_text = json.dumps(response).lower()
        found_emphasis = [emp for emp in expected_emphasis if emp.lower() in response_text]
        
        return {
            "passed": len(found_emphasis) > 0,
            "warnings": [] if len(found_emphasis) > 0 else 
                       [f"Missing context emphasis. Expected terms: {expected_emphasis}"]
        }
    
    def _check_shallow_avoidance(self, response: Dict, avoid_terms: List[str]) -> Dict[str, Any]:
        """Check that response avoids shallow statements"""
        why_matters = response.get("why_this_matters", [])
        shallow_found = []
        
        for matter in why_matters:
            if isinstance(matter, str):
                matter_lower = matter.lower()
                for term in avoid_terms:
                    if term.lower() in matter_lower:
                        # Check if it's accompanied by mechanism language
                        mechanism_words = ["because", "which", "by", "due to", "causes", "leads to"]
                        if not any(mech in matter_lower for mech in mechanism_words):
                            shallow_found.append(f"Shallow statement: '{matter}'")
        
        return {
            "passed": len(shallow_found) == 0,
            "warnings": shallow_found
        }
    
    def _check_language_preservation(self, response: Dict, language: str) -> Dict[str, Any]:
        """Check if non-English responses preserve reasoning depth"""
        warnings = []
        
        # Check that JSON keys are still in English
        english_keys = ["ai_insight_title", "quick_verdict", "why_this_matters", "trade_offs", "uncertainty", "ai_advice"]
        missing_english_keys = [key for key in english_keys if key not in response]
        
        if missing_english_keys:
            warnings.append(f"Missing English JSON keys: {missing_english_keys}")
        
        # Check that content is in the expected language
        sample_text = response.get("quick_verdict", "")
        if language == "hi":
            # Check for Devanagari script
            if not any('\u0900' <= char <= '\u097F' for char in sample_text):
                warnings.append("Hindi response should contain Devanagari script")
        elif language == "hinglish":
            # Check for English script with Hindi words
            if not sample_text or sample_text.isascii() and len(sample_text.split()) < 3:
                warnings.append("Hinglish response should contain mixed language content")
        
        return {
            "passed": len(warnings) == 0,
            "warnings": warnings
        }
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test suite summary"""
        test_results = results["test_results"]
        
        # Calculate average scores
        avg_mechanism_score = sum(r.get("validation_result", {}).get("mechanism_score", 0) for r in test_results) / len(test_results)
        avg_uncertainty_score = sum(r.get("validation_result", {}).get("uncertainty_score", 0) for r in test_results) / len(test_results)
        avg_quality_score = sum(r.get("validation_result", {}).get("quality_score", 0) for r in test_results) / len(test_results)
        
        # Identify common issues
        all_warnings = []
        for result in test_results:
            all_warnings.extend(result.get("warnings", []))
        
        common_issues = {}
        for warning in all_warnings:
            common_issues[warning] = common_issues.get(warning, 0) + 1
        
        return {
            "pass_rate": results["passed"] / results["total_tests"] * 100,
            "average_scores": {
                "mechanism": avg_mechanism_score,
                "uncertainty": avg_uncertainty_score,
                "overall_quality": avg_quality_score
            },
            "common_issues": dict(sorted(common_issues.items(), key=lambda x: x[1], reverse=True)[:5]),
            "recommendations": self._generate_recommendations(avg_mechanism_score, avg_uncertainty_score, avg_quality_score)
        }
    
    def _generate_recommendations(self, mech_score: float, uncert_score: float, quality_score: float) -> List[str]:
        """Generate improvement recommendations based on test results"""
        recommendations = []
        
        if mech_score < 0.7:
            recommendations.append("Improve mechanism-level reasoning by adding more causal explanations")
        
        if uncert_score < 0.6:
            recommendations.append("Enhance uncertainty specificity by referencing exact variables")
        
        if quality_score < 0.8:
            recommendations.append("Overall response quality needs improvement - focus on depth and clarity")
        
        if mech_score > 0.8 and uncert_score > 0.7 and quality_score > 0.8:
            recommendations.append("System performing well - maintain current standards")
        
        return recommendations

# Test runner function
async def run_enhanced_reasoning_tests():
    """Run the enhanced reasoning test suite"""
    test_suite = EnhancedReasoningTestSuite()
    results = await test_suite.run_all_tests()
    
    # Print summary
    print("\n" + "="*60)
    print("ENHANCED AI REASONING ENGINE TEST RESULTS")
    print("="*60)
    print(f"Tests Passed: {results['passed']}/{results['total_tests']} ({results['summary']['pass_rate']:.1f}%)")
    print(f"Warnings: {results['warnings']}")
    print(f"\nAverage Scores:")
    print(f"  Mechanism Reasoning: {results['summary']['average_scores']['mechanism']:.2f}")
    print(f"  Uncertainty Specificity: {results['summary']['average_scores']['uncertainty']:.2f}")
    print(f"  Overall Quality: {results['summary']['average_scores']['overall_quality']:.2f}")
    
    if results['summary']['common_issues']:
        print(f"\nCommon Issues:")
        for issue, count in results['summary']['common_issues'].items():
            print(f"  - {issue} ({count} times)")
    
    print(f"\nRecommendations:")
    for rec in results['summary']['recommendations']:
        print(f"  - {rec}")
    
    return results

if __name__ == "__main__":
    # Run tests
    asyncio.run(run_enhanced_reasoning_tests())