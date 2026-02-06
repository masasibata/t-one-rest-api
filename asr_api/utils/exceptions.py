"""Custom exceptions for ASR API"""


class ASRException(Exception):
    """Base exception for ASR API"""

    pass


class ModelNotLoadedError(ASRException):
    """Raised when model is not loaded"""

    pass


class StateNotFoundError(ASRException):
    """Raised when streaming state is not found"""

    pass
