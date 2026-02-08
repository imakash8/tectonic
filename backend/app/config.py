"""
Configuration settings for Tectonic Trading Platform Backend
"""

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os
from dotenv import load_dotenv

# Load .env file from backend directory (works regardless of working directory)
backend_dir = Path(__file__).parent.parent
env_file = backend_dir / ".env"
if env_file.exists():
    load_dotenv(env_file, override=True)

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Tectonic Trading Platform"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./tectonic.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # API Keys
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    
    # Financial Data APIs
    ALPHA_VANTAGE_KEY: str = ""
    FINNHUB_API_KEY: str = ""
    POLYGON_API_KEY: str = ""
    IEX_CLOUD_TOKEN: str = ""
    NEWS_API_KEY: str = ""
    
    # Payment APIs (Stripe)
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLIC_KEY: str = ""
    
    # Real-time Data Configuration
    PREFERRED_MARKET_DATA_PROVIDER: str = "finnhub"  # Options: "alpha_vantage", "finnhub"
    MARKET_DATA_CACHE_TTL: int = 30  # Cache for 30 seconds
    USE_REAL_TIME_DATA: bool = True  # ALWAYS TRUE - System uses only real market data
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:8000,https://tectonic-frontend.onrender.com,https://tectonic-4prz.onrender.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_allowed_origins(self) -> list:
        """Parse ALLOWED_ORIGINS string to list"""
        if isinstance(self.ALLOWED_ORIGINS, list):
            return self.ALLOWED_ORIGINS
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

settings = Settings()

settings = Settings()
