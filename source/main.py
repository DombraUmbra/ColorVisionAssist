import os
import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QStatusBar
from PyQt5.QtCore import Qt, QTimer, QSize, QSettings
from PyQt5.QtGui import QImage, QPixmap, QIcon

# Paketin kendi modüllerini import et
from .translations import translator as tr
from .gallery import ScreenshotGallery
from .color_detection import ColorDetector
from .camera import CameraManager, create_camera_ui, show_camera_permission_ui
from .utils import draw_text_with_utf8
from .ui_components import (create_camera_controls, create_color_detection_group,
                          create_display_settings_group, create_camera_settings_group,
                          create_language_group, create_about_group, apply_dark_theme)

class ColorVisionAid(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Ayarları yükle
        self.settings = QSettings("ColorVisionAid", "CVA")
        language = self.settings.value("language", "en")
        tr.set_language(language)
        
        # Kullanıcı tercihlerini yükle
        self.camera_permission = self.settings.value("camera_permission", "ask")  # "granted", "denied", "ask"
        
        # Camera manager ve color detector oluştur
        self.camera_manager = CameraManager(self)
        self.color_detector = ColorDetector()
        
        # UI kurulumu
        self.setup_ui()
        
        # Timer for updating the camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def setup_ui(self):
        """UI bileşenlerini ve düzeni oluştur"""
        # Window setup
        self.setWindowTitle(tr.get_text("app_title"))
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons', 'app_icon.png')))
        
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Kamera görünüm alanı
        self.setup_camera_view()
        
        # Ayarlar paneli
        self.setup_settings_panel()
        
        # Ana bileşenleri düzene ekle
        self.main_layout.addWidget(self.camera_container, 7)
        self.main_layout.addWidget(self.settings_panel, 3)
        
        # Durum çubuğu
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(tr.get_text("ready"))
        
        # Stil temasını uygula
        apply_dark_theme(self)

    def setup_camera_view(self):
        """Kamera görüntü alanını oluştur"""
        # Ana kamera konteyneri
        self.camera_container = QWidget()
        self.camera_layout = QVBoxLayout(self.camera_container)
        
        # Kamera beslemesi için konteyner
        self.camera_feed_container = QWidget()
        self.camera_feed_container.setStyleSheet("background-color: #222; border-radius: 10px;")
        self.camera_feed_layout = QVBoxLayout(self.camera_feed_container)
        self.camera_feed_layout.setContentsMargins(20, 20, 20, 20)
        
        # Kamera mesajını göster
        create_camera_ui(self, self.camera_feed_layout)
        
        self.camera_layout.addWidget(self.camera_feed_container)
        
        # Kamera kontrol butonları - UI Components modülünü kullan
        self.camera_layout.addLayout(create_camera_controls(self))

    def setup_settings_panel(self):
        """Ayarlar panelini oluştur"""
        self.settings_panel = QWidget()
        self.settings_panel.setMaximumWidth(300)
        self.settings_layout = QVBoxLayout(self.settings_panel)
        
        # UI Components modülünden grupları oluştur
        self.color_group = create_color_detection_group(self)
        self.display_group = create_display_settings_group(self)
        self.camera_settings_group = create_camera_settings_group(self)
        self.language_group = create_language_group(self)
        self.about_group = create_about_group(self)
        
        # Ayar gruplarını panele ekle
        self.settings_layout.addWidget(self.color_group)
        self.settings_layout.addWidget(self.display_group)
        self.settings_layout.addWidget(self.camera_settings_group)
        self.settings_layout.addWidget(self.language_group)
        self.settings_layout.addWidget(self.about_group)
        self.settings_layout.addStretch()

    def change_language(self, index):
        """Uygulama dilini değiştir"""
        language_code = self.language_combo.itemData(index)
        if tr.set_language(language_code):
            # Dil ayarını kaydet
            self.settings.setValue("language", language_code)
            
            # Görünür elemanların dilini güncelle
            self.update_ui_language()
            
            # Durum mesajını göster
            self.status_bar.showMessage(tr.get_text("language_changed"))
    
    def update_ui_language(self):
        """UI elemanlarını yeni dile göre güncelle"""
        # Pencere başlığını güncelle
        self.setWindowTitle(tr.get_text("app_title"))
        
        # Butonları güncelle
        self.snapshot_button.setText(tr.get_text("take_screenshot"))
        self.gallery_button.setText(tr.get_text("gallery"))
        
        # Kamera butonunu güncelle
        if self.camera_manager.camera_on:
            self.toggle_camera_button.setText(tr.get_text("stop"))
            self.toggle_camera_button.setToolTip(tr.get_text("stop_tooltip"))
        else:
            self.toggle_camera_button.setText(tr.get_text("start"))
            self.toggle_camera_button.setToolTip(tr.get_text("start_tooltip"))

        # Grupları güncelle
        self.color_group.setTitle(tr.get_text("color_detection"))
        self.display_group.setTitle(tr.get_text("display_settings"))
        self.camera_settings_group.setTitle(tr.get_text("camera_settings"))
        self.language_group.setTitle(tr.get_text("language"))
        self.about_group.setTitle(tr.get_text("about"))
        
        # Onay kutularını güncelle
        self.red_checkbox.setText(tr.get_text("detect_red"))
        self.green_checkbox.setText(tr.get_text("detect_green"))
        self.blue_checkbox.setText(tr.get_text("detect_blue"))
        self.yellow_checkbox.setText(tr.get_text("detect_yellow"))
        
        # Etiketleri güncelle
        self.detection_sensitivity_label.setText(tr.get_text("detection_sensitivity"))
        self.contrast_label.setText(tr.get_text("contrast"))
        self.display_mode_label.setText(tr.get_text("display_mode"))
        self.camera_info_label.setText(tr.get_text("camera_settings_info"))
        self.about_label.setText(tr.get_text("about_text"))
        self.reset_permission_button.setText(tr.get_text("reset_camera_permission"))
        
        # İzin durumunu güncelle
        permission_status_text = ""
        if self.camera_permission == "granted":
            permission_status_text = tr.get_text("permission_status_granted")
        elif self.camera_permission == "denied":
            permission_status_text = tr.get_text("permission_status_denied")
        else:
            permission_status_text = tr.get_text("permission_status_ask")
        self.permission_status_label.setText(f"{tr.get_text('current_permission_status')}: {permission_status_text}")
        
        # Durum çubuğunu güncelle
        if not self.camera_manager.camera_on:
            self.status_bar.showMessage(tr.get_text("ready"))
        
        # Kamera görüntüsü açık değilse, başlangıç mesajını güncelle
        if not self.camera_manager.camera_on:
            create_camera_ui(self, self.camera_feed_layout)

    def reset_camera_permission(self):
        """Kaydedilmiş kamera izinlerini sıfırla"""
        self.camera_permission = "ask"
        self.settings.setValue("camera_permission", "ask")
        self.status_bar.showMessage(tr.get_text("permission_reset"))
        
        # İzin durumu göstergesini güncelle
        self.permission_status_label.setText(f"{tr.get_text('current_permission_status')}: {tr.get_text('permission_status_ask')}")

    def on_camera_permission_granted(self):
        """Kamera izni verildiğinde yapılacaklar"""
        # İzin tercihini kaydet
        if hasattr(self, 'remember_permission') and self.remember_permission.isChecked():
            self.camera_permission = "granted"
            self.settings.setValue("camera_permission", "granted")
            # İzin durumu göstergesini güncelle
            self.permission_status_label.setText(f"{tr.get_text('current_permission_status')}: {tr.get_text('permission_status_granted')}")
            
        # Kamera başlatma işlemine devam et
        self.start_camera_process()
    
    def on_camera_permission_denied(self):
        """Kamera izni reddedildiğinde yapılacaklar"""
        # İzin tercihini kaydet
        if hasattr(self, 'remember_permission') and self.remember_permission.isChecked():
            self.camera_permission = "denied"
            self.settings.setValue("camera_permission", "denied")
            # İzin durumu göstergesini güncelle
            self.permission_status_label.setText(f"{tr.get_text('current_permission_status')}: {tr.get_text('permission_status_denied')}")
        
        # Durum mesajını göster
        self.status_bar.showMessage(tr.get_text("camera_permission_denied"))
        # Başlangıç mesajına dön
        create_camera_ui(self, self.camera_feed_layout)

    def start_camera_process(self):
        """İzin verildikten sonra kamerayı başlat"""
        # Kamera besleme düzenindeki tüm widget'ları temizle
        for i in reversed(range(self.camera_feed_layout.count())): 
            self.camera_feed_layout.itemAt(i).widget().setParent(None)
            
        # Başlatma mesajını göster
        initializing_label = QLabel(tr.get_text("camera_initializing"))
        initializing_label.setStyleSheet("color: white; font-size: 12pt;")
        initializing_label.setAlignment(Qt.AlignCenter)
        self.camera_feed_layout.addWidget(initializing_label)
        QApplication.processEvents()  # UI'ı hemen güncelle
        
        # Şimdi kamerayı başlatmayı dene
        if self.camera_manager.start_camera():
            self.timer.start(33)  # ~30 FPS
            self.status_bar.showMessage(tr.get_text("camera_started"))
            
            # "Durdur" butonu görünümünü güncelle
            self.toggle_camera_button.setText(tr.get_text("stop"))
            self.toggle_camera_button.setToolTip(tr.get_text("stop_tooltip"))
            self.toggle_camera_button.setStyleSheet("""
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
            
            # Ekran görüntüsü butonunu göster
            self.snapshot_button.setVisible(True)
        else:
            self.status_bar.showMessage(tr.get_text("camera_start_failed"))
            create_camera_ui(self, self.camera_feed_layout)  # Kamera başlatılamazsa başlangıç mesajını göster

    def stop_camera(self):
        """Kamerayı durdur"""
        if self.camera_manager.stop_camera():
            self.timer.stop()
            
            # Başlangıç mesajına dön
            create_camera_ui(self, self.camera_feed_layout)
            
            self.status_bar.showMessage(tr.get_text("camera_stopped"))
            
            # "Başlat" butonu görünümünü güncelle
            self.toggle_camera_button.setText(tr.get_text("start"))
            self.toggle_camera_button.setToolTip(tr.get_text("start_tooltip"))
            self.toggle_camera_button.setStyleSheet("""
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
            
            # Ekran görüntüsü butonunu gizle
            self.snapshot_button.setVisible(False)

    def take_snapshot(self):
        """Ekran görüntüsü al"""
        success, result = self.camera_manager.take_snapshot()
        if success:
            # Dosya yolunu göstermek için dosya adını path'den ayır
            filename = os.path.basename(result)
            self.status_bar.showMessage(tr.get_text("screenshot_saved", filename))
        else:
            self.status_bar.showMessage(tr.get_text("screenshot_failed", result))

    def open_gallery(self):
        """Galeriyi aç"""
        gallery = ScreenshotGallery(self)
        gallery.exec_()

    def update_frame(self):
        ret, frame = self.camera_manager.get_frame()
        if ret:
            selected_colors = {
                'red': self.red_checkbox.isChecked(),
                'green': self.green_checkbox.isChecked(),
                'blue': self.blue_checkbox.isChecked(),
                'yellow': self.yellow_checkbox.isChecked()
            }
            
            # Çevrilmiş renk isimleri
            color_translated = {
                'red': tr.get_text("red"),
                'green': tr.get_text("green"),
                'blue': tr.get_text("blue"),
                'yellow': tr.get_text("yellow")
            }
            
            # Renk detektörü ile kareyi işle
            combined_result = self.color_detector.process_frame(
                frame, 
                selected_colors,
                self.sensitivity_slider.value(),
                self.contrast_slider.value(),
                color_translated
            )
            
            # Sonucu QImage'a çevir ve göster
            h, w, c = combined_result.shape
            bytesPerLine = 3 * w
            qImg = QImage(combined_result.data, w, h, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
            
            # Tüm mevcut widget'ları temizle
            for i in reversed(range(self.camera_feed_layout.count())): 
                self.camera_feed_layout.itemAt(i).widget().setParent(None)
                
            # Resim etiketini oluştur ve ekle
            image_label = QLabel()
            image_label.setPixmap(QPixmap.fromImage(qImg).scaled(
                self.camera_feed_container.width() - 40,  # Kenar boşluklarını hesaba kat
                self.camera_feed_container.height() - 40, 
                Qt.KeepAspectRatio
            ))
            image_label.setAlignment(Qt.AlignCenter)
            self.camera_feed_layout.addWidget(image_label)
    
    def toggle_camera(self):
        """Kamerayı açıp kapatma"""
        if self.camera_manager.camera_on:
            self.stop_camera()
        else:
            self.start_camera()
            
    def start_camera(self):
        """İzinleri kontrol ettikten sonra kamerayı başlat"""
        if not self.camera_manager.camera_on:
            # Kaydedilmiş izin tercihini kontrol et
            if self.camera_permission == "granted":
                # İzin zaten verildi, kamerayı doğrudan başlat
                self.start_camera_process()
            elif self.camera_permission == "denied":
                # İzin zaten reddedildi
                self.status_bar.showMessage(tr.get_text("camera_permission_denied"))
            else:
                # İzin sor
                show_camera_permission_ui(
                    self, 
                    self.camera_feed_layout,
                    self.on_camera_permission_granted,
                    self.on_camera_permission_denied
                )