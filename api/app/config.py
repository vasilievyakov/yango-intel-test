from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App
    APP_NAME: str = "Yango Competitive Intelligence API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://localhost/yango_intel"
    DATABASE_ECHO: bool = False
    
    # Security
    WEBHOOK_SECRET: str = "change-me-in-production"
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # Clerk Auth
    CLERK_JWKS_URL: Optional[str] = None
    CLERK_ISSUER: Optional[str] = None
    
    # AI Services
    # Google Gemini (primary)
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"  # Fast & cheap, good for classification
    GEMINI_MODEL_PRO: str = "gemini-1.5-pro"  # For digest generation
    
    # Anthropic (optional fallback)
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Parallel AI for web search
    PARALLEL_API_KEY: Optional[str] = None
    PARALLEL_BASE_URL: str = "https://api.parallel.ai/v1beta"
    PARALLEL_BETA_HEADER: str = "search-extract-2025-10-10"
    
    # Alternative search providers
    PERPLEXITY_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None
    SERPAPI_KEY: Optional[str] = None
    
    # Telegram notifications (optional)
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


settings = get_settings()

