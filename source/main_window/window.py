"""
Main window class for ColorVisionAid
Contains the core window class with all functionality combined
"""

import os
import sys
import cv2
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer, QSettings
from PyQt5.QtGui import QIcon

# Import all required modules
from ..translations import translator as tr
from ..ui_components import ScreenshotGallery
from ..color_detection import ColorDetector
from .camera import CameraManager
from ..color_detection.utils import draw_text_with_utf8

# Import mixin classes
from .ui_setup import UISetup
from .camera_handlers import CameraHandlers
from .event_handlers import EventHandlers

class ColorVisionAid(QMainWindow, UISetup, CameraHandlers, EventHandlers):
    """
    Main application window combining all functionality through mixin classes
    """
    
    def __init__(self):
        super().__init__()
        
        # Load settings
        self.settings = QSettings("ColorVisionAid", "CVA")
        language = self.settings.value("language", "en")
        tr.set_language(language)
        
        # Load user preferences
        self.camera_permission = self.settings.value("camera_permission", "ask")  # "granted", "denied", "ask"
        
        # Create camera manager and color detector
        self.camera_manager = CameraManager(self)
        self.color_detector = ColorDetector()
        
        # UI setup (from UISetup mixin)
        self.setup_ui()
        
        # Timer for updating the camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
