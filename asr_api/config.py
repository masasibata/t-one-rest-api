"""Configuration management for ASR API"""

import os
from typing import List


class Settings:
    """Application settings"""
    
    # API Configuration
    api_title: str = os.getenv("API_TITLE", "T-one ASR API")
    api_description: str = os.getenv(
        "API_DESCRIPTION", 
        "REST API for Russian speech recognition using T-one model"
    )
    api_version: str = os.getenv("API_VERSION", "1.0.0")
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    reload: bool = os.getenv("RELOAD", "true").lower() == "true"
    
    # CORS Configuration
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    cors_credentials: bool = os.getenv("CORS_CREDENTIALS", "true").lower() == "true"
    cors_methods: List[str] = os.getenv("CORS_METHODS", "*").split(",")
    cors_headers: List[str] = os.getenv("CORS_HEADERS", "*").split(",")


settings = Settings()

