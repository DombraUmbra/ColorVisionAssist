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
from ..profile_manager import ProfileManager, UserProfile

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

        # Initialize profile manager
        self.profile_manager = ProfileManager()
        
        # Load settings
        self.settings = QSettings("ColorVisionAid", "CVA")
        
        # Load current profile or create default
        current_profile_name = self.settings.value("current_profile", "Default Profile")
        self.current_profile = self.profile_manager.load_profile(current_profile_name)
        
        if not self.current_profile:
            # Create default profile if not found
            self.current_profile = self.profile_manager.create_profile("Default Profile")
            self.profile_manager.save_profile(self.current_profile)
        
        # Apply profile settings to QSettings
        self.profile_manager.apply_profile_to_settings(self.current_profile)
        
        # Set language and theme from profile
        language = self.current_profile.language
        tr.set_language(language)
        self.theme = self.current_profile.theme

        # Load user preferences from profile
        self.camera_permission = self.current_profile.camera_permission

        # Create camera manager and color detector
        self.camera_manager = CameraManager(self)
        self.color_detector = ColorDetector()

        # UI setup (from UISetup mixin)
        self.setup_ui()
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "icons", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
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
        
        # Apply theme to profile selector after main theme application
        if hasattr(self, 'profile_selector'):
            self.profile_selector.apply_theme()

        # Apply window position/size from profile only at startup
        self._apply_startup_window_properties()

        # Timer for updating the camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
    
    def _apply_startup_window_properties(self):
        """Apply window position and size from profile only at application startup"""
        if self.current_profile:
            try:
                # Apply window properties from profile
                if not self.current_profile.is_maximized:
                    self.resize(self.current_profile.window_width, self.current_profile.window_height)
                    self.move(self.current_profile.window_x, self.current_profile.window_y)
                else:
                    self.showMaximized()
            except Exception as e:
                print(f"Warning: Could not apply window properties from profile: {e}")
                # Use default window size if profile properties are invalid
                self.resize(1000, 600)
        
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
            
            # Windows 10/11 dark title bar support - delayed to ensure window is ready
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, self._apply_dark_title_bar)
                
        else:
            # Light theme - use default Windows styling
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #F5F5F7;
                    color: #222;
                }
            """)
            
            # Windows 10/11 light title bar - delayed to ensure window is ready
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, self._apply_light_title_bar)

    def _apply_dark_title_bar(self):
        """Apply dark title bar for Windows 10/11"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Get window handle
            hwnd = int(self.winId())
            
            # DWMWA_USE_IMMERSIVE_DARK_MODE
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            
            # Set dark mode for title bar
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(1)),
                ctypes.sizeof(ctypes.c_int)
            )
        except Exception as e:
            # Fallback - just print error, don't crash
            print(f"Could not apply dark title bar: {e}")

    def _apply_light_title_bar(self):
        """Apply light title bar for Windows 10/11"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Get window handle
            hwnd = int(self.winId())
            
            # DWMWA_USE_IMMERSIVE_DARK_MODE
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            
            # Set light mode for title bar
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(0)),
                ctypes.sizeof(ctypes.c_int)
            )
        except Exception as e:
            # Fallback - just print error, don't crash
            print(f"Could not apply light title bar: {e}")

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
                        font-weight: bold;
                        border: 2px solid #E0E0E0;
                        border-radius: 5px;
                        margin: 8px 0px;
                        padding-top: 10px;
                        background-color: #FAFAFA;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 10px;
                        padding: 0 8px 0 8px;
                        color: #1976D2;
                    }
                """)
            else:
                print(f"Applying dark theme to QGroupBox: {group_box.title()}")
                group_box.setStyleSheet("""
                    QGroupBox {
                        font-weight: bold;
                        border: 2px solid #444;
                        border-radius: 5px;
                        margin: 8px 0px;
                        padding-top: 10px;
                        background-color: #333;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 10px;
                        padding: 0 8px 0 8px;
                        color: #64B5F6;
                    }
                """)
            
            # Force update
            group_box.update()
            group_box.repaint()
    
    def _update_child_window_themes(self):
        """Update theme for any open child dialogs/windows"""
        from PyQt5.QtWidgets import QApplication
        from ..ui_components.dialogs import AdvancedSettingsDialog
        from ..ui_components.gallery import ScreenshotGallery
        
        # Find all open dialogs and galleries
        for window in QApplication.topLevelWidgets():
            if isinstance(window, AdvancedSettingsDialog):
                window.apply_dialog_theme(self.theme)
                # Apply title bar theme with delay
                QTimer.singleShot(50, lambda w=window: w._apply_dialog_title_bar(self.theme))
            elif isinstance(window, ScreenshotGallery):
                window.apply_gallery_theme(self.theme)
                # Force scroll area background with delay
                QTimer.singleShot(100, lambda w=window: w._force_scroll_area_background(self.theme))
                # Apply title bar theme with delay
                QTimer.singleShot(150, lambda w=window: w._apply_gallery_title_bar(self.theme))
    
    def resizeEvent(self, event):
        """Handle window resize events to update responsive UI elements"""
        super().resizeEvent(event)
        
        # Update camera interface with new responsive sizes if camera is not running
        if not self.camera_manager.camera_open:
            # Recreate camera interface with new responsive sizing
            from ..ui_components import create_camera_interface
            create_camera_interface(self, self.camera_feed_layout)
        
        # Update any existing camera permission interfaces
        self._update_camera_permission_interface_theme()
    
    def open_profile_manager(self):
        """Open profile management dialog"""
        from ..ui_components import ProfileDialog
        
        dialog = ProfileDialog(self, self.current_profile)
        dialog.profile_changed.connect(self.apply_profile)
        dialog.exec_()
    
    def apply_profile(self, profile: UserProfile):
        """Apply a profile to the application"""
        # Update current profile
        self.current_profile = profile
        
        # Apply profile settings
        self.profile_manager.apply_profile_to_settings(profile)
        
        # Update language if changed
        if tr.current_language != profile.language:
            tr.set_language(profile.language)
            self.retranslate_ui()
        
        # Update theme if changed
        if self.theme != profile.theme:
            self.theme = profile.theme
            from ..ui_components import apply_theme
            apply_theme(self, self.theme)
            self._apply_window_theme()
            
            # Apply theme to components
            if hasattr(self, 'apply_theme_to_components'):
                self.apply_theme_to_components()
            
            # Force refresh group boxes
            self._force_refresh_group_boxes()
            
            # Update child windows
            self._update_child_window_themes()
        
        # Update window geometry if specified in profile
        if profile.window_width > 0 and profile.window_height > 0:
            self.resize(profile.window_width, profile.window_height)
            
        if profile.window_x >= 0 and profile.window_y >= 0:
            self.move(profile.window_x, profile.window_y)
            
        if profile.is_maximized:
            self.showMaximized()
        
        # Update camera permission
        self.camera_permission = profile.camera_permission
        
        # Update status
        self.status_bar.showMessage(f"{tr.get_text('profile_applied')}: {profile.name}" if tr.get_text('profile_applied') != 'profile_applied' else f"Profile applied: {profile.name}")
        
        # Save the profile as current
        self.profile_manager.save_profile(profile)
    
    def save_current_settings_to_profile(self):
        """Save current application state to the current profile"""
        if not self.current_profile:
            return
        
        # Update profile with current settings
        self.current_profile.language = tr.current_language
        self.current_profile.theme = self.theme
        self.current_profile.camera_permission = self.camera_permission
        
        # Update window geometry
        self.current_profile.window_width = self.width()
        self.current_profile.window_height = self.height()
        self.current_profile.window_x = self.x()
        self.current_profile.window_y = self.y()
        self.current_profile.is_maximized = self.isMaximized()
        
        # Save advanced settings if available
        if hasattr(self, 'detection_sensitivity'):
            self.current_profile.detection_sensitivity = getattr(self, 'detection_sensitivity', 0.5)
        if hasattr(self, 'color_enhancement'):
            self.current_profile.color_enhancement = getattr(self, 'color_enhancement', True)
        if hasattr(self, 'voice_feedback'):
            self.current_profile.voice_feedback = getattr(self, 'voice_feedback', False)
        if hasattr(self, 'auto_detection'):
            self.current_profile.auto_detection = getattr(self, 'auto_detection', True)
        
        # Save to file
        self.profile_manager.save_profile(self.current_profile)
    
    def retranslate_ui(self):
        """Update UI texts when language changes"""
        # Update window title
        self.setWindowTitle(tr.get_text("app_title"))
        
        # Update status bar
        self.status_bar.showMessage(tr.get_text("ready"))
        
        # Recreate UI groups to update texts
        # This is a simplified approach - in production you might want more granular updates
        self.setup_settings_panel()
        
        # Update camera interface if not running
        if not self.camera_manager.camera_open:
            from ..ui_components import create_camera_interface
            create_camera_interface(self, self.camera_feed_layout)
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Save current settings to profile before closing
        self.save_current_settings_to_profile()
        
        # Call parent close event
        super().closeEvent(event)