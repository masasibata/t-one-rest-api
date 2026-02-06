"""In-memory storage implementation for streaming states"""

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class StateStorage(ABC):
    """Abstract interface for state storage"""

    @abstractmethod
    def create_state(self) -> str:
        """Create a new state and return its ID"""
        pass

    @abstractmethod
    def get_state(self, state_id: str) -> Optional[Any]:
        """Get state by ID"""
        pass

    @abstractmethod
    def update_state(self, state_id: str, state: Any) -> None:
        """Update state by ID"""
        pass

    @abstractmethod
    def delete_state(self, state_id: str) -> None:
        """Delete state by ID"""
        pass

    @abstractmethod
    def state_exists(self, state_id: str) -> bool:
        """Check if state exists"""
        pass

    @abstractmethod
    def cleanup_expired(self) -> int:
        """Clean up expired states and return count of cleaned states"""
        pass

    @abstractmethod
    def get_all_state_ids(self) -> list:
        """Get all active state IDs (for shutdown cleanup)"""
        pass


class MemoryStorage(StateStorage):
    """In-memory implementation of state storage with automatic cleanup"""

    def __init__(self, timeout_seconds: int = 3600):
        """
        Initialize memory storage

        Args:
            timeout_seconds: Session timeout in seconds for automatic cleanup
        """
        self._states: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}
        self.timeout_seconds = timeout_seconds

    def create_state(self) -> str:
        """Create a new state and return its ID"""
        self._cleanup_expired()
        state_id = str(uuid.uuid4())
        self._states[state_id] = None
        self._timestamps[state_id] = datetime.now()
        return state_id

    def get_state(self, state_id: str) -> Optional[Any]:
        """Get state by ID"""
        self._cleanup_expired()
        return self._states.get(state_id)

    def update_state(self, state_id: str, state: Any) -> None:
        """Update state by ID"""
        if state_id not in self._states:
            raise KeyError(f"State ID '{state_id}' not found")
        self._states[state_id] = state
        # Update timestamp on state update to extend session lifetime
        if state_id in self._timestamps:
            self._timestamps[state_id] = datetime.now()

    def delete_state(self, state_id: str) -> None:
        """Delete state by ID"""
        self._states.pop(state_id, None)
        self._timestamps.pop(state_id, None)

    def state_exists(self, state_id: str) -> bool:
        """Check if state exists"""
        return state_id in self._states

    def _cleanup_expired(self) -> None:
        """Internal method to clean up expired states"""
        now = datetime.now()
        expired = [
            sid
            for sid, ts in self._timestamps.items()
            if (now - ts).total_seconds() > self.timeout_seconds
        ]
        for sid in expired:
            self.delete_state(sid)
            logger.debug(f"Cleaned up expired session: {sid}")

    def cleanup_expired(self) -> int:
        """
        Clean up expired states and return count of cleaned states

        Returns:
            Number of cleaned up states
        """
        before_count = len(self._states)
        self._cleanup_expired()
        cleaned_count = before_count - len(self._states)
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} expired session(s)")
        return cleaned_count

    def get_all_state_ids(self) -> list:
        """
        Get all active state IDs (for shutdown cleanup)

        Returns:
            List of all state IDs
        """
        return list(self._states.keys())
