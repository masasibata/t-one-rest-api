"""Audio processing and T-one model integration"""

import logging
import os
import tempfile
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np

from asr_api.onnx_patch import apply_onnx_patch
from tone import StreamingCTCPipeline, read_audio

apply_onnx_patch()

from asr_api.utils.exceptions import ModelNotLoadedError

logger = logging.getLogger(__name__)


def require_model(func: Callable) -> Callable:
    """Decorator to ensure model is loaded before method execution"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.pipeline is None:
            raise ModelNotLoadedError("Model is not loaded. Call load_model() first.")
        return func(self, *args, **kwargs)

    return wrapper


class AudioProcessor:
    """Class for audio processing and working with T-one model"""

    def __init__(self):
        """Initialize audio processor and load model"""
        self.pipeline: Optional[StreamingCTCPipeline] = None
        self.load_model()

    def load_model(self):
        """Load T-one model from local folder or HuggingFace"""
        if self.pipeline is not None:
            logger.debug("Model already loaded, skipping")
            return

        model_folder = os.environ.get("LOAD_FROM_FOLDER")

        if model_folder and os.path.exists(model_folder):
            logger.info(f"Loading T-one model from local folder: {model_folder}")
            try:
                import sys

                sys.stdout.flush()

                logger.info("Initializing StreamingCTCPipeline from local folder...")
                sys.stdout.flush()

                self.pipeline = StreamingCTCPipeline.from_local(model_folder)

                logger.info("Model loaded successfully from local folder!")
                logger.info("API is ready to process requests")
                sys.stdout.flush()
                return
            except Exception as e:
                logger.warning(
                    f"Failed to load from local folder ({model_folder}): {str(e)}"
                )
                logger.warning("Falling back to HuggingFace download...")

        logger.info("Loading T-one model from HuggingFace...")
        logger.info("This may take a few minutes on first run (downloading model)")

        try:
            import sys

            sys.stdout.flush()

            logger.info("Initializing StreamingCTCPipeline...")
            sys.stdout.flush()

            self.pipeline = StreamingCTCPipeline.from_hugging_face()

            logger.info("Model loaded successfully from HuggingFace!")
            logger.info("API is ready to process requests")
            sys.stdout.flush()

        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            import sys

            sys.stdout.flush()
            raise

    def process_audio_file(self, audio_bytes: bytes, filename: str) -> np.ndarray:
        """
        Process audio file from bytes

        Args:
            audio_bytes: Audio file bytes
            filename: Filename (for format detection)

        Returns:
            audio_array: Audio array (mono, 8kHz, int32)
        """
        suffix = Path(filename).suffix or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name

        try:
            audio = read_audio(tmp_path)
            return audio
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @require_model
    def transcribe_offline(self, audio_bytes: bytes, filename: str) -> list:
        """
        Transcribe speech from audio file (offline mode)

        Args:
            audio_bytes: Audio file bytes
            filename: Filename

        Returns:
            List of phrases from tone pipeline
        """
        audio = self.process_audio_file(audio_bytes, filename)
        phrases = self.pipeline.forward_offline(audio)
        return phrases

    @require_model
    def transcribe_streaming(
        self, audio_chunk: bytes, state: Any, filename: str = "chunk.wav"
    ):
        """
        Transcribe speech from audio chunk (streaming mode)

        Automatically splits large audio files into chunks of 2400 samples (300ms)
        and processes them sequentially, maintaining state between chunks.
        If audio is smaller than chunk size, it will be padded to chunk size.

        Args:
            audio_chunk: Audio chunk bytes (can be full file or chunk)
            state: Pipeline state (None for first chunk)
            filename: Chunk filename

        Returns:
            Tuple[new_phrases, new_state]
        """
        audio = self.process_audio_file(audio_chunk, filename)
        chunk_size = self.pipeline.CHUNK_SIZE

        if len(audio) > chunk_size:
            logger.debug(
                f"Audio file ({len(audio)} samples) is larger than chunk size ({chunk_size}). Splitting into chunks."
            )
            all_phrases = []
            current_state = state

            remainder = len(audio) % chunk_size
            if remainder != 0:
                audio = np.pad(
                    audio,
                    (0, chunk_size - remainder),
                    mode="constant",
                    constant_values=0,
                )

            num_chunks = len(audio) // chunk_size
            audio_chunks = np.split(audio, num_chunks)

            for i, chunk in enumerate(audio_chunks):
                is_last = i == len(audio_chunks) - 1
                new_phrases, current_state = self.pipeline.forward(
                    chunk, current_state, is_last=is_last
                )
                all_phrases.extend(new_phrases)
                logger.debug(
                    f"Processed chunk {i+1}/{num_chunks}, got {len(new_phrases)} phrases"
                )

            return all_phrases, current_state
        elif len(audio) < chunk_size:
            logger.debug(
                f"Audio chunk ({len(audio)} samples) is smaller than chunk size ({chunk_size}). Padding to chunk size."
            )
            padded_audio = np.pad(
                audio, (0, chunk_size - len(audio)), mode="constant", constant_values=0
            )
            new_phrases, new_state = self.pipeline.forward(
                padded_audio, state, is_last=False
            )
            return new_phrases, new_state
        else:
            new_phrases, new_state = self.pipeline.forward(audio, state, is_last=False)
            return new_phrases, new_state

    @require_model
    def finalize_streaming(self, state: Any) -> list:
        """
        Finalize streaming and get final phrases

        Args:
            state: Pipeline state

        Returns:
            Final phrases
        """
        new_phrases, _ = self.pipeline.finalize(state)
        return new_phrases


audio_processor = AudioProcessor()
