"""In-memory storage implementation for streaming states"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import uuid


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


class MemoryStorage(StateStorage):
    """In-memory implementation of state storage"""
    
    def __init__(self):
        """Initialize memory storage"""
        self._states: Dict[str, Any] = {}
    
    def create_state(self) -> str:
        """Create a new state and return its ID"""
        state_id = str(uuid.uuid4())
        self._states[state_id] = None
        return state_id
    
    def get_state(self, state_id: str) -> Optional[Any]:
        """Get state by ID"""
        return self._states.get(state_id)
    
    def update_state(self, state_id: str, state: Any) -> None:
        """Update state by ID"""
        if state_id not in self._states:
            raise KeyError(f"State ID '{state_id}' not found")
        self._states[state_id] = state
    
    def delete_state(self, state_id: str) -> None:
        """Delete state by ID"""
        self._states.pop(state_id, None)
    
    def state_exists(self, state_id: str) -> bool:
        """Check if state exists"""
        return state_id in self._states

