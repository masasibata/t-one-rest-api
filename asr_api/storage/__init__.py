"""Storage abstraction for streaming states"""

from enum import Enum
from typing import Union
from .memory_storage import MemoryStorage, StateStorage

__all__ = ["MemoryStorage", "StateStorage", "create_storage", "StorageType"]

# Import RedisStorage (module handles missing redis package gracefully)
from .redis_storage import RedisStorage, REDIS_AVAILABLE

if REDIS_AVAILABLE:
    __all__.append("RedisStorage")


class StorageType(str, Enum):
    """Storage type enumeration"""
    MEMORY = "memory"
    REDIS = "redis"


def create_storage(
    storage_type: Union[StorageType, str] = StorageType.MEMORY,
    timeout_seconds: int = 3600,
    redis_url: str = "redis://localhost:6379/0",
    redis_key_prefix: str = "asr:session:"
) -> StateStorage:
    """
    Factory function to create storage instance
    
    Args:
        storage_type: Type of storage (StorageType enum or string)
        timeout_seconds: Session timeout in seconds
        redis_url: Redis connection URL (only for redis storage)
        redis_key_prefix: Redis key prefix (only for redis storage)
        
    Returns:
        StateStorage instance
        
    Raises:
        ValueError: If storage_type is invalid
        ImportError: If redis storage requested but not installed
    """
    # Convert string to enum if needed (for backward compatibility)
    if isinstance(storage_type, str):
        try:
            storage_type = StorageType(storage_type.lower())
        except ValueError:
            raise ValueError(
                f"Invalid storage_type: {storage_type}. "
                f"Must be one of: {[e.value for e in StorageType]}"
            )
    
    if storage_type == StorageType.MEMORY:
        return MemoryStorage(timeout_seconds=timeout_seconds)
    elif storage_type == StorageType.REDIS:
        if not REDIS_AVAILABLE:
            raise ImportError(
                "Redis storage requested but redis package is not installed. "
                "Install it with: poetry install --extras redis"
            )
        return RedisStorage(
            redis_url=redis_url,
            key_prefix=redis_key_prefix,
            timeout_seconds=timeout_seconds
        )
    else:
        raise ValueError(
            f"Invalid storage_type: {storage_type}. "
            f"Must be one of: {[e.value for e in StorageType]}"
        )

