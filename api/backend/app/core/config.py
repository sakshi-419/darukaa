import os
from pydantic_settings import BaseSettings
from typing import Optional

def is_serverless() -> bool:
    if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
        return True
    if os.getenv("AWS_LAMBDA_FUNCTION_NAME") or os.getenv("LAMBDA_TASK_ROOT"):
        return True
    if os.path.exists("/var/task"):
        return True
    if os.name != "nt":
        try:
            test_file = f".write_test_{os.getpid()}"
            with open(test_file, "w") as f:
                f.write("1")
            os.remove(test_file)
        except Exception:
            return True
    return False

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

    @property
    def effective_database_url(self) -> str:
        if is_serverless():
            if self.DATABASE_URL and not self.DATABASE_URL.startswith("sqlite"):
                return self.DATABASE_URL
            return "sqlite:////tmp/darukaa.db"
        return self.DATABASE_URL

settings = Settings()
