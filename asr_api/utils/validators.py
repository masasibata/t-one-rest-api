"""Validation utilities"""

from fastapi import HTTPException


def validate_audio_file(audio_bytes: bytes, filename: str = "audio") -> None:
    """
    Validate audio file
    
    Args:
        audio_bytes: Audio file bytes
        filename: Filename for error messages
        
    Raises:
        HTTPException: If file is empty
    """
    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail=f"Empty file: {filename}")

