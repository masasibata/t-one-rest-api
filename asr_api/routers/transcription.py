"""Transcription endpoints"""

import time
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends
from asr_api.models import TranscriptionResponse
from asr_api.services.audio_service import AudioService
from asr_api.utils.converters import phrases_to_text_phrases, calculate_duration, extract_full_text
from asr_api.utils.validators import validate_audio_file
from asr_api.utils.exceptions import ASRException, ModelNotLoadedError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transcribe", tags=["transcription"])


def get_audio_service() -> AudioService:
    """Dependency to get audio service instance"""
    from asr_api.audio_processor import audio_processor
    return AudioService(audio_processor)


@router.post("", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file for recognition"),
    return_timestamps: bool = Form(True, description="Return timestamps"),
    audio_service: AudioService = Depends(get_audio_service)
):
    """
    Transcribe speech from audio file (offline mode)
    
    Accepts an audio file and returns full text with timestamps.
    Suitable for processing ready audio files.
    
    **Supported formats:** WAV, FLAC, MP3 and other formats supported by librosa
    """
    
    start_time = time.time()
    
    try:
        logger.info(f"Received file: {file.filename}, content_type: {file.content_type}")
        audio_bytes = await file.read()
        
        validate_audio_file(audio_bytes, file.filename or "audio.wav")
        
        phrases = audio_service.transcribe_offline(
            audio_bytes, 
            file.filename or "audio.wav"
        )
        
        phrase_objects = phrases_to_text_phrases(phrases)
        full_text = extract_full_text(phrases)
        duration = calculate_duration(phrases)
        processing_time = time.time() - start_time
        
        return TranscriptionResponse(
            phrases=phrase_objects if return_timestamps else [],
            full_text=full_text,
            duration=duration,
            processing_time=processing_time
        )
        
    except ModelNotLoadedError as e:
        logger.error(f"Model not loaded: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable: Model not loaded")
    except ASRException as e:
        logger.error(f"ASR error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Recognition error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

