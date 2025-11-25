"""
Application configuration using Pydantic BaseSettings.
Environment variables are loaded from .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001
    DEBUG: bool = False

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "https://script.google.com",
        "https://docs.google.com",
    ]

    # cite-assist Integration
    CITE_ASSIST_API_URL: str = "http://localhost:8000"
    CITE_ASSIST_API_KEY: str = ""

    # Gemini AI (Phase 2)
    GOOGLE_GENAI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"

    # Agent Configuration (Phase 2)
    AGENT_FILTER_THRESHOLD: float = 0.7
    AGENT_MAX_CHUNKS: int = 20
    AGENT_TIMEOUT_SECONDS: int = 5

    # Caching (Future)
    CACHE_ENABLED: bool = False
    CACHE_TTL_SECONDS: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Global settings instance
settings = Settings()
