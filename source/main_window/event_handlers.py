"""
Event handlers for ColorVisionAid main window
Contains non-camera event handling functions
"""

import os
import cv2
from PyQt5.QtWidgets import QFileDialog, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from ..translations import translator as tr
from ..ui_components import ScreenshotGallery
from ..ui_components import AdvancedSettingsDialog
from ..ui_components import apply_theme

class EventHandlers:
    """Mixin class for event handling functionality"""
    
    def take_screenshot(self):
        """Take screenshot"""
        success, result = self.camera_manager.take_screenshot()
        if success:
            # Separate filename from path to show file name
            filename = os.path.basename(result)
            self.status_bar.showMessage(tr.get_text("screenshot_saved", filename))
        else:
            self.status_bar.showMessage(tr.get_text("screenshot_failed", result))

    def open_gallery(self):
        """Open gallery"""
        gallery = ScreenshotGallery(self)
        gallery.exec_()

    def load_file(self):
        """File loading and analysis"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr.get_text("select_image_file"),
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.gif);;All Files (*)"
        )
        
        if file_path:
            try:
                # Load image
                image = cv2.imread(file_path)
                if image is None:
                    self.status_bar.showMessage(tr.get_text("file_load_failed"))
                    return
                
                # Stop camera (if active)
                if self.camera_manager.camera_open:
                    self.stop_camera()
                
                # Analyze and display loaded image
                self.analyze_loaded_image(image, file_path)
                
            except Exception as e:
                self.status_bar.showMessage(f"File loading error: {str(e)}")

    def analyze_loaded_image(self, image, file_path):
        """Analyze loaded image and show result"""
        try:
            # Resize image to appropriate size (reduce if too large)
            height, width = image.shape[:2]
            max_size = 800
            
            if max(height, width) > max_size:
                scale_factor = max_size / max(height, width)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = cv2.resize(image, (new_width, new_height))
            
            # Perform color analysis
            selected_colors = {
                'skin': True,  # Skin tone works in background
                'red': self.red_checkbox.isChecked(),
                'green': self.green_checkbox.isChecked(),
                'blue': self.blue_checkbox.isChecked(),
                'yellow': self.yellow_checkbox.isChecked()
            }
            
            translated_color_names = {
                'red': tr.get_text("red"),
                'green': tr.get_text("green"),
                'blue': tr.get_text("blue"),
                'yellow': tr.get_text("yellow")
            }
            
            color_blindness_type = self.color_blindness_combo.currentData() or 'red_green'
            
            # Analyze with color detector
            analysis_result = self.color_detector.process_frame(
                image,
                selected_colors,
                self.sensitivity_slider.value(),
                self.contrast_value,
                translated_color_names,
                self.skin_tone_filtering_active,
                self.stability_enhancement_active,
                color_blindness_type,
                False,  # mobile_optimization
                self.debug_mode_active
            )
            
            # Show result
            self.show_analysis_result(analysis_result, file_path)
            
        except Exception as e:
            self.status_bar.showMessage(f"Analysis error: {str(e)}")

    def show_analysis_result(self, analysis_result, file_path):
        """Show analysis result in camera area"""
        try:
            # Convert result to QImage
            h, w, c = analysis_result.shape
            bytes_per_line = 3 * w
            qImg = QImage(analysis_result.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            
            # Clear existing widgets
            for i in reversed(range(self.camera_feed_layout.count())): 
                widget = self.camera_feed_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # Show file name
            file_name = os.path.basename(file_path)
            title_label = QLabel(f"📁 {tr.get_text('analyzing_file')}: {file_name}")
            title_label.setStyleSheet("""
                QLabel {
                    color: #2196F3;
                    font-size: 12pt;
                    font-weight: bold;
                    padding: 10px;
                    text-align: center;
                }
            """)
            title_label.setAlignment(Qt.AlignCenter)
            self.camera_feed_layout.addWidget(title_label)
            
            # Show analyzed image
            image_label = QLabel()
            image_label.setPixmap(QPixmap.fromImage(qImg).scaled(
                self.camera_feed_container.width() - 40,
                self.camera_feed_container.height() - 80,  # Leave space for title
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            image_label.setAlignment(Qt.AlignCenter)
            self.camera_feed_layout.addWidget(image_label)
            
            # Status message
            self.status_bar.showMessage(tr.get_text("file_analysis_complete"))
            
        except Exception as e:
            self.status_bar.showMessage(f"Display error: {str(e)}")

    def color_blindness_type_changed(self, index):
        """Automatic color selection when color blindness type changes"""
        type_code = self.color_blindness_combo.itemData(index)
        
        # Turn off all colors first
        self.red_checkbox.setChecked(False)
        self.green_checkbox.setChecked(False)
        self.blue_checkbox.setChecked(False)
        self.yellow_checkbox.setChecked(False)
        
        # Turn on appropriate colors based on selected type
        if type_code == "red_green":
            # Red-Green color blindness
            self.red_checkbox.setChecked(True)
            self.green_checkbox.setChecked(True)
        elif type_code == "blue_yellow":
            # Blue-Yellow color blindness
            self.blue_checkbox.setChecked(True)
            self.yellow_checkbox.setChecked(True)
        elif type_code == "protanopia":
            # Protanopia (Red blindness) - Difficulty distinguishing red and green
            self.red_checkbox.setChecked(True)
            self.green_checkbox.setChecked(True)
            self.blue_checkbox.setChecked(True)  # Blue is clearly visible
        elif type_code == "deuteranopia":
            # Deuteranopia (Green blindness) - Difficulty distinguishing red and green
            self.red_checkbox.setChecked(True)
            self.green_checkbox.setChecked(True)
            self.blue_checkbox.setChecked(True)  # Blue is clearly visible
        elif type_code == "tritanopia":
            # Tritanopia (Blue blindness) - Difficulty distinguishing blue and yellow
            self.blue_checkbox.setChecked(True)
            self.yellow_checkbox.setChecked(True)
            self.red_checkbox.setChecked(True)  # Red is clearly visible
        elif type_code == "complete":
            # Complete color blindness - All colors
            self.red_checkbox.setChecked(True)
            self.green_checkbox.setChecked(True)
            self.blue_checkbox.setChecked(True)
            self.yellow_checkbox.setChecked(True)
        elif type_code == "custom":
            # Custom color selection - Open advanced settings
            self.open_advanced_settings()

    def open_advanced_settings(self):
        """Open advanced settings dialog"""
        dialog = AdvancedSettingsDialog(self)
        dialog.exec_()

    def change_language(self, index):
        """Change application language"""
        language_code = self.language_combo.itemData(index)
        if tr.set_language(language_code):
            # Save language setting
            self.settings.setValue("language", language_code)
            
            # Update visible elements language
            self.update_ui_language()
            
            # Show status message
            self.status_bar.showMessage(tr.get_text("language_changed"))

            # Update theme labels and tooltip according to new language
            if hasattr(self, 'theme_combo'):
                # Refill items preserving data
                current_data = self.theme_combo.currentData()
                self.theme_combo.blockSignals(True)
                self.theme_combo.clear()
                self.theme_combo.addItem(tr.get_text("dark"), "dark")
                self.theme_combo.addItem(tr.get_text("light"), "light")
                # restore selection
                restore_index = 0
                for i in range(self.theme_combo.count()):
                    if self.theme_combo.itemData(i) == current_data:
                        restore_index = i
                        break
                self.theme_combo.setCurrentIndex(restore_index)
                self.theme_combo.setToolTip(tr.get_text("theme_tooltip"))
                self.theme_combo.blockSignals(False)

    def change_theme(self, index):
        """Change application theme"""
        theme_value = self.theme_combo.itemData(index) if hasattr(self, 'theme_combo') else 'dark'
        self.theme = theme_value or 'dark'
        # Persist and apply
        self.settings.setValue("theme", self.theme)
        
        # Apply window theme
        self._apply_window_theme()
        
        apply_theme(self, self.theme)
        # Update inline-styled widgets and buttons
        if hasattr(self, 'apply_theme_to_components'):
            self.apply_theme_to_components()
        
        # Force refresh all QGroupBox styling for the new theme
        if hasattr(self, '_force_refresh_group_boxes'):
            self._force_refresh_group_boxes()
        
        # Update combo box themes
        from ..ui_components.groups import update_combo_themes
        update_combo_themes(self)
        
        # Update any open dialog/gallery windows with new theme
        self._update_child_window_themes()
