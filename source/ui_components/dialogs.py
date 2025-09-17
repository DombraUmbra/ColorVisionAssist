"""
Dialog windows for ColorVisionAid
Contains advanced settings dialog and other dialog components
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QWidget, QLabel, QCheckBox, QPushButton, QSlider, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from ..translations import translator as tr
from .buttons import update_button_theme

class AdvancedSettingsDialog(QDialog):
    """Advanced settings dialog - Compatible design with main application"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._canceled = False  # Track if user explicitly canceled
        self.setWindowTitle(tr.get_text("advanced_settings"))
        self.setModal(True)
        
        # Remove context help button for all themes
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # Set application icon
        import os
        from PyQt5.QtGui import QIcon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "icons", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Responsive sizing - Adapt to screen size
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.desktop().screenGeometry()
        width = min(max(650, int(screen.width() * 0.65)), 900)
        height = min(max(700, int(screen.height() * 0.75)), 950)
        
        self.setMinimumSize(width, height)
        self.setMaximumSize(width + 150, height + 150)
        self.resize(width, height)
        
        # Initialize dialog checkboxes
        self.red_checkbox = None
        self.green_checkbox = None
        self.blue_checkbox = None
        self.yellow_checkbox = None
        
        self.setup()
        # Capture initial state after UI is built
        self._capture_initial_state()

    def set_color_checkboxes(self, red: bool, green: bool, blue: bool, yellow: bool):
        """Sync checkbox states from parent while dialog is open."""
        print(f"[DEBUG] AdvancedSettingsDialog.set_color_checkboxes called: red={red}, green={green}, blue={blue}, yellow={yellow}")
        try:
            if hasattr(self, 'red_checkbox') and self.red_checkbox is not None:
                self.red_checkbox.setChecked(bool(red))
                print(f"[DEBUG] Dialog red checkbox set to: {bool(red)}")
            if hasattr(self, 'green_checkbox') and self.green_checkbox is not None:
                self.green_checkbox.setChecked(bool(green))
                print(f"[DEBUG] Dialog green checkbox set to: {bool(green)}")
            if hasattr(self, 'blue_checkbox') and self.blue_checkbox is not None:
                self.blue_checkbox.setChecked(bool(blue))
                print(f"[DEBUG] Dialog blue checkbox set to: {bool(blue)}")
            if hasattr(self, 'yellow_checkbox') and self.yellow_checkbox is not None:
                self.yellow_checkbox.setChecked(bool(yellow))
                print(f"[DEBUG] Dialog yellow checkbox set to: {bool(yellow)}")
            try:
                self.update()
                self.repaint()
                print(f"[DEBUG] Dialog updated and repainted")
            except Exception as e:
                print(f"[DEBUG] Dialog update/repaint failed: {e}")
        except Exception as e:
            print(f"[DEBUG] set_color_checkboxes failed: {e}")

    def _capture_initial_state(self):
        """Snapshot initial values to detect unsaved changes on close."""
        self._initial_state = self._get_current_state()

    def _get_current_state(self) -> dict:
        """Return current control values as a comparable dict."""
        state = {}
        try:
            if hasattr(self, 'red_checkbox') and self.red_checkbox is not None:
                state['red'] = bool(self.red_checkbox.isChecked())
            if hasattr(self, 'green_checkbox') and self.green_checkbox is not None:
                state['green'] = bool(self.green_checkbox.isChecked())
            if hasattr(self, 'blue_checkbox') and self.blue_checkbox is not None:
                state['blue'] = bool(self.blue_checkbox.isChecked())
            if hasattr(self, 'yellow_checkbox') and self.yellow_checkbox is not None:
                state['yellow'] = bool(self.yellow_checkbox.isChecked())
            if hasattr(self, 'sensitivity_slider') and self.sensitivity_slider is not None:
                state['sensitivity'] = int(self.sensitivity_slider.value())
            if hasattr(self, 'skin_tone_filtering') and self.skin_tone_filtering is not None:
                state['skin_tone_filtering'] = bool(self.skin_tone_filtering.isChecked())
            if hasattr(self, 'stability_enhancement') and self.stability_enhancement is not None:
                state['stability_enhancement'] = bool(self.stability_enhancement.isChecked())
            if hasattr(self, 'debug_mode') and self.debug_mode is not None:
                state['debug_mode'] = bool(self.debug_mode.isChecked())
            if hasattr(self, 'disable_background_dimming') and self.disable_background_dimming is not None:
                state['disable_background_dimming'] = bool(self.disable_background_dimming.isChecked())
        except Exception:
            # In case of any unexpected widget errors, return what we have
            pass
        return state

    def _has_unsaved_changes(self) -> bool:
        """Compare current state to initial snapshot."""
        try:
            current = self._get_current_state()
            initial = getattr(self, '_initial_state', {})
            return current != initial
        except Exception:
            # Be conservative: assume changes to avoid silent data loss
            return True

    def _get_theme(self) -> str:
        """Return current theme ('light' or 'dark') inherited from parent if available."""
        return (getattr(self.parent, 'theme', 'dark') if self.parent else 'dark').lower()
        
    def setup(self):
        """Set up dialog layout - Compatible with main application theme"""
        # Create main content layout
        content_layout = QVBoxLayout(self)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Create tab widget - Compatible with main theme
        tab_widget = QTabWidget()
        if self._get_theme() == 'light':
            tab_widget.setStyleSheet(
                """
                QTabWidget::pane { border: 2px solid #DDD; border-radius: 5px; background-color: #FFFFFF; padding: 10px; margin-top: 5px; }
                QTabBar::tab { background-color: #EDEFF1; color: #222; padding: 12px 14px; margin: 1px; border-radius: 3px; font-size: 9pt; min-width: 70px; max-width: 120px; border: 1px solid #D0D4D9; }
                QTabBar::tab:selected { background-color: #1976D2; color: white; font-weight: bold; border: 1px solid #1976D2; }
                QTabBar::tab:hover { background-color: #F5F6F7; }
                """
            )
        else:
            tab_widget.setStyleSheet(
                """
                QTabWidget::pane { border: 2px solid #555; border-radius: 5px; background-color: #444; padding: 10px; margin-top: 5px; }
                QTabBar::tab { background-color: #555; color: #EEE; padding: 12px 14px; margin: 1px; border-radius: 3px; font-size: 9pt; min-width: 70px; max-width: 120px; }
                QTabBar::tab:selected { background-color: #2196F3; color: white; font-weight: bold; }
                QTabBar::tab:hover { background-color: #666; }
                """
            )

        # Tabs
        color_tab = self.create_color_tab()
        tab_widget.addTab(color_tab, tr.get_text("color_selection_short"))

        parameters_tab = self.create_parameters_tab()
        tab_widget.addTab(parameters_tab, tr.get_text("parameters_short"))

        filtering_tab = self.create_filtering_tab()
        tab_widget.addTab(filtering_tab, tr.get_text("filtering_short"))

        content_layout.addWidget(tab_widget)

        # Buttons
        button_layout = self.create_button_layout()
        content_layout.addLayout(button_layout)

        # Apply main theme
        theme = getattr(self.parent, 'theme', 'dark') if self.parent else 'dark'
        self.apply_dialog_theme(theme)

        # Apply title bar theme with delay
        QTimer.singleShot(100, lambda: self._apply_dialog_title_bar(theme))
        
    def apply_dialog_theme(self, theme: str = 'dark'):
        """Apply main theme for dialog (dark or light)"""
        if (theme or 'dark').lower() == 'light':
            self.setStyleSheet("""
                QDialog { 
                    background-color: #F5F5F7; 
                    color: #222; 
                }
                QWidget { background-color: #F5F5F7; color: #222; }
                QScrollArea { background-color: #F5F5F7; border: none; }
                QScrollArea > QWidget > QWidget { background-color: #F5F5F7; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { 
                    background-color: #2b2b2b; 
                    color: #EEE; 
                    border: 1px solid #555;
                }
                QWidget { background-color: #2b2b2b; color: #EEE; }
                QScrollArea { background-color: #2b2b2b; border: none; }
                QScrollArea > QWidget > QWidget { background-color: #2b2b2b; }
            """)

    def _apply_dialog_title_bar(self, theme: str):
        """Apply theme-appropriate title bar for dialog"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Get window handle
            hwnd = int(self.winId())
            
            # DWMWA_USE_IMMERSIVE_DARK_MODE
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            
            # Set dark/light mode for title bar
            mode_value = 1 if (theme or 'dark').lower() == 'dark' else 0
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(mode_value)),
                ctypes.sizeof(ctypes.c_int)
            )
        except Exception as e:
            # Fallback - just print error, don't crash
            print(f"Could not apply dialog title bar theme: {e}")
        
    def create_color_tab(self):
        """Create color selection tab - Compatible with main theme"""
        color_tab = QWidget()
        color_layout = QVBoxLayout(color_tab)
        color_layout.setSpacing(12)
        color_layout.setContentsMargins(10, 10, 10, 10)
        
        # Description - Main application style
        description = QLabel(tr.get_text("manual_color_selection_desc"))
        description.setWordWrap(True)
        if self._get_theme() == 'light':
            description.setStyleSheet("""
                QLabel { color: #444; font-size: 9pt; padding: 10px; background-color: #F1F3F4; border-radius: 5px; border-left: 4px solid #1976D2; line-height: 1.4; }
            """)
        else:
            description.setStyleSheet("""
                QLabel { color: #CCC; font-size: 9pt; padding: 10px; background-color: #3A3A3A; border-radius: 5px; border-left: 4px solid #2196F3; line-height: 1.4; }
            """)
        color_layout.addWidget(description)
        
        # Color selection group - Main application GroupBox style
        color_group = QGroupBox(tr.get_text("select_colors_to_detect"))
        if self._get_theme() == 'light':
            color_group.setStyleSheet("""
                QGroupBox { color: #222; font-size: 10pt; font-weight: bold; border: 2px solid #DDD; border-radius: 8px; margin-top: 12px; padding-top: 15px; background-color: #FFFFFF; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 8px; color: #1976D2; font-size: 10pt; font-weight: bold; }
                QGroupBox:hover { border: 2px solid #1976D2; }
            """)
        else:
            color_group.setStyleSheet("""
                QGroupBox { color: #EEE; font-size: 10pt; font-weight: bold; border: 2px solid #555; border-radius: 8px; margin-top: 12px; padding-top: 15px; background-color: #444; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 8px; color: #2196F3; font-size: 10pt; font-weight: bold; }
                QGroupBox:hover { border: 2px solid #2196F3; }
            """)
        
        color_layout_inner = QVBoxLayout()
        color_layout_inner.setSpacing(10)
        color_layout_inner.setContentsMargins(15, 10, 15, 15)
        
        # Create checkboxes - Main application style
        self.red_checkbox = QCheckBox(tr.get_text("detect_red"))
        self.green_checkbox = QCheckBox(tr.get_text("detect_green"))
        self.blue_checkbox = QCheckBox(tr.get_text("detect_blue"))
        self.yellow_checkbox = QCheckBox(tr.get_text("detect_yellow"))
        
        # Get current detection settings from main window or use defaults based on color blindness type
        print(f"[DEBUG] Dialog init - Getting detection settings from parent")
        
        # Initialize with default values based on color blindness type
        red_checked = True
        green_checked = True  
        blue_checked = False
        yellow_checked = False
        
        # Get current detection settings from parent if available
        if hasattr(self.parent, 'current_detection_settings') and self.parent.current_detection_settings:
            detection_settings = self.parent.current_detection_settings
            red_checked = detection_settings.get('red', True)
            green_checked = detection_settings.get('green', True)
            blue_checked = detection_settings.get('blue', False)
            yellow_checked = detection_settings.get('yellow', False)
            print(f"[DEBUG] Using parent detection settings: {detection_settings}")
        else:
            # Fallback: use color blindness type to determine defaults
            try:
                cb_type = self.parent.color_blindness_combo.currentData()
                if cb_type in ['protanopia', 'deuteranopia']:
                    red_checked = True
                    green_checked = True
                    blue_checked = False
                    yellow_checked = False
                elif cb_type == 'tritanopia':
                    red_checked = False
                    green_checked = False
                    blue_checked = True
                    yellow_checked = True
                print(f"[DEBUG] Using color blindness type defaults for {cb_type}")
            except:
                print("[DEBUG] Failed to get color blindness type, using defaults")
        
        self.red_checkbox.setChecked(red_checked)
        self.green_checkbox.setChecked(green_checked)
        self.blue_checkbox.setChecked(blue_checked)
        self.yellow_checkbox.setChecked(yellow_checked)
        
        print(f"[DEBUG] Dialog checkboxes after setting:")
        print(f"[DEBUG] Dialog red_checkbox.isChecked(): {self.red_checkbox.isChecked()}")
        print(f"[DEBUG] Dialog green_checkbox.isChecked(): {self.green_checkbox.isChecked()}")
        print(f"[DEBUG] Dialog blue_checkbox.isChecked(): {self.blue_checkbox.isChecked()}")
        print(f"[DEBUG] Dialog yellow_checkbox.isChecked(): {self.yellow_checkbox.isChecked()}")

        # If none selected, enforce automatic defaults based on current CB type
        try:
            if not (self.red_checkbox.isChecked() or self.green_checkbox.isChecked() or self.blue_checkbox.isChecked() or self.yellow_checkbox.isChecked()):
                cb_type = None
                try:
                    if hasattr(self.parent, 'color_blindness_combo') and self.parent.color_blindness_combo is not None:
                        cb_type = self.parent.color_blindness_combo.currentData()
                except Exception:
                    cb_type = 'none'
                cb_type = (cb_type or 'none').lower()
                if cb_type in ('protanopia', 'deuteranopia'):
                    # Select Red + Green
                    self.red_checkbox.setChecked(True)
                    self.green_checkbox.setChecked(True)
                    self.blue_checkbox.setChecked(False)
                    self.yellow_checkbox.setChecked(False)
                    # Sync back to parent immediately for consistency
                    try:
                        if hasattr(self.parent, '_apply_detect_flags'):
                            self.parent._apply_detect_flags(True, True, False, False, persist=True)
                    except Exception:
                        pass
                elif cb_type == 'tritanopia':
                    # Select Blue + Yellow
                    self.red_checkbox.setChecked(False)
                    self.green_checkbox.setChecked(False)
                    self.blue_checkbox.setChecked(True)
                    self.yellow_checkbox.setChecked(True)
                    try:
                        if hasattr(self.parent, '_apply_detect_flags'):
                            self.parent._apply_detect_flags(False, False, True, True, persist=True)
                    except Exception:
                        pass
                else:
                    # Leave as-is for 'none' or unknown
                    pass
        except Exception:
            pass
        
        # Main application checkbox style
        if self._get_theme() == 'light':
            checkbox_style = """
                QCheckBox { color: #222; font-size: 10pt; spacing: 10px; padding: 8px; background-color: #F5F6F7; border-radius: 4px; margin: 2px 0; }
                QCheckBox:hover { color: #1976D2; background-color: #ECEFF1; }
                QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px; border: 2px solid #BBB; background-color: #FFF; }
                QCheckBox::indicator:checked { background-color: #1976D2; border: 2px solid #1976D2; }
                QCheckBox::indicator:hover { border: 2px solid #64B5F6; }
            """
        else:
            checkbox_style = """
                QCheckBox { color: #EEE; font-size: 10pt; spacing: 10px; padding: 8px; background-color: #3A3A3A; border-radius: 4px; margin: 2px 0; }
                QCheckBox:hover { color: #2196F3; background-color: #454545; }
                QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px; border: 2px solid #666; background-color: #333; }
                QCheckBox::indicator:checked { background-color: #2196F3; border: 2px solid #2196F3; }
                QCheckBox::indicator:hover { border: 2px solid #64B5F6; }
            """
        
        for checkbox in [self.red_checkbox, self.green_checkbox, self.blue_checkbox, self.yellow_checkbox]:
            checkbox.setStyleSheet(checkbox_style)
        
        # Tooltips
        self.red_checkbox.setToolTip(tr.get_text("red_checkbox_tooltip"))
        self.green_checkbox.setToolTip(tr.get_text("green_checkbox_tooltip"))
        self.blue_checkbox.setToolTip(tr.get_text("blue_checkbox_tooltip"))
        self.yellow_checkbox.setToolTip(tr.get_text("yellow_checkbox_tooltip"))
        
        # Add checkboxes
        color_layout_inner.addWidget(self.red_checkbox)
        color_layout_inner.addWidget(self.green_checkbox)
        color_layout_inner.addWidget(self.blue_checkbox)
        color_layout_inner.addWidget(self.yellow_checkbox)
        
        color_group.setLayout(color_layout_inner)
        color_layout.addWidget(color_group)
        
        color_layout.addStretch()
        return color_tab
    
    def create_parameters_tab(self):
        """Create detection parameters tab - Compatible with main theme"""
        parameters_tab = QWidget()
        parameters_layout = QVBoxLayout(parameters_tab)
        parameters_layout.setSpacing(15)
        parameters_layout.setContentsMargins(10, 10, 10, 10)
        
        # Description
        description = QLabel(tr.get_text("detection_parameters_desc"))
        description.setWordWrap(True)
        if self._get_theme() == 'light':
            description.setStyleSheet("""
                QLabel { color: #444; font-size: 9pt; padding: 8px; background-color: #F1F3F4; border-radius: 3px; border-left: 3px solid #1976D2; }
            """)
        else:
            description.setStyleSheet("""
                QLabel { color: #CCC; font-size: 9pt; padding: 8px; background-color: #3A3A3A; border-radius: 3px; border-left: 3px solid #2196F3; }
            """)
        parameters_layout.addWidget(description)
        
        # Sensitivity group - Main application style
        sensitivity_group = QGroupBox(tr.get_text("real_world_sensitivity"))
        if self._get_theme() == 'light':
            sensitivity_group.setStyleSheet("""
                QGroupBox { color: #222; font-size: 10pt; border: 2px solid #DDD; border-radius: 5px; margin-top: 10px; padding-top: 10px; background-color: #FFFFFF; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 5px; color: #1976D2; }
                QGroupBox:hover { border: 2px solid #1976D2; }
            """)
        else:
            sensitivity_group.setStyleSheet("""
                QGroupBox { color: #EEE; font-size: 10pt; border: 2px solid #555; border-radius: 5px; margin-top: 10px; padding-top: 10px; background-color: #444; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 5px; color: #2196F3; }
                QGroupBox:hover { border: 2px solid #2196F3; }
            """)
        
        sensitivity_layout = QVBoxLayout()
        
        # Sensitivity slider - Main application style
        slider_layout = QHBoxLayout()
        
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(1, 10)
        self.sensitivity_slider.setValue(self.parent.sensitivity_slider.value())
        
        # Main application slider style
        if self._get_theme() == 'light':
            self.sensitivity_slider.setStyleSheet("""
                QSlider::groove:horizontal { height: 8px; background: #E0E0E0; border-radius: 4px; }
                QSlider::handle:horizontal { background: #1976D2; border: 1px solid #1976D2; width: 18px; margin: -2px 0; border-radius: 9px; }
                QSlider::handle:horizontal:hover { background: #42A5F5; border: 1px solid #90CAF9; width: 20px; margin: -3px 0; }
            """)
        else:
            self.sensitivity_slider.setStyleSheet("""
                QSlider::groove:horizontal { height: 8px; background: #333; border-radius: 4px; }
                QSlider::handle:horizontal { background: #2196F3; border: 1px solid #2196F3; width: 18px; margin: -2px 0; border-radius: 9px; }
                QSlider::handle:horizontal:hover { background: #64B5F6; border: 1px solid #90CAF9; width: 20px; margin: -3px 0; }
            """)
        
        slider_layout.addWidget(self.sensitivity_slider)
        
        # Value label
        self.sensitivity_value_label = QLabel(str(self.sensitivity_slider.value()))
        if self._get_theme() == 'light':
            self.sensitivity_value_label.setStyleSheet("""
                QLabel { color: #1976D2; font-size: 12pt; font-weight: bold; padding: 2px 8px; background-color: #EDEFF1; border-radius: 3px; min-width: 20px; }
            """)
        else:
            self.sensitivity_value_label.setStyleSheet("""
                QLabel { color: #2196F3; font-size: 12pt; font-weight: bold; padding: 2px 8px; background-color: #555; border-radius: 3px; min-width: 20px; }
            """)
        self.sensitivity_value_label.setAlignment(Qt.AlignCenter)
        slider_layout.addWidget(self.sensitivity_value_label)
        
        self.sensitivity_slider.valueChanged.connect(self.sensitivity_changed)
        sensitivity_layout.addLayout(slider_layout)
        
        # Sensitivity description
        self.sensitivity_description = QLabel(self.get_sensitivity_description(self.sensitivity_slider.value()))
        self.sensitivity_description.setWordWrap(True)
        if self._get_theme() == 'light':
            self.sensitivity_description.setStyleSheet("""
                QLabel { color: #555; font-size: 9pt; padding: 8px; background-color: #F1F3F4; border-radius: 3px; margin-top: 5px; }
            """)
        else:
            self.sensitivity_description.setStyleSheet("""
                QLabel { color: #BBB; font-size: 9pt; padding: 8px; background-color: #3A3A3A; border-radius: 3px; margin-top: 5px; }
            """)
        sensitivity_layout.addWidget(self.sensitivity_description)
        
        sensitivity_group.setLayout(sensitivity_layout)
        parameters_layout.addWidget(sensitivity_group)
        
        parameters_layout.addStretch()
        return parameters_tab
    
    def create_filtering_tab(self):
        """Create filtering tab - Compatible with main theme"""
        filtering_tab = QWidget()
        filtering_layout = QVBoxLayout(filtering_tab)
        filtering_layout.setSpacing(15)
        filtering_layout.setContentsMargins(10, 10, 10, 10)
        
        # Description
        description = QLabel(tr.get_text("color_filtering_desc"))
        description.setWordWrap(True)
        if self._get_theme() == 'light':
            description.setStyleSheet("""
                QLabel { color: #444; font-size: 9pt; padding: 8px; background-color: #F1F3F4; border-radius: 3px; border-left: 3px solid #1976D2; }
            """)
        else:
            description.setStyleSheet("""
                QLabel { color: #CCC; font-size: 9pt; padding: 8px; background-color: #3A3A3A; border-radius: 3px; border-left: 3px solid #2196F3; }
            """)
        filtering_layout.addWidget(description)
        
        # Skin tone filtering group - Main application style
        skin_tone_group = QGroupBox(tr.get_text("skin_tone_filtering"))
        if self._get_theme() == 'light':
            skin_tone_group.setStyleSheet("""
                QGroupBox { color: #222; font-size: 10pt; border: 2px solid #DDD; border-radius: 5px; margin-top: 10px; padding-top: 10px; background-color: #FFFFFF; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 5px; color: #1976D2; }
                QGroupBox:hover { border: 2px solid #1976D2; }
            """)
        else:
            skin_tone_group.setStyleSheet("""
                QGroupBox { color: #EEE; font-size: 10pt; border: 2px solid #555; border-radius: 5px; margin-top: 10px; padding-top: 10px; background-color: #444; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 5px; color: #2196F3; }
                QGroupBox:hover { border: 2px solid #2196F3; }
            """)
        
        skin_tone_layout = QVBoxLayout()
        
        self.skin_tone_filtering = QCheckBox(tr.get_text("enable_skin_tone_filtering"))
        self.skin_tone_filtering.setChecked(self.parent.skin_tone_filtering_active)  # Load current value from main application
        self.skin_tone_filtering.setToolTip(tr.get_text("skin_tone_filtering_tooltip"))
        if self._get_theme() == 'light':
            self.skin_tone_filtering.setStyleSheet("""
                QCheckBox { color: #222; font-size: 10pt; spacing: 8px; padding: 5px; }
                QCheckBox:hover { color: #1976D2; }
            """)
        else:
            self.skin_tone_filtering.setStyleSheet("""
                QCheckBox { color: #EEE; font-size: 10pt; spacing: 8px; padding: 5px; }
                QCheckBox:hover { color: #2196F3; }
            """)
        skin_tone_layout.addWidget(self.skin_tone_filtering)
        
        # Skin tone description
        skin_tone_description = QLabel(tr.get_text("skin_tone_filtering_explanation"))
        skin_tone_description.setWordWrap(True)
        if self._get_theme() == 'light':
            skin_tone_description.setStyleSheet("""
                QLabel { color: #555; font-size: 9pt; padding: 8px; background-color: #F1F3F4; border-radius: 3px; }
            """)
        else:
            skin_tone_description.setStyleSheet("""
                QLabel { color: #BBB; font-size: 9pt; padding: 8px; background-color: #3A3A3A; border-radius: 3px; }
            """)
        skin_tone_layout.addWidget(skin_tone_description)
        
        # Debug mode checkbox
        self.debug_mode = QCheckBox(tr.get_text("debug_mode"))
        self.debug_mode.setChecked(self.parent.debug_mode_active)
        self.debug_mode.setToolTip(tr.get_text("debug_mode_tooltip"))
        if self._get_theme() == 'light':
            self.debug_mode.setStyleSheet("""
                QCheckBox { color: #222; font-size: 10pt; spacing: 8px; padding: 5px; }
                QCheckBox:hover { color: #1976D2; }
            """)
        else:
            self.debug_mode.setStyleSheet("""
                QCheckBox { color: #EEE; font-size: 10pt; spacing: 8px; padding: 5px; }
                QCheckBox:hover { color: #2196F3; }
            """)
        skin_tone_layout.addWidget(self.debug_mode)
        
        skin_tone_group.setLayout(skin_tone_layout)
        filtering_layout.addWidget(skin_tone_group)
        
        # Stability group - Main application style
        stability_group = QGroupBox(tr.get_text("stability_enhancement"))
        if self._get_theme() == 'light':
            stability_group.setStyleSheet("""
                QGroupBox { color: #222; font-size: 10pt; border: 2px solid #DDD; border-radius: 5px; margin-top: 10px; padding-top: 10px; background-color: #FFFFFF; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 5px; color: #1976D2; }
                QGroupBox:hover { border: 2px solid #1976D2; }
            """)
        else:
            stability_group.setStyleSheet("""
                QGroupBox { color: #EEE; font-size: 10pt; border: 2px solid #555; border-radius: 5px; margin-top: 10px; padding-top: 10px; background-color: #444; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 5px; color: #2196F3; }
                QGroupBox:hover { border: 2px solid #2196F3; }
            """)
        
        stability_layout = QVBoxLayout()
        
        self.stability_enhancement = QCheckBox(tr.get_text("enable_stability_enhancement"))
        self.stability_enhancement.setChecked(self.parent.stability_enhancement_active)  # Load current value from main application
        self.stability_enhancement.setToolTip(tr.get_text("stability_enhancement_tooltip"))
        if self._get_theme() == 'light':
            self.stability_enhancement.setStyleSheet("""
                QCheckBox { color: #222; font-size: 10pt; spacing: 8px; padding: 5px; }
                QCheckBox:hover { color: #1976D2; }
            """)
        else:
            self.stability_enhancement.setStyleSheet("""
                QCheckBox { color: #EEE; font-size: 10pt; spacing: 8px; padding: 5px; }
                QCheckBox:hover { color: #2196F3; }
            """)
        stability_layout.addWidget(self.stability_enhancement)
        
        # Stability description
        stability_description = QLabel(tr.get_text("stability_enhancement_explanation"))
        stability_description.setWordWrap(True)
        if self._get_theme() == 'light':
            stability_description.setStyleSheet("""
                QLabel { color: #555; font-size: 9pt; padding: 8px; background-color: #F1F3F4; border-radius: 3px; }
            """)
        else:
            stability_description.setStyleSheet("""
                QLabel { color: #BBB; font-size: 9pt; padding: 8px; background-color: #3A3A3A; border-radius: 3px; }
            """)
        stability_layout.addWidget(stability_description)
        
        stability_group.setLayout(stability_layout)
        filtering_layout.addWidget(stability_group)

        # Background dimming group
        dimming_group = QGroupBox(tr.get_text("background_dimming"))
        if self._get_theme() == 'light':
            dimming_group.setStyleSheet("""
                QGroupBox { color: #222; font-size: 10pt; border: 2px solid #DDD; border-radius: 5px; margin-top: 10px; padding-top: 10px; background-color: #FFFFFF; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 5px; color: #1976D2; }
                QGroupBox:hover { border: 2px solid #1976D2; }
            """)
        else:
            dimming_group.setStyleSheet("""
                QGroupBox { color: #EEE; font-size: 10pt; border: 2px solid #555; border-radius: 5px; margin-top: 10px; padding-top: 10px; background-color: #444; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 5px; color: #2196F3; }
                QGroupBox:hover { border: 2px solid #2196F3; }
            """)

        dimming_layout = QVBoxLayout()
        self.disable_background_dimming = QCheckBox(tr.get_text("disable_background_dimming"))
        # Initialize from parent flag if available; default False (dimming enabled)
        parent_flag = getattr(self.parent, 'background_dimming_enabled', True)
        self.disable_background_dimming.setChecked(not bool(parent_flag))
        self.disable_background_dimming.setToolTip(tr.get_text("disable_background_dimming_tooltip"))
        if self._get_theme() == 'light':
            self.disable_background_dimming.setStyleSheet("""
                QCheckBox { color: #222; font-size: 10pt; spacing: 8px; padding: 5px; }
                QCheckBox:hover { color: #1976D2; }
            """)
        else:
            self.disable_background_dimming.setStyleSheet("""
                QCheckBox { color: #EEE; font-size: 10pt; spacing: 8px; padding: 5px; }
                QCheckBox:hover { color: #2196F3; }
            """)
        dimming_layout.addWidget(self.disable_background_dimming)

        # Help text
        dimming_desc = QLabel(tr.get_text("background_dimming_explanation"))
        dimming_desc.setWordWrap(True)
        if self._get_theme() == 'light':
            dimming_desc.setStyleSheet("""
                QLabel { color: #555; font-size: 9pt; padding: 8px; background-color: #F1F3F4; border-radius: 3px; }
            """)
        else:
            dimming_desc.setStyleSheet("""
                QLabel { color: #BBB; font-size: 9pt; padding: 8px; background-color: #3A3A3A; border-radius: 3px; }
            """)
        dimming_layout.addWidget(dimming_desc)

        dimming_group.setLayout(dimming_layout)
        filtering_layout.addWidget(dimming_group)
        
        filtering_layout.addStretch()
        return filtering_tab

    # Real-time autosave intentionally removed: changes apply only when Save is pressed
    
    def create_button_layout(self):
        """Create button layout - Main application button style"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Cancel button - CB-aware style
        cancel_button = QPushButton(tr.get_text("cancel"))
        try:
            theme = getattr(self.parent, 'theme', 'dark') if self.parent else 'dark'
            cb_type = 'none'
            if hasattr(self.parent, 'current_profile') and self.parent.current_profile:
                cb_type = getattr(self.parent.current_profile, 'color_blindness_type', 'none') or 'none'
            # Use 'stop' class semantics for a clear cancel color, mapped per CB type
            update_button_theme(cancel_button, 'stop', theme, cb_type)
            # Keep a reasonable min width similar to previous style
            cancel_button.setMinimumWidth(80)
        except Exception:
            pass
        # Mark as canceled so closeEvent won't auto-save
        cancel_button.clicked.connect(self._on_cancel_clicked)
        button_layout.addWidget(cancel_button)
        
        # Save button - Use unified theming (respects color-blindness mapping)
        save_button = QPushButton(tr.get_text("save"))
        # Ensure a reasonable min width similar to previous style
        save_button.setMinimumWidth(80)
        # Apply style consistent with 'start' (green) class, mapped via accessibility colors
        theme = getattr(self.parent, 'theme', 'dark') if self.parent else 'dark'
        cb_type = 'none'
        try:
            if hasattr(self.parent, 'current_profile') and self.parent.current_profile:
                cb_type = getattr(self.parent.current_profile, 'color_blindness_type', 'none') or 'none'
        except Exception:
            cb_type = 'none'
        update_button_theme(save_button, 'start', theme, cb_type)
        save_button.clicked.connect(self.save_settings_and_close)
        button_layout.addWidget(save_button)
        
        return button_layout
    
    def sensitivity_changed(self, value):
        """Called when sensitivity changes"""
        self.sensitivity_value_label.setText(str(value))
        self.sensitivity_description.setText(self.get_sensitivity_description(value))
    
    def get_sensitivity_description(self, value):
        """Return description based on sensitivity value"""
        if value <= 3:
            return tr.get_text("low_sensitivity_desc")
        elif value <= 7:
            return tr.get_text("medium_sensitivity_desc")
        else:
            return tr.get_text("high_sensitivity_desc")
        
    def save_settings_and_close(self):
        """Save settings and close dialog"""
        # Update color selections using _apply_detect_flags
        try:
            if hasattr(self.parent, '_apply_detect_flags'):
                self.parent._apply_detect_flags(
                    self.red_checkbox.isChecked(),
                    self.green_checkbox.isChecked(),
                    self.blue_checkbox.isChecked(),
                    self.yellow_checkbox.isChecked(),
                    persist=True
                )
                print("[DEBUG] Detection settings applied from dialog")
            else:
                # Fallback: directly update detection settings and persist
                self.parent.current_detection_settings = {
                    'red': self.red_checkbox.isChecked(),
                    'green': self.green_checkbox.isChecked(),
                    'blue': self.blue_checkbox.isChecked(),
                    'yellow': self.yellow_checkbox.isChecked()
                }
                
                # Persist to QSettings
                if hasattr(self.parent, 'settings'):
                    self.parent.settings.setValue("detect_red", self.red_checkbox.isChecked())
                    self.parent.settings.setValue("detect_green", self.green_checkbox.isChecked())
                    self.parent.settings.setValue("detect_blue", self.blue_checkbox.isChecked())
                    self.parent.settings.setValue("detect_yellow", self.yellow_checkbox.isChecked())
                print("[DEBUG] Detection settings saved directly")
        except Exception as e:
            print(f"[DEBUG] Failed to save detection settings: {e}")
        
        # Update sensitivity value
        if hasattr(self, 'sensitivity_slider'):
            self.parent.sensitivity_slider.setValue(self.sensitivity_slider.value())
            # Persist to QSettings so autosave serializes correct value (0.1-1.0)
            try:
                if hasattr(self.parent, 'settings'):
                    self.parent.settings.setValue("detection_sensitivity", float(self.sensitivity_slider.value()) / 10.0)
            except Exception:
                pass
        
        # Store filtering settings in main application
        if hasattr(self, 'skin_tone_filtering'):
            self.parent.skin_tone_filtering_active = self.skin_tone_filtering.isChecked()
            try:
                if hasattr(self.parent, 'settings'):
                    self.parent.settings.setValue("skin_tone_filtering_active", self.parent.skin_tone_filtering_active)
            except Exception:
                pass
        if hasattr(self, 'stability_enhancement'):
            self.parent.stability_enhancement_active = self.stability_enhancement.isChecked()
            try:
                if hasattr(self.parent, 'settings'):
                    self.parent.settings.setValue("stability_enhancement_active", self.parent.stability_enhancement_active)
            except Exception:
                pass
        if hasattr(self, 'debug_mode'):
            self.parent.debug_mode_active = self.debug_mode.isChecked()
            try:
                if hasattr(self.parent, 'settings'):
                    self.parent.settings.setValue("debug_mode_active", self.parent.debug_mode_active)
            except Exception:
                pass
        # Background dimming flag
        if hasattr(self, 'disable_background_dimming'):
            self.parent.background_dimming_enabled = not self.disable_background_dimming.isChecked()
            try:
                if hasattr(self.parent, 'settings'):
                    self.parent.settings.setValue("background_dimming_enabled", self.parent.background_dimming_enabled)
            except Exception:
                pass
        
        # Decide how to update CB type based on color changes
        try:
            initial = getattr(self, '_initial_state', {})
            current = self._get_current_state()
            colors_changed = (
                bool(current.get('red')) != bool(initial.get('red')) or
                bool(current.get('green')) != bool(initial.get('green')) or
                bool(current.get('blue')) != bool(initial.get('blue')) or
                bool(current.get('yellow')) != bool(initial.get('yellow'))
            )
        except Exception:
            colors_changed = False

        if colors_changed:
            # Map exact color pairs to CB types; otherwise fall back to 'custom'
            r = bool(current.get('red'))
            g = bool(current.get('green'))
            b = bool(current.get('blue'))
            y = bool(current.get('yellow'))

            target_cb = "custom"
            try:
                prev_cb = None
                if hasattr(self.parent, 'color_blindness_combo') and self.parent.color_blindness_combo is not None:
                    prev_cb = (self.parent.color_blindness_combo.currentData() or 'none').lower()
                elif hasattr(self.parent, 'current_profile') and self.parent.current_profile:
                    prev_cb = (getattr(self.parent.current_profile, 'color_blindness_type', 'none') or 'none').lower()
            except Exception:
                prev_cb = 'none'

            if r and g and not b and not y:
                # Red + Green -> prefer keeping existing RG type; default to protanopia
                target_cb = prev_cb if prev_cb in ("protanopia", "deuteranopia") else "protanopia"
            elif b and y and not r and not g:
                # Blue + Yellow -> Tritanopia
                target_cb = "tritanopia"

            # Apply target selection: trigger handler for non-custom to persist and update UI
            try:
                if hasattr(self.parent, 'color_blindness_combo') and self.parent.color_blindness_combo is not None:
                    if target_cb == 'custom':
                        # Avoid reopening Advanced Settings by suppressing signal
                        self.parent.color_blindness_combo.blockSignals(True)
                        for i in range(self.parent.color_blindness_combo.count()):
                            if self.parent.color_blindness_combo.itemData(i) == target_cb:
                                self.parent.color_blindness_combo.setCurrentIndex(i)
                                break
                        self.parent.color_blindness_combo.blockSignals(False)
                    else:
                        # Let the change handler run to update profile, buttons, etc.
                        for i in range(self.parent.color_blindness_combo.count()):
                            if self.parent.color_blindness_combo.itemData(i) == target_cb:
                                self.parent.color_blindness_combo.setCurrentIndex(i)
                                break
            except Exception:
                pass
        
        # Auto-save profile when advanced settings change
        if hasattr(self.parent, 'auto_save_profile_on_change'):
            self.parent.auto_save_profile_on_change()
        
        # Close dialog
        self.accept()
    
    def apply_settings_and_close(self):
        """Old function - for backward compatibility"""
        self.save_settings_and_close()

    def _on_cancel_clicked(self):
        """Handle explicit cancel click: do not save and mark canceled."""
        self._canceled = True
        self.reject()

    def closeEvent(self, event):
        """On window close (X), ask for confirmation and discard changes if confirmed."""
        from PyQt5.QtWidgets import QMessageBox
        # If not already accepted or explicitly canceled, confirm discard
        if self.result() == 0 and not self._canceled:
            # If nothing has changed, just close without warning
            try:
                if not self._has_unsaved_changes():
                    event.accept()
                    return
            except Exception:
                # On safe-side, fall through to confirmation
                pass
            box = QMessageBox(self)
            # Prefer non-native look for consistent styling (ignore if unsupported)
            try:
                box.setOption(QMessageBox.DontUseNativeDialog, True)
            except Exception:
                pass
            is_light = self._get_theme() == 'light'
            # Theme-aware basic styling
            try:
                if is_light:
                    box.setStyleSheet("""
                        QDialog, QMessageBox { background-color: #F5F5F7; color: #222; border: 1px solid #D0D4D9; border-radius: 8px; }
                        QLabel { color: #222; }
                        QPushButton { background-color: #F8F9FA; color: #495057; border: 1px solid #D0D4D9; border-radius: 6px; font-weight: 600; padding: 6px 12px; min-width: 84px; }
                        QPushButton:hover { background-color: #E9ECEF; }
                    """)
                else:
                    box.setStyleSheet("""
                        QDialog, QMessageBox { background-color: #2b2b2b; color: #EEE; border: 1px solid #3D3D3D; border-radius: 8px; }
                        QLabel { color: #EEE; }
                        QPushButton { background-color: #3A3A3A; color: #DDD; border: 1px solid #4A4A4A; border-radius: 6px; font-weight: 600; padding: 6px 12px; min-width: 84px; }
                        QPushButton:hover { background-color: #4A4A4A; }
                    """)
            except Exception:
                # Styling failure shouldn't close the dialog
                pass
            box.setIcon(QMessageBox.Warning)
            box.setWindowTitle(tr.get_text("warning"))
            box.setText(tr.get_text("unsaved_changes_discard_confirm"))
            # Use explicit Yes/No order: No left, Yes right
            box.setStandardButtons(QMessageBox.NoButton)
            no_btn = box.addButton(tr.get_text("no"), QMessageBox.ActionRole)
            yes_btn = box.addButton(tr.get_text("yes"), QMessageBox.ActionRole)
            # Color buttons (No=red, Yes=green) for accessibility & consistency
            try:
                if is_light:
                    no_btn.setStyleSheet("""
                        QPushButton { background-color: #FFEBEE; color: #C62828; border: 1px solid #FFCDD2; }
                        QPushButton:hover { background-color: #FFCDD2; }
                    """)
                    yes_btn.setStyleSheet("""
                        QPushButton { background-color: #E8F5E9; color: #2E7D32; border: 1px solid #C8E6C9; }
                        QPushButton:hover { background-color: #C8E6C9; }
                    """)
                else:
                    no_btn.setStyleSheet("""
                        QPushButton { background-color: #512F2F; color: #FF6B6B; border: 1px solid #6A3A3A; }
                        QPushButton:hover { background-color: #6A3A3A; }
                    """)
                    yes_btn.setStyleSheet("""
                        QPushButton { background-color: #294030; color: #7DDE86; border: 1px solid #355A3E; }
                        QPushButton:hover { background-color: #355A3E; }
                    """)
            except Exception:
                pass
            try:
                box.setEscapeButton(no_btn)
                box.setDefaultButton(yes_btn)
            except Exception:
                pass
            # Apply dark title bar when in dark theme (Windows)
            if not is_light:
                try:
                    import ctypes
                    hwnd = int(box.winId())
                    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd,
                        DWMWA_USE_IMMERSIVE_DARK_MODE,
                        ctypes.byref(ctypes.c_int(1)),
                        ctypes.sizeof(ctypes.c_int)
                    )
                except Exception:
                    pass
            # Execute and decide
            try:
                box.exec_()
                if box.clickedButton() is yes_btn:
                    # Discard changes
                    self._canceled = True
                    event.accept()
                else:
                    # Keep dialog open
                    event.ignore()
            except Exception:
                # If anything goes wrong, do NOT close silently
                event.ignore()
            return
        # Default behavior if already accepted/canceled
        event.accept()
