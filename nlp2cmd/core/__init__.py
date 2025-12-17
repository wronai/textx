"""Core functionality for NLP2CMD"""

from nlp2cmd.core.base import BaseConverter, ConversionResult
from nlp2cmd.core.pipeline import Pipeline

# ModelWrapper requires torch - import only when needed
try:
    from nlp2cmd.core.model import ModelWrapper
    __all__ = ["BaseConverter", "ConversionResult", "ModelWrapper", "Pipeline"]
except ImportError:
    # torch not available - ModelWrapper will not be available
    __all__ = ["BaseConverter", "ConversionResult", "Pipeline"]
