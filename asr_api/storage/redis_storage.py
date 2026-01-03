"""Redis storage implementation for streaming states"""

import pickle
import logging
from typing import Optional, Any
from datetime import datetime
import uuid

try:
    import redis
    from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    RedisError = Exception
    RedisConnectionError = Exception

from .memory_storage import StateStorage

logger = logging.getLogger(__name__)


class RedisStorage(StateStorage):
    """Redis implementation of state storage"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        key_prefix: str = "asr:session:",
        timeout_seconds: int = 3600
    ):
        """
        Initialize Redis storage
        
        Args:
            redis_url: Redis connection URL
            key_prefix: Prefix for Redis keys
            timeout_seconds: Session timeout in seconds (used as TTL)
            
        Raises:
            ImportError: If redis package is not installed
            ConnectionError: If cannot connect to Redis
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "Redis is not installed. Install it with: "
                "poetry install --extras redis"
            )
        
        self.redis_client = redis.from_url(redis_url, decode_responses=False)
        self.key_prefix = key_prefix
        self.timeout_seconds = timeout_seconds
        
        # Test connection
        try:
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {redis_url}")
        except RedisConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError(f"Failed to connect to Redis: {e}") from e
    
    def _make_key(self, state_id: str) -> str:
        """Create Redis key from state ID"""
        return f"{self.key_prefix}{state_id}"
    
    def _make_timestamp_key(self, state_id: str) -> str:
        """Create timestamp key for state ID"""
        return f"{self.key_prefix}ts:{state_id}"
    
    def create_state(self) -> str:
        """Create a new state and return its ID"""
        state_id = str(uuid.uuid4())
        key = self._make_key(state_id)
        ts_key = self._make_timestamp_key(state_id)
        
        try:
            # Store None state and timestamp
            self.redis_client.setex(
                key,
                self.timeout_seconds,
                pickle.dumps(None)
            )
            self.redis_client.setex(
                ts_key,
                self.timeout_seconds,
                pickle.dumps(datetime.now())
            )
            return state_id
        except RedisError as e:
            logger.error(f"Redis error creating state: {e}")
            raise
    
    def get_state(self, state_id: str) -> Optional[Any]:
        """Get state by ID"""
        key = self._make_key(state_id)
        
        try:
            data = self.redis_client.get(key)
            if data is None:
                return None
            return pickle.loads(data)
        except RedisError as e:
            logger.error(f"Redis error getting state: {e}")
            raise
        except (pickle.PickleError, Exception) as e:
            logger.error(f"Error unpickling state: {e}")
            return None
    
    def update_state(self, state_id: str, state: Any) -> None:
        """Update state by ID"""
        key = self._make_key(state_id)
        ts_key = self._make_timestamp_key(state_id)
        
        try:
            # Check if state exists
            if not self.redis_client.exists(key):
                raise KeyError(f"State ID '{state_id}' not found")
            
            # Update state and extend TTL
            ttl = self.redis_client.ttl(key)
            if ttl > 0:
                self.redis_client.setex(key, ttl, pickle.dumps(state))
                self.redis_client.setex(ts_key, ttl, pickle.dumps(datetime.now()))
            else:
                # TTL expired, set new timeout
                self.redis_client.setex(
                    key,
                    self.timeout_seconds,
                    pickle.dumps(state)
                )
                self.redis_client.setex(
                    ts_key,
                    self.timeout_seconds,
                    pickle.dumps(datetime.now())
                )
        except RedisError as e:
            logger.error(f"Redis error updating state: {e}")
            raise
    
    def delete_state(self, state_id: str) -> None:
        """Delete state by ID"""
        key = self._make_key(state_id)
        ts_key = self._make_timestamp_key(state_id)
        
        try:
            self.redis_client.delete(key, ts_key)
        except RedisError as e:
            logger.error(f"Redis error deleting state: {e}")
            # Don't raise - deletion is best effort
    
    def state_exists(self, state_id: str) -> bool:
        """Check if state exists"""
        key = self._make_key(state_id)
        
        try:
            return self.redis_client.exists(key) > 0
        except RedisError as e:
            logger.error(f"Redis error checking state: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired states (Redis handles this automatically via TTL)
        
        Returns:
            Always returns 0 as Redis handles expiration automatically
        """
        # Redis handles expiration automatically via TTL
        # This method exists for interface compatibility
        return 0
    
    def get_all_state_ids(self) -> list:
        """
        Get all active state IDs (for shutdown cleanup)
        
        Returns:
            List of all state IDs
        """
        try:
            pattern = f"{self.key_prefix}*"
            # Get all keys matching pattern
            keys = self.redis_client.keys(pattern)
            # Filter out timestamp keys and decode if needed
            state_keys = []
            for key in keys:
                key_str = key.decode() if isinstance(key, bytes) else key
                # Exclude timestamp keys
                if not key_str.endswith(":ts:") and ":ts:" not in key_str:
                    state_keys.append(key_str)
            
            # Remove prefix
            prefix_len = len(self.key_prefix)
            return [key[prefix_len:] for key in state_keys]
        except RedisError as e:
            logger.error(f"Redis error getting all state IDs: {e}")
            return []

