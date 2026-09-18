import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Darukaa.Earth — Biodiversity Intelligence"
    TAGLINE: str = "From environmental data to evidence-backed biodiversity action."
    API_V1_STR: str = "/api"
    
    # LLM Settings
    LLM_PROVIDER: str = "mock"  # mock, openai, gemini
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Vector DB Settings
    VECTOR_DB_TYPE: str = "chroma"  # chroma, qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///./darukaa.db"
    
    # Optional Weather API
    OPTIONAL_WEATHER_API_KEY: Optional[str] = None
    DEBUG: bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()
