"""Monkey patch for T-one ONNX Runtime configuration to support parallel workers.

This module patches the StreamingCTCModel.from_local method to configure
ONNX Runtime for parallel execution. This allows multiple workers to process
requests concurrently without blocking each other.

The patch is applied explicitly in audio_processor.py after tone is imported
but before the model is loaded. This ensures the patch is applied at the
correct time without modifying the T-one package directly.
"""

import logging

logger = logging.getLogger(__name__)

# Flag to ensure patch is applied only once
_patch_applied = False


def apply_onnx_patch():
    """Apply monkey patch to T-one's ONNX Runtime configuration.
    
    This patches StreamingCTCModel.from_local to configure ONNX Runtime
    with settings that allow parallel workers to work concurrently.
    """
    global _patch_applied
    
    if _patch_applied:
        return
    
    try:
        # Import onnxruntime - may not be available in all environments
        import onnxruntime as ort
    except ImportError:
        logger.warning("onnxruntime not available - patch will be applied when tone is imported")
        return
    
    try:
        from tone.onnx_wrapper import StreamingCTCModel
        
        original_from_local = StreamingCTCModel.from_local
        
        @classmethod
        def patched_from_local(cls, model_path):
            """Patched version of from_local with ONNX Runtime configuration."""
            sess_options = ort.SessionOptions()
            sess_options.intra_op_num_threads = 1
            sess_options.inter_op_num_threads = 1
            sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            
            ort_sess = ort.InferenceSession(model_path, sess_options)
            return cls(ort_sess)
        
        StreamingCTCModel.from_local = patched_from_local
        _patch_applied = True
        
        message = "ONNX Runtime patch applied successfully for parallel workers"
        logger.info(message)
        print(f"INFO: {message}", flush=True)
        
    except ImportError:
        logger.warning("Could not import tone.onnx_wrapper - patch will be applied when tone is imported")
    except Exception as e:
        logger.error(f"Failed to apply ONNX Runtime patch: {str(e)}")
