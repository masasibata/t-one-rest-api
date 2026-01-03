"""Configuration management for ASR API"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from asr_api.storage import StorageType


class Settings(BaseSettings):
    """Application settings with Pydantic BaseSettings"""
    
    # API Configuration
    api_title: str = Field(default="T-one ASR API", description="API title")
    api_description: str = Field(
        default="REST API for Russian speech recognition using T-one model",
        description="API description"
    )
    api_version: str = Field(default="1.0.0", description="API version")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Enable auto-reload (development only)")
    
    # CORS Configuration
    cors_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    cors_credentials: bool = Field(default=True, description="Allow CORS credentials")
    cors_methods: List[str] = Field(default=["*"], description="Allowed CORS methods")
    cors_headers: List[str] = Field(default=["*"], description="Allowed CORS headers")
    
    # New Configuration Options
    max_file_size_mb: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum file size in MB"
    )
    session_timeout_seconds: int = Field(
        default=3600,
        ge=60,
        description="Session timeout in seconds for automatic cleanup"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    # Storage Configuration
    storage_type: StorageType = Field(
        default=StorageType.MEMORY,
        description="Storage type: 'memory' or 'redis'"
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL (only used if storage_type='redis')"
    )
    redis_key_prefix: str = Field(
        default="asr:session:",
        description="Redis key prefix for session states"
    )
    
    # API Security Configuration
    api_key: Optional[str] = Field(
        default=None,
        description="Optional API key for authentication. If set, all endpoints (except /health and /) require X-API-Key header"
    )
    
    @field_validator("storage_type", mode="before")
    @classmethod
    def parse_storage_type(cls, v):
        """Parse storage type string to enum"""
        if isinstance(v, str):
            return v.lower()
        return v
    
    @field_validator("cors_origins", "cors_methods", "cors_headers", mode="before")
    @classmethod
    def parse_list_from_string(cls, v):
        """Parse comma-separated string into list"""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

