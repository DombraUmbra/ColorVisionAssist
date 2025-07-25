"""
Color Detection Package
Modular color detection system for ColorVisionAid

This package provides:
- ColorDetector: Main detection class (backward compatible)
- SkinToneFilters: Advanced skin tone filtering algorithms
- ColorDetectionAlgorithms: Core color detection and highlighting
- draw_text_with_utf8: UTF-8 text rendering utility
"""

from .detector import ColorDetector
from .filters import SkinToneFilters
from .algorithms import ColorDetectionAlgorithms
from .utils import draw_text_with_utf8

# Maintain backward compatibility
__all__ = [
    'ColorDetector',
    'SkinToneFilters', 
    'ColorDetectionAlgorithms',
    'draw_text_with_utf8'
]
