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
        from ..translations import translator as tr
        current_profile_name = self.settings.value("current_profile", tr.get_text("default_profile"))
        self.current_profile = self.profile_manager.load_profile(current_profile_name)
        if not self.current_profile:
            self.current_profile = self.profile_manager.create_profile(tr.get_text("default_profile"))
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
        # Background dimming runtime flag (default enabled)
        self.background_dimming_enabled = True

        # UI setup (from UISetup mixin)
        self.setup_ui()

        # Apply current profile after UI is completely initialized
        # This ensures profile values override any default UI settings
        from PyQt5.QtCore import QTimer
        def apply_profile_after_ui_complete():
            if self.current_profile:
                try:
                    # Apply profile values to checkboxes
                    if hasattr(self, 'red_checkbox'):
                        self.red_checkbox.setChecked(getattr(self.current_profile, 'detect_red', True))
                    if hasattr(self, 'green_checkbox'):
                        self.green_checkbox.setChecked(getattr(self.current_profile, 'detect_green', True))
                    if hasattr(self, 'blue_checkbox'):
                        self.blue_checkbox.setChecked(getattr(self.current_profile, 'detect_blue', False))
                    if hasattr(self, 'yellow_checkbox'):
                        self.yellow_checkbox.setChecked(getattr(self.current_profile, 'detect_yellow', False))

                    # Apply sensitivity slider value
                    if hasattr(self, 'sensitivity_slider'):
                        sens = float(getattr(self.current_profile, 'detection_sensitivity', 0.5))
                        slider_val = max(1, min(10, int(round(sens * 10))))
                        self.sensitivity_slider.setValue(slider_val)

                    # Apply advanced settings flags
                    self.skin_tone_filtering_active = bool(getattr(self.current_profile, 'skin_tone_filtering_active', True))
                    self.stability_enhancement_active = bool(getattr(self.current_profile, 'stability_enhancement_active', True))
                    self.debug_mode_active = bool(getattr(self.current_profile, 'debug_mode_active', False))
                    # Load background dimming from settings/profile (default True)
                    try:
                        self.background_dimming_enabled = self.settings.value('background_dimming_enabled', True, type=bool)
                    except Exception:
                        self.background_dimming_enabled = True

                    # Apply color blindness type to dropdown
                    if hasattr(self, 'color_blindness_combo'):
                        color_blindness_type = getattr(self.current_profile, 'color_blindness_type', 'protanopia')
                        if color_blindness_type == "complete":
                            color_blindness_type = "custom"
                        try:
                            self.color_blindness_combo.blockSignals(True)
                            success = self.color_blindness_combo.setCurrentData(color_blindness_type)
                            if not success:
                                self.color_blindness_combo.setCurrentData('protanopia')
                        finally:
                            try:
                                self.color_blindness_combo.blockSignals(False)
                            except Exception:
                                pass
                        # Manually update button/accessibility accents since handler didn't run
                        try:
                            cb_type_final = self.color_blindness_combo.currentData() or color_blindness_type
                            if hasattr(self, 'update_button_colors_for_accessibility'):
                                self.update_button_colors_for_accessibility(cb_type_final)
                            if hasattr(self, '_apply_accessible_accent_colors'):
                                self._apply_accessible_accent_colors()
                        except Exception:
                            pass
                except Exception as e:
                    print(f"Warning: Could not apply profile values during UI setup: {e}")

        # Apply profile after a short delay to ensure all UI components are ready
        QTimer.singleShot(100, apply_profile_after_ui_complete)

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

    def _apply_advanced_settings_from_profile(self):
        """Apply persisted advanced settings (profile/QSettings) to runtime widgets."""
        try:
            # Sensitivity: profile stores 0.1–1.0, hidden slider expects 1–10
            if hasattr(self, 'sensitivity_slider') and self.current_profile:
                sens = getattr(self.current_profile, 'detection_sensitivity', None)
                if sens is None:
                    # Fallback to QSettings if profile missing the field
                    sens = float(self.settings.value('detection_sensitivity', 0.5))
                # Clamp and convert
                slider_val = max(1, min(10, int(round(float(sens) * 10))))
                self.sensitivity_slider.setValue(slider_val)

            # Optional booleans (if later persisted), keep existing defaults otherwise
            if hasattr(self, 'skin_tone_filtering_active'):
                val = self.settings.value('skin_tone_filtering_active', self.skin_tone_filtering_active, type=bool)
                self.skin_tone_filtering_active = val
            if hasattr(self, 'stability_enhancement_active'):
                val = self.settings.value('stability_enhancement_active', self.stability_enhancement_active, type=bool)
                self.stability_enhancement_active = val
            if hasattr(self, 'debug_mode_active'):
                val = self.settings.value('debug_mode_active', self.debug_mode_active, type=bool)
                self.debug_mode_active = val
            if hasattr(self, 'background_dimming_enabled'):
                val = self.settings.value('background_dimming_enabled', self.background_dimming_enabled, type=bool)
                self.background_dimming_enabled = val

            # Manual color selections for analysis (checkboxes)
            for key, attr in (
                ('detect_red', 'red_checkbox'),
                ('detect_green', 'green_checkbox'),
                ('detect_blue', 'blue_checkbox'),
                ('detect_yellow', 'yellow_checkbox'),
            ):
                if hasattr(self, attr):
                    checkbox = getattr(self, attr)
                    # Determine default from current checkbox state, fallback to profile
                    default_val = checkbox.isChecked()
                    if self.current_profile is not None:
                        default_val = bool(getattr(self.current_profile, key, default_val))
                    val = self.settings.value(key, default_val, type=bool)
                    try:
                        checkbox.blockSignals(True)
                        checkbox.setChecked(bool(val))
                    finally:
                        checkbox.blockSignals(False)
        except Exception as e:
            print(f"Warning: Could not apply advanced settings from profile: {e}")
        
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
        
        # Find all QGroupBox widgets in the main window
        group_boxes = self.findChildren(QGroupBox)
        
        for group_box in group_boxes:
            # Force repaint by temporarily hiding and showing
            group_box.hide()
            group_box.show()
            
            # Reapply theme-specific styling
            if self.theme == 'light':
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
        # After theme propagation, adjust accent colors if needed (e.g., tritanopia)
        try:
            self._apply_accessible_accent_colors()
        except Exception:
            pass

    def _apply_accessible_accent_colors(self):
        """Adjust accent hex codes in stylesheets based on color blindness type.
        - Tritanopia: ensure pink accents are converted to Start-button blue; do not convert blues to pink.
        - Others: revert any pink accents back to the app's default blue accents.
        """
        try:
            # Determine current color blindness type
            cb_type = None
            if hasattr(self, 'color_blindness_combo') and self.color_blindness_combo is not None:
                cb_type = self.color_blindness_combo.currentData()
            if not cb_type and hasattr(self, 'current_profile') and self.current_profile is not None:
                cb_type = getattr(self.current_profile, 'color_blindness_type', 'none')
            cb_type = cb_type or 'none'

            from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
            from ..ui_components.styles import adjust_color_brightness

            # Define palettes
            blue_primary = '#2196F3'
            blue_primary_alt = '#1976D2'
            blue_dark_ui = '#1E88E5'
            blue_darker = '#1565C0'
            blue_light = '#64B5F6'
            blue_lighter = '#90CAF9'
            blue_lightest = '#BBDEFB'

            pink = '#E91E63'
            pink_light = adjust_color_brightness(pink, 1.25)
            pink_lighter = adjust_color_brightness(pink, 1.45)
            # Start-button accessible blue used under tritanopia for green class
            start_blue = '#64B5F6'
            start_blue_light = adjust_color_brightness(start_blue, 1.2)
            start_blue_lighter = adjust_color_brightness(start_blue, 1.4)

            if str(cb_type).lower() == 'tritanopia':
                # Map existing pink accents -> Start-button blue; keep blues as blue
                replace_map = {
                    pink: start_blue,
                    pink_light: start_blue_light,
                    pink_lighter: start_blue_lighter,
                }
            else:
                # Map pinks -> blues (best-effort defaults)
                replace_map = {
                    pink: blue_primary,
                    pink_light: blue_light,
                    pink_lighter: blue_lighter,
                }

            # Build target list: main window + its children + open dialogs/galleries with their children
            targets = [self] + self.findChildren(QWidget)
            try:
                from ..ui_components.dialogs import AdvancedSettingsDialog
                from ..ui_components.gallery import ScreenshotGallery
                for w in QApplication.topLevelWidgets():
                    if isinstance(w, (AdvancedSettingsDialog, ScreenshotGallery)):
                        targets.append(w)
                        targets.extend(w.findChildren(QWidget))
            except Exception:
                pass

            for widget in targets:
                try:
                    # Skip replacing accents on specific widgets and all QPushButtons.
                    # Buttons already apply CB-aware styles via update_button_theme; don't override them here.
                    try:
                        if widget.objectName() in ('camera_start_button', 'gallery_button', 'permission_deny_button'):
                            continue
                    except Exception:
                        pass
                    try:
                        if isinstance(widget, QPushButton):
                            continue
                    except Exception:
                        pass
                    ss = widget.styleSheet() or ''
                    if not ss:
                        continue
                    new_ss = ss
                    for old, new in replace_map.items():
                        new_ss = new_ss.replace(old, new).replace(old.lower(), new)
                    if new_ss != ss:
                        widget.setStyleSheet(new_ss)
                        widget.update()
                except Exception:
                    continue
        except Exception:
            pass

    def _update_child_window_languages(self):
        """Update language texts for any open child dialogs/windows."""
        try:
            from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget
            from ..ui_components.dialogs import AdvancedSettingsDialog
            from ..ui_components.gallery import ScreenshotGallery
            from ..translations import translator as tr

            for window in QApplication.topLevelWidgets():
                if isinstance(window, ScreenshotGallery):
                    # Update all texts and refresh to update dynamic labels (e.g., counts)
                    try:
                        window.update_ui_language()
                    except Exception:
                        pass
                    try:
                        # Re-apply sort styles to reflect any language-specific spacing
                        window._apply_sort_styles(getattr(self, 'theme', 'dark'))
                    except Exception:
                        pass
                    try:
                        # Refresh to recalc info label with localized prefix
                        window.refresh_gallery()
                    except Exception:
                        pass
                elif isinstance(window, AdvancedSettingsDialog):
                    # Best-effort: rebuild simple texts by recreating the dialog labels/buttons
                    try:
                        window.setWindowTitle(tr.get_text("advanced_settings"))
                        # Recreate tab titles
                        # If tab widget exists and supports setTabText, update with localized short titles
                        for child in window.findChildren(QWidget):
                            # TabWidget identification through property check
                            try:
                                if isinstance(child, QTabWidget):
                                    # Update 3 tabs if present
                                    titles = [
                                        tr.get_text("color_selection_short"),
                                        tr.get_text("parameters_short"),
                                        tr.get_text("filtering_short"),
                                    ]
                                    for i, title in enumerate(titles):
                                        if i < child.count():
                                            child.setTabText(i, title)
                            except Exception:
                                pass
                    except Exception:
                        pass
        except Exception:
            pass
    
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
            
            # Debug: Check if gallery window exists
            print(f"Main window: Theme changed to {self.theme}")
            print(f"Main window: Has gallery window: {hasattr(self, '_gallery_window')}")
            if hasattr(self, '_gallery_window'):
                print(f"Main window: Gallery window is None: {self._gallery_window is None}")
            
            # Update open gallery window if exists
            if hasattr(self, '_gallery_window') and self._gallery_window is not None:
                try:
                    print(f"Main window: Updating gallery theme from {getattr(self._gallery_window, 'theme', 'unknown')} to {self.theme}")
                    self._gallery_window.theme = self.theme
                    self._gallery_window.apply_gallery_theme(self.theme)
                    self._gallery_window._force_complete_theme_application(self.theme)
                    print(f"Main window: Gallery theme update completed")
                except Exception as e:
                    print(f"Error updating gallery theme: {e}")
            else:
                print(f"Main window: No gallery window to update")
            
            # Force refresh group boxes
            self._force_refresh_group_boxes()
            
            # Update child windows
            self._update_child_window_themes()
        
        # Update window geometry if specified in profile (clamp to available screen size)
        if profile.window_width > 0 and profile.window_height > 0:
            try:
                from PyQt5.QtWidgets import QApplication
                avail = QApplication.desktop().availableGeometry(self)
                new_w = min(max(100, int(profile.window_width)), avail.width())
                new_h = min(max(100, int(profile.window_height)), avail.height())
                self.resize(new_w, new_h)
            except Exception:
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
        # Detection sensitivity from hidden slider (1-10) -> 0.1-1.0
        try:
            if hasattr(self, 'sensitivity_slider') and self.sensitivity_slider is not None:
                self.current_profile.detection_sensitivity = float(self.sensitivity_slider.value()) / 10.0
                # Keep QSettings in sync for restart consistency
                if hasattr(self, 'settings'):
                    self.settings.setValue('detection_sensitivity', self.current_profile.detection_sensitivity)
        except Exception:
            pass

        if hasattr(self, 'color_enhancement'):
            self.current_profile.color_enhancement = getattr(self, 'color_enhancement', True)
        if hasattr(self, 'voice_feedback'):
            self.current_profile.voice_feedback = getattr(self, 'voice_feedback', False)
        if hasattr(self, 'auto_detection'):
            self.current_profile.auto_detection = getattr(self, 'auto_detection', True)

        # Manual color selections
        try:
            if hasattr(self, 'red_checkbox'):
                self.current_profile.detect_red = bool(self.red_checkbox.isChecked())
            if hasattr(self, 'green_checkbox'):
                self.current_profile.detect_green = bool(self.green_checkbox.isChecked())
            if hasattr(self, 'blue_checkbox'):
                self.current_profile.detect_blue = bool(self.blue_checkbox.isChecked())
            if hasattr(self, 'yellow_checkbox'):
                self.current_profile.detect_yellow = bool(self.yellow_checkbox.isChecked())
        except Exception:
            pass

        # Additional advanced flags
        try:
            if hasattr(self, 'skin_tone_filtering_active'):
                self.current_profile.skin_tone_filtering_active = bool(self.skin_tone_filtering_active)
            if hasattr(self, 'stability_enhancement_active'):
                self.current_profile.stability_enhancement_active = bool(self.stability_enhancement_active)
            if hasattr(self, 'debug_mode_active'):
                self.current_profile.debug_mode_active = bool(self.debug_mode_active)
        except Exception:
            pass
        
        # Save to file
        self.profile_manager.save_profile(self.current_profile)
        # Also reflect into QSettings for immediate persistence
        try:
            self.profile_manager.apply_profile_to_settings(self.current_profile)
        except Exception:
            pass
    
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