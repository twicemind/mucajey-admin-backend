"""
Configuration Settings für Admin Backend
"""

from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List
import os


class Settings(BaseSettings):
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite Dev Server
        "http://localhost:3000",  # Alternative
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:8080",  # Nginx-served frontend inside Docker
        "http://localhost:8081",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081",
        "http://admin.mucajey.twicemind.com",
        "https://admin.mucajey.twicemind.com"
    ]
    
    # Paths (Docker)
    DATA_DIR: Path = Path("/app/data/cards")
    SCRIPTS_DIR: Path = Path("/app/scripts")
    
    # Node.js Cards API
    CARDS_API_URL: str = "http://mucajey-api:3000"  # Docker service name
    CARDS_API_KEY: str = "mucajey-dev-key-2024"  # Muss mit Master-Key übereinstimmen
    
    # API Settings
    API_PREFIX: str = "/api"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
