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
    def __init__(self, ebeveyn=None):
        """
        Kamera yönetimi için sınıf
        
        Args:
            ebeveyn: Ana uygulama penceresi referansı
        """
        self.ebeveyn = ebeveyn
        self.kamera_acik = False
        self.kamera = None
        self.mevcut_kare = None
    
    def kamera_baslat(self):
        """Kamerayı başlat"""
        if self.kamera_acik:
            return
            
        self.kamera = cv2.VideoCapture(0)
        if self.kamera.isOpened():
            self.kamera_acik = True
            return True
        else:
            return False
    
    def kamera_durdur(self):
        """Kamerayı durdur"""
        if self.kamera_acik:
            self.kamera.release()
            self.kamera_acik = False
            self.mevcut_kare = None
            return True
        return False
    
    def kare_al(self):
        """
        Kameradan bir kare al
        
        Returns:
            (başarı durumu, kare)
        """
        if not self.kamera_acik:
            return False, None
            
        sonuc, kare = self.kamera.read()
        if sonuc:
            self.mevcut_kare = kare.copy()
        return sonuc, kare
    
    def ekran_goruntusu_al(self):
        """
        Bir ekran görüntüsü al ve kaydet
        
        Returns:
            (başarılı mı, dosya adı veya hata mesajı)
        """
        if not hasattr(self, 'mevcut_kare') or self.mevcut_kare is None:
            return False, "No frame available"
                
        # Ensure screenshots directory exists - ana klasör yerine source klasörünün üstünü kullan
        kok_dizin = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ekran_goruntusu_dizin = os.path.join(kok_dizin, "screenshots")
        if not os.path.exists(ekran_goruntusu_dizin):
            os.makedirs(ekran_goruntusu_dizin)
        
        # Find all PNG files in the screenshots directory that start with "screenshot_"
        ekran_goruntusu_dosyalari = glob.glob(os.path.join(ekran_goruntusu_dizin, "screenshot_*.png"))
        sonraki_numara = 1
        if ekran_goruntusu_dosyalari:
            # Extract numbers from existing files and find the maximum
            mevcut_numaralar = []
            for dosya_adi in ekran_goruntusu_dosyalari:
                try:
                    temel_dosya_adi = os.path.basename(dosya_adi)
                    numara = int(temel_dosya_adi.replace("screenshot_", "").replace(".png", ""))
                    mevcut_numaralar.append(numara)
                except ValueError:
                    pass
            if mevcut_numaralar:
                sonraki_numara = max(mevcut_numaralar) + 1
                
        dosya_adi = os.path.join(ekran_goruntusu_dizin, f"screenshot_{sonraki_numara}.png")
        cv2.imwrite(dosya_adi, self.mevcut_kare)
        return True, dosya_adi

