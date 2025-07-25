"""
UI setup functions for ColorVisionAid main window
Contains all UI initialization and setup functions
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStatusBar, 
                           QCheckBox, QSlider, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from ..translations import translator as tr
from ..ui_components import (
    create_camera_controls, 
    create_color_blindness_type_group,
    create_camera_settings_group,
    create_language_group, 
    create_about_group, 
    apply_dark_theme, 
    create_camera_interface
)

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
        
        # Apply style theme
        apply_dark_theme(self)

    def setup_camera_view(self):
        """Create camera display area"""
        # Main camera container
        self.camera_container = QWidget()
        self.camera_layout = QVBoxLayout(self.camera_container)
        
        # Camera feed container
        self.camera_feed_container = QWidget()
        self.camera_feed_container.setStyleSheet("background-color: #222; border-radius: 10px;")
        self.camera_feed_layout = QVBoxLayout(self.camera_feed_container)
        self.camera_feed_layout.setContentsMargins(20, 20, 20, 20)
        
        # Show camera message
        create_camera_interface(self, self.camera_feed_layout)
        
        self.camera_layout.addWidget(self.camera_feed_container)
        # Camera control buttons - Use UI Components module
        self.camera_layout.addLayout(create_camera_controls(self))

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
        self.gallery_button.setText(tr.get_text("gallery"))
        self.load_file_button.setText(tr.get_text("load_file"))
        
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
        self.language_group.setTitle(tr.get_text("language"))
        self.about_group.setTitle(tr.get_text("about"))
        
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
