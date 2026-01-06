"""
Application configuration settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App settings
    APP_NAME: str = "CrossFit Performance API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./crossfit_performance.db"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "https://5173-ieglgxq9xkxsb9vk47uk1-8f57ffe2.sandbox.novita.ai",
        "https://5174-ieglgxq9xkxsb9vk47uk1-8f57ffe2.sandbox.novita.ai",
    ]
    
    # Scoring Engine
    DISTRIBUTION_WINDOW_DAYS: int = 180
    CONFIDENCE_LOW_THRESHOLD: int = 5
    CONFIDENCE_MEDIUM_THRESHOLD: int = 15
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
