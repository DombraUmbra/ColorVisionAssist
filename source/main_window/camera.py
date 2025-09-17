import os
import cv2
import glob
import time
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton, QCheckBox, QHBoxLayout
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap

# Import package's own modules
from ..translations import translator as tr
from ..ui_components.buttons import update_button_theme

def get_camera_names_windows():
    """
    Get camera device names on Windows using various methods
    Returns a dictionary mapping device indices to friendly names
    """
    camera_names = {}
    
    # Method 1: Try WMI if available
    try:
        import wmi
        c = wmi.WMI()
        
        # Query video input devices
        video_devices = c.Win32_PnPEntity(ConfigManagerErrorCode=0, PNPClass="Camera")
        image_devices = c.Win32_PnPEntity(ConfigManagerErrorCode=0, PNPClass="Image")
        
        all_devices = list(video_devices) + list(image_devices)
        
        device_index = 0
        for device in all_devices:
            if device.Name and any(keyword in device.Name.lower() for keyword in 
                                 ["camera", "webcam", "usb", "integrated", "virtual", "broadcast"]):
                camera_names[device_index] = device.Name
                device_index += 1
        
        if camera_names:
            return camera_names
            
    except (ImportError, Exception):
        pass
    
    # Method 2: Try Windows registry
    try:
        import winreg
        reg_path = r"SYSTEM\CurrentControlSet\Control\DeviceClasses\{65e8773d-8f56-11d0-a3b9-00a0c9223196}"
        
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
        device_index = 0
        
        for i in range(50):  # Limit iterations
            try:
                subkey_name = winreg.EnumKey(reg_key, i)
                if any(keyword in subkey_name.lower() for keyword in ["capture", "camera", "video"]):
                    # Extract and clean device name
                    if "#" in subkey_name:
                        parts = subkey_name.split("#")
                        if len(parts) >= 2:
                            device_name = parts[1].replace("&", " ").replace("_", " ").title()
                            # Improve naming based on patterns
                            if "vid" in device_name.lower() and "pid" in device_name.lower():
                                device_name = f"USB Camera {device_index}"
                            elif "root" in device_name.lower():
                                device_name = f"Integrated Camera"
                            elif len(device_name.strip()) < 3:
                                device_name = f"Camera {device_index}"
                            
                            camera_names[device_index] = device_name
                            device_index += 1
            except OSError:
                break
        
        winreg.CloseKey(reg_key)
        
        if camera_names:
            return camera_names
            
    except (ImportError, FileNotFoundError, Exception):
        pass
    
    # Method 3: Try PowerShell command as last resort
    try:
        import subprocess
        result = subprocess.run([
            "powershell", 
            "Get-PnpDevice -Class Camera | Select-Object -ExpandProperty FriendlyName"
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if line and line != "FriendlyName":
                    camera_names[i] = line
                    
        if camera_names:
            return camera_names
            
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    
    return camera_names

def get_camera_names_generic():
    """
    Fallback method to get camera names using registry on Windows
    """
    try:
        import winreg
        camera_names = {}
        
        # Try to read from Windows registry
        reg_path = r"SYSTEM\CurrentControlSet\Control\DeviceClasses\{65e8773d-8f56-11d0-a3b9-00a0c9223196}"
        
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            device_index = 0
            
            for i in range(100):  # Limit iterations
                try:
                    subkey_name = winreg.EnumKey(reg_key, i)
                    if "capture" in subkey_name.lower() or "camera" in subkey_name.lower():
                        # Extract device name from the key
                        if "#" in subkey_name:
                            parts = subkey_name.split("#")
                            if len(parts) >= 2:
                                device_name = parts[1].replace("&", " ").replace("#", "")
                                # Clean up the name
                                if "vid_" in device_name.lower():
                                    device_name = f"USB Camera {device_index}"
                                elif "root" in device_name.lower():
                                    device_name = f"Integrated Camera {device_index}"
                                else:
                                    device_name = f"Camera {device_index}"
                                
                                camera_names[device_index] = device_name
                                device_index += 1
                except OSError:
                    break
            
            winreg.CloseKey(reg_key)
        except FileNotFoundError:
            pass
        
        return camera_names
    except ImportError:
        return {}
    except Exception:
        return {}

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
        # Currently selected camera index
        self.selected_camera_index = 0
        # List of available cameras
        self.available_cameras = []
        # Detect available cameras on initialization
        self.detect_available_cameras()
    
    def detect_available_cameras(self):
        """
        Detect all available cameras in the system including virtual cameras
        
        Returns:
            list: List of tuples containing (index, name) of available cameras
        """
        self.available_cameras = []
        
        # Get real camera names from Windows
        camera_names_dict = get_camera_names_windows()
        
        # Test camera indices from 0 to 10 (covers most systems)
        for i in range(11):
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    # Try to read a frame to verify the camera is working
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        # Get camera name from our detection methods
                        camera_name = camera_names_dict.get(i, f"Camera {i}")
                        
                        # If we got a generic name, try to improve it with technical details
                        if camera_name == f"Camera {i}":
                            try:
                                # Get camera properties for better identification
                                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                                fps = int(cap.get(cv2.CAP_PROP_FPS))
                                
                                # Try to detect camera type based on properties
                                if width >= 1920 or height >= 1080:
                                    camera_name = f"HD Camera {i}"
                                elif width >= 1280 or height >= 720:
                                    camera_name = f"Camera {i} (720p)"
                                else:
                                    camera_name = f"Camera {i} ({width}x{height})"
                                
                                if fps > 0:
                                    camera_name += f" @{fps}fps"
                                    
                                # Add stability warning for very high resolution cameras
                                if width > 1920 or height > 1080:
                                    camera_name += " [Auto-Scaled]"
                                    
                            except:
                                camera_name = f"Camera {i}"
                        # Don't add resolution info here since it may change after camera starts
                        # Resolution info will be added dynamically when needed
                        
                        self.available_cameras.append((i, camera_name))
                cap.release()
            except Exception:
                # Skip cameras that can't be opened
                continue
        
        # If no cameras found, add default camera as fallback
        if not self.available_cameras:
            self.available_cameras.append((0, tr.get_text("default_camera")))
        
        return self.available_cameras
    
    def set_camera_index(self, camera_index):
        """
        Set the camera index to use - always stops current camera for safety
        
        Args:
            camera_index (int): Index of the camera to use
        """
        if camera_index == self.selected_camera_index:
            return True  # No change needed
            
        print(f"Camera change requested from {self.selected_camera_index} to {camera_index}")
        
        # Always stop the camera first for safety and consistency
        if self.camera_open:
            print("Stopping current camera due to camera change...")
            self.camera_stop()
            
            # Give extra time for camera resources to be fully released after camera change
            print("Waiting for camera resources to be released...")
            time.sleep(0.5)  # Increased wait time for camera switching
        
        # Update the selected camera index
        self.selected_camera_index = camera_index
        print(f"Camera index updated to {camera_index}")
        
        return True
    
    def set_selected_camera(self, camera_index):
        """
        Set the selected camera index (alias for set_camera_index for compatibility)
        
        Args:
            camera_index (int): Index of the camera to use
        """
        return self.set_camera_index(camera_index)
    
    def get_available_cameras(self):
        """
        Get list of available cameras
        
        Returns:
            list: List of tuples containing (index, name) of available cameras
        """
        return self.available_cameras
    
    def refresh_cameras(self):
        """
        Refresh the list of available cameras
        
        Returns:
            list: Updated list of available cameras
        """
        return self.detect_available_cameras()
    
    def get_current_camera_name(self):
        """
        Get current camera name with real-time resolution information
        
        Returns:
            str: Camera name with current resolution info
        """
        # Find the camera entry that matches the selected index
        base_name = None
        for index, name in self.available_cameras:
            if index == self.selected_camera_index:
                base_name = name
                break
        
        if base_name is None:
            return tr.get_text("default_camera")
            
        # If camera is active, add current resolution info
        if self.camera_open and self.camera:
            try:
                width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                if width > 0 and height > 0:
                    resolution_info = f" ({width}x{height})"
                    
                    # Check if we're using auto-scaling
                    if width > 1280 or height > 720:
                        resolution_info += " [Auto-Scaled]"
                    
                    return base_name + resolution_info
            except:
                pass
        
        return base_name

    def is_camera_active(self):
        """Check if camera is active"""
        return self.camera_open
    
    def camera_start(self):
        """Start camera with selected camera index and resolution management"""
        print(f"=== CameraManager.camera_start() called ===")
        print(f"Current camera_open state: {self.camera_open}")
        print(f"Selected camera index: {self.selected_camera_index}")
        
        if self.camera_open:
            print("Camera is already open - returning True")
            return True
            
        print(f"Starting camera with index {self.selected_camera_index}...")
        try:
            # Add timeout protection for camera initialization
            self.camera = cv2.VideoCapture(self.selected_camera_index)
            print(f"VideoCapture created for index {self.selected_camera_index}")
            
            # Set timeout for camera operations (5 seconds)
            self.camera.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
            self.camera.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 1000)
            
            # Check if camera opened successfully with timeout
            if not self.camera.isOpened():
                print(f"Failed to open camera {self.selected_camera_index} - isOpened() returned False")
                return False
                
            print("Camera opened successfully, configuring...")
            
            # Set reasonable buffer size to prevent frame delays
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Try to set optimal frame rate for stability
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # Verify camera works by reading a test frame with timeout protection
            print("Testing camera frame capture...")
            ret, test_frame = self.camera.read()
            
            if ret and test_frame is not None:
                print(f"Camera test frame captured successfully: {test_frame.shape}")
                # Check if we need to adjust resolution for stability
                height, width = test_frame.shape[:2]
                
                # If resolution is very high, try to set a more manageable resolution
                if width > 1920 or height > 1080:
                    print(f"High resolution detected ({width}x{height}), attempting to set lower resolution...")
                    
                    # Try to set 1280x720 first
                    self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                    self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                    
                    # Test if the new resolution works
                    ret2, test_frame2 = self.camera.read()
                    if ret2 and test_frame2 is not None:
                        new_height, new_width = test_frame2.shape[:2]
                        print(f"Resolution adjusted to {new_width}x{new_height}")
                    else:
                        print("Could not adjust resolution, will use frame downscaling")
                
                self.camera_open = True
                print("Camera started successfully")
                
                # Notify parent window to update camera name if available
                if hasattr(self.parent, 'camera_selector') and self.parent.camera_selector:
                    self.parent.camera_selector.update_current_camera_name()
                
                return True
            else:
                print("Failed to capture test frame")
                self.camera.release()
                return False
                
        except Exception as e:
            print(f"Error starting camera: {e}")
            if hasattr(self, 'camera') and self.camera:
                try:
                    self.camera.release()
                except:
                    pass
                self.camera = None
            return False
    
    def camera_stop(self):
        """Stop camera safely with error handling and resource cleanup"""
        print(f"=== CameraManager.camera_stop() called ===")
        print(f"Current camera_open state: {self.camera_open}")
        
        if not self.camera_open:
            print("Camera was not open - returning True")
            return True  # Already stopped
            
        print("Stopping camera...")
        try:
            # First, mark camera as stopped to prevent new frame requests
            self.camera_open = False
            print("Camera marked as stopped")
            
            # Give a small delay to let any ongoing frame operations complete
            import time
            time.sleep(0.05)
            
            # Now safely release the camera resource
            if hasattr(self, 'camera') and self.camera is not None:
                try:
                    print("Releasing camera resource...")
                    self.camera.release()
                    print("Camera released successfully")
                except Exception as e:
                    print(f"Error releasing camera resource: {e}")
                finally:
                    self.camera = None
                    print("Camera object set to None")
            
            # Clear frame data
            self.current_frame = None
            self.current_frame_processed = None
            
            return True
            
        except Exception as e:
            print(f"Error during camera stop: {e}")
            # Force cleanup even if there's an error
            self.camera_open = False
            self.current_frame = None
            self.current_frame_processed = None
            if hasattr(self, 'camera'):
                self.camera = None
            return True
    
    def get_frame(self):
        """
        Get a frame from camera with automatic resolution management and thread safety
        
        Returns:
            (success status, frame)
        """
        # Double check camera state for thread safety
        if not self.camera_open or not hasattr(self, 'camera') or self.camera is None:
            return False, None
            
        try:
            # Additional safety check before reading
            if not self.camera.isOpened():
                return False, None
                
            success, frame = self.camera.read()
            if success and frame is not None:
                # Get frame dimensions
                height, width = frame.shape[:2]
                
                # Define maximum allowed dimensions for stable processing
                max_width = 1280
                max_height = 720
                
                # Check if frame is too large and needs downscaling
                if width > max_width or height > max_height:
                    # Calculate scaling factor to maintain aspect ratio
                    scale_factor = min(max_width / width, max_height / height)
                    
                    # Calculate new dimensions
                    new_width = int(width * scale_factor)
                    new_height = int(height * scale_factor)
                    
                    # Resize frame using high-quality interpolation
                    frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
                    
                # Store processed frame
                self.current_frame = frame.copy()
                
                return True, frame
            else:
                return False, None
                
        except Exception as e:
            print(f"Error reading camera frame: {e}")
            return False, None
    
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
