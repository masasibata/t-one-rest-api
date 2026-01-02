"""Data conversion utilities"""

from typing import List
from asr_api.models import TextPhrase


def phrases_to_text_phrases(phrases: List) -> List[TextPhrase]:
    """
    Convert tone phrases to TextPhrase objects
    
    Args:
        phrases: List of phrases from tone pipeline
        
    Returns:
        List of TextPhrase objects
    """
    return [
        TextPhrase(
            text=phrase.text,
            start_time=phrase.start_time,
            end_time=phrase.end_time
        )
        for phrase in phrases
    ]


def calculate_duration(phrases: List) -> float:
    """
    Calculate total duration from phrases
    
    Args:
        phrases: List of phrases
        
    Returns:
        Total duration in seconds
    """
    return phrases[-1].end_time if phrases else 0.0


def extract_full_text(phrases: List) -> str:
    """
    Extract full text from phrases
    
    Args:
        phrases: List of phrases
        
    Returns:
        Full text string
    """
    return " ".join([p.text for p in phrases])

