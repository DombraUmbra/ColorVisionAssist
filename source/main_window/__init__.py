"""
Main Window package for ColorVisionAid
Provides the main application window with modular architecture
"""

from .window import ColorVisionAid
from .camera import CameraManager

__all__ = ['ColorVisionAid', 'CameraManager']
