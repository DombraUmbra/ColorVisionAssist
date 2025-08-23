"""
UI setup functions for ColorVisionAid main window
Contains all UI initialization and setup functions
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStatusBar, 
                           QCheckBox, QSlider, QApplication, QLabel)
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
        # Camera area background
        if theme == 'light':
            self.camera_feed_container.setStyleSheet("background-color: #EDEFF1; border-radius: 10px;")
        else:
            self.camera_feed_container.setStyleSheet("background-color: #222; border-radius: 10px;")

        # Apply combo box themes using the unified approach
        from ..ui_components.groups import update_combo_themes
        update_combo_themes(self)

        # Buttons
        if self.camera_manager.camera_open:
            update_button_theme(self.camera_toggle_button, 'stop', theme)
        else:
            update_button_theme(self.camera_toggle_button, 'start', theme)
        update_button_theme(self.screenshot_button, 'snapshot', theme)
        update_button_theme(self.load_file_button, 'load_file', theme)
        update_button_theme(self.gallery_button, 'gallery', theme)
        update_button_theme(self.advanced_settings_button, 'default', theme)

        # Camera settings info label
        if theme == 'light':
            self.camera_info_label.setStyleSheet(
                "QLabel { color: #444; font-size: 9pt; padding: 10px; line-height: 1.5; background-color: #F1F3F4; border-radius: 5px; border-left: 3px solid #64B5F6; max-height: 80px; }"
            )
        else:
            self.camera_info_label.setStyleSheet(
                "QLabel { color: #CCC; font-size: 9pt; padding: 10px; line-height: 1.5; background-color: #3A3A3A; border-radius: 5px; border-left: 3px solid #64B5F6; max-height: 80px; }"
            )

        # Reset camera permission button
        if theme == 'light':
            self.permission_reset_button.setStyleSheet(
                "QPushButton { background-color: #E0E0E0; color: #222; padding: 8px 6px; border-radius: 5px; text-align: center; font-size: 9pt; min-height: 25px; border: 1px solid #C7C7C7; }"
                " QPushButton:hover { background-color: #EEEEEE; border: 1px solid #1976D2; }"
                " QPushButton:pressed { background-color: #D5D5D5; }"
            )
        else:
            self.permission_reset_button.setStyleSheet(
                "QPushButton { background-color: #555; color: white; padding: 8px 6px; border-radius: 5px; text-align: center; font-size: 9pt; min-height: 25px; }"
                " QPushButton:hover { background-color: #777; border: 1px solid #999; }"
                " QPushButton:pressed { background-color: #444; }"
            )

        # About section readability
        if theme == 'light':
            self.about_label.setStyleSheet("QLabel { font-size: 9pt; line-height: 1.4; padding: 8px; color: #333; }")
        else:
            self.about_label.setStyleSheet("QLabel { font-size: 9pt; line-height: 1.4; padding: 8px; color: #CCC; }")

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
        self.color_blindness_group = create_color_blindness_type_group(self)
        self.camera_settings_group = create_camera_settings_group(self)
        self.language_group = create_language_group(self)
        self.about_group = create_about_group(self)
        
        # Add setting groups to panel
        self.settings_layout.addWidget(self.color_blindness_group)
        self.settings_layout.addWidget(self.camera_settings_group)
        self.settings_layout.addWidget(self.language_group)
        self.settings_layout.addWidget(self.about_group)
        self.settings_layout.addStretch()
        
        # Default color selection checkboxes (for advanced settings)
        # These checkboxes will only be visible in advanced settings
        self.red_checkbox = QCheckBox(tr.get_text("detect_red"))
        self.green_checkbox = QCheckBox(tr.get_text("detect_green"))
        self.blue_checkbox = QCheckBox(tr.get_text("detect_blue"))
        self.yellow_checkbox = QCheckBox(tr.get_text("detect_yellow"))
        
        # Default selected colors (Red-Green color blindness)
        self.red_checkbox.setChecked(True)
        self.green_checkbox.setChecked(True)
        
        # Filtering settings
        self.skin_tone_filtering_active = True  # Skin tone filtering default active
        self.stability_enhancement_active = True  # Stability enhancement default active
        self.debug_mode_active = False  # Debug mode default off
        
        # Default values for sensitivity and contrast (to be used in advanced settings)
        self.sensitivity_value = 5
        self.contrast_value = 5
        
        # Hidden slider for advanced settings (just to hold value)
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(1, 10)
        self.sensitivity_slider.setValue(5)
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
        
        # Update color blindness combo box
        self.color_blindness_combo.clear()
        self.color_blindness_combo.addItem(tr.get_text("red_green_colorblind"), "red_green")
        self.color_blindness_combo.addItem(tr.get_text("blue_yellow_colorblind"), "blue_yellow")
        self.color_blindness_combo.addItem(tr.get_text("protanopia"), "protanopia")
        self.color_blindness_combo.addItem(tr.get_text("deuteranopia"), "deuteranopia")
        self.color_blindness_combo.addItem(tr.get_text("tritanopia"), "tritanopia")
        self.color_blindness_combo.addItem(tr.get_text("complete_colorblind"), "complete")
        self.color_blindness_combo.addItem(tr.get_text("custom_colors"), "custom")
        
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
        if not self.camera_manager.camera_open:
            create_camera_interface(self, self.camera_feed_layout)

        # Re-apply theme-specific component styles after text changes
        if hasattr(self, 'apply_theme_to_components'):
            self.apply_theme_to_components()
