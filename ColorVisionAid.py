import cv2
import numpy as np
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QWidget, QSlider, QCheckBox,
                           QGroupBox, QGridLayout, QComboBox, QStatusBar, QSplashScreen,
                           QDialog, QScrollArea, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QTimer, QSize, QSettings
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon
import os
import glob
from translations import translator as tr
from PIL import Image, ImageDraw, ImageFont

class ScreenshotGallery(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr.get_text("gallery_title"))
        self.setGeometry(200, 200, 800, 600)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons', 'gallery_icon.png')))
        
        # Main layout
        layout = QVBoxLayout()
        
        # Info label
        self.info_label = QLabel(tr.get_text("saved_screenshots"))
        layout.addWidget(self.info_label)
        
        # Create a scroll area for the gallery
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.gallery_layout = QGridLayout(scroll_widget)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        # Add buttons
        self.refresh_button = QPushButton(tr.get_text("refresh"))
        self.refresh_button.clicked.connect(self.load_screenshots)
        
        self.delete_button = QPushButton(tr.get_text("delete_selected"))
        self.delete_button.clicked.connect(self.delete_selected)
        self.delete_button.setEnabled(False)
        
        self.export_button = QPushButton(tr.get_text("export"))
        self.export_button.clicked.connect(self.export_selected)
        self.export_button.setEnabled(False)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.export_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Variables
        self.screenshots = []
        self.selected_index = -1
        self.thumbnail_labels = []
        
        # Load screenshots
        self.load_screenshots()
        
        # Apply the dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #333;
                color: #EEE;
            }
            QLabel {
                color: #EEE;
            }
            QPushButton {
                background-color: #555;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #777;
            }
            QPushButton:disabled {
                background-color: #444;
                color: #888;
            }
            QScrollArea {
                border: 1px solid #555;
                background-color: #444;
            }
        """)
    
    def load_screenshots(self):
        # Clear existing thumbnails
        for label in self.thumbnail_labels:
            self.gallery_layout.removeWidget(label)
            label.deleteLater()
        
        self.thumbnail_labels = []
        self.screenshots = []
        
        # Find all PNG files in the current directory that start with "snapshot_"
        screenshot_files = glob.glob("snapshot_*.png")
        
        if not screenshot_files:
            self.info_label.setText(tr.get_text("no_screenshots"))
            self.selected_index = -1
            self.delete_button.setEnabled(False)
            self.export_button.setEnabled(False)
            return
        
        # Sort files by creation time (newest first)
        screenshot_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        self.screenshots = screenshot_files
        
        # Display thumbnails in a grid (4 columns)
        cols = 4
        for i, file_path in enumerate(screenshot_files):
            # Create thumbnail
            pixmap = QPixmap(file_path)
            thumbnail = pixmap.scaled(QSize(150, 150), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Create label and add to layout
            label = QLabel()
            label.setPixmap(thumbnail)
            label.setAlignment(Qt.AlignCenter)
            label.setToolTip(file_path)
            label.setStyleSheet("border: 2px solid #555; margin: 5px; background-color: #222; padding: 5px;")
            label.setFixedSize(QSize(180, 180))
            label.mousePressEvent = lambda event, idx=i: self.select_screenshot(idx)
            
            row, col = i // cols, i % cols
            self.gallery_layout.addWidget(label, row, col)
            self.thumbnail_labels.append(label)
        
        # Update info text
        self.info_label.setText(f"{tr.get_text('saved_screenshots')} {len(screenshot_files)}")

    def select_screenshot(self, index):
        # Deselect the previous selection
        if 0 <= self.selected_index < len(self.thumbnail_labels):
            self.thumbnail_labels[self.selected_index].setStyleSheet("border: 2px solid #555; margin: 5px; background-color: #222; padding: 5px;")
        
        # Select the new one
        self.selected_index = index
        self.thumbnail_labels[index].setStyleSheet("border: 2px solid #2196F3; margin: 5px; background-color: #333; padding: 5px;")
        
        # Enable buttons
        self.delete_button.setEnabled(True)
        self.export_button.setEnabled(True)
    
    def delete_selected(self):
        if 0 <= self.selected_index < len(self.screenshots):
            file_to_delete = self.screenshots[self.selected_index]
            
            # Confirm deletion
            reply = QMessageBox.question(
                self, 
                tr.get_text("delete_confirmation"), 
                tr.get_text("delete_confirm_text", file_to_delete),
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    os.remove(file_to_delete)
                    self.load_screenshots()  # Refresh the gallery
                    self.parent().status_bar.showMessage(tr.get_text("file_deleted", file_to_delete))
                except Exception as e:
                    QMessageBox.critical(self, tr.get_text("error"), tr.get_text("delete_failed", str(e)))
    
    def export_selected(self):
        if 0 <= self.selected_index < len(self.screenshots):
            file_to_export = self.screenshots[self.selected_index]
            
            # Open file dialog to choose export location
            export_path, _ = QFileDialog.getSaveFileName(
                self, 
                tr.get_text("export_title"), 
                os.path.basename(file_to_export),
                "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*.*)"
            )
            
            if export_path:
                try:
                    # Read the original image
                    img = cv2.imread(file_to_export)
                    
                    # Save to the selected path
                    cv2.imwrite(export_path, img)
                    self.parent().status_bar.showMessage(tr.get_text("file_exported", export_path))
                except Exception as e:
                    QMessageBox.critical(self, tr.get_text("error"), tr.get_text("export_failed", str(e)))


class ColorVisionAid(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load settings
        self.settings = QSettings("ColorVisionAid", "CVA")
        language = self.settings.value("language", "en")
        tr.set_language(language)
        
        # Window setup
        self.setWindowTitle(tr.get_text("app_title"))
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons', 'app_icon.png')))
        
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Camera view area
        self.camera_container = QWidget()
        self.camera_layout = QVBoxLayout(self.camera_container)
        
        # Camera feed with permission information
        self.camera_feed_container = QWidget()
        self.camera_feed_container.setStyleSheet("background-color: #222; border-radius: 10px;")
        
        self.camera_feed_layout = QVBoxLayout(self.camera_feed_container)
        self.camera_feed_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add initial camera message without permission buttons
        self.show_camera_initial_message()
        
        self.camera_layout.addWidget(self.camera_feed_container)
        
        # Add buttons under camera
        button_layout = QHBoxLayout()
        # Replace separate buttons with a single toggle button
        self.toggle_camera_button = QPushButton(tr.get_text("start"))
        self.toggle_camera_button.setToolTip(tr.get_text("start_tooltip"))
        self.toggle_camera_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #66BB6A;
                border: 2px solid #81C784;
            }
            QPushButton:pressed {
                background-color: #43A047;
            }
        """)
        self.toggle_camera_button.clicked.connect(self.toggle_camera)
        
        self.snapshot_button = QPushButton(tr.get_text("take_screenshot"))
        self.gallery_button = QPushButton(tr.get_text("gallery"))
        
        # Add tooltips to buttons
        self.snapshot_button.setToolTip(tr.get_text("snapshot_tooltip"))
        self.gallery_button.setToolTip(tr.get_text("gallery_tooltip"))
        
        # Add hover style effects for other buttons
        self.snapshot_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #42A5F5;
                border: 2px solid #64B5F6;
            }
            QPushButton:pressed {
                background-color: #1E88E5;
            }
        """)
        self.gallery_button.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #AB47BC;
                border: 2px solid #BA68C8;
            }
            QPushButton:pressed {
                background-color: #8E24AA;
            }
        """)
        
        button_layout.addWidget(self.toggle_camera_button)
        button_layout.addWidget(self.snapshot_button)
        button_layout.addWidget(self.gallery_button)
        
        self.camera_layout.addLayout(button_layout)
        
        # Settings panel
        self.settings_panel = QWidget()
        self.settings_panel.setMaximumWidth(300)
        self.settings_layout = QVBoxLayout(self.settings_panel)
        
        # Color detection settings
        color_group = QGroupBox(tr.get_text("color_detection"))
        color_layout = QVBoxLayout()
        
        self.red_checkbox = QCheckBox(tr.get_text("detect_red"))
        self.green_checkbox = QCheckBox(tr.get_text("detect_green"))
        self.blue_checkbox = QCheckBox(tr.get_text("detect_blue"))
        self.yellow_checkbox = QCheckBox(tr.get_text("detect_yellow"))
        
        self.red_checkbox.setChecked(True)
        self.green_checkbox.setChecked(True)
        
        color_layout.addWidget(self.red_checkbox)
        color_layout.addWidget(self.green_checkbox)
        color_layout.addWidget(self.blue_checkbox)
        color_layout.addWidget(self.yellow_checkbox)
        color_group.setLayout(color_layout)
        self.color_group = color_group
        
        # Display settings
        display_group = QGroupBox(tr.get_text("display_settings"))
        display_layout = QGridLayout()
        
        self.detection_sensitivity_label = QLabel(tr.get_text("detection_sensitivity"))
        display_layout.addWidget(self.detection_sensitivity_label, 0, 0)
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(1, 10)
        self.sensitivity_slider.setValue(5)
        display_layout.addWidget(self.sensitivity_slider, 0, 1)
        
        self.contrast_label = QLabel(tr.get_text("contrast"))
        display_layout.addWidget(self.contrast_label, 1, 0)
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(1, 10) 
        self.contrast_slider.setValue(5)
        display_layout.addWidget(self.contrast_slider, 1, 1)
        
        self.display_mode_label = QLabel(tr.get_text("display_mode"))
        display_layout.addWidget(self.display_mode_label, 2, 0)
        self.display_mode = QComboBox()
        self.display_mode.addItems(["Normal", "Deuteranopia", "Protanopia", "Tritanopia"])
        display_layout.addWidget(self.display_mode, 2, 1)
        
        display_group.setLayout(display_layout)
        self.display_group = display_group
        
        # Add Camera Settings group
        camera_settings_group = QGroupBox(tr.get_text("camera_settings"))
        camera_layout = QVBoxLayout()
        
        # Add info text explaining camera permissions
        camera_info_label = QLabel(tr.get_text("camera_settings_info"))
        camera_info_label.setWordWrap(True)
        camera_info_label.setStyleSheet("color: #CCC; font-size: 9pt;")
        camera_layout.addWidget(camera_info_label)
        
        # Show current permission status
        self.camera_permission = self.settings.value("camera_permission", "ask")
        permission_status_text = ""
        if self.camera_permission == "granted":
            permission_status_text = tr.get_text("permission_status_granted")
        elif self.camera_permission == "denied":
            permission_status_text = tr.get_text("permission_status_denied")
        else:
            permission_status_text = tr.get_text("permission_status_ask")
            
        permission_status_label = QLabel(f"{tr.get_text('current_permission_status')}: {permission_status_text}")
        permission_status_label.setStyleSheet("color: #2196F3; margin-top: 8px;")
        camera_layout.addWidget(permission_status_label)
        self.permission_status_label = permission_status_label
        
        # Add reset camera permission button with icon
        self.reset_permission_button = QPushButton(tr.get_text("reset_camera_permission"))
        self.reset_permission_button.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                padding: 8px;
                border-radius: 5px;
                text-align: left;
                padding-left: 30px;
            }
            QPushButton:hover {
                background-color: #777;
                border: 1px solid #999;
            }
            QPushButton:pressed {
                background-color: #444;
            }
        """)
        
        # Try to add icon to button
        reset_icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'reset_icon.png')
        if os.path.exists(reset_icon_path):
            self.reset_permission_button.setIcon(QIcon(reset_icon_path))
        
        self.reset_permission_button.clicked.connect(self.reset_camera_permission)
        camera_layout.addWidget(self.reset_permission_button)
        
        camera_settings_group.setLayout(camera_layout)
        self.camera_settings_group = camera_settings_group
        self.camera_info_label = camera_info_label
        
        # Language settings
        language_group = QGroupBox(tr.get_text("language"))
        language_layout = QVBoxLayout()
        
        self.language_combo = QComboBox()
        for code, name in tr.LANGUAGES.items():
            self.language_combo.addItem(name, code)
        
        # Set current language in combobox
        current_index = 0
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == language:
                current_index = i
                break
                
        self.language_combo.setCurrentIndex(current_index)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        
        language_layout.addWidget(self.language_combo)
        language_group.setLayout(language_layout)
        self.language_group = language_group
        
        # Add groups to settings panel
        self.settings_layout.addWidget(color_group)
        self.settings_layout.addWidget(display_group)
        self.settings_layout.addWidget(camera_settings_group)
        self.settings_layout.addWidget(language_group)
        
        # About section
        about_group = QGroupBox(tr.get_text("about"))
        about_layout = QVBoxLayout()
        self.about_label = QLabel(tr.get_text("about_text"))
        self.about_label.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(self.about_label)
        about_group.setLayout(about_layout)
        self.about_group = about_group
        self.settings_layout.addWidget(about_group)
        
        self.settings_layout.addStretch()
        
        # Add main components to layout
        self.main_layout.addWidget(self.camera_container, 7)
        self.main_layout.addWidget(self.settings_panel, 3)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(tr.get_text("ready"))
        
        # Initialize colors and camera variables
        self.initialize_color_ranges()
        self.min_contour_area = 500
        self.camera_on = False
        self.cam = None
        
        # Connect signals - update these lines to match our new approach
        # Remove the start_button and stop_button connections and use toggle_camera_button instead
        self.snapshot_button.clicked.connect(self.take_snapshot)
        self.gallery_button.clicked.connect(self.open_gallery)
        
        # Timer for updating the camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # Apply a dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #333;
            }
            QLabel, QCheckBox, QGroupBox, QPushButton {
                color: #EEE;
                font-size: 10pt;
            }
            QCheckBox:hover {
                color: #2196F3;
            }
            QGroupBox {
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #444;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 5px;
                color: #2196F3;
            }
            QGroupBox:hover {
                border: 2px solid #2196F3;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #333;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                border: 1px solid #2196F3;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #64B5F6;
                border: 1px solid #90CAF9;
                width: 20px;
                margin: -3px 0;
            }
            QComboBox {
                background-color: #555;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox:hover {
                background-color: #666;
                border: 1px solid #2196F3;
            }
            QToolTip {
                background-color: #444;
                color: white;
                border: 1px solid #2196F3;
                padding: 2px;
                border-radius: 3px;
                opacity: 200;
            }
        """)
        
        # Load user preferences
        self.camera_permission = self.settings.value("camera_permission", "ask")  # "granted", "denied", "ask"

        # Add tooltips to checkboxes
        self.red_checkbox.setToolTip(tr.get_text("red_checkbox_tooltip"))
        self.green_checkbox.setToolTip(tr.get_text("green_checkbox_tooltip"))
        self.blue_checkbox.setToolTip(tr.get_text("blue_checkbox_tooltip"))
        self.yellow_checkbox.setToolTip(tr.get_text("yellow_checkbox_tooltip"))
        
        # Add tooltips to sliders
        self.sensitivity_slider.setToolTip(tr.get_text("sensitivity_tooltip"))
        self.contrast_slider.setToolTip(tr.get_text("contrast_tooltip"))
        self.display_mode.setToolTip(tr.get_text("display_mode_tooltip"))

    def initialize_color_ranges(self):
        self.color_ranges = {
            'red1': (
                np.array([0, 150, 70]),
                np.array([10, 255, 255])
            ),
            'red2': (
                np.array([170, 150, 70]),
                np.array([180, 255, 255])
            ),
            'green': (
                np.array([35, 70, 70]),
                np.array([85, 255, 255])
            ),
            'blue': (
                np.array([90, 70, 70]),
                np.array([130, 255, 255])
            ),
            'yellow': (
                np.array([20, 100, 100]),
                np.array([35, 255, 255])
            )
        }

    def change_language(self, index):
        """Change the application language"""
        language_code = self.language_combo.itemData(index)
        if tr.set_language(language_code):
            # Save the language setting
            self.settings.setValue("language", language_code)
            
            # Update UI text for visible elements
            self.update_ui_language()
            
            # Show status message
            self.status_bar.showMessage(tr.get_text("language_changed"))
    
    def update_ui_language(self):
        """Update UI elements with new language"""
        # Update window title
        self.setWindowTitle(tr.get_text("app_title"))
        
        # Update buttons
        self.snapshot_button.setText(tr.get_text("take_screenshot"))
        self.gallery_button.setText(tr.get_text("gallery"))
        
        # Update group boxes
        found_groups = {
            "color_detection": False,
            "display_settings": False,
            "language": False,
            "about": False
        }
        
        for group_box in self.findChildren(QGroupBox):
            if not found_groups["color_detection"] and group_box == self.color_group:
                group_box.setTitle(tr.get_text("color_detection"))
                found_groups["color_detection"] = True
            elif not found_groups["display_settings"] and group_box == self.display_group:
                group_box.setTitle(tr.get_text("display_settings"))
                found_groups["display_settings"] = True
            elif not found_groups["language"] and group_box == self.language_group:
                group_box.setTitle(tr.get_text("language"))
                found_groups["language"] = True
            elif not found_groups["about"] and group_box == self.about_group:
                group_box.setTitle(tr.get_text("about"))
                found_groups["about"] = True
        
        # Update checkboxes
        self.red_checkbox.setText(tr.get_text("detect_red"))
        self.green_checkbox.setText(tr.get_text("detect_green"))
        self.blue_checkbox.setText(tr.get_text("detect_blue"))
        self.yellow_checkbox.setText(tr.get_text("detect_yellow"))
        
        # Update labels
        self.detection_sensitivity_label.setText(tr.get_text("detection_sensitivity"))
        self.contrast_label.setText(tr.get_text("contrast"))
        self.display_mode_label.setText(tr.get_text("display_mode"))
        
        # Update camera settings group
        self.camera_settings_group.setTitle(tr.get_text("camera_settings"))
        self.camera_info_label.setText(tr.get_text("camera_settings_info"))
        self.reset_permission_button.setText(tr.get_text("reset_camera_permission"))
        
        # Update permission status
        permission_status_text = ""
        if self.camera_permission == "granted":
            permission_status_text = tr.get_text("permission_status_granted")
        elif self.camera_permission == "denied":
            permission_status_text = tr.get_text("permission_status_denied")
        else:
            permission_status_text = tr.get_text("permission_status_ask")
        self.permission_status_label.setText(f"{tr.get_text('current_permission_status')}: {permission_status_text}")
        
        if not self.camera_on:
            # Refresh the initial message UI with the new language
            self.show_camera_initial_message()
        
        self.about_label.setText(tr.get_text("about_text"))
        
        # Update status bar
        if not self.camera_on:
            self.status_bar.showMessage(tr.get_text("ready"))

        # Update tooltips
        self.snapshot_button.setToolTip(tr.get_text("snapshot_tooltip"))
        self.gallery_button.setToolTip(tr.get_text("gallery_tooltip"))
        
        self.red_checkbox.setToolTip(tr.get_text("red_checkbox_tooltip"))
        self.green_checkbox.setToolTip(tr.get_text("green_checkbox_tooltip"))
        self.blue_checkbox.setToolTip(tr.get_text("blue_checkbox_tooltip"))
        self.yellow_checkbox.setToolTip(tr.get_text("yellow_checkbox_tooltip"))
        
        self.sensitivity_slider.setToolTip(tr.get_text("sensitivity_tooltip"))
        self.contrast_slider.setToolTip(tr.get_text("contrast_tooltip"))
        self.display_mode.setToolTip(tr.get_text("display_mode_tooltip"))
        
        # Update the toggle button text based on camera state
        if self.camera_on:
            self.toggle_camera_button.setText(tr.get_text("stop"))
            self.toggle_camera_button.setToolTip(tr.get_text("stop_tooltip"))
        else:
            self.toggle_camera_button.setText(tr.get_text("start"))
            self.toggle_camera_button.setToolTip(tr.get_text("start_tooltip"))

    def show_camera_initial_message(self):
        """Display the initial camera message without permission buttons"""
        # Clear any existing widgets in camera feed
        for i in reversed(range(self.camera_feed_layout.count())): 
            self.camera_feed_layout.itemAt(i).widget().setParent(None)
        
        # Create message layout
        message_layout = QVBoxLayout()
        
        # Add camera icon
        camera_icon_label = QLabel()
        camera_icon = QPixmap(os.path.join(os.path.dirname(__file__), 'icons', 'camera_icon.png'))
        if camera_icon.isNull():
            # If icon file doesn't exist, create a text placeholder
            camera_icon_label.setText("📷")
            camera_icon_label.setStyleSheet("font-size: 48pt; color: #4CAF50;")
        else:
            # Scale icon to appropriate size
            camera_icon = camera_icon.scaled(QSize(64, 64), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            camera_icon_label.setPixmap(camera_icon)
        
        camera_icon_label.setAlignment(Qt.AlignCenter)
        message_layout.addWidget(camera_icon_label)
        
        # Add information about click to start
        info_text = QLabel(tr.get_text("camera_ready"))
        info_text.setStyleSheet("color: white; font-size: 14pt; margin: 15px;")
        info_text.setWordWrap(True)
        info_text.setAlignment(Qt.AlignCenter)
        message_layout.addWidget(info_text)
        
        # Create a container widget for the message layout
        message_widget = QWidget()
        message_widget.setLayout(message_layout)
        
        # Add the message widget to the camera feed layout
        self.camera_feed_layout.addWidget(message_widget)

    def show_camera_permission_ui(self):
        """Display the camera permission UI in the camera feed area with enhanced buttons"""
        # Clear any existing widgets in camera feed
        for i in reversed(range(self.camera_feed_layout.count())): 
            self.camera_feed_layout.itemAt(i).widget().setParent(None)
        
        # Create permission layout
        permission_layout = QVBoxLayout()
        
        # Add camera icon
        camera_icon_label = QLabel()
        camera_icon = QPixmap(os.path.join(os.path.dirname(__file__), 'icons', 'camera_icon.png'))
        if camera_icon.isNull():
            # If icon file doesn't exist, create a text placeholder
            camera_icon_label.setText("📷")
            camera_icon_label.setStyleSheet("font-size: 48pt; color: #4CAF50;")
        else:
            # Scale icon to appropriate size
            camera_icon = camera_icon.scaled(QSize(64, 64), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            camera_icon_label.setPixmap(camera_icon)
        
        camera_icon_label.setAlignment(Qt.AlignCenter)
        permission_layout.addWidget(camera_icon_label)
        
        # Add permission text
        permission_text = QLabel(tr.get_text("camera_permission_text"))
        permission_text.setStyleSheet("color: white; font-size: 12pt; margin: 15px;")
        permission_text.setWordWrap(True)
        permission_text.setAlignment(Qt.AlignCenter)
        permission_layout.addWidget(permission_text)
        
        # Add buttons for permission
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        # Grant permission button with enhanced hover effects
        grant_button = QPushButton(tr.get_text("grant_permission"))
        grant_button.setToolTip(tr.get_text("grant_permission_tooltip"))
        grant_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #66BB6A;
                border: 2px solid #81C784;
            }
            QPushButton:pressed {
                background-color: #43A047;
            }
        """)
        grant_button.clicked.connect(self.on_camera_permission_granted)
        
        # Deny permission button with enhanced hover effects
        deny_button = QPushButton(tr.get_text("deny_permission"))
        deny_button.setToolTip(tr.get_text("deny_permission_tooltip"))
        deny_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #EF5350;
                border: 2px solid #E57373;
            }
            QPushButton:pressed {
                background-color: #E53935;
            }
        """)
        deny_button.clicked.connect(self.on_camera_permission_denied)
        
        # Add checkbox to remember decision with hover effect
        self.remember_permission = QCheckBox(tr.get_text("remember_decision"))
        self.remember_permission.setToolTip(tr.get_text("remember_decision_tooltip"))
        self.remember_permission.setStyleSheet("""
            QCheckBox {
                color: white;
            }
            QCheckBox:hover {
                color: #2196F3;
            }
        """)
        self.remember_permission.setChecked(True)
        
        button_layout.addWidget(deny_button)
        button_layout.addWidget(grant_button)
        
        permission_layout.addWidget(button_widget)
        permission_layout.addWidget(self.remember_permission)
        
        # Create a container widget for the permission layout
        permission_widget = QWidget()
        permission_widget.setLayout(permission_layout)
        
        # Add the permission widget to the camera feed layout
        self.camera_feed_layout.addWidget(permission_widget)

    def reset_camera_permission(self):
        """Reset saved camera permission to ask again next time"""
        self.camera_permission = "ask"
        self.settings.setValue("camera_permission", "ask")
        self.status_bar.showMessage(tr.get_text("permission_reset"))
        
        # Update the permission status display
        self.update_permission_status_display()
    
    def on_camera_permission_granted(self):
        """Handle when permission is granted by the user"""
        # Save permission preference if requested
        if hasattr(self, 'remember_permission') and self.remember_permission.isChecked():
            self.camera_permission = "granted"
            self.settings.setValue("camera_permission", "granted")
            # Update the permission status display
            self.update_permission_status_display()
            
        # Continue with starting the camera
        self.start_camera_process()
    
    def on_camera_permission_denied(self):
        """Handle when permission is denied by the user"""
        # Save permission preference if requested
        if hasattr(self, 'remember_permission') and self.remember_permission.isChecked():
            self.camera_permission = "denied"
            self.settings.setValue("camera_permission", "denied")
            # Update the permission status display
            self.update_permission_status_display()
        
        self.status_bar.showMessage(tr.get_text("camera_permission_denied"))
        # Return to initial message
        self.show_camera_initial_message()
    
    def update_permission_status_display(self):
        """Update the permission status display in Camera Settings"""
        permission_status_text = ""
        if self.camera_permission == "granted":
            permission_status_text = tr.get_text("permission_status_granted")
        elif self.camera_permission == "denied":
            permission_status_text = tr.get_text("permission_status_denied")
        else:
            permission_status_text = tr.get_text("permission_status_ask")
        
        self.permission_status_label.setText(f"{tr.get_text('current_permission_status')}: {permission_status_text}")
    
    def toggle_camera(self):
        """Toggle camera on and off"""
        if self.camera_on:
            self.stop_camera()
        else:
            self.start_camera()
    
    def start_camera(self):
        """Start the camera after checking permissions"""
        if not self.camera_on:
            # Check saved permission preference
            if self.camera_permission == "granted":
                # Permission already granted, start camera directly
                self.start_camera_process()
            elif self.camera_permission == "denied":
                # Permission already denied
                self.status_bar.showMessage(tr.get_text("camera_permission_denied"))
            else:
                # Ask for permission
                self.show_camera_permission_ui()
    
    def start_camera_process(self):
        """Start the camera process after permission is granted"""
        # Clear the camera feed layout
        for i in reversed(range(self.camera_feed_layout.count())): 
            self.camera_feed_layout.itemAt(i).widget().setParent(None)
            
        # Show initializing message
        initializing_label = QLabel(tr.get_text("camera_initializing"))
        initializing_label.setStyleSheet("color: white; font-size: 12pt;")
        initializing_label.setAlignment(Qt.AlignCenter)
        self.camera_feed_layout.addWidget(initializing_label)
        QApplication.processEvents()  # Update UI immediately
        
        # Now try to start the camera
        self.cam = cv2.VideoCapture(0)
        if self.cam.isOpened():
            self.camera_on = True
            self.timer.start(33)  # ~30 FPS
            self.status_bar.showMessage(tr.get_text("camera_started"))
            
            # Update the toggle button appearance for "Stop"
            self.toggle_camera_button.setText(tr.get_text("stop"))
            self.toggle_camera_button.setToolTip(tr.get_text("stop_tooltip"))
            self.toggle_camera_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    padding: 8px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #EF5350;
                    border: 2px solid #E57373;
                }
                QPushButton:pressed {
                    background-color: #E53935;
                }
            """)
        else:
            self.status_bar.showMessage(tr.get_text("camera_start_failed"))
            self.show_camera_initial_message()  # Show initial message again if camera fails to start

    def take_snapshot(self):
        if hasattr(self, 'current_frame'):
            # Create a screenshots directory if it doesn't exist
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
                
            # Find the next available snapshot number
            screenshots = glob.glob("snapshot_*.png")
            next_num = 1
            if screenshots:
                # Extract numbers from existing files and find the maximum
                existing_nums = []
                for filename in screenshots:
                    try:
                        num = int(filename.replace("snapshot_", "").replace(".png", ""))
                        existing_nums.append(num)
                    except ValueError:
                        pass
                if existing_nums:
                    next_num = max(existing_nums) + 1
                    
            filename = f"snapshot_{next_num}.png"
            cv2.imwrite(filename, self.current_frame)
            self.status_bar.showMessage(tr.get_text("screenshot_saved", filename))

    def update_frame(self):
        ret, frame = self.cam.read()
        if ret:
            self.current_frame = frame.copy()
            
            # Convert BGR to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create masks for selected colors
            masks = {}
            if self.red_checkbox.isChecked():
                mask_red1 = cv2.inRange(hsv, self.color_ranges['red1'][0], self.color_ranges['red1'][1])
                mask_red2 = cv2.inRange(hsv, self.color_ranges['red2'][0], self.color_ranges['red2'][1])
                masks['red'] = mask_red1 | mask_red2
            
            if self.green_checkbox.isChecked():
                masks['green'] = cv2.inRange(hsv, self.color_ranges['green'][0], self.color_ranges['green'][1])
            
            if self.blue_checkbox.isChecked():
                masks['blue'] = cv2.inRange(hsv, self.color_ranges['blue'][0], self.color_ranges['blue'][1])
            
            if self.yellow_checkbox.isChecked():
                masks['yellow'] = cv2.inRange(hsv, self.color_ranges['yellow'][0], self.color_ranges['yellow'][1])
                
            # Combine all masks
            mask_combined = np.zeros_like(hsv[:, :, 0])
            for color, mask in masks.items():
                mask_combined = mask_combined | mask
            
            # Expand masks
            kernel = np.ones((5, 5), np.uint8)
            mask_combined = cv2.dilate(mask_combined, kernel, iterations=2)
            
            # Filter the colors
            result = cv2.bitwise_and(frame, frame, mask=mask_combined)
            
            # Adjusting vibrance for masked colors based on sensitivity
            sensitivity = self.sensitivity_slider.value() * 20 + 40  # Map 1-10 to 60-240
            result[np.where((result != [0, 0, 0]).all(axis=2))] = [sensitivity, sensitivity, sensitivity]
            
            # Darkening the original frame
            contrast = self.contrast_slider.value() / 10  # Map 1-10 to 0.1-1.0
            darkened_frame = cv2.addWeighted(frame, contrast, np.zeros_like(frame), 1-contrast, 0)
            
            # Combining the results
            combined_result = cv2.addWeighted(darkened_frame, 0.7, result, 0.3, 0)
            
            # Tag colors based on contours
            colors = {
                'red': (0, 0, 255) if self.red_checkbox.isChecked() else None,
                'green': (0, 255, 0) if self.green_checkbox.isChecked() else None,
                'blue': (255, 0, 0) if self.blue_checkbox.isChecked() else None,
                'yellow': (0, 255, 255) if self.yellow_checkbox.isChecked() else None
            }
            
            # Translate color names based on current language
            color_translated = {
                'red': tr.get_text("red"),
                'green': tr.get_text("green"),
                'blue': tr.get_text("blue"),
                'yellow': tr.get_text("yellow")
            }
            
            # First draw the rectangles
            for color_name, mask in masks.items():
                if colors[color_name] is not None:
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    for contour in contours:
                        if cv2.contourArea(contour) > self.min_contour_area:
                            x, y, w, h = cv2.boundingRect(contour)
                            mask_contour = mask[y:y+h, x:x+w]
                            contour_area = cv2.contourArea(contour)
                            mask_area = np.sum(mask_contour > 0)
                            accuracy = min((mask_area / contour_area) * 100, 100)
                            
                            # Draw rectangle around the detected object
                            cv2.rectangle(combined_result, (x, y), (x + w, y + h), colors[color_name], 2)
            
            # Then use PIL to draw the text with proper UTF-8 support
            for color_name, mask in masks.items():
                if colors[color_name] is not None:
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    for contour in contours:
                        if cv2.contourArea(contour) > self.min_contour_area:
                            x, y, w, h = cv2.boundingRect(contour)
                            mask_contour = mask[y:y+h, x:x+w]
                            contour_area = cv2.contourArea(contour)
                            mask_area = np.sum(mask_contour > 0)
                            accuracy = min((mask_area / contour_area) * 100, 100)
                            
                            # Create text with color name and accuracy
                            text = f"{color_translated[color_name]} ({accuracy:.1f}%)"
                            
                            # Use our UTF-8 text drawing function
                            combined_result = draw_text_with_utf8(
                                combined_result,
                                text,
                                (x, y - 25),  # Position the text above the rectangle
                                text_color=colors[color_name],
                                font_size=16,
                                stroke_color=(0, 0, 0),  # Black outline
                                stroke_width=1
                            )
            
            # Convert result to QImage for display
            h, w, c = combined_result.shape
            bytesPerLine = 3 * w
            qImg = QImage(combined_result.data, w, h, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
            
            # Since we no longer have a camera_feed QLabel, we need to create one for displaying the image
            # Clear any existing widgets
            for i in reversed(range(self.camera_feed_layout.count())): 
                self.camera_feed_layout.itemAt(i).widget().setParent(None)
                
            # Create and add image label
            image_label = QLabel()
            image_label.setPixmap(QPixmap.fromImage(qImg).scaled(
                self.camera_feed_container.width() - 40,  # Account for margins
                self.camera_feed_container.height() - 40, 
                Qt.KeepAspectRatio
            ))
            image_label.setAlignment(Qt.AlignCenter)
            self.camera_feed_layout.addWidget(image_label)

    def stop_camera(self):
        if self.camera_on:
            self.timer.stop()
            self.cam.release()
            self.camera_on = False
            
            # Return to initial message
            self.show_camera_initial_message()
            
            self.status_bar.showMessage(tr.get_text("camera_stopped"))
            
            # Update the toggle button appearance for "Start"
            self.toggle_camera_button.setText(tr.get_text("start"))
            self.toggle_camera_button.setToolTip(tr.get_text("start_tooltip"))
            self.toggle_camera_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 8px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #66BB6A;
                    border: 2px solid #81C784;
                }
                QPushButton:pressed {
                    background-color: #43A047;
                }
            """)

    def open_gallery(self):
        gallery = ScreenshotGallery(self)
        gallery.exec_()

