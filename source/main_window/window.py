"""
Main window class for ColorVisionAid
Contains the core window class with all functionality combined
"""

import os
import sys
import cv2
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer, QSettings, Qt
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
        # Theme preference
        self.theme = self.settings.value("theme", "dark")

        # Load user preferences
        self.camera_permission = self.settings.value("camera_permission", "ask")  # "granted", "denied", "ask"

        # Create camera manager and color detector
        self.camera_manager = CameraManager(self)
        self.color_detector = ColorDetector()

        # UI setup (from UISetup mixin)
        self.setup_ui()
        
        # Apply theme after UI setup - try to make Windows frame dark-compatible
        from ..ui_components import apply_theme
        apply_theme(self, self.theme)
        self._apply_window_theme()
        
        # Also apply component-specific styles for current theme
        if hasattr(self, 'apply_theme_to_components'):
            self.apply_theme_to_components()
        
        # Force refresh all QGroupBox styling to ensure proper theme application
        self._force_refresh_group_boxes()
        
        # Ensure combo boxes get proper theme on startup
        from ..ui_components.groups import update_combo_themes
        update_combo_themes(self)

        # Timer for updating the camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
    def _apply_window_theme(self):
        """Apply theme-appropriate window styling"""
        if self.theme == 'dark':
            # Try to make Windows frame compatible with dark theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #EEE;
                }
            """)
        else:
            # Light theme - use default Windows styling
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #F5F5F7;
                    color: #222;
                }
            """)

    def _force_refresh_group_boxes(self):
        """Force refresh all QGroupBox widgets to apply proper theme styling"""
        from PyQt5.QtWidgets import QGroupBox
        from ..ui_components import apply_light_theme, apply_dark_theme
        
        # Debug: Print current theme
        print(f"Current theme in _force_refresh_group_boxes: {self.theme}")
        
        # Find all QGroupBox widgets in the main window
        group_boxes = self.findChildren(QGroupBox)
        print(f"Found {len(group_boxes)} QGroupBox widgets")
        
        for group_box in group_boxes:
            # Force repaint by temporarily hiding and showing
            group_box.hide()
            group_box.show()
            
            # Reapply theme-specific styling
            if self.theme == 'light':
                print(f"Applying light theme to QGroupBox: {group_box.title()}")
                group_box.setStyleSheet("""
                    QGroupBox {
                        border: 2px solid #DDD;
                        border-radius: 5px;
                        margin-top: 10px;
                        padding-top: 10px;
                        background-color: #F8F9FA;
                        font-size: 9pt;
                        color: #222;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        padding: 5px 8px;
                        font-weight: bold;
                        color: #1565C0;
                        background-color: transparent;
                    }
                """)
            else:
                print(f"Applying dark theme to QGroupBox: {group_box.title()}")
                group_box.setStyleSheet("""
                    QGroupBox {
                        border: 2px solid #555;
                        border-radius: 5px;
                        margin-top: 10px;
                        padding-top: 10px;
                        background-color: #444;
                        font-size: 9pt;
                        color: #EEE;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        padding: 5px 8px;
                        font-weight: bold;
                        color: #64B5F6;
                        background-color: transparent;
                    }
                """)
            
            # Force update
            group_box.update()
            group_box.repaint()