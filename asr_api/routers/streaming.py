"""Streaming recognition endpoints"""

import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends
from asr_api.models import StreamingStateResponse
from asr_api.services.streaming_service import StreamingService
from asr_api.services.audio_service import AudioService
from asr_api.storage import create_storage, StateStorage
from asr_api.config import settings
from asr_api.utils.converters import phrases_to_text_phrases
from asr_api.utils.validators import validate_audio_file
from asr_api.utils.exceptions import ASRException, StateNotFoundError, ModelNotLoadedError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transcribe/streaming", tags=["streaming"])

# Create storage based on configuration
_storage = create_storage(
    storage_type=settings.storage_type,
    timeout_seconds=settings.session_timeout_seconds,
    redis_url=settings.redis_url,
    redis_key_prefix=settings.redis_key_prefix
)


def get_storage() -> StateStorage:
    """Get the global storage instance (for shutdown cleanup)"""
    return _storage


def get_streaming_service() -> StreamingService:
    """Dependency to get streaming service instance"""
    from asr_api.audio_processor import audio_processor
    audio_service = AudioService(audio_processor)
    return StreamingService(audio_service, _storage)


@router.post("", response_model=StreamingStateResponse)
async def start_streaming(
    streaming_service: StreamingService = Depends(get_streaming_service)
):
    """
    Start streaming recognition session
    
    Returns state ID to use for subsequent requests.
    """
    
    try:
        state_id = streaming_service.create_session()
        return StreamingStateResponse(
            phrases=[],
            state_id=state_id,
            is_final=False
        )
    except Exception as e:
        logger.error(f"Error creating streaming session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.post("/chunk", response_model=StreamingStateResponse)
async def process_streaming_chunk(
    state_id: str = Form(..., description="State ID from start_streaming"),
    file: UploadFile = File(..., description="Audio chunk for processing"),
    streaming_service: StreamingService = Depends(get_streaming_service)
):
    """
    Process audio chunk in streaming mode
    
    Accepts audio chunk and state, returns newly recognized phrases.
    Use for real-time audio processing.
    """
    try:
        audio_bytes = await file.read()
        validate_audio_file(audio_bytes, file.filename or "chunk.wav")
        
        new_phrases, state_id = streaming_service.process_chunk(
            state_id,
            audio_bytes,
            file.filename or "chunk.wav"
        )
        
        phrase_objects = phrases_to_text_phrases(new_phrases)
        
        return StreamingStateResponse(
            phrases=phrase_objects,
            state_id=state_id,
            is_final=False
        )
        
    except StateNotFoundError as e:
        logger.warning(f"State not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ModelNotLoadedError as e:
        logger.error(f"Model not loaded: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable: Model not loaded")
    except ASRException as e:
        logger.error(f"ASR error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/finalize", response_model=StreamingStateResponse)
async def finalize_streaming(
    state_id: str = Form(..., description="State ID for finalization"),
    streaming_service: StreamingService = Depends(get_streaming_service)
):
    """
    Finalize streaming session and get final results
    
    Call this endpoint after sending the last chunk.
    """
    try:
        final_phrases, state_id = streaming_service.finalize_session(state_id)
        
        phrase_objects = phrases_to_text_phrases(final_phrases)
        
        return StreamingStateResponse(
            phrases=phrase_objects,
            state_id=state_id,
            is_final=True
        )
        
    except StateNotFoundError as e:
        logger.warning(f"State not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ModelNotLoadedError as e:
        logger.error(f"Model not loaded: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable: Model not loaded")
    except ASRException as e:
        logger.error(f"ASR error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Finalization error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Ensure state is cleaned up
        if _storage.state_exists(state_id):
            _storage.delete_state(state_id)

