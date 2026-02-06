"""Validation utilities"""

from fastapi import HTTPException

from asr_api.config import settings


def validate_file_size(audio_bytes: bytes, filename: str = "audio") -> None:
    """
    Validate file size against maximum allowed size

    Args:
        audio_bytes: Audio file bytes
        filename: Filename for error messages

    Raises:
        HTTPException: If file exceeds maximum size (413 Payload Too Large)
    """
    max_size_bytes = settings.max_file_size_mb * 1024 * 1024
    file_size_bytes = len(audio_bytes)

    if file_size_bytes > max_size_bytes:
        file_size_mb = file_size_bytes / (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=(
                f"File '{filename}' too large: {file_size_mb:.2f} MB "
                f"(maximum: {settings.max_file_size_mb} MB)"
            ),
        )


def validate_audio_file(audio_bytes: bytes, filename: str = "audio") -> None:
    """
    Validate audio file (size and non-empty)

    Args:
        audio_bytes: Audio file bytes
        filename: Filename for error messages

    Raises:
        HTTPException: If file is empty or exceeds maximum size
    """
    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail=f"Empty file: {filename}")

    validate_file_size(audio_bytes, filename)
