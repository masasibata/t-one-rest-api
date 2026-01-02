"""Streaming recognition service"""

import logging
from typing import Tuple, List, Optional
from asr_api.services.audio_service import AudioService
from asr_api.storage.memory_storage import StateStorage
from asr_api.utils.exceptions import StateNotFoundError

logger = logging.getLogger(__name__)


class StreamingService:
    """Service for managing streaming recognition sessions"""
    
    def __init__(self, audio_service: AudioService, storage: StateStorage):
        """
        Initialize streaming service
        
        Args:
            audio_service: AudioService instance
            storage: StateStorage instance
        """
        self.audio_service = audio_service
        self.storage = storage
    
    def create_session(self) -> str:
        """
        Create a new streaming session
        
        Returns:
            State ID for the session
        """
        state_id = self.storage.create_state()
        logger.info(f"Created streaming session: {state_id}")
        return state_id
    
    def process_chunk(
        self, 
        state_id: str, 
        audio_chunk: bytes, 
        filename: str = "chunk.wav"
    ) -> Tuple[List, str]:
        """
        Process audio chunk in streaming mode
        
        Args:
            state_id: Session state ID
            audio_chunk: Audio chunk bytes
            filename: Chunk filename
            
        Returns:
            Tuple[new_phrases, state_id]
            
        Raises:
            StateNotFoundError: If state_id not found
        """
        if not self.storage.state_exists(state_id):
            raise StateNotFoundError(f"State ID '{state_id}' not found")
        
        state = self.storage.get_state(state_id)
        new_phrases, new_state = self.audio_service.transcribe_streaming(
            audio_chunk, 
            state, 
            filename
        )
        
        self.storage.update_state(state_id, new_state)
        logger.debug(f"Processed chunk for session {state_id}, got {len(new_phrases)} phrases")
        
        return new_phrases, state_id
    
    def finalize_session(self, state_id: str) -> Tuple[List, str]:
        """
        Finalize streaming session and get final results
        
        Args:
            state_id: Session state ID
            
        Returns:
            Tuple[final_phrases, state_id]
            
        Raises:
            StateNotFoundError: If state_id not found
        """
        if not self.storage.state_exists(state_id):
            raise StateNotFoundError(f"State ID '{state_id}' not found")
        
        state = self.storage.get_state(state_id)
        final_phrases = self.audio_service.finalize_streaming(state)
        
        self.storage.delete_state(state_id)
        logger.info(f"Finalized streaming session: {state_id}")
        
        return final_phrases, state_id

