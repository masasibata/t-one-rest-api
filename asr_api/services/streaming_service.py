"""Streaming recognition service"""

import logging
from typing import List, Tuple

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
        self.storage.update_state(state_id, (None, []))
        logger.info(f"Created streaming session: {state_id}")
        return state_id

    def process_chunk(
        self, state_id: str, audio_chunk: bytes, filename: str = "chunk.wav"
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

        stored_data = self.storage.get_state(state_id)
        if stored_data is None:
            pipeline_state, accumulated_phrases = None, []
        elif isinstance(stored_data, tuple) and len(stored_data) == 2:
            pipeline_state, accumulated_phrases = stored_data
        else:
            pipeline_state, accumulated_phrases = stored_data, []

        new_phrases, new_state = self.audio_service.transcribe_streaming(
            audio_chunk, pipeline_state, filename
        )

        accumulated_phrases = accumulated_phrases or []
        accumulated_phrases.extend(new_phrases)
        self.storage.update_state(state_id, (new_state, accumulated_phrases))
        logger.debug(
            f"Processed chunk for session {state_id}, got {len(new_phrases)} phrases (total accumulated: {len(accumulated_phrases)})"
        )

        return new_phrases, state_id

    def finalize_session(self, state_id: str) -> Tuple[List, str]:
        """
        Finalize streaming session and get final results

        Args:
            state_id: Session state ID

        Returns:
            Tuple[all_phrases, state_id] - All phrases accumulated during the session

        Raises:
            StateNotFoundError: If state_id not found
        """
        if not self.storage.state_exists(state_id):
            raise StateNotFoundError(f"State ID '{state_id}' not found")

        stored_data = self.storage.get_state(state_id)
        if stored_data is None:
            pipeline_state, accumulated = None, []
        elif isinstance(stored_data, tuple) and len(stored_data) == 2:
            pipeline_state, accumulated = stored_data
        else:
            pipeline_state, accumulated = stored_data, []

        final_phrases = self.audio_service.finalize_streaming(pipeline_state)

        accumulated = accumulated or []
        accumulated_keys = {(p.start_time, p.end_time) for p in accumulated}
        unique_final_phrases = [
            p for p in final_phrases
            if (p.start_time, p.end_time) not in accumulated_keys
        ]
        
        all_phrases = accumulated + unique_final_phrases
        self.storage.delete_state(state_id)
        
        logger.info(
            f"Finalized streaming session: {state_id}, "
            f"returning {len(all_phrases)} total phrases "
            f"({len(accumulated)} from chunks, {len(final_phrases)} from finalize, "
            f"{len(unique_final_phrases)} unique final phrases after deduplication)"
        )

        return all_phrases, state_id
