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
        """Open gallery as a non-modal window (single instance)."""
        # Keep one instance to avoid modality issues blocking child viewers
        if not hasattr(self, "_gallery_window") or self._gallery_window is None:
            self._gallery_window = ScreenshotGallery(self)
            # Ensure it's deleted on close so our reference can be cleared
            self._gallery_window.setAttribute(Qt.WA_DeleteOnClose, True)
            try:
                # Clear reference when destroyed
                self._gallery_window.destroyed.connect(lambda _=None: setattr(self, "_gallery_window", None))
            except Exception:
                pass
        # Show and bring to front
        self._gallery_window.show()
        self._gallery_window.raise_()
        self._gallery_window.activateWindow()

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
        
        # Auto-save profile when color blindness type changes
        self.auto_save_profile_on_change()

    def open_advanced_settings(self):
        """Open advanced settings dialog"""
        dialog = AdvancedSettingsDialog(self)
        dialog.exec_()

    def change_language(self, index):
        """Change application language"""
        language_code = self.language_combo.itemData(index)
        # Capture old language context for name localization
        old_lang = getattr(tr, 'current_language', 'en')
        # Keep old language's default profile name to detect and rename after switch
        old_default_name = tr.get_text("default_profile")
        if tr.set_language(language_code):
            # Update current profile
            if hasattr(self, 'current_profile') and self.current_profile:
                self.current_profile.language = language_code
                self.profile_manager.save_profile(self.current_profile)

            # Save language setting
            self.settings.setValue("language", language_code)

            # Update visible elements language
            self.update_ui_language()

            # If current profile was the default profile in previous language,
            # rename it to the new language's default name so it stays localized
            try:
                if hasattr(self, 'current_profile') and self.current_profile:
                    new_default_name = tr.get_text("default_profile")
                    if self.current_profile.name == old_default_name and old_default_name != new_default_name:
                        if self.profile_manager.rename_profile(old_default_name, new_default_name):
                            self.current_profile.name = new_default_name
                            # Persist and refresh UI list
                            self.settings.setValue("current_profile", new_default_name)
                            if hasattr(self, 'profile_selector'):
                                self.profile_selector.load_profiles()
                                idx = self.profile_selector.profile_combo.findText(new_default_name)
                                if idx >= 0:
                                    self.profile_selector.profile_combo.setCurrentIndex(idx)
                    else:
                        # Also localize custom names that end with the language-specific "profile" suffix
                        # e.g., "My Color profile" -> "My Color profil" when switching to Turkish (and vice versa)
                        new_lang = getattr(tr, 'current_language', 'en')
                        old_suffix = 'profil' if (old_lang == 'tr') else 'profile'
                        new_suffix = 'profil' if (new_lang == 'tr') else 'profile'
                        name_lower = (self.current_profile.name or '').lower()
                        # Skip if name equals the default names to avoid double processing
                        if self.current_profile.name not in (old_default_name, tr.get_text("default_profile")):
                            token = ' ' + old_suffix
                            if name_lower.endswith(token):
                                base = self.current_profile.name[:-(len(old_suffix))].rstrip()
                                candidate = f"{base} {new_suffix}".strip()
                                if candidate and candidate != self.current_profile.name:
                                    if self.profile_manager.rename_profile(self.current_profile.name, candidate):
                                        self.current_profile.name = candidate
                                        self.settings.setValue("current_profile", candidate)
                                        if hasattr(self, 'profile_selector'):
                                            self.profile_selector.load_profiles()
                                            idx2 = self.profile_selector.profile_combo.findText(candidate)
                                            if idx2 >= 0:
                                                self.profile_selector.profile_combo.setCurrentIndex(idx2)
                # Bulk suffix localization for all profiles
                try:
                    import os as _os
                    new_lang = getattr(tr, 'current_language', 'en')
                    old_suffix = 'profil' if (old_lang == 'tr') else 'profile'
                    new_suffix = 'profil' if (new_lang == 'tr') else 'profile'
                    token = ' ' + old_suffix
                    profiles = self.profile_manager.get_all_profiles()
                    used_names = set(profiles)
                    new_default_name = tr.get_text("default_profile")
                    for name in list(profiles):
                        # Skip default names and already converted names
                        if name in (old_default_name, new_default_name):
                            continue
                        # Skip the currently renamed profile if already updated
                        if hasattr(self, 'current_profile') and self.current_profile and name == self.current_profile.name:
                            continue
                        if name.lower().endswith(token):
                            base = name[:-(len(old_suffix))].rstrip()
                            candidate = f"{base} {new_suffix}".strip()
                            final_name = candidate
                            # Ensure uniqueness by appending (n) if needed
                            counter = 2
                            while final_name in used_names:
                                final_name = f"{candidate} ({counter})"
                                counter += 1
                            if final_name != name:
                                if self.profile_manager.rename_profile(name, final_name):
                                    used_names.discard(name)
                                    used_names.add(final_name)
                                    # Update UI selection if we just renamed the selected text in combo
                                    if hasattr(self, 'profile_selector'):
                                        idx_old = self.profile_selector.profile_combo.findText(name)
                                        if idx_old >= 0:
                                            self.profile_selector.load_profiles()
                except Exception:
                    pass
            except Exception as _e:
                # Non-fatal: just skip renaming if anything goes wrong
                pass

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

            # Auto-save profile
            self.auto_save_profile_on_change()

    def change_theme(self, index):
        """Change application theme"""
        theme_value = self.theme_combo.itemData(index) if hasattr(self, 'theme_combo') else 'dark'
        self.theme = theme_value or 'dark'
        
        # Update current profile
        if hasattr(self, 'current_profile') and self.current_profile:
            self.current_profile.theme = self.theme
            self.profile_manager.save_profile(self.current_profile)
        
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
        
        # Update profile selector theme (after group box refresh)
        if hasattr(self, 'profile_selector'):
            self.profile_selector.apply_theme()
        
        # Update combo box themes
        from ..ui_components.groups import update_combo_themes
        update_combo_themes(self)
        
        # Update any open dialog/gallery windows with new theme
        self._update_child_window_themes()
        
        # Auto-save profile
        self.auto_save_profile_on_change()

    def on_profile_changed(self, profile_name):
        """Handle profile change from profile selector"""
        self.status_bar.showMessage(tr.get_text("profile_loaded_successfully", profile_name), 2000)
        # Update window title using localized app title
        app_title = tr.get_text("app_title")
        self.setWindowTitle(f"{app_title} - {profile_name}")

        # Update auto-save reference
        if hasattr(self, 'profile_selector'):
            self.profile_selector.auto_save_current_profile()
    
    def auto_save_profile_on_change(self):
        """Auto-save current profile when any setting changes"""
        if hasattr(self, 'profile_selector'):
            self.profile_selector.auto_save_current_profile()
