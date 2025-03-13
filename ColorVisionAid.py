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
        self.camera_feed = QLabel(tr.get_text("camera_initializing"))
        self.camera_feed.setAlignment(Qt.AlignCenter)
        self.camera_feed.setStyleSheet("background-color: #222; color: white; border-radius: 10px;")
        self.camera_layout.addWidget(self.camera_feed)
        
        # Add buttons under camera
        button_layout = QHBoxLayout()
        self.start_button = QPushButton(tr.get_text("start"))
        self.stop_button = QPushButton(tr.get_text("stop"))
        self.snapshot_button = QPushButton(tr.get_text("take_screenshot"))
        self.gallery_button = QPushButton(tr.get_text("gallery"))
        
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; border-radius: 5px;")
        self.stop_button.setStyleSheet("background-color: #f44336; color: white; padding: 8px; border-radius: 5px;")
        self.snapshot_button.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; border-radius: 5px;")
        self.gallery_button.setStyleSheet("background-color: #9C27B0; color: white; padding: 8px; border-radius: 5px;")
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
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
        
        # Connect signals
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)
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
            QComboBox {
                background-color: #555;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
        """)

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
        self.start_button.setText(tr.get_text("start"))
        self.stop_button.setText(tr.get_text("stop"))
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
        
        if not self.camera_on:
            self.camera_feed.setText(tr.get_text("camera_initializing"))
            
        self.about_label.setText(tr.get_text("about_text"))
        
        # Update status bar
        if not self.camera_on:
            self.status_bar.showMessage(tr.get_text("ready"))

    def start_camera(self):
        if not self.camera_on:
            self.cam = cv2.VideoCapture(0)
            if self.cam.isOpened():
                self.camera_on = True
                self.timer.start(33)  # ~30 FPS
                self.status_bar.showMessage(tr.get_text("camera_started"))
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
            else:
                self.status_bar.showMessage(tr.get_text("camera_start_failed"))

    def stop_camera(self):
        if self.camera_on:
            self.timer.stop()
            self.cam.release()
            self.camera_on = False
            self.camera_feed.setText(tr.get_text("camera_stopped"))
            self.status_bar.showMessage(tr.get_text("camera_stopped"))
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

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
            self.camera_feed.setPixmap(QPixmap.fromImage(qImg).scaled(self.camera_feed.width(), self.camera_feed.height(), Qt.KeepAspectRatio))

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
