# Loads all environment variables
# Validates configuration on startup
# Provides singleton configuration object
# Type-safe settings using Pydantic

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Settings
    API_HOST: str
    API_PORT: int
    DEBUG: bool
    
    # LLM Settings
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash-exp"
    LLM_TEMPERATURE: float
    MAX_TOKENS: int
    
    # Redis Settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    SESSION_EXPIRE_SECONDS: int
    
    # Upload Settings
    MAX_UPLOAD_SIZE: int
    ALLOWED_IMAGE_TYPES: str
    UPLOAD_DIR: str
    
    # CORS Settings
    ALLOWED_ORIGINS: str
    
    # OpenFoodFacts Settings
    OFF_BASE_URL: str = "https://world.openfoodfacts.org"
    OFF_TIMEOUT_SECONDS: int = 10
    
    # Tools API Settings
    TOOLS_API_KEY: str = "debug-tools-key-2024"
    
    class Config:
        env_file = ".env"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def allowed_image_types_list(self) -> List[str]:
        return [type.strip() for type in self.ALLOWED_IMAGE_TYPES.split(",")]

settings = Settings()
