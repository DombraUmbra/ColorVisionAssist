import os
import cv2
import glob
import numpy as np
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton, QCheckBox, QHBoxLayout
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap

# Import package's own modules
from ..translations import translator as tr

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
        Take and save a screenshot
        
        Returns:
            (successful, filename or error message)
        """
        if not hasattr(self, 'current_frame') or self.current_frame is None:
            return False, "No frame available"
        
        # Ensure screenshots directory exists - use repository root (parent of 'source' folder)
        # __file__ is .../source/main_window/camera.py -> go up 3 levels to reach repo root
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        screenshot_dir = os.path.join(root_dir, "screenshots")
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        
        # Find all PNG files in the screenshots directory that start with "screenshot_"
        screenshot_files = glob.glob(os.path.join(screenshot_dir, "screenshot_*.png"))
        next_number = 1
        if screenshot_files:
            # Extract numbers from existing files and find the maximum
            current_numbers = []
            for file_name in screenshot_files:
                try:
                    base_file_name = os.path.basename(file_name)
                    number = int(base_file_name.replace("screenshot_", "").replace(".png", ""))
                    current_numbers.append(number)
                except ValueError:
                    pass
            if current_numbers:
                next_number = max(current_numbers) + 1
                
        file_name = os.path.join(screenshot_dir, f"screenshot_{next_number}.png")
        cv2.imwrite(file_name, self.current_frame)
        return True, file_name

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
    if grant_callback:
        grant_button.clicked.connect(grant_callback)
    
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
