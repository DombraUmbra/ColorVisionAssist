import os
import cv2
import glob
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton, QCheckBox, QHBoxLayout
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap

# Import package's own modules
from ..translations import translator as tr
from ..ui_components.buttons import update_button_theme

class CameraManager:
    def __init__(self, parent=None):
        """
        Class for camera management
        
        Args:
            parent: Main application window reference
        """
        self.parent = parent
        self.camera_open = False
        self.camera = None
        self.current_frame = None
        # Last processed frame including overlays (labels/frames); used for screenshots
        self.current_frame_processed = None
    
    def is_camera_active(self):
        """Check if camera is active"""
        return self.camera_open
    
    def camera_start(self):
        """Start camera"""
        if self.camera_open:
            return
            
        self.camera = cv2.VideoCapture(0)
        if self.camera.isOpened():
            self.camera_open = True
            return True
        else:
            return False
    
    def camera_stop(self):
        """Stop camera"""
        if self.camera_open:
            self.camera.release()
            self.camera_open = False
            self.current_frame = None
            self.current_frame_processed = None
            return True
        return False
    
    def get_frame(self):
        """
        Get a frame from camera
        
        Returns:
            (success status, frame)
        """
        if not self.camera_open:
            return False, None
            
        success, frame = self.camera.read()
        if success:
            self.current_frame = frame.copy()
        return success, frame
    
    def take_screenshot(self):
        """
        Take and save a screenshot with date format (dd/mm/yyyy)
        
        Returns:
            (successful, filename or error message)
        """
        # Prefer processed frame (with overlays). Fallback to raw frame.
        frame_to_save = None
        if hasattr(self, 'current_frame_processed') and self.current_frame_processed is not None:
            frame_to_save = self.current_frame_processed
        elif hasattr(self, 'current_frame') and self.current_frame is not None:
            frame_to_save = self.current_frame
        if frame_to_save is None:
            return False, "No frame available"

        # Ensure screenshots directory exists - use repository root (parent of 'source' folder)
        # __file__ is .../source/main_window/camera.py -> go up 3 levels to reach repo root
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        screenshot_dir = os.path.join(root_dir, "screenshots")
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

        # Migrate old screenshot files to new format if needed
        self._migrate_old_screenshots(screenshot_dir)

        # Generate filename with current date and time; include milliseconds to ensure uniqueness
        now = datetime.now()
        date_str = now.strftime("%d-%m-%Y")
        time_str = now.strftime("%H-%M-%S")
        ms = int(now.microsecond / 1000)
        # New format: screenshot_dd-mm-yyyy_hh-mm-ss-SSS.png
        file_name = os.path.join(screenshot_dir, f"screenshot_{date_str}_{time_str}-{ms:03d}.png")

        # Avoid rare collisions by bumping milliseconds if file exists
        try:
            bump = 0
            while os.path.exists(file_name) and bump < 1000:
                bump += 1
                file_name = os.path.join(screenshot_dir, f"screenshot_{date_str}_{time_str}-{(ms + bump) % 1000:03d}.png")
        except Exception:
            pass

        try:
            cv2.imwrite(file_name, frame_to_save)
        except Exception as e:
            return False, str(e)
        return True, file_name

    def save_image_to_gallery(self, image):
        """Save a provided BGR image to the screenshots folder using the app's naming scheme.

        Args:
            image: numpy ndarray (BGR) to save.

        Returns:
            (successful: bool, path_or_error: str)
        """
        if image is None:
            return False, "No image provided"

        # Ensure screenshots directory exists - use repository root (parent of 'source' folder)
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        screenshot_dir = os.path.join(root_dir, "screenshots")
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

        # Migrate old screenshots if needed
        self._migrate_old_screenshots(screenshot_dir)

        # Generate filename with current date and time; include milliseconds to ensure uniqueness
        now = datetime.now()
        date_str = now.strftime("%d-%m-%Y")
        time_str = now.strftime("%H-%M-%S")
        ms = int(now.microsecond / 1000)
        file_name = os.path.join(screenshot_dir, f"screenshot_{date_str}_{time_str}-{ms:03d}.png")

        # Avoid rare collisions by bumping milliseconds if file exists
        try:
            bump = 0
            while os.path.exists(file_name) and bump < 1000:
                bump += 1
                file_name = os.path.join(screenshot_dir, f"screenshot_{date_str}_{time_str}-{(ms + bump) % 1000:03d}.png")
        except Exception:
            pass

        try:
            cv2.imwrite(file_name, image)
        except Exception as e:
            return False, str(e)
        return True, file_name
    
    def _migrate_old_screenshots(self, screenshot_dir):
        """
        Migrate old screenshot files (screenshot_1.png, screenshot_2.png, etc.) 
        to new date format using file modification time
        """
        # Find old format files (screenshot_number.png)
        old_files = []
        for file_path in glob.glob(os.path.join(screenshot_dir, "screenshot_*.png")):
            file_name = os.path.basename(file_path)
            # Check if it's old format (just screenshot_number.png)
            if file_name.startswith("screenshot_") and file_name.endswith(".png"):
                name_part = file_name[11:-4]  # Remove "screenshot_" and ".png"
                try:
                    # If it's just a number, it's old format
                    int(name_part)
                    old_files.append(file_path)
                except ValueError:
                    # If conversion fails, it's already new format or different format
                    continue

        # Migrate old files
        for old_file in old_files:
            try:
                # Get file modification time
                mod_time = os.path.getmtime(old_file)
                file_date = datetime.fromtimestamp(mod_time)

                # Create new filename with file's modification date (no numbering, include ms)
                date_str = file_date.strftime("%d-%m-%Y")
                time_str = file_date.strftime("%H-%M-%S")
                ms = int(file_date.microsecond / 1000)
                new_filename = f"screenshot_{date_str}_{time_str}-{ms:03d}.png"
                new_path = os.path.join(screenshot_dir, new_filename)

                # Avoid collision: bump ms if file already exists
                bump = 0
                while os.path.exists(new_path) and bump < 1000:
                    bump += 1
                    new_filename = f"screenshot_{date_str}_{time_str}-{(ms + bump) % 1000:03d}.png"
                    new_path = os.path.join(screenshot_dir, new_filename)

                # Rename the file
                os.rename(old_file, new_path)
                print(f"Migrated {os.path.basename(old_file)} to {new_filename}")

            except Exception as e:
                print(f"Failed to migrate {old_file}: {e}")
                # Continue with other files if one fails

