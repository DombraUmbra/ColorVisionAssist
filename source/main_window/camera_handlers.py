"""
Camera handling functions for ColorVisionAid main window
Contains all camera-related operations and event handlers
"""

import os
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from ..translations import translator as tr
from ..ui_components import create_camera_interface
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

    def camera_startup_process(self):
        """Start camera after permission is granted"""
        # Clear all widgets in camera feed layout
        for i in reversed(range(self.camera_feed_layout.count())): 
            self.camera_feed_layout.itemAt(i).widget().setParent(None)
            
        # Show startup message
        starting_label = QLabel(tr.get_text("camera_initializing"))
        starting_label.setStyleSheet("color: white; font-size: 12pt;")
        starting_label.setAlignment(Qt.AlignCenter)
        self.camera_feed_layout.addWidget(starting_label)
        QApplication.processEvents()  # Update UI immediately
        
        # Now try to start camera
        if self.camera_manager.camera_start():
            self.timer.start(33)  # ~30 FPS
            self.status_bar.showMessage(tr.get_text("camera_started"))
            
            # Update "Stop" button appearance
            self.camera_toggle_button.setText(tr.get_text("stop"))
            self.camera_toggle_button.setToolTip(tr.get_text("stop_tooltip"))
            self.camera_toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    padding: 8px 6px;
                    border-radius: 5px;
                    font-size: 9pt;
                    min-height: 25px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #EF5350;
                    border: 2px solid #E57373;
                }
                QPushButton:pressed {
                    background-color: #E53935;
                }
            """)
            # Show screenshot button
            self.screenshot_button.setVisible(True)
        else:
            self.status_bar.showMessage(tr.get_text("camera_start_failed"))
            create_camera_interface(self, self.camera_feed_layout)  # Show start message if camera can't start

    def stop_camera(self):
        """Stop camera"""
        if self.camera_manager.camera_stop():
            self.timer.stop()
            # Return to start message
            create_camera_interface(self, self.camera_feed_layout)
            
            self.status_bar.showMessage(tr.get_text("camera_stopped"))
            
            # Update "Start" button appearance
            self.camera_toggle_button.setText(tr.get_text("start"))
            self.camera_toggle_button.setToolTip(tr.get_text("start_tooltip"))
            self.camera_toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 8px 6px;
                    border-radius: 5px;
                    font-size: 9pt;
                    min-height: 25px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #66BB6A;
                    border: 2px solid #81C784;
                }
                QPushButton:pressed {
                    background-color: #43A047;
                }
            """)
            
            # Hide screenshot button
            self.screenshot_button.setVisible(False)

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
                # Permission already denied
                self.status_bar.showMessage(tr.get_text("camera_permission_denied"))
            else:
                # Ask for permission
                show_camera_permission_interface(
                    self, 
                    self.camera_feed_layout,
                    self.camera_permission_granted,
                    self.camera_permission_denied
                )

    def update_frame(self):
        """Update camera frame and process color detection"""
        success, frame = self.camera_manager.get_frame()
        if success:
            selected_colors = {
                'skin': True,  # Skin tone works in background (invisible)
                'red': self.red_checkbox.isChecked(),
                'green': self.green_checkbox.isChecked(),
                'blue': self.blue_checkbox.isChecked(),
                'yellow': self.yellow_checkbox.isChecked()
            }
            
            # Translated color names (skin tone not included - invisible)
            translated_color_names = {
                'red': tr.get_text("red"),
                'green': tr.get_text("green"),
                'blue': tr.get_text("blue"),
                'yellow': tr.get_text("yellow")
            }
            
            # Get color blindness type
            color_blindness_type = self.color_blindness_combo.currentData() or 'red_green'
            
            # Process frame with color detector
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
                self.debug_mode_active  # Debug mode
            )
            
            # Convert result to QImage and display
            h, w, c = combined_result.shape
            bytes_per_line = 3 * w
            qImg = QImage(combined_result.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            
            # Clear all existing widgets
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
