"""Authentication utilities for API key protection"""

from typing import Optional

from fastapi import Header, HTTPException

from asr_api.config import settings


def verify_api_key(
    x_api_key: Optional[str] = Header(
        None, alias="X-API-Key", description="API key for authentication"
    )
) -> bool:
    """
    Verify API key from X-API-Key header if authentication is enabled.

    If settings.api_key is None, authentication is disabled and all requests are allowed.
    If settings.api_key is set, the provided X-API-Key header must match.

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        True if authentication passes

    Raises:
        HTTPException: 401 if API key is invalid or missing when authentication is enabled
    """
    if settings.api_key is None:
        return True

    if x_api_key is None or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Provide X-API-Key header",
        )
    return True