# Function to draw text with UTF-8 support using PIL
def draw_text_with_utf8(img, text, position, text_color=(255, 255, 255), font_size=20, stroke_color=(0, 0, 0), stroke_width=2):
    # Convert the image from OpenCV BGR format to RGB for PIL
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img)
    
    # Try to load a font that supports UTF-8
    try:
        # Try to find a suitable system font (Arial supports Turkish chars)
        if os.name == 'nt':  # Windows
            font_path = "C:\\Windows\\Fonts\\arial.ttf"
        else:  # Linux/Mac
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        
        if not os.path.exists(font_path):
            # Fallback to default
            font = ImageFont.load_default()
        else:
            font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw text with stroke (outline)
    x, y = position
    
    # Draw stroke (outline)
    draw.text((x-stroke_width, y-stroke_width), text, font=font, fill=stroke_color)
    draw.text((x+stroke_width, y-stroke_width), text, font=font, fill=stroke_color)
    draw.text((x-stroke_width, y+stroke_width), text, font=font, fill=stroke_color)
    draw.text((x+stroke_width, y+stroke_width), text, font=font, fill=stroke_color)
    
    # Draw the main text
    draw.text(position, text, font=font, fill=text_color)
    
    # Convert back to OpenCV format (BGR)
    img_with_text = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return img_with_text

def main():
    app = QApplication(sys.argv)
    window = ColorVisionAid()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
