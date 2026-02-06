from typing import List

from pydantic import BaseModel


class TextPhrase(BaseModel):
    """Phrase with timestamps"""

    text: str
    start_time: float
    end_time: float


class TranscriptionResponse(BaseModel):
    """Response with recognition results"""

    phrases: List[TextPhrase]
    full_text: str
    duration: float
    processing_time: float


class StreamingStateResponse(BaseModel):
    """Response for streaming mode"""

    phrases: List[TextPhrase]
    state_id: str
    is_final: bool
