"""
Event handlers for ColorVisionAid main window
Contains non-camera event handling functions
"""

import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QFileDialog, QLabel, QSizePolicy, QApplication
from PyQt5.QtCore import Qt, QObject, QEvent, QSize
from PyQt5.QtGui import QImage, QPixmap
from ..translations import translator as tr
from ..ui_components import ScreenshotGallery
from ..ui_components import AdvancedSettingsDialog
from ..ui_components import apply_theme
from ..ui_components.groups import _apply_combo_theme

class EventHandlers:
    """Mixin class for event handling functionality"""
    def on_camera_selection_changed(self, index: int):
        """Handle camera selection combo change"""
        try:
            if not hasattr(self, 'camera_combo'):
                return
            camera_index = self.camera_combo.itemData(index)
            if camera_index is None:
                return
            
            # Set selected camera in camera manager
            self.camera_manager.set_selected_camera(int(camera_index))
            
            # Persist selection in settings
            self.settings.setValue('selected_camera_index', int(camera_index))
            
            # Save to current profile
            if hasattr(self, 'current_profile') and self.current_profile is not None:
                setattr(self.current_profile, 'selected_camera_index', int(camera_index))
                if hasattr(self, 'profile_manager'):
                    self.profile_manager.save_profile(self.current_profile)
            
            # If camera is running, restart with new camera
            if self.camera_manager.camera_open:
                self.stop_camera()
                self.camera_startup_process()
                
        except Exception as e:
            print(f"Error changing camera selection: {e}")
    
    def on_camera_device_changed(self, index: int):
        """Handle camera device combo selection change."""
        try:
            if not hasattr(self, 'camera_device_combo'):
                return
            device_index = self.camera_device_combo.itemData(index)
            if device_index is None:
                return
            # Persist selection
            self.selected_camera_index = int(device_index)
            try:
                self.settings.setValue('selected_camera_index', int(device_index))
            except Exception:
                pass
            try:
                if hasattr(self, 'current_profile') and self.current_profile is not None:
                    setattr(self.current_profile, 'selected_camera_index', int(device_index))
                    # Save profile silently
                    if hasattr(self, 'profile_manager'):
                        self.profile_manager.save_profile(self.current_profile)
            except Exception:
                pass
            # If camera is running, switch device safely
            if hasattr(self, 'camera_manager') and self.camera_manager is not None and self.camera_manager.camera_open:
                try:
                    self.stop_camera()
                    # If permission previously granted, restart automatically
                    self.camera_startup_process()
                except Exception:
                    pass
            # Nudge theme of combo for consistency
            try:
                _apply_combo_theme(self.camera_device_combo, self)
            except Exception:
                pass
        except Exception:
            pass
    def _apply_detect_flags(self, red: bool, green: bool, blue: bool, yellow: bool, persist: bool = True):
        """Apply detection flags by storing them and updating button themes."""
        print(f"[DEBUG] _apply_detect_flags called: red={red}, green={green}, blue={blue}, yellow={yellow}, persist={persist}")
        
        # Store current detection settings for use by camera handlers and dialogs
        self.current_detection_settings = {
            'red': red,
            'green': green,
            'blue': blue,
            'yellow': yellow
        }
        
        if persist:
            # Persist immediately to QSettings to avoid later overrides
            try:
                if hasattr(self, 'settings') and self.settings is not None:
                    self.settings.setValue('detect_red', bool(red))
                    self.settings.setValue('detect_green', bool(green))
                    self.settings.setValue('detect_blue', bool(blue))
                    self.settings.setValue('detect_yellow', bool(yellow))
                    print(f"[DEBUG] Detection settings persisted to QSettings")
            except Exception as e:
                print(f"[DEBUG] Failed to persist detection settings: {e}")

        # Update button themes based on current detection settings
        try:
            from source.ui_components.buttons import update_button_theme
            update_button_theme(self)
            print("[DEBUG] Button theme updated after detection flags changed")
        except Exception as e:
            print(f"[DEBUG] Failed to update button theme: {e}")
            
        print(f"[DEBUG] Detection settings stored: {self.current_detection_settings}")

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
            # Create gallery with self as parent to ensure proper theme inheritance
            self._gallery_window = ScreenshotGallery(self)
            # Set theme to match main window
            self._gallery_window.theme = getattr(self, 'theme', 'dark')
            # Apply theme immediately after construction
            self._gallery_window.apply_gallery_theme(self._gallery_window.theme)
            # Force complete theme application
            self._gallery_window._force_complete_theme_application(self._gallery_window.theme)
            # Restore last geometry if present in current profile
            try:
                prof = getattr(self, 'current_profile', None)
                if prof:
                    gx = int(getattr(prof, 'gallery_x', -1))
                    gy = int(getattr(prof, 'gallery_y', -1))
                    gw = int(getattr(prof, 'gallery_width', -1))
                    gh = int(getattr(prof, 'gallery_height', -1))
                    if gw > 100 and gh > 100 and gx >= 0 and gy >= 0:
                        self._gallery_window.setGeometry(gx, gy, gw, gh)
            except Exception:
                pass
            # Ensure it's deleted on close so our reference can be cleared
            self._gallery_window.setAttribute(Qt.WA_DeleteOnClose, True)
            try:
                # Clear reference when destroyed
                self._gallery_window.destroyed.connect(lambda _=None: setattr(self, "_gallery_window", None))
            except Exception:
                pass
        else:
            # If window already exists, sync theme before showing
            current_theme = getattr(self, 'theme', 'dark')
            if self._gallery_window.theme != current_theme:
                self._gallery_window.theme = current_theme
                self._gallery_window.apply_gallery_theme(current_theme)
                self._gallery_window._force_complete_theme_application(current_theme)
        
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
                print(f"Attempting to load image from: {file_path}")
                
                # Validate file exists and is readable
                if not os.path.exists(file_path):
                    self.status_bar.showMessage("File does not exist")
                    return
                
                if not os.access(file_path, os.R_OK):
                    self.status_bar.showMessage("File is not readable")
                    return
                
                # Load image using numpy to handle Unicode file paths
                # Read file as binary data
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                # Decode image from binary data
                nparr = np.frombuffer(file_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is None:
                    print(f"cv2.imdecode returned None for file: {file_path}")
                    self.status_bar.showMessage(tr.get_text("file_load_failed"))
                    return
                
                print(f"Image loaded successfully. Shape: {image.shape}")
                
                # Stop camera (if active) - check if camera_manager exists
                if hasattr(self, 'camera_manager') and self.camera_manager and self.camera_manager.camera_open:
                    print("Stopping camera before analyzing file...")
                    self.stop_camera()
                
                # Analyze and display loaded image
                self.analyze_loaded_image(image, file_path)
                
            except Exception as e:
                print(f"Exception in load_file: {str(e)}")
                import traceback
                traceback.print_exc()
                self.status_bar.showMessage(f"File loading error: {str(e)}")

    def analyze_loaded_image(self, image, file_path):
        """Analyze loaded image and show result"""
        try:
            print(f"Starting image analysis for: {file_path}")
            print(f"Image shape: {image.shape}")
            
            # Resize image to appropriate size (reduce if too large)
            height, width = image.shape[:2]
            max_size = 800
            
            if max(height, width) > max_size:
                scale_factor = max_size / max(height, width)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = cv2.resize(image, (new_width, new_height))
                print(f"Image resized to: {new_width}x{new_height}")
            
            # Check if detection settings exist
            if not hasattr(self, 'current_detection_settings'):
                # Initialize default detection settings if not set
                self.current_detection_settings = {
                    'red': True,
                    'green': True, 
                    'blue': False,
                    'yellow': False
                }
            
            # Perform color analysis
            selected_colors = self.current_detection_settings.copy()
            selected_colors['skin'] = True  # Skin tone works in background
            
            print(f"Selected colors: {selected_colors}")

            # If no manual colors are selected yet (common on first app start before profile applies),
            # auto-select by color blindness type to avoid empty detection, mirroring camera live logic.
            if not (selected_colors['red'] or selected_colors['green'] or selected_colors['blue'] or selected_colors['yellow']):
                try:
                    cb_type_auto = self.color_blindness_combo.currentData() or 'none'
                except Exception:
                    cb_type_auto = 'none'
                    
                print(f"Auto-selecting colors based on CB type: {cb_type_auto}")
                if cb_type_auto in ('protanopia', 'deuteranopia'):
                    selected_colors['red'] = True
                    selected_colors['green'] = True
                    # Reflect in UI and persist once for consistency
                    try:
                        if hasattr(self, '_apply_detect_flags'):
                            self._apply_detect_flags(True, True, False, False, persist=True)
                    except Exception:
                        pass
                elif cb_type_auto == 'tritanopia':
                    selected_colors['blue'] = True
                    selected_colors['yellow'] = True
                    try:
                        if hasattr(self, '_apply_detect_flags'):
                            self._apply_detect_flags(False, False, True, True, persist=True)
                    except Exception:
                        pass
            
            # Check if color_detector exists
            if not hasattr(self, 'color_detector') or self.color_detector is None:
                self.status_bar.showMessage("Color detector not initialized")
                return
                
            translated_color_names = {
                'red': tr.get_text("red"),
                'green': tr.get_text("green"),
                'blue': tr.get_text("blue"),
                'yellow': tr.get_text("yellow")
            }
            
            color_blindness_type = self.color_blindness_combo.currentData() or 'red_green'
            
            print("Calling color detector...")
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
                self.debug_mode_active,
                getattr(self, 'background_dimming_enabled', True)
            )
            
            print("Color analysis completed, showing result...")
            # Show result
            self.show_analysis_result(analysis_result, file_path)
            
        except Exception as e:
            print(f"Exception in analyze_loaded_image: {str(e)}")
            import traceback
            traceback.print_exc()
            self.status_bar.showMessage(f"Analysis error: {str(e)}")

    def show_analysis_result(self, analysis_result, file_path):
        """Show analysis result in camera area"""
        try:
            # Mark that we are showing file analysis result (not camera feed)
            self._file_loaded_view_active = True
            
            # Convert result to QImage
            h, w, c = analysis_result.shape
            bytes_per_line = 3 * w
            qImg = QImage(analysis_result.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            
            # Clear existing widgets thoroughly 
            for i in reversed(range(self.camera_feed_layout.count())): 
                child = self.camera_feed_layout.itemAt(i)
                if child:
                    widget = child.widget()
                    if widget:
                        # Remove any event filters
                        try:
                            widget.removeEventFilter(widget)
                        except:
                            pass
                        # Properly disconnect all signals
                        try:
                            widget.disconnect()
                        except:
                            pass
                        # Remove from layout and delete
                        self.camera_feed_layout.removeWidget(widget)
                        widget.setParent(None)
                        widget.deleteLater()
                    else:
                        # Handle layout items
                        self.camera_feed_layout.removeItem(child)
            
            # Process any pending deletions
            QApplication.processEvents()
            
            # Show file analysis completed title with file name
            file_name = os.path.basename(file_path)
            title_label = QLabel(f"📁 {tr.get_text('file_analysis_complete')}: {file_name}")
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
            
            # Show analyzed image keeping aspect ratio and adapting on resize
            image_label = QLabel()
            image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            image_label.setMinimumSize(1, 1)
            original_pix = QPixmap.fromImage(qImg)
            image_label.setPixmap(original_pix)
            image_label.setAlignment(Qt.AlignCenter)
            self.camera_feed_layout.addWidget(image_label)

            # Add a small action row with a "Save to Gallery" button below the image
            from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
            action_row = QWidget()
            row_layout = QHBoxLayout(action_row)
            row_layout.setContentsMargins(10, 0, 10, 10)
            row_layout.setSpacing(10)
            row_layout.addStretch()
            save_btn = QPushButton(tr.get_text("save_to_gallery") if hasattr(tr, 'get_text') else "Save to Gallery")
            save_btn.setObjectName("saveToGalleryButton")
            # Theme-aware styling using existing button theming if available
            try:
                from ..ui_components.buttons import update_button_theme
                theme = getattr(self, 'theme', 'dark')
                cb_type = None
                try:
                    if hasattr(self, 'color_blindness_combo') and self.color_blindness_combo is not None:
                        cb_type = self.color_blindness_combo.currentData()
                    if not cb_type and hasattr(self, 'current_profile') and self.current_profile is not None:
                        cb_type = getattr(self.current_profile, 'color_blindness_type', 'none')
                except Exception:
                    cb_type = 'none'
                cb_type = (cb_type or 'none')
                update_button_theme(save_btn, 'snapshot', theme, cb_type)
            except Exception:
                pass

            def _save_to_gallery():
                try:
                    # analysis_result is in BGR (OpenCV) in this flow; save as is
                    ok, path_or_err = self.camera_manager.save_image_to_gallery(analysis_result)
                    if ok:
                        self.status_bar.showMessage(tr.get_text("screenshot_saved", os.path.basename(path_or_err)))
                        # If gallery is open, refresh it briefly
                        try:
                            if hasattr(self, '_gallery_window') and self._gallery_window is not None:
                                self._gallery_window.refresh_gallery()
                        except Exception:
                            pass
                    else:
                        self.status_bar.showMessage(tr.get_text("screenshot_failed", path_or_err))
                except Exception as e:
                    self.status_bar.showMessage(tr.get_text("screenshot_failed", str(e)))

            save_btn.clicked.connect(_save_to_gallery)
            row_layout.addWidget(save_btn)
            row_layout.addStretch()
            self.camera_feed_layout.addWidget(action_row)

            # Install an event filter to rescale image smoothly on container/label resize
            class _ImageFitHelper(QObject):
                def __init__(self, container, title, label, pix):
                    super().__init__()
                    self.container = container
                    self.title = title
                    self.label = label
                    self.pix = pix

                def _target_size(self) -> QSize:
                    try:
                        # Account for layout margins: camera_feed_layout has 20px margins
                        margins_w = 40
                        margins_h = 40
                        title_h = self.title.height() if self.title and self.title.height() > 0 else 50
                        w = max(1, self.container.width() - margins_w)
                        h = max(1, self.container.height() - margins_h - title_h)
                        return QSize(w, h)
                    except Exception:
                        return QSize(800, 600)

                def _apply(self):
                    try:
                        target = self._target_size()
                        scaled = self.pix.scaled(target, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        # Avoid unnecessary churn
                        self.label.setPixmap(scaled)
                    except Exception:
                        pass

                def eventFilter(self, obj, event):
                    if event.type() == QEvent.Resize:
                        self._apply()
                    return False

            helper = _ImageFitHelper(self.camera_feed_container, title_label, image_label, original_pix)
            # Keep a reference to avoid GC
            image_label._fit_helper = helper  # type: ignore[attr-defined]
            self.camera_feed_container.installEventFilter(helper)
            image_label.installEventFilter(helper)
            # Apply initial fit after layout completes
            try:
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(0, helper._apply)
            except Exception:
                helper._apply()
            
            # Mark that file-loaded analyzed view is active and keep helper for window-level resize
            try:
                self._file_loaded_view_active = True
                self._loaded_fit_helper = helper
            except Exception:
                pass
            
            # Status message
            self.status_bar.showMessage(tr.get_text("file_analysis_complete"))
            
        except Exception as e:
            self.status_bar.showMessage(f"Display error: {str(e)}")

    def color_blindness_type_changed(self, index):
        """Automatic color selection when color blindness type changes"""
        # Use the index parameter directly instead of currentData() which may be unreliable
        print(f"[DEBUG] Color blindness type changed - signal index: {index}")
        
        # Get data directly from the model using the signal's index
        type_code = None
        if hasattr(self.color_blindness_combo, 'model'):
            item = self.color_blindness_combo.model.item(index)
            if item and item.isEnabled():
                type_code = item.data(Qt.UserRole)
                print(f"[DEBUG] Got type_code from signal index {index}: {type_code}")
            else:
                print(f"[DEBUG] Item at signal index {index} is disabled or doesn't exist")
                return
        else:
            # Fallback to currentData method
            type_code = self.color_blindness_combo.currentData()
            print(f"[DEBUG] Fallback - got type_code from currentData(): {type_code}")
        
        # Skip if this is a category header or no valid data
        if type_code is None or type_code == "category":
            print("[DEBUG] Skipping - no valid type_code or category header")
            return
        
        # Apply appropriate colors based on selected type
        if type_code == "none":
            # No color blindness - no automatic selection
            self._apply_detect_flags(False, False, False, False, persist=True)
        elif type_code == "protanopia":
            # Protanopia: focus on detecting Red and Green
            self._apply_detect_flags(True, True, False, False, persist=True)
        elif type_code == "deuteranopia":
            # Deuteranopia: focus on detecting Red and Green
            self._apply_detect_flags(True, True, False, False, persist=True)
        elif type_code == "tritanopia":
            # Tritanopia: focus on detecting Blue and Yellow
            self._apply_detect_flags(False, False, True, True, persist=True)
        elif type_code == "custom":
            # Custom color selection - Open advanced settings
            self.open_advanced_settings()
        
        # If Advanced Settings dialog is open, sync its checkboxes as well
        try:
            self._sync_advanced_settings_color_checkboxes()
        except Exception:
            pass
        
        # Update current profile immediately so child windows (e.g., gallery) can read the new value
        try:
            if hasattr(self, 'current_profile') and self.current_profile is not None:
                self.current_profile.color_blindness_type = type_code
        except Exception:
            pass

        # Update button colors for color blindness accessibility
        print(f"[DEBUG] Calling update_button_colors_for_accessibility with: {type_code}")
        self.update_button_colors_for_accessibility(type_code)

        # Update open gallery button themes if gallery is open
        try:
            if hasattr(self, '_gallery_window') and self._gallery_window is not None:
                if hasattr(self._gallery_window, 'refresh_button_themes'):
                    self._gallery_window.refresh_button_themes()
                # Also force a minor style/palette nudge to trigger repaint cascades
                try:
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(0, self._gallery_window.update)
                    QTimer.singleShot(10, self._gallery_window.repaint)
                except Exception:
                    pass
        except Exception:
            pass

        # Adjust or restore accent colors based on selection
        try:
            if hasattr(self, '_apply_accessible_accent_colors'):
                if type_code == 'tritanopia':
                    # Under tritanopia, convert any pink accents to Start-button blue; keep blues as blue
                    self._apply_accessible_accent_colors()
                else:
                    # Restore baseline theme accents (re-apply group boxes and child window themes)
                    if hasattr(self, '_force_refresh_group_boxes'):
                        self._force_refresh_group_boxes()
                        # Re-apply profile selector theme so its button styles aren't overridden
                        try:
                            if hasattr(self, 'profile_selector') and self.profile_selector is not None:
                                self.profile_selector.apply_theme()
                        except Exception:
                            pass
                    if hasattr(self, '_update_child_window_themes'):
                        self._update_child_window_themes()
        except Exception:
            pass
        
        # Auto-save profile when color blindness type changes
        self.auto_save_profile_on_change()

        # Ensure profile selector buttons keep their intended styles
        try:
            if hasattr(self, 'profile_selector') and self.profile_selector is not None:
                self.profile_selector.apply_theme()
        except Exception:
            pass

    def _sync_advanced_settings_color_checkboxes(self):
        """If Advanced Settings dialog is open, align its color checkboxes with main window."""
        try:
            from PyQt5.QtWidgets import QApplication
            from ..ui_components.dialogs import AdvancedSettingsDialog
            for window in QApplication.topLevelWidgets():
                if isinstance(window, AdvancedSettingsDialog):
                    if hasattr(window, 'red_checkbox') and window.red_checkbox is not None:
                        window.red_checkbox.setChecked(self.red_checkbox.isChecked())
                    if hasattr(window, 'green_checkbox') and window.green_checkbox is not None:
                        window.green_checkbox.setChecked(self.green_checkbox.isChecked())
                    if hasattr(window, 'blue_checkbox') and window.blue_checkbox is not None:
                        window.blue_checkbox.setChecked(self.blue_checkbox.isChecked())
                    if hasattr(window, 'yellow_checkbox') and window.yellow_checkbox is not None:
                        window.yellow_checkbox.setChecked(self.yellow_checkbox.isChecked())
                    try:
                        window.update()
                        window.repaint()
                    except Exception:
                        pass
        except Exception:
            pass

    def open_advanced_settings(self):
        """Open advanced settings dialog"""
        print("[DEBUG] Opening Advanced Settings dialog")
        try:
            self._advanced_settings_dialog = AdvancedSettingsDialog(self)
            print(f"[DEBUG] Created dialog reference: {self._advanced_settings_dialog}")
        except Exception as e:
            print(f"[DEBUG] Failed to create dialog: {e}")
            self._advanced_settings_dialog = None
        dialog = self._advanced_settings_dialog
        if dialog is not None:
            print("[DEBUG] Executing dialog...")
            dialog.exec_()
            print("[DEBUG] Dialog closed")
        # Clear reference after close to avoid stale pointer
        try:
            print("[DEBUG] Clearing dialog reference")
            self._advanced_settings_dialog = None
        except Exception:
            pass

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

            # Update all dropdown themes after language change
            self._update_dropdown_themes()

            # Auto-save profile
            self.auto_save_profile_on_change()

            # Update languages of any open child windows (gallery/dialogs)
            if hasattr(self, '_update_child_window_languages'):
                self._update_child_window_languages()

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
        
        # Update all dropdown themes
        self._update_dropdown_themes()
        
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

    def update_button_colors_for_accessibility(self, color_blindness_type):
        """Update button colors based on color blindness type for better accessibility"""
        print(f"[DEBUG] update_button_colors_for_accessibility called with: {color_blindness_type}")
        from ..ui_components.buttons import update_button_theme
        
        # Get current theme
        theme = getattr(self, 'theme', 'dark')
        print(f"[DEBUG] Current theme: {theme}")
        
        # Update all main buttons with accessibility colors
        if hasattr(self, 'camera_toggle_button'):
            if self.camera_manager.camera_open:
                print(f"[DEBUG] Updating camera_toggle_button to 'stop' style")
                update_button_theme(self.camera_toggle_button, 'stop', theme, color_blindness_type)
            else:
                print(f"[DEBUG] Updating camera_toggle_button to 'start' style")
                update_button_theme(self.camera_toggle_button, 'start', theme, color_blindness_type)
                
        if hasattr(self, 'screenshot_button'):
            print(f"[DEBUG] Updating screenshot_button")
            update_button_theme(self.screenshot_button, 'snapshot', theme, color_blindness_type)
            
        if hasattr(self, 'load_file_button'):
            print(f"[DEBUG] Updating load_file_button")
            update_button_theme(self.load_file_button, 'load_file', theme, color_blindness_type)
            
        if hasattr(self, 'gallery_button'):
            print(f"[DEBUG] Updating gallery_button")
            update_button_theme(self.gallery_button, 'gallery', theme, color_blindness_type)
            
        # Keep Advanced Settings button style constant (not color-blindness dependent)
        # so it matches the Reset Camera Permission button at all times
        if hasattr(self, 'advanced_settings_button'):
            update_button_theme(self.advanced_settings_button, 'default', theme, 'none')

        # Also update permission dialog buttons if the permission UI is visible
        try:
            if hasattr(self, '_update_camera_permission_interface_theme'):
                self._update_camera_permission_interface_theme()
        except Exception:
            pass

    def _update_dropdown_themes(self):
        """Update all dropdown themes when theme changes"""
        if hasattr(self, 'color_blindness_combo'):
            _apply_combo_theme(self.color_blindness_combo, self)
        
        if hasattr(self, 'language_combo'):
            _apply_combo_theme(self.language_combo, self)
        
        if hasattr(self, 'theme_combo'):
            _apply_combo_theme(self.theme_combo, self)
