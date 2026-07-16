# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Yeh class .env file se automatically saari
    values read kar leti hai.
    Agar .env mein DATABASE_URL hai toh
    settings.DATABASE_URL se access kar sakte ho.
    """

    # App info
    APP_NAME: str = "Finance Intelligence Agent"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/finance_db"

    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # LLM Provider — "openai" ya "groq"
    LLM_PROVIDER: str = "groq"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT Auth
    SECRET_KEY: str = "change-this-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OpenAI (Day 12 mein use hoga)
    OPENAI_API_KEY: Optional[str] = None

    # CORS — Frontend kis URL se aayega
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # Alternative
    ]

    class Config:
        # Yeh file se values read karega
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Case insensitive — DATABASE_URL ya database_url dono chalega
        case_sensitive = False

# Single instance banao — poori app mein yahi use hoga
# "Singleton pattern" kehte hain isse
settings = Settings()