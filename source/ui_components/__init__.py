"""
UI Components package for ColorVisionAid
Modular UI component system with organized imports
"""

# Import all button functions
from .buttons import create_button, create_camera_controls

# Import all group creation functions  
from .groups import (
    create_color_blindness_type_group,
    create_color_detection_group,
    create_camera_settings_group,
    create_language_group,
    create_about_group
)

# Import styling functions
from .styles import apply_dark_theme, apply_light_theme, apply_theme, create_camera_interface

# Import dialog classes
from .dialogs import AdvancedSettingsDialog

# Import gallery component
from .gallery import ScreenshotGallery

# Backward compatibility - export all functions at package level
__all__ = [
    # Button functions
    'create_button',
    'create_camera_controls',
    
    # Group functions
    'create_color_blindness_type_group',
    'create_color_detection_group', 
    'create_camera_settings_group',
    'create_language_group',
    'create_about_group',
    
    # Style functions
    'apply_dark_theme',
    'apply_light_theme',
    'apply_theme',
    'create_camera_interface',
    
    # Dialog classes
    'AdvancedSettingsDialog',
    
    # Gallery component
    'ScreenshotGallery'
]
