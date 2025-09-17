"""
Camera handling functions for ColorVisionAid main window
Contains all camera-related operations and event handlers
"""

import os
from PyQt5.QtWidgets import QApplication, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from ..translations import translator as tr
from ..ui_components import create_camera_interface
from ..ui_components.buttons import update_button_theme
from .camera import show_camera_permission_interface

class CameraHandlers:
    """Mixin class for camera-related functionality"""
    
    def setup_camera_view(self):
        """Setup initial camera view"""
        # Show initial message
        create_camera_interface(self, self.camera_feed_layout)
    
    def reset_camera_permission(self):
        """Reset saved camera permissions"""
        self.camera_permission = "ask"
        self.settings.setValue("camera_permission", "ask")
        self.status_bar.showMessage(tr.get_text("permission_reset"))
        
        # Update permission status indicator
        self.permission_status_label.setText(f"{tr.get_text('current_permission_status')}: {tr.get_text('permission_status_ask')}")

    def camera_permission_granted(self):
        """Actions when camera permission is granted"""
        # Save permission preference
        if hasattr(self, 'remember_permission') and self.remember_permission.isChecked():
            self.camera_permission = "granted"
            self.settings.setValue("camera_permission", "granted")
            # Update permission status indicator
            self.permission_status_label.setText(f"{tr.get_text('current_permission_status')}: {tr.get_text('permission_status_granted')}")
            
        # Continue with camera startup process
        self.camera_startup_process()
    
    def camera_permission_denied(self):
        """Actions when camera permission is denied"""
        # Save permission preference
        if hasattr(self, 'remember_permission') and self.remember_permission.isChecked():
            self.camera_permission = "denied"
            self.settings.setValue("camera_permission", "denied")
            # Update permission status indicator
            self.permission_status_label.setText(f"{tr.get_text('current_permission_status')}: {tr.get_text('permission_status_denied')}")
        # Show status message
        self.status_bar.showMessage(tr.get_text("camera_permission_denied"))
        # Return to start message
        create_camera_interface(self, self.camera_feed_layout)
        # Clear analyzed file view state if any
        try:
            self._file_loaded_view_active = False
            self._loaded_fit_helper = None
        except Exception:
            pass

    def camera_startup_process(self):
        """Start camera after permission is granted with timeout protection"""
        print("=== Camera startup process initiated ===")
        
        # Stop timer if it's running to avoid conflicts
        if hasattr(self, 'timer') and self.timer.isActive():
            print("Stopping existing timer before camera startup...")
            self.timer.stop()
        
        # Clear the camera image label reference
        if hasattr(self, '_camera_image_label'):
            print("Clearing camera image label reference...")
            self._camera_image_label = None
        
        # Clear all widgets in camera feed layout with more thorough cleanup
        print("Clearing camera feed layout...")
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
                    
        # Clear analyzed file view state if any
        try:
            self._file_loaded_view_active = False
            self._loaded_fit_helper = None
        except Exception:
            pass
        
        # Process any pending deletions
        QApplication.processEvents()
        print("Layout cleared successfully")
            
        # Show startup message
        starting_label = QLabel(tr.get_text("camera_initializing"))
        # Theme-aware styling for startup message
        theme = getattr(self, 'theme', 'dark').lower()
        if theme == 'light':
            starting_label.setStyleSheet("color: #222; font-size: 12pt;")
        else:
            starting_label.setStyleSheet("color: white; font-size: 12pt;")
        starting_label.setAlignment(Qt.AlignCenter)
        self.camera_feed_layout.addWidget(starting_label)
        QApplication.processEvents()  # Update UI immediately
        
        # Try to start camera with timeout protection
        print("Attempting to start camera...")
        try:
            camera_started = self.camera_manager.camera_start()
            
            if camera_started:
                print("Camera started successfully, initializing timer...")
                
                # Ensure timer is stopped before starting
                if hasattr(self, 'timer'):
                    self.timer.stop()
                    
                # Start timer for frame updates
                self.timer.start(33)  # ~30 FPS
                print(f"Timer started successfully. Active: {self.timer.isActive()}")
                
                self.status_bar.showMessage(tr.get_text("camera_started"))
                
                # Expand camera feed container size when camera starts
                self.camera_feed_container.setMinimumHeight(400)  # Increase height for active camera
                
                # Update camera name in selector with real-time resolution info
                if hasattr(self, 'camera_selector') and self.camera_selector:
                    self.camera_selector.update_current_camera_name()
                
                # Update "Stop" button appearance
                self.camera_toggle_button.setText(tr.get_text("stop"))
                self.camera_toggle_button.setToolTip(tr.get_text("stop_tooltip"))
                # Apply CB-aware theme for Stop button on first start
                try:
                    theme = getattr(self, 'theme', 'dark')
                    cb_type = None
                    if hasattr(self, 'color_blindness_combo') and self.color_blindness_combo is not None:
                        cb_type = self.color_blindness_combo.currentData()
                    if not cb_type and hasattr(self, 'current_profile') and self.current_profile is not None:
                        cb_type = getattr(self.current_profile, 'color_blindness_type', 'none')
                    cb_type = (cb_type or 'none')
                    update_button_theme(self.camera_toggle_button, 'stop', theme, cb_type)
                except Exception:
                    pass
                # Show screenshot button
                self.screenshot_button.setVisible(True)
            else:
                print("Failed to start camera")
                self.status_bar.showMessage(tr.get_text("camera_start_failed"))
                create_camera_interface(self, self.camera_feed_layout)  # Show start message if camera can't start
                
        except Exception as e:
            print(f"Error during camera startup: {e}")
            self.status_bar.showMessage(tr.get_text("camera_start_failed"))
            create_camera_interface(self, self.camera_feed_layout)  # Show start message on error

    def stop_camera(self):
        """Stop camera"""
        print("=== Camera stop process initiated ===")
        print(f"Camera manager state: {self.camera_manager.camera_open}")
        print(f"Timer active: {self.timer.isActive()}")
        
        if self.camera_manager.camera_stop():
            print("Camera manager stopped successfully")
            
            # Stop timer with verification
            if hasattr(self, 'timer'):
                print("Stopping timer...")
                self.timer.stop()
                print(f"Timer active after stop: {self.timer.isActive()}")
            
            # Clear the camera image label reference to prevent deleted widget errors
            if hasattr(self, '_camera_image_label'):
                print("Clearing camera image label reference...")
                self._camera_image_label = None
            
            # Reduce camera feed container size when camera stops
            self.camera_feed_container.setMinimumHeight(200)  # Back to minimum height for start message
            
            # Clear all widgets thoroughly before showing start message
            print("Clearing widgets from layout...")
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
            print("Widgets cleared successfully")
            
            # Return to start message
            create_camera_interface(self, self.camera_feed_layout)
            print("Camera interface created")
            
            # Clear analyzed file view state if any
            try:
                self._file_loaded_view_active = False
                self._loaded_fit_helper = None
            except Exception:
                pass
            
            self.status_bar.showMessage(tr.get_text("camera_stopped"))
            
            # Update "Start" button appearance
            self.camera_toggle_button.setText(tr.get_text("start"))
            self.camera_toggle_button.setToolTip(tr.get_text("start_tooltip"))
            # Apply CB-aware theme for Start button after stopping
            try:
                theme = getattr(self, 'theme', 'dark')
                cb_type = None
                if hasattr(self, 'color_blindness_combo') and self.color_blindness_combo is not None:
                    cb_type = self.color_blindness_combo.currentData()
                if not cb_type and hasattr(self, 'current_profile') and self.current_profile is not None:
                    cb_type = getattr(self.current_profile, 'color_blindness_type', 'none')
                cb_type = (cb_type or 'none')
                update_button_theme(self.camera_toggle_button, 'start', theme, cb_type)
            except Exception:
                pass
            
            # Hide screenshot button
            self.screenshot_button.setVisible(False)
            print("=== Camera stop process completed ===")
        else:
            print("Warning: Camera manager failed to stop")

    def toggle_camera(self):
        """Turn camera on and off"""
        if self.camera_manager.camera_open:
            self.stop_camera()
        else:
            self.start_camera()
            
    def start_camera(self):
        """Start camera after checking permissions"""
        if not self.camera_manager.camera_open:
            # Check saved permission preference
            if self.camera_permission == "granted":
                # Permission already granted, start camera directly
                self.camera_startup_process()
            elif self.camera_permission == "denied":
                # Permission was denied previously; show permission prompt again
                show_camera_permission_interface(
                    self,
                    self.camera_feed_layout,
                    self.camera_permission_granted,
                    self.camera_permission_denied
                )
            else:
                # Ask for permission
                show_camera_permission_interface(
                    self, 
                    self.camera_feed_layout,
                    self.camera_permission_granted,
                    self.camera_permission_denied
                )

    def update_frame(self):
        """Update camera frame and process color detection with error handling"""
        try:
            # Debug: Check if timer is being called
            if not hasattr(self, '_frame_update_debug_counter'):
                self._frame_update_debug_counter = 0
            
            self._frame_update_debug_counter += 1
            if self._frame_update_debug_counter % 30 == 1:  # Print every 30 frames (~ once per second)
                print(f"update_frame called #{self._frame_update_debug_counter}")
                
            success, frame = self.camera_manager.get_frame()
            if not success or frame is None:
                if self._frame_update_debug_counter % 30 == 1:
                    print("No frame available from camera")
                return
            
            # Validate frame before processing
            if len(frame.shape) != 3 or frame.shape[2] != 3:
                print("Invalid frame format detected")
                return
                
            height, width = frame.shape[:2]
            if width <= 0 or height <= 0:
                print("Invalid frame dimensions detected")
                return
            
            # Check for reasonable frame size to prevent memory issues
            max_pixels = 1920 * 1080  # Max 1080p
            current_pixels = width * height
            
            if current_pixels > max_pixels:
                print(f"Frame too large ({width}x{height}), this should have been handled by get_frame()")
                return

            # Get detection settings from current state
            if not hasattr(self, 'current_detection_settings'):
                # Initialize default detection settings if not set
                self.current_detection_settings = {
                    'red': True,
                    'green': True,
                    'blue': False,
                    'yellow': False
                }
            
            selected_colors = self.current_detection_settings.copy()
            selected_colors['skin'] = True  # Skin tone works in background (invisible)

            # If all manual selections are off, auto-select based on CB type to keep detection working
            if not (selected_colors['red'] or selected_colors['green'] or selected_colors['blue'] or selected_colors['yellow']):
                try:
                    cb_type_auto = self.color_blindness_combo.currentData() or 'none'
                except Exception:
                    cb_type_auto = 'none'
                if cb_type_auto in ('protanopia', 'deuteranopia'):
                    selected_colors['red'] = True
                    selected_colors['green'] = True
                    # Update UI checkboxes once to reflect the auto-selection
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
            
            # Translated color names (skin tone not included - invisible)
            translated_color_names = {
                'red': tr.get_text("red"),
                'green': tr.get_text("green"),
                'blue': tr.get_text("blue"),
                'yellow': tr.get_text("yellow")
            }
            
            # Get color blindness type
            color_blindness_type = self.color_blindness_combo.currentData() or 'red_green'
            
            # Process frame with color detector (with error handling)
            try:
                combined_result = self.color_detector.process_frame(
                    frame, 
                    selected_colors,
                    self.sensitivity_slider.value(),
                    self.contrast_value,  # Use fixed contrast value
                    translated_color_names,
                    self.skin_tone_filtering_active,
                    self.stability_enhancement_active,
                    color_blindness_type,  # Send color blindness type
                    False,  # mobile_optimization
                    self.debug_mode_active,  # Debug mode
                    getattr(self, 'background_dimming_enabled', True)
                )
            except Exception as e:
                print(f"Error processing frame: {e}")
                # Fall back to original frame if processing fails
                combined_result = frame
                
            # Persist processed frame with overlays for screenshot feature
            try:
                if hasattr(self, 'camera_manager') and self.camera_manager is not None:
                    self.camera_manager.current_frame_processed = combined_result.copy()
            except Exception:
                pass
            
            # Convert result to QImage once (with error handling)
            try:
                h, w, c = combined_result.shape
                if c != 3:
                    print("Invalid processed frame format")
                    return
                    
                bytes_per_line = 3 * w
                qImg = QImage(combined_result.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
                
                if qImg.isNull():
                    print("Failed to create QImage from frame data")
                    return
            except Exception as e:
                print(f"Error converting frame to QImage: {e}")
                return

            # Ensure a persistent image label exists (avoid recreating per frame)
            if not hasattr(self, '_camera_image_label') or self._camera_image_label is None:
                try:
                    # Clear permission/start widgets once when first frame arrives
                    for i in reversed(range(self.camera_feed_layout.count())):
                        item = self.camera_feed_layout.itemAt(i)
                        widget = item.widget() if item else None
                        if widget is not None:
                            widget.setParent(None)
                    self._camera_image_label = QLabel()
                    self._camera_image_label.setAlignment(Qt.AlignCenter)
                    # Allow window/container to resize freely
                    self._camera_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    self._camera_image_label.setMinimumSize(1, 1)
                    self.camera_feed_layout.addWidget(self._camera_image_label)
                except Exception as e:
                    print(f"Error setting up camera image label: {e}")
                    return

            # Double-check that the widget still exists and is valid
            try:
                # Try to access a method to verify widget is still valid
                self._camera_image_label.isVisible()
            except (AttributeError, RuntimeError) as e:
                print(f"Camera image label is invalid, recreating: {e}")
                # Widget was deleted, clear reference and let it be recreated
                self._camera_image_label = None
                return

            # Scale pixmap to current container size (accounting for margins)
            try:
                target_w = max(1, self.camera_feed_container.width() - 40)
                target_h = max(1, self.camera_feed_container.height() - 40)
                scaled = QPixmap.fromImage(qImg).scaled(
                    target_w,
                    target_h,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self._camera_image_label.setPixmap(scaled)
            except Exception as e:
                print(f"Error scaling and displaying frame: {e}")
                # Clear the invalid widget reference
                self._camera_image_label = None
                
        except Exception as e:
            print(f"Critical error in update_frame: {e}")
            # Stop camera to prevent further errors
            try:
                self.stop_camera()
            except:
                pass