# Kamera arayüzü bileşenleri
def kamera_arayuzu_olustur(ebeveyn, kamera_besleme_duzen):
    """
    Kamera kullanıcı arayüzü oluştur
    
    Args:
        ebeveyn: Ana uygulama penceresi
        kamera_besleme_duzen: Kamera beslemesinin ekleneceği layout
    """
    # Clear any existing widgets in camera feed
    for i in reversed(range(kamera_besleme_duzen.count())): 
        kamera_besleme_duzen.itemAt(i).widget().setParent(None)
    
    # Create message layout
    mesaj_duzen = QVBoxLayout()
    
    # Add camera icon - ikon yolunu güncelle
    kamera_ikon_etiket = QLabel()
    ikon_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'camera_icon.png')
    kamera_ikon = QPixmap(ikon_yolu)
    if kamera_ikon.isNull():
        # If icon file doesn't exist, create a text placeholder
        kamera_ikon_etiket.setText("📷")
        kamera_ikon_etiket.setStyleSheet("font-size: 48pt; color: #4CAF50;")
    else:
        # Scale icon to appropriate size - Fix Qt constants
        kamera_ikon = kamera_ikon.scaled(QSize(64, 64), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        kamera_ikon_etiket.setPixmap(kamera_ikon)
    
    kamera_ikon_etiket.setAlignment(Qt.AlignCenter)  # Fixed: use Qt.AlignCenter
    mesaj_duzen.addWidget(kamera_ikon_etiket)
    
    # Add information about click to start
    bilgi_metni = QLabel(tr.get_text("camera_ready"))
    bilgi_metni.setStyleSheet("color: white; font-size: 14pt; margin: 15px;")
    bilgi_metni.setWordWrap(True)
    bilgi_metni.setAlignment(Qt.AlignCenter)  # Fixed: use Qt.AlignCenter
    mesaj_duzen.addWidget(bilgi_metni)
    
    # Create a container widget for the message layout
    mesaj_widget = QWidget()
    mesaj_widget.setLayout(mesaj_duzen)
    
    # Add the message widget to the camera feed layout
    kamera_besleme_duzen.addWidget(mesaj_widget)

def kamera_izin_arayuzunu_goster(ebeveyn, kamera_besleme_duzen, izin_ver_callback=None, izin_reddet_callback=None):
    """
    Kamera izin arayüzünü göster
    
    Args:
        ebeveyn: Ana uygulama penceresi
        kamera_besleme_duzen: Kamera beslemesinin ekleneceği layout
        izin_ver_callback: İzin verildiğinde çağrılacak fonksiyon
        izin_reddet_callback: İzin reddedildiğinde çağrılacak fonksiyon
    """
    # Clear any existing widgets in camera feed
    for i in reversed(range(kamera_besleme_duzen.count())): 
        kamera_besleme_duzen.itemAt(i).widget().setParent(None)
    
    # Create permission layout
    izin_duzen = QVBoxLayout()
    
    # Add camera icon - ikon yolunu güncelle
    kamera_ikon_etiket = QLabel()
    ikon_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'camera_icon.png')
    kamera_ikon = QPixmap(ikon_yolu)
    if kamera_ikon.isNull():
        # If icon file doesn't exist, create a text placeholder
        kamera_ikon_etiket.setText("📷")
        kamera_ikon_etiket.setStyleSheet("font-size: 48pt; color: #4CAF50;")
    else:
        # Scale icon to appropriate size - Fix Qt constants
        kamera_ikon = kamera_ikon.scaled(QSize(64, 64), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        kamera_ikon_etiket.setPixmap(kamera_ikon)
    
    kamera_ikon_etiket.setAlignment(Qt.AlignCenter)  # Fixed: use Qt.AlignCenter
    izin_duzen.addWidget(kamera_ikon_etiket)
    
    # Add permission text
    izin_metni = QLabel(tr.get_text("camera_permission_text"))
    izin_metni.setStyleSheet("color: white; font-size: 12pt; margin: 15px;")
    izin_metni.setWordWrap(True)
    izin_metni.setAlignment(Qt.AlignCenter)  # Fixed: use Qt.AlignCenter
    izin_duzen.addWidget(izin_metni)
    
    # Add buttons for permission
    buton_widget = QWidget()
    buton_duzen = QHBoxLayout(buton_widget)
    
    # Grant permission button with enhanced hover effects
    izin_ver_buton = QPushButton(tr.get_text("grant_permission"))
    izin_ver_buton.setToolTip(tr.get_text("grant_permission_tooltip"))
    izin_ver_buton.setStyleSheet("""
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
    if izin_ver_callback:
        izin_ver_buton.clicked.connect(izin_ver_callback)
    
    # Deny permission button with enhanced hover effects
    izin_reddet_buton = QPushButton(tr.get_text("deny_permission"))
    izin_reddet_buton.setToolTip(tr.get_text("deny_permission_tooltip"))
    izin_reddet_buton.setStyleSheet("""
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
    if izin_reddet_callback:
        izin_reddet_buton.clicked.connect(izin_reddet_callback)
    
    # Add checkbox to remember decision with hover effect
    izni_hatirla = QCheckBox(tr.get_text("remember_decision"))
    izni_hatirla.setToolTip(tr.get_text("remember_decision_tooltip"))
    izni_hatirla.setStyleSheet("""
        QCheckBox {
            color: white;
        }
        QCheckBox:hover {
            color: #2196F3;
        }
    """)
    izni_hatirla.setChecked(True)
    ebeveyn.izni_hatirla = izni_hatirla  # Ana pencereye referansı sakla
    
    buton_duzen.addWidget(izin_reddet_buton)
    buton_duzen.addWidget(izin_ver_buton)
    
    izin_duzen.addWidget(buton_widget)
    izin_duzen.addWidget(izni_hatirla)
    
    # Create a container widget for the permission layout
    izin_widget = QWidget()
    izin_widget.setLayout(izin_duzen)
    
    # Add the permission widget to the camera feed layout
    kamera_besleme_duzen.addWidget(izin_widget)
