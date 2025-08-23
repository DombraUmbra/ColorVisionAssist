"""
Whisper of Colors - Color vision aid application
This package contains modules for the Whisper of Colors application.

Modules:
- main: Main application and UI logic
- camera: Camera management and related UI features
- color_detection: Color detection algorithms
- gallery: Screenshots gallery
- translations: Multi-language support
- utils: Utility functions
- ui_components: UI component creation functions
"""

# Make main class directly accessible from package
from .main_window import ColorVisionAid

# Make frequently used components directly importable from package
from .main_window import CameraManager
from .color_detection import ColorDetector
from .ui_components import ScreenshotGallery
from .translations import translator
