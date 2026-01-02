"""Audio processing service"""

import logging
from typing import List, Tuple, Optional
from asr_api.audio_processor import AudioProcessor
from asr_api.utils.exceptions import ModelNotLoadedError

logger = logging.getLogger(__name__)


class AudioService:
    """Service for audio transcription operations"""
    
    def __init__(self, processor: Optional[AudioProcessor] = None):
        """
        Initialize audio service
        
        Args:
            processor: AudioProcessor instance (creates new one if None)
        """
        self.processor = processor or AudioProcessor()
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.processor.pipeline is not None
    
    def transcribe_offline(self, audio_bytes: bytes, filename: str) -> List:
        """
        Transcribe speech from audio file (offline mode)
        
        Args:
            audio_bytes: Audio file bytes
            filename: Filename
            
        Returns:
            List of phrases from tone pipeline
            
        Raises:
            ModelNotLoadedError: If model is not loaded
        """
        if not self.is_model_loaded():
            raise ModelNotLoadedError("Model is not loaded")
        
        return self.processor.transcribe_offline(audio_bytes, filename)
    
    def transcribe_streaming(
        self, 
        audio_chunk: bytes, 
        state: Optional[any], 
        filename: str = "chunk.wav"
    ) -> Tuple[List, any]:
        """
        Transcribe speech from audio chunk (streaming mode)
        
        Args:
            audio_chunk: Audio chunk bytes
            state: Pipeline state (None for first chunk)
            filename: Chunk filename
            
        Returns:
            Tuple[new_phrases, new_state]
            
        Raises:
            ModelNotLoadedError: If model is not loaded
        """
        if not self.is_model_loaded():
            raise ModelNotLoadedError("Model is not loaded")
        
        return self.processor.transcribe_streaming(audio_chunk, state, filename)
    
    def finalize_streaming(self, state: any) -> List:
        """
        Finalize streaming and get final phrases
        
        Args:
            state: Pipeline state
            
        Returns:
            Final phrases
            
        Raises:
            ModelNotLoadedError: If model is not loaded
        """
        if not self.is_model_loaded():
            raise ModelNotLoadedError("Model is not loaded")
        
        return self.processor.finalize_streaming(state)

