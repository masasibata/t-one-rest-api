"""FastAPI application initialization"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asr_api.config import settings
from asr_api.routers import transcription_router, streaming_router
from asr_api.audio_processor import audio_processor
from asr_api.services.audio_service import AudioService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Register routers
app.include_router(transcription_router)
app.include_router(streaming_router)


@app.on_event("startup")
async def startup_event():
    """Verify model is loaded on application startup"""
    logger.info("Starting T-one ASR API...")
    audio_service = AudioService(audio_processor)
    if audio_service.is_model_loaded():
        logger.info("Model loaded successfully. API is ready to accept requests.")
    else:
        logger.error("Model failed to load during initialization!")
        raise RuntimeError("Model is not loaded. Check initialization logs for errors.")


@app.get("/")
async def root():
    """API information"""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "endpoints": {
            "POST /transcribe": "Transcribe speech from audio file (offline)",
            "POST /transcribe/streaming": "Start streaming recognition",
            "POST /transcribe/streaming/chunk": "Send audio chunk for streaming",
            "POST /transcribe/streaming/finalize": "Finalize streaming"
        }
    }


@app.get("/health")
async def health_check():
    """API health check"""
    audio_service = AudioService(audio_processor)
    return {
        "status": "healthy",
        "model_loaded": audio_service.is_model_loaded()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.host, 
        port=settings.port, 
        reload=settings.reload
    )
