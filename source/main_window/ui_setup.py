"""
UI setup functions for ColorVisionAid main window
Contains all UI initialization and setup functions
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStatusBar, 
                           QCheckBox, QSlider, QApplication, QLabel, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from ..translations import translator as tr
from ..ui_components import (
    create_camera_controls, 
    create_color_blindness_type_group,
    create_camera_settings_group,
    create_language_group, 
    create_about_group, 
    create_camera_interface
)
from ..ui_components.groups import update_color_blindness_combo_language
from ..ui_components.buttons import update_button_theme

class UISetup:
    """Mixin class for UI setup functionality"""
    
    def setup_ui(self):
        """Setup UI components and layout"""
        # Window setup
        self.setWindowTitle(tr.get_text("app_title"))
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons', 'app_icon.png')))
        
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Camera view area
        self.setup_camera_view()
        
        # Settings panel
        self.setup_settings_panel()
        
        # Add main components to layout
        self.main_layout.addWidget(self.camera_container, 7)
        self.main_layout.addWidget(self.settings_panel, 3)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(tr.get_text("ready"))
        
    # Theme is applied in main window after UI setup

    def setup_camera_view(self):
        """Create camera display area"""
        # Main camera container
        self.camera_container = QWidget()
        self.camera_layout = QVBoxLayout(self.camera_container)
        
        # Camera feed container
        self.camera_feed_container = QWidget()
        self.camera_feed_layout = QVBoxLayout(self.camera_feed_container)
        self.camera_feed_layout.setContentsMargins(20, 20, 20, 20)
        
        # Show camera message
        create_camera_interface(self, self.camera_feed_layout)
        
        self.camera_layout.addWidget(self.camera_feed_container)
        # Camera control buttons - Use UI Components module
        self.camera_layout.addLayout(create_camera_controls(self))

    def apply_theme_to_components(self):
        """Apply theme-specific styles to inline-styled widgets and buttons."""
        theme = getattr(self, 'theme', 'dark').lower()
        # Determine color blindness type for accent-aware styling (tritanopia uses Start-button blue)
        try:
            cb_type = None
            if hasattr(self, 'color_blindness_combo') and self.color_blindness_combo is not None:
                cb_type = self.color_blindness_combo.currentData()
            if not cb_type and hasattr(self, 'current_profile') and self.current_profile is not None:
                cb_type = getattr(self.current_profile, 'color_blindness_type', 'none')
            cb_type = (cb_type or 'none').lower()
        except Exception:
            cb_type = 'none'

        accent_border = '#64B5F6'
        # Camera area background
        if theme == 'light':
            self.camera_feed_container.setStyleSheet("background-color: #EDEFF1; border-radius: 10px;")
        else:
            self.camera_feed_container.setStyleSheet("background-color: #222; border-radius: 10px;")

        # Buttons - Include color blindness support
        color_blindness_type = getattr(self.current_profile, 'color_blindness_type', 'none') if hasattr(self, 'current_profile') and self.current_profile else 'none'
        
        if self.camera_manager.camera_open:
            update_button_theme(self.camera_toggle_button, 'stop', theme, color_blindness_type)
        else:
            update_button_theme(self.camera_toggle_button, 'start', theme, color_blindness_type)
        update_button_theme(self.screenshot_button, 'snapshot', theme, color_blindness_type)
        update_button_theme(self.load_file_button, 'load_file', theme, color_blindness_type)
        update_button_theme(self.gallery_button, 'gallery', theme, color_blindness_type)
        update_button_theme(self.advanced_settings_button, 'default', theme, "none")

        # Camera settings info label (accent-aware left border)
        if theme == 'light':
            self.camera_info_label.setStyleSheet(
                f"QLabel {{ color: #444; font-size: 9pt; padding: 10px; line-height: 1.5; background-color: #F1F3F4; border-radius: 5px; border-left: 3px solid {accent_border}; max-height: 80px; }}"
            )
        else:
            self.camera_info_label.setStyleSheet(
                f"QLabel {{ color: #CCC; font-size: 9pt; padding: 10px; line-height: 1.5; background-color: #3A3A3A; border-radius: 5px; border-left: 3px solid {accent_border}; max-height: 80px; }}"
            )

        # Reset camera permission button
        if theme == 'light':
            self.permission_reset_button.setStyleSheet("""
                QPushButton {
                    background-color: #F8F9FA;
                    color: #495057;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 10pt;
                    padding: 8px 12px;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background-color: #E9ECEF;
                    color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #DEE2E6;
                }
            """)
        else:
            self.permission_reset_button.setStyleSheet("""
                QPushButton {
                    background-color: #3A3A3A;
                    color: #CCC;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 10pt;
                    padding: 8px 12px;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background-color: #4A4A4A;
                    color: #64B5F6;
                }
                QPushButton:pressed {
                    background-color: #5A5A5A;
                }
            """)

        # About section readability
        if theme == 'light':
            self.about_label.setStyleSheet("QLabel { font-size: 9pt; line-height: 1.4; padding: 8px; color: #333; }")
        else:
            self.about_label.setStyleSheet("QLabel { font-size: 9pt; line-height: 1.4; padding: 8px; color: #CCC; }")

        # Update camera interface if not currently running
        if not self.camera_manager.camera_open and not getattr(self, '_file_loaded_view_active', False):
            # Recreate camera interface with updated theme only when no analyzed image is shown
            create_camera_interface(self, self.camera_feed_layout)
        
        # Update any existing camera permission interface 
        self._update_camera_permission_interface_theme()

    def setup_settings_panel(self):
        """Create settings panel"""
        self.settings_panel = QWidget()
        # Responsive width - Adjust according to screen size
        screen = QApplication.desktop().screenGeometry()
        min_width = min(280, max(250, int(screen.width() * 0.25)))
        max_width = min(350, int(screen.width() * 0.35))
        
        self.settings_panel.setMinimumWidth(min_width)
        self.settings_panel.setMaximumWidth(max_width)
        
        self.settings_layout = QVBoxLayout(self.settings_panel)
        self.settings_layout.setSpacing(8)
        self.settings_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create groups from UI Components module
        # Add profile selector first
        from ..ui_components.profile_selector import ProfileSelector
        self.profile_selector = ProfileSelector(self)
        self.profile_selector.profile_changed.connect(self.on_profile_changed)
        
        self.color_blindness_group = create_color_blindness_type_group(self)
        self.camera_settings_group = create_camera_settings_group(self)
        self.language_group = create_language_group(self)
        self.about_group = create_about_group(self)
        
        # Add setting groups to panel - profile selector first
        self.settings_layout.addWidget(self.profile_selector)
        self.settings_layout.addWidget(self.color_blindness_group)
        self.settings_layout.addWidget(self.camera_settings_group)
        self.settings_layout.addWidget(self.language_group)
        self.settings_layout.addWidget(self.about_group)

    def _update_camera_permission_interface_theme(self):
        """Update camera permission interface theme if it's currently visible"""
        # Check if camera permission interface is currently shown
        for i in range(self.camera_feed_layout.count()):
            widget = self.camera_feed_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'layout'):
                layout = widget.layout()
                if layout:
                    # Look for permission text and camera icon to update
                    for j in range(layout.count()):
                        child_widget = layout.itemAt(j).widget()
                        if child_widget:
                            # Update camera icon with responsive sizing
                            if isinstance(child_widget, QLabel) and ("🎥" in child_widget.text() or "📷" in child_widget.text() or "📹" in child_widget.text() or "●REC" in child_widget.text()):
                                theme = getattr(self, 'theme', 'dark').lower()
                                
                                # Calculate responsive icon size based on current window size
                                window_width = self.width() if hasattr(self, 'width') else 1000
                                responsive_icon_size = max(35, min(80, int(window_width * 0.06)))
                                
                                if theme == 'light':
                                    child_widget.setStyleSheet(f"""
                                        font-size: {responsive_icon_size}pt; 
                                        color: #333; 
                                        background-color: transparent; 
                                        border: none; 
                                        font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji';
                                    """)
                                else:
                                    child_widget.setStyleSheet(f"""
                                        font-size: {responsive_icon_size}pt; 
                                        color: #BBB; 
                                        background-color: transparent; 
                                        border: none; 
                                        font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji';
                                    """)
                            # Update permission text with responsive sizing
                            elif isinstance(child_widget, QLabel) and tr.get_text("camera_permission_text") in child_widget.text():
                                theme = getattr(self, 'theme', 'dark').lower()
                                
                                # Calculate responsive text size
                                window_width = self.width() if hasattr(self, 'width') else 1000
                                responsive_text_size = max(10, min(16, int(window_width * 0.014)))
                                responsive_margin = max(10, min(25, int(window_width * 0.02)))
                                
                                if theme == 'light':
                                    child_widget.setStyleSheet(f"color: #222; font-size: {responsive_text_size}pt; margin: {responsive_margin}px;")
                                else:
                                    child_widget.setStyleSheet(f"color: white; font-size: {responsive_text_size}pt; margin: {responsive_margin}px;")
                            # Update checkbox
                            elif hasattr(child_widget, 'layout'):
                                inner_layout = child_widget.layout()
                                if inner_layout:
                                    for k in range(inner_layout.count()):
                                        inner_widget = inner_layout.itemAt(k).widget()
                                        if isinstance(inner_widget, QCheckBox):
                                            theme = getattr(self, 'theme', 'dark').lower()
                                            if theme == 'light':
                                                inner_widget.setStyleSheet("""
                                                    QCheckBox {
                                                        color: #222;
                                                    }
                                                    QCheckBox:hover {
                                                        color: #1976D2;
                                                    }
                                                """)
                                            else:
                                                inner_widget.setStyleSheet("""
                                                    QCheckBox {
                                                        color: white;
                                                    }
                                                    QCheckBox:hover {
                                                        color: #2196F3;
                                                    }
                                                """)
                                        # Update permission buttons with color-blind aware styles
                                        try:
                                            from ..ui_components.buttons import update_button_theme
                                            if isinstance(inner_widget, QPushButton):
                                                name = inner_widget.objectName() or ""
                                                theme_val = getattr(self, 'theme', 'dark')
                                                cb_type_val = None
                                                try:
                                                    if hasattr(self, 'color_blindness_combo') and self.color_blindness_combo is not None:
                                                        cb_type_val = self.color_blindness_combo.currentData()
                                                    if not cb_type_val and hasattr(self, 'current_profile') and self.current_profile is not None:
                                                        cb_type_val = getattr(self.current_profile, 'color_blindness_type', 'none')
                                                except Exception:
                                                    cb_type_val = 'none'
                                                cb_type_val = (cb_type_val or 'none')
                                                if name == 'permission_grant_button':
                                                    update_button_theme(inner_widget, 'start', theme_val, cb_type_val)
                                                elif name == 'permission_deny_button':
                                                    update_button_theme(inner_widget, 'stop', theme_val, cb_type_val)
                                        except Exception:
                                            pass
        self.settings_layout.addStretch()
        
        # Default color selection checkboxes (for advanced settings)
        # These checkboxes will only be visible in advanced settings
        self.red_checkbox = QCheckBox(tr.get_text("detect_red"))
        self.green_checkbox = QCheckBox(tr.get_text("detect_green"))
        self.blue_checkbox = QCheckBox(tr.get_text("detect_blue"))
        self.yellow_checkbox = QCheckBox(tr.get_text("detect_yellow"))
        
        # NOTE: Default values will be set from profile in window.py after UI setup
        # Don't set defaults here to avoid overwriting profile values
        
        # Filtering settings - will be set from profile
        self.skin_tone_filtering_active = True  # Temporary default, will be overridden
        self.stability_enhancement_active = True  # Temporary default, will be overridden  
        self.debug_mode_active = False  # Temporary default, will be overridden
        
        # Default values for sensitivity and contrast (to be used in advanced settings)
        self.sensitivity_value = 5
        self.contrast_value = 5
        
        # Hidden slider for advanced settings (just to hold value)
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(1, 10)
        self.sensitivity_slider.setValue(5)  # Will be overridden from profile
        self.sensitivity_slider.setVisible(False)  # Invisible

    def update_ui_language(self):
        """Update UI elements to new language"""
        # Update window title
        self.setWindowTitle(tr.get_text("app_title"))
        
        # Update buttons
        self.screenshot_button.setText(tr.get_text("take_screenshot"))
        self.screenshot_button.setToolTip(tr.get_text("snapshot_tooltip"))
        self.gallery_button.setText(tr.get_text("gallery"))
        self.gallery_button.setToolTip(tr.get_text("gallery_tooltip"))
        self.load_file_button.setText(tr.get_text("load_file"))
        self.load_file_button.setToolTip(tr.get_text("load_file_tooltip"))
        
        # Update camera button
        if self.camera_manager.camera_open:
            self.camera_toggle_button.setText(tr.get_text("stop"))
            self.camera_toggle_button.setToolTip(tr.get_text("stop_tooltip"))
        else:
            self.camera_toggle_button.setText(tr.get_text("start"))
            self.camera_toggle_button.setToolTip(tr.get_text("start_tooltip"))

        # Update groups (new UI structure)
        self.color_blindness_group.setTitle(tr.get_text("color_blindness_type"))
        self.camera_settings_group.setTitle(tr.get_text("camera_settings"))
        self.language_group.setTitle(tr.get_text("interface"))
        self.about_group.setTitle(tr.get_text("about"))
        
        # Update theme and language labels if they exist
        if hasattr(self, 'language_group') and hasattr(self.language_group, 'layout'):
            layout = self.language_group.layout()
            if layout:
                # Find and update language label (first label)
                for i in range(layout.count()):
                    widget = layout.itemAt(i).widget()
                    if isinstance(widget, QLabel) and i == 0:  # First label is language
                        widget.setText(tr.get_text("language"))
                    elif isinstance(widget, QLabel) and i == 2:  # Third widget should be theme label
                        widget.setText(tr.get_text("theme"))
        
        # Update color blindness combo box with hierarchical structure
        update_color_blindness_combo_language(self.color_blindness_combo)
        
        # Update advanced settings button
        self.advanced_settings_button.setText(tr.get_text("advanced_settings"))
        self.advanced_settings_button.setToolTip(tr.get_text("advanced_settings_tooltip"))
        
        # Update color blindness combo tooltip
        self.color_blindness_combo.setToolTip(tr.get_text("color_blindness_type_tooltip"))
        
        # Update checkboxes (for internal use only)
        self.red_checkbox.setText(tr.get_text("detect_red"))
        self.green_checkbox.setText(tr.get_text("detect_green"))
        self.blue_checkbox.setText(tr.get_text("detect_blue"))
        self.yellow_checkbox.setText(tr.get_text("detect_yellow"))
        
        # Update labels
        self.camera_info_label.setText(tr.get_text("camera_settings_info"))
        self.about_label.setText(tr.get_text("about_text"))
        self.contributors_title.setText(tr.get_text("contributors"))
        self.permission_reset_button.setText(tr.get_text("reset_camera_permission"))
        
        # Update permission status
        permission_status_text = ""
        if self.camera_permission == "granted":
            permission_status_text = tr.get_text("permission_status_granted")
        elif self.camera_permission == "denied":
            permission_status_text = tr.get_text("permission_status_denied")
        else:
            permission_status_text = tr.get_text("permission_status_ask")
            
        self.permission_status_label.setText(f"{tr.get_text('current_permission_status')}: {permission_status_text}")
        
        # Update camera interface if camera is not active
        if not self.camera_manager.camera_open and not getattr(self, '_file_loaded_view_active', False):
            create_camera_interface(self, self.camera_feed_layout)

        # Re-apply theme-specific component styles after text changes
        if hasattr(self, 'apply_theme_to_components'):
            self.apply_theme_to_components()

        # Update language-dependent texts inside ProfileSelector (group title + tooltips)
        if hasattr(self, 'profile_selector') and hasattr(self.profile_selector, 'update_ui_language'):
            self.profile_selector.update_ui_language()