# Camera interface components - moved to ui_components/styles.py

def show_camera_permission_interface(parent, camera_feed_layout, grant_callback=None, deny_callback=None):
    """
    Show camera permission interface
    
    Args:
        parent: Main application window
        camera_feed_layout: Layout where camera feed will be added
        grant_callback: Function to call when permission is granted
        deny_callback: Function to call when permission is denied
    """
    # Clear any existing widgets in camera feed
    for i in reversed(range(camera_feed_layout.count())): 
        camera_feed_layout.itemAt(i).widget().setParent(None)
    
    # Create permission layout
    permission_layout = QVBoxLayout()
    
    # Add camera icon - update icon path with responsive sizing
    camera_icon_label = QLabel()
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'camera_icon.png')
    camera_icon = QPixmap(icon_path)
    
    # Calculate responsive sizes based on window size
    window_width = parent.width() if hasattr(parent, 'width') else 1000
    window_height = parent.height() if hasattr(parent, 'height') else 600
    
    # Calculate responsive icon size (minimum 35pt, maximum 80pt)
    responsive_icon_size = max(35, min(80, int(window_width * 0.06)))
    
    if camera_icon.isNull():
        # If icon file doesn't exist, create a text placeholder with theme-aware styling
        try:
            camera_icon_label.setText("🎥")  # Video camera icon - widely supported
        except:
            try:
                camera_icon_label.setText("📷")  # Fallback to photo camera
            except:
                camera_icon_label.setText("📹")  # Alternative camera symbol
            
        # Additional fallback in case of encoding issues
        if not camera_icon_label.text() or len(camera_icon_label.text()) == 0:
            camera_icon_label.setText("●REC")  # Simple text fallback
        
        theme = getattr(parent, 'theme', 'dark').lower()
        if theme == 'light':
            camera_icon_label.setStyleSheet(f"""
                font-size: {responsive_icon_size}pt; 
                color: #333; 
                background-color: transparent; 
                border: none; 
                font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji';
            """)
        else:
            camera_icon_label.setStyleSheet(f"""
                font-size: {responsive_icon_size}pt; 
                color: #BBB; 
                background-color: transparent; 
                border: none; 
                font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji';
            """)
    else:
        # Scale icon to appropriate size based on window size
        icon_size = max(48, min(96, int(window_width * 0.08)))
        camera_icon = camera_icon.scaled(QSize(icon_size, icon_size), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        camera_icon_label.setPixmap(camera_icon)
    
    camera_icon_label.setAlignment(Qt.AlignCenter)  # Fixed: use Qt.AlignCenter
    permission_layout.addWidget(camera_icon_label)
    
    # Add permission text with responsive sizing
    permission_text = QLabel(tr.get_text("camera_permission_text"))
    
    # Calculate responsive text size (minimum 10pt, maximum 16pt)
    responsive_text_size = max(10, min(16, int(window_width * 0.014)))
    responsive_margin = max(10, min(25, int(window_width * 0.02)))
    
    # Theme-aware styling for permission text with responsive sizing
    theme = getattr(parent, 'theme', 'dark').lower()
    if theme == 'light':
        permission_text.setStyleSheet(f"color: #222; font-size: {responsive_text_size}pt; margin: {responsive_margin}px;")
    else:
        permission_text.setStyleSheet(f"color: white; font-size: {responsive_text_size}pt; margin: {responsive_margin}px;")
    permission_text.setWordWrap(True)
    permission_text.setAlignment(Qt.AlignCenter)  # Fixed: use Qt.AlignCenter
    permission_layout.addWidget(permission_text)
    
    # Add buttons for permission
    button_widget = QWidget()
    button_layout = QHBoxLayout(button_widget)
    
    # Grant permission button (color-blind aware)
    grant_button = QPushButton(tr.get_text("grant_permission"))
    grant_button.setToolTip(tr.get_text("grant_permission_tooltip"))
    grant_button.setObjectName("permission_grant_button")
    # Determine theme and color blindness type
    current_theme = getattr(parent, 'theme', 'dark')
    try:
        cb_type = None
        if hasattr(parent, 'color_blindness_combo') and parent.color_blindness_combo is not None:
            cb_type = parent.color_blindness_combo.currentData()
        if not cb_type and hasattr(parent, 'current_profile') and parent.current_profile is not None:
            cb_type = getattr(parent.current_profile, 'color_blindness_type', 'none')
        cb_type = (cb_type or 'none')
    except Exception:
        cb_type = 'none'
    update_button_theme(grant_button, 'start', current_theme, cb_type)
    if grant_callback:
        grant_button.clicked.connect(grant_callback)
    
    # Deny permission button (color-blind aware)
    deny_button = QPushButton(tr.get_text("deny_permission"))
    deny_button.setToolTip(tr.get_text("deny_permission_tooltip"))
    deny_button.setObjectName("permission_deny_button")
    update_button_theme(deny_button, 'stop', current_theme, cb_type)
    if deny_callback:
        deny_button.clicked.connect(deny_callback)
    
    # Add checkbox to remember decision with theme-aware hover effect
    remember_checkbox = QCheckBox(tr.get_text("remember_decision"))
    remember_checkbox.setToolTip(tr.get_text("remember_decision_tooltip"))
    theme = getattr(parent, 'theme', 'dark').lower()
    if theme == 'light':
        remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #222;
            }
            QCheckBox:hover {
                color: #1976D2;
            }
        """)
    else:
        remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
            }
            QCheckBox:hover {
                color: #2196F3;
            }
        """)
    remember_checkbox.setChecked(True)
    parent.remember_permission = remember_checkbox  # Store reference to main window
    
    button_layout.addWidget(deny_button)
    button_layout.addWidget(grant_button)
    
    permission_layout.addWidget(button_widget)
    permission_layout.addWidget(remember_checkbox)
    
    # Create a container widget for the permission layout
    permission_widget = QWidget()
    permission_widget.setLayout(permission_layout)
    
    # Add the permission widget to the camera feed layout
    camera_feed_layout.addWidget(permission_widget)
