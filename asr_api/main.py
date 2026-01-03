"""FastAPI application initialization"""

import logging
import sys

# Configure logging FIRST, before importing modules that load the model
# This ensures we see logs during model loading
logging.basicConfig(
    level=logging.INFO,  # Use INFO initially, will be updated from settings
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True  # Override any existing configuration
)

# Now import settings and update log level
from asr_api.config import settings

# Update log level from settings
logging.getLogger().setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

logger = logging.getLogger(__name__)

# Log initial message
logger.info("Initializing T-one ASR API...")

# Now import modules (model will start loading here)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from asr_api.routers import transcription_router, streaming_router
from asr_api.audio_processor import audio_processor
from asr_api.services.audio_service import AudioService


class DocsAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to protect documentation endpoints with API key"""
    
    async def dispatch(self, request: Request, call_next):
        # Only protect docs if API key is configured
        if settings.api_key is None:
            return await call_next(request)
        
        # Check if accessing docs endpoints
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            api_key = request.headers.get("X-API-Key")
            if api_key != settings.api_key:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or missing API key. Provide X-API-Key header"}
                )
        
        return await call_next(request)


app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version
)

# Add docs protection middleware (before CORS)
app.add_middleware(DocsAuthMiddleware)

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
    import sys
    sys.stdout.flush()
    
    logger.info("T-one ASR API startup event...")
    sys.stdout.flush()
    
    # Model is loaded during audio_processor import, so we just verify
    audio_service = AudioService(audio_processor)
    if audio_service.is_model_loaded():
        logger.info("Startup complete! API is ready to accept requests")
        logger.info(f"API available at http://0.0.0.0:{settings.port}")
        logger.info(f"Documentation at http://0.0.0.0:{settings.port}/docs")
    else:
        logger.error("Model failed to load during initialization!")
        logger.error("Check logs above for detailed error messages")
        raise RuntimeError("Model is not loaded. Check initialization logs for errors.")
    
    sys.stdout.flush()


@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown handler"""
    logger.info("Shutting down T-one ASR API...")
    
    try:
        # Clean up all active streaming sessions
        from asr_api.routers.streaming import get_storage
        storage = get_storage()
        active_sessions = storage.get_all_state_ids()
        
        if active_sessions:
            logger.info(f"Cleaning up {len(active_sessions)} active streaming session(s)...")
            for state_id in active_sessions:
                storage.delete_state(state_id)
            logger.info("All streaming sessions cleaned up")
        else:
            logger.info("No active streaming sessions to clean up")
        
        # Clean up model resources if needed
        if hasattr(audio_processor, 'pipeline') and audio_processor.pipeline is not None:
            logger.info("Model resources will be cleaned up by Python garbage collector")
        
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)


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
