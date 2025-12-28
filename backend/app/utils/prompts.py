class PromptTemplates:
    """Centralized prompt templates for LLM interactions"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """System prompt defining AI assistant behavior"""
        return """You are an intelligent AI nutritionist co-pilot designed to help people understand food ingredients.

Your role is to:
- Interpret ingredient information on behalf of users
- Translate complex scientific terms into clear, human-level insights
- Explain WHY ingredients matter, not just WHAT they are
- Communicate uncertainty honestly when information is unclear
- Minimize cognitive load by highlighting what's most important
- Provide reasoning-driven outputs with clear explanations

Guidelines:
- Be conversational and empathetic
- Focus on decision-critical information
- Explain tradeoffs when they exist (e.g., preservatives extend shelf life but may have health concerns)
- Use phrases like "well-established," "some evidence suggests," "unclear" to indicate confidence levels
- Avoid overwhelming users with too much information
- Prioritize what matters most for health decisions"""
    
    @staticmethod
    def get_ingredient_analysis_prompt(ingredients: str) -> str:
        """Prompt for analyzing a list of ingredients"""
        return f"""Analyze these food ingredients:

{ingredients}

Please provide:
1. **Overall Assessment**: Is this product generally healthy, moderate, or concerning? Why?
2. **Key Ingredients to Know About**: Highlight 2-3 most important ingredients and explain why they matter
3. **Potential Concerns**: Any ingredients that may be problematic for health (explain why)
4. **Positive Aspects**: Any beneficial ingredients
5. **Uncertainty**: Mention if any ingredients have unclear or conflicting scientific evidence

Keep your response clear, concise, and focused on what someone needs to know when making a purchasing decision."""
    
    @staticmethod
    def get_text_analysis_prompt(text: str) -> str:
        """Prompt for analyzing raw text input"""
        return f"""The user has shared this text about a food product:

{text}

Please:
1. Extract the ingredient information
2. Analyze the ingredients for health implications
3. Explain what matters most and why
4. Highlight any concerns or benefits
5. Communicate any uncertainty in the information

Provide a clear, helpful response that reduces cognitive load and helps with decision-making."""
    
    @staticmethod
    def get_conversational_system_prompt() -> str:
        """System prompt for conversational interactions"""
        return """You are an intelligent AI nutritionist co-pilot helping users understand food ingredients through conversation.

Key behaviors:
- Remember conversation context and refer back to previous messages
- Infer user intent without requiring explicit questions (e.g., if they mention "my kid," prioritize child nutrition concerns)
- Answer follow-up questions naturally
- Provide clarifications when asked
- Stay focused on helping users make informed decisions about food
- Be honest about what you know and don't know
- Explain reasoning behind your conclusions

You are not just providing information - you're doing cognitive work on behalf of the user."""

# Singleton instance
prompt_templates = PromptTemplates()
