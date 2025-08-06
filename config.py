from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    openai_api_key: str
    chroma_db_path: str = "./chroma_db"
    model_name: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 2000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Ensure ChromaDB directory exists
os.makedirs(settings.chroma_db_path, exist_ok=True) 
