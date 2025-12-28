# Define custom exceptions for the application
# Provide meaningful error messages
# Enable proper error handling across services


class NutriAIException(Exception):
    """Base exception for NutriAI application"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ImageProcessingError(NutriAIException):
    """Raised when image processing fails"""
    def __init__(self, message: str = "Failed to process image"):
        super().__init__(message, status_code=400)

class LLMServiceError(NutriAIException):
    """Raised when LLM service fails"""
    def __init__(self, message: str = "LLM service error"):
        super().__init__(message, status_code=500)

class InvalidInputError(NutriAIException):
    """Raised when input validation fails"""
    def __init__(self, message: str = "Invalid input"):
        super().__init__(message, status_code=422)

class SessionNotFoundError(NutriAIException):
    """Raised when session not found"""
    def __init__(self, message: str = "Session not found"):
        super().__init__(message, status_code=404)