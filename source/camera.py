import os
import cv2
import glob
import numpy as np
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton, QCheckBox, QHBoxLayout
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap

# Paketin kendi modüllerini import et
from .translations import translator as tr

class CameraManager:
    def __init__(self, parent=None):
        """
        Kamera yönetimi için sınıf
        
        Args:
            parent: Ana uygulama penceresi referansı
        """
        self.parent = parent
        self.camera_on = False
        self.cam = None
        self.current_frame = None
    
    def start_camera(self):
        """Kamerayı başlat"""
        if self.camera_on:
            return
            
        self.cam = cv2.VideoCapture(0)
        if self.cam.isOpened():
            self.camera_on = True
            return True
        else:
            return False
    
    def stop_camera(self):
        """Kamerayı durdur"""
        if self.camera_on:
            self.cam.release()
            self.camera_on = False
            self.current_frame = None
            return True
        return False
    
    def get_frame(self):
        """
        Kameradan bir kare al
        
        Returns:
            (başarı durumu, kare)
        """
        if not self.camera_on:
            return False, None
            
        ret, frame = self.cam.read()
        if ret:
            self.current_frame = frame.copy()
        return ret, frame
    
    def take_snapshot(self):
        """
        Bir ekran görüntüsü al ve kaydet
        
        Returns:
            (başarılı mı, dosya adı veya hata mesajı)
        """
        if not hasattr(self, 'current_frame') or self.current_frame is None:
            return False, "No frame available"
                
        # Ensure screenshots directory exists - ana klasör yerine source klasörünün üstünü kullan
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        screenshots_dir = os.path.join(root_dir, "screenshots")
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
        
        # Find all PNG files in the screenshots directory that start with "screenshot_"
        screenshot_files = glob.glob(os.path.join(screenshots_dir, "screenshot_*.png"))
        next_num = 1
        if screenshot_files:
            # Extract numbers from existing files and find the maximum
            existing_nums = []
            for filename in screenshot_files:
                try:
                    base_filename = os.path.basename(filename)
                    num = int(base_filename.replace("screenshot_", "").replace(".png", ""))
                    existing_nums.append(num)
                except ValueError:
                    pass
            if existing_nums:
                next_num = max(existing_nums) + 1
                
        filename = os.path.join(screenshots_dir, f"screenshot_{next_num}.png")
        cv2.imwrite(filename, self.current_frame)
        return True, filename

# Kamera arayüzü bileşenleri
def create_camera_ui(parent, camera_feed_layout):
    """
    Kamera kullanıcı arayüzü oluştur
    
    Args:
        parent: Ana uygulama penceresi
        camera_feed_layout: Kamera beslemesinin ekleneceği layout
    """
    # Clear any existing widgets in camera feed
    for i in reversed(range(camera_feed_layout.count())): 
        camera_feed_layout.itemAt(i).widget().setParent(None)
    
    # Create message layout
    message_layout = QVBoxLayout()
    
    # Add camera icon - ikon yolunu güncelle
    camera_icon_label = QLabel()
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'camera_icon.png')
    camera_icon = QPixmap(icon_path)
    if camera_icon.isNull():
        # If icon file doesn't exist, create a text placeholder
        camera_icon_label.setText("📷")
        camera_icon_label.setStyleSheet("font-size: 48pt; color: #4CAF50;")
    else:
        # Scale icon to appropriate size - Fix Qt constants
        camera_icon = camera_icon.scaled(QSize(64, 64), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        camera_icon_label.setPixmap(camera_icon)
    
    camera_icon_label.setAlignment(Qt.AlignCenter)  # Fixed: use Qt.AlignCenter
    message_layout.addWidget(camera_icon_label)
    
    # Add information about click to start
    info_text = QLabel(tr.get_text("camera_ready"))
    info_text.setStyleSheet("color: white; font-size: 14pt; margin: 15px;")
    info_text.setWordWrap(True)
    info_text.setAlignment(Qt.AlignCenter)  # Fixed: use Qt.AlignCenter
    message_layout.addWidget(info_text)
    
    # Create a container widget for the message layout
    message_widget = QWidget()
    message_widget.setLayout(message_layout)
    
    # Add the message widget to the camera feed layout
    camera_feed_layout.addWidget(message_widget)

def show_camera_permission_ui(parent, camera_feed_layout, grant_callback=None, deny_callback=None):
    """
    Kamera izin arayüzünü göster
    
    Args:
        parent: Ana uygulama penceresi
        camera_feed_layout: Kamera beslemesinin ekleneceği layout
        grant_callback: İzin verildiğinde çağrılacak fonksiyon
        deny_callback: İzin reddedildiğinde çağrılacak fonksiyon
    """
    # Clear any existing widgets in camera feed
    for i in reversed(range(camera_feed_layout.count())): 
        camera_feed_layout.itemAt(i).widget().setParent(None)
    
    # Create permission layout
    permission_layout = QVBoxLayout()
    
    # Add camera icon - ikon yolunu güncelle
    camera_icon_label = QLabel()
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'camera_icon.png')
    camera_icon = QPixmap(icon_path)
    if camera_icon.isNull():
        # If icon file doesn't exist, create a text placeholder
        camera_icon_label.setText("📷")
        camera_icon_label.setStyleSheet("font-size: 48pt; color: #4CAF50;")
    else:
        # Scale icon to appropriate size - Fix Qt constants
        camera_icon = camera_icon.scaled(QSize(64, 64), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        camera_icon_label.setPixmap(camera_icon)
    
    camera_icon_label.setAlignment(Qt.AlignCenter)  # Fixed: use Qt.AlignCenter
    permission_layout.addWidget(camera_icon_label)
    
    # Add permission text
    permission_text = QLabel(tr.get_text("camera_permission_text"))
    permission_text.setStyleSheet("color: white; font-size: 12pt; margin: 15px;")
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
    
    # Add checkbox to remember decision with hover effect
    remember_permission = QCheckBox(tr.get_text("remember_decision"))
    remember_permission.setToolTip(tr.get_text("remember_decision_tooltip"))
    remember_permission.setStyleSheet("""
        QCheckBox {
            color: white;
        }
        QCheckBox:hover {
            color: #2196F3;
        }
    """)
    remember_permission.setChecked(True)
    parent.remember_permission = remember_permission  # Ana pencereye referansı sakla
    
    button_layout.addWidget(deny_button)
    button_layout.addWidget(grant_button)
    
    permission_layout.addWidget(button_widget)
    permission_layout.addWidget(remember_permission)
    
    # Create a container widget for the permission layout
    permission_widget = QWidget()
    permission_widget.setLayout(permission_layout)
    
    # Add the permission widget to the camera feed layout
    camera_feed_layout.addWidget(permission_widget)
