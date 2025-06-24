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
from .camera import CameraManager, kamera_arayuzu_olustur, kamera_izin_arayuzunu_goster
from .utils import draw_text_with_utf8
from .ui_components import (kamera_kontrolleri_olustur, renk_algilama_grubu_olustur,
                          gorunum_ayarlari_grubu_olustur, kamera_ayarlari_grubu_olustur,
                          dil_grubu_olustur, hakkinda_grubu_olustur, koyu_tema_uygula)

class ColorVisionAid(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Ayarları yükle
        self.ayarlar = QSettings("ColorVisionAid", "CVA")
        dil = self.ayarlar.value("language", "en")
        tr.set_language(dil)
        
        # Kullanıcı tercihlerini yükle
        self.kamera_izni = self.ayarlar.value("camera_permission", "ask")  # "granted", "denied", "ask"
        
        # Camera manager ve color detector oluştur
        self.kamera_yoneticisi = CameraManager(self)
        self.renk_algilayici = ColorDetector()
        
        # UI kurulumu
        self.arayuzu_kur()
        
        # Timer for updating the camera feed
        self.zamanlayici = QTimer()
        self.zamanlayici.timeout.connect(self.kareyi_guncelle)

    def arayuzu_kur(self):
        """UI bileşenlerini ve düzeni oluştur"""
        # Window setup
        self.setWindowTitle(tr.get_text("app_title"))
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons', 'app_icon.png')))
        
        # Main widget and layout
        self.merkezi_widget = QWidget()
        self.setCentralWidget(self.merkezi_widget)
        self.ana_duzen = QHBoxLayout(self.merkezi_widget)
        
        # Kamera görünüm alanı
        self.kamera_gorunumunu_kur()
        
        # Ayarlar paneli
        self.ayarlar_panelini_kur()
        
        # Ana bileşenleri düzene ekle
        self.ana_duzen.addWidget(self.kamera_konteyner, 7)
        self.ana_duzen.addWidget(self.ayarlar_paneli, 3)
        
        # Durum çubuğu
        self.durum_cubugu = QStatusBar()
        self.setStatusBar(self.durum_cubugu)
        self.durum_cubugu.showMessage(tr.get_text("ready"))
          # Stil temasını uygula
        koyu_tema_uygula(self)

    def kamera_gorunumunu_kur(self):
        """Kamera görüntü alanını oluştur"""
        # Ana kamera konteyneri
        self.kamera_konteyner = QWidget()
        self.kamera_duzen = QVBoxLayout(self.kamera_konteyner)
        
        # Kamera beslemesi için konteyner
        self.kamera_besleme_konteyner = QWidget()
        self.kamera_besleme_konteyner.setStyleSheet("background-color: #222; border-radius: 10px;")
        self.kamera_besleme_duzen = QVBoxLayout(self.kamera_besleme_konteyner)
        self.kamera_besleme_duzen.setContentsMargins(20, 20, 20, 20)
          # Kamera mesajını göster
        kamera_arayuzu_olustur(self, self.kamera_besleme_duzen)
        
        self.kamera_duzen.addWidget(self.kamera_besleme_konteyner)
          # Kamera kontrol butonları - UI Components modülünü kullan
        self.kamera_duzen.addLayout(kamera_kontrolleri_olustur(self))

    def ayarlar_panelini_kur(self):
        """Ayarlar panelini oluştur"""
        self.ayarlar_paneli = QWidget()
        self.ayarlar_paneli.setMaximumWidth(300)
        self.ayarlar_duzen = QVBoxLayout(self.ayarlar_paneli)
          # UI Components modülünden grupları oluştur
        self.renk_grubu = renk_algilama_grubu_olustur(self)
        self.gorunum_grubu = gorunum_ayarlari_grubu_olustur(self)
        self.kamera_ayarlari_grubu = kamera_ayarlari_grubu_olustur(self)
        self.dil_grubu = dil_grubu_olustur(self)
        self.hakkinda_grubu = hakkinda_grubu_olustur(self)
        
        # Ayar gruplarını panele ekle
        self.ayarlar_duzen.addWidget(self.renk_grubu)
        self.ayarlar_duzen.addWidget(self.gorunum_grubu)
        self.ayarlar_duzen.addWidget(self.kamera_ayarlari_grubu)
        self.ayarlar_duzen.addWidget(self.dil_grubu)
        self.ayarlar_duzen.addWidget(self.hakkinda_grubu)
        self.ayarlar_duzen.addStretch()

    def dil_degistir(self, indeks):
        """Uygulama dilini değiştir"""
        dil_kodu = self.dil_combo.itemData(indeks)
        if tr.set_language(dil_kodu):
            # Dil ayarını kaydet
            self.ayarlar.setValue("language", dil_kodu)
            
            # Görünür elemanların dilini güncelle
            self.arayuz_dilini_guncelle()
            
            # Durum mesajını göster
            self.durum_cubugu.showMessage(tr.get_text("language_changed"))
    
    def arayuz_dilini_guncelle(self):
        """UI elemanlarını yeni dile göre güncelle"""
        # Pencere başlığını güncelle
        self.setWindowTitle(tr.get_text("app_title"))
        
        # Butonları güncelle
        self.ekran_goruntusu_buton.setText(tr.get_text("take_screenshot"))
        self.galeri_buton.setText(tr.get_text("gallery"))
        
        # Kamera butonunu güncelle
        if self.kamera_yoneticisi.kamera_acik:
            self.kamera_acma_kapama_buton.setText(tr.get_text("stop"))
            self.kamera_acma_kapama_buton.setToolTip(tr.get_text("stop_tooltip"))
        else:
            self.kamera_acma_kapama_buton.setText(tr.get_text("start"))
            self.kamera_acma_kapama_buton.setToolTip(tr.get_text("start_tooltip"))

        # Grupları güncelle
        self.renk_grubu.setTitle(tr.get_text("color_detection"))
        self.gorunum_grubu.setTitle(tr.get_text("display_settings"))
        self.kamera_ayarlari_grubu.setTitle(tr.get_text("camera_settings"))
        self.dil_grubu.setTitle(tr.get_text("language"))
        self.hakkinda_grubu.setTitle(tr.get_text("about"))
        
        # Onay kutularını güncelle
        self.kirmizi_onay_kutu.setText(tr.get_text("detect_red"))
        self.yesil_onay_kutu.setText(tr.get_text("detect_green"))
        self.mavi_onay_kutu.setText(tr.get_text("detect_blue"))
        self.sari_onay_kutu.setText(tr.get_text("detect_yellow"))
        
        # Etiketleri güncelle
        self.algilama_hassasiyet_etiket.setText(tr.get_text("detection_sensitivity"))
        self.kontrast_etiket.setText(tr.get_text("contrast"))
        self.gorunum_modu_etiket.setText(tr.get_text("display_mode"))
        self.kamera_bilgi_etiket.setText(tr.get_text("camera_settings_info"))
        self.hakkinda_etiket.setText(tr.get_text("about_text"))
        self.izin_sifirlama_buton.setText(tr.get_text("reset_camera_permission"))
        
        # İzin durumunu güncelle
        izin_durum_metni = ""
        if self.kamera_izni == "granted":
            izin_durum_metni = tr.get_text("permission_status_granted")
        elif self.kamera_izni == "denied":
            izin_durum_metni = tr.get_text("permission_status_denied")
        else:
            izin_durum_metni = tr.get_text("permission_status_ask")
        self.izin_durum_etiket.setText(f"{tr.get_text('current_permission_status')}: {izin_durum_metni}")
        
        # Durum çubuğunu güncelle
        if not self.kamera_yoneticisi.kamera_acik:
            self.durum_cubugu.showMessage(tr.get_text("ready"))
          # Kamera görüntüsü açık değilse, başlangıç mesajını güncelle
        if not self.kamera_yoneticisi.kamera_acik:
            kamera_arayuzu_olustur(self, self.kamera_besleme_duzen)

    def kamera_iznini_sifirla(self):
        """Kaydedilmiş kamera izinlerini sıfırla"""
        self.kamera_izni = "ask"
        self.ayarlar.setValue("camera_permission", "ask")
        self.durum_cubugu.showMessage(tr.get_text("permission_reset"))
        
        # İzin durumu göstergesini güncelle
        self.izin_durum_etiket.setText(f"{tr.get_text('current_permission_status')}: {tr.get_text('permission_status_ask')}")

    def kamera_izni_verildiginde(self):
        """Kamera izni verildiğinde yapılacaklar"""
        # İzin tercihini kaydet
        if hasattr(self, 'izni_hatirla') and self.izni_hatirla.isChecked():
            self.kamera_izni = "granted"
            self.ayarlar.setValue("camera_permission", "granted")
            # İzin durumu göstergesini güncelle
            self.izin_durum_etiket.setText(f"{tr.get_text('current_permission_status')}: {tr.get_text('permission_status_granted')}")
            
        # Kamera başlatma işlemine devam et
        self.kamera_baslatma_islemi()
    
    def kamera_izni_reddedildiginde(self):
        """Kamera izni reddedildiğinde yapılacaklar"""
        # İzin tercihini kaydet
        if hasattr(self, 'izni_hatirla') and self.izni_hatirla.isChecked():
            self.kamera_izni = "denied"
            self.ayarlar.setValue("camera_permission", "denied")
            # İzin durumu göstergesini güncelle
            self.izin_durum_etiket.setText(f"{tr.get_text('current_permission_status')}: {tr.get_text('permission_status_denied')}")
          # Durum mesajını göster
        self.durum_cubugu.showMessage(tr.get_text("camera_permission_denied"))
        # Başlangıç mesajına dön
        kamera_arayuzu_olustur(self, self.kamera_besleme_duzen)

    def kamera_baslatma_islemi(self):
        """İzin verildikten sonra kamerayı başlat"""
        # Kamera besleme düzenindeki tüm widget'ları temizle
        for i in reversed(range(self.kamera_besleme_duzen.count())): 
            self.kamera_besleme_duzen.itemAt(i).widget().setParent(None)
            
        # Başlatma mesajını göster
        baslatiliyor_etiket = QLabel(tr.get_text("camera_initializing"))
        baslatiliyor_etiket.setStyleSheet("color: white; font-size: 12pt;")
        baslatiliyor_etiket.setAlignment(Qt.AlignCenter)
        self.kamera_besleme_duzen.addWidget(baslatiliyor_etiket)
        QApplication.processEvents()  # UI'ı hemen güncelle
        
        # Şimdi kamerayı başlatmayı dene
        if self.kamera_yoneticisi.kamera_baslat():
            self.zamanlayici.start(33)  # ~30 FPS
            self.durum_cubugu.showMessage(tr.get_text("camera_started"))
            
            # "Durdur" butonu görünümünü güncelle
            self.kamera_acma_kapama_buton.setText(tr.get_text("stop"))
            self.kamera_acma_kapama_buton.setToolTip(tr.get_text("stop_tooltip"))
            self.kamera_acma_kapama_buton.setStyleSheet("""
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
            self.ekran_goruntusu_buton.setVisible(True)
        else:
            self.durum_cubugu.showMessage(tr.get_text("camera_start_failed"))
            kamera_arayuzu_olustur(self, self.kamera_besleme_duzen)  # Kamera başlatılamazsa başlangıç mesajını göster

    def kamerayi_durdur(self):
        """Kamerayı durdur"""
        if self.kamera_yoneticisi.kamera_durdur():
            self.zamanlayici.stop()
              # Başlangıç mesajına dön
            kamera_arayuzu_olustur(self, self.kamera_besleme_duzen)
            
            self.durum_cubugu.showMessage(tr.get_text("camera_stopped"))
            
            # "Başlat" butonu görünümünü güncelle
            self.kamera_acma_kapama_buton.setText(tr.get_text("start"))
            self.kamera_acma_kapama_buton.setToolTip(tr.get_text("start_tooltip"))
            self.kamera_acma_kapama_buton.setStyleSheet("""
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
            self.ekran_goruntusu_buton.setVisible(False)

    def ekran_goruntusu_al(self):
        """Ekran görüntüsü al"""
        basarili, sonuc = self.kamera_yoneticisi.ekran_goruntusu_al()
        if basarili:
            # Dosya yolunu göstermek için dosya adını path'den ayır
            dosya_adi = os.path.basename(sonuc)
            self.durum_cubugu.showMessage(tr.get_text("screenshot_saved", dosya_adi))
        else:
            self.durum_cubugu.showMessage(tr.get_text("screenshot_failed", sonuc))

    def galeri_ac(self):
        """Galeriyi aç"""
        galeri = ScreenshotGallery(self)
        galeri.exec_()

    def kareyi_guncelle(self):
        sonuc, kare = self.kamera_yoneticisi.kare_al()
        if sonuc:
            secili_renkler = {
                'red': self.kirmizi_onay_kutu.isChecked(),
                'green': self.yesil_onay_kutu.isChecked(),
                'blue': self.mavi_onay_kutu.isChecked(),
                'yellow': self.sari_onay_kutu.isChecked()
            }
            
            # Çevrilmiş renk isimleri
            cevrilmis_renk_isimleri = {
                'red': tr.get_text("red"),
                'green': tr.get_text("green"),
                'blue': tr.get_text("blue"),
                'yellow': tr.get_text("yellow")
            }
            
            # Renk detektörü ile kareyi işle
            birlestirilmis_sonuc = self.renk_algilayici.kareyi_isle(
                kare, 
                secili_renkler,
                self.hassasiyet_kaydirici.value(),
                self.kontrast_kaydirici.value(),
                cevrilmis_renk_isimleri
            )
            
            # Sonucu QImage'a çevir ve göster
            y, g, k = birlestirilmis_sonuc.shape
            satir_basina_bayt = 3 * g
            qImg = QImage(birlestirilmis_sonuc.data, g, y, satir_basina_bayt, QImage.Format_RGB888).rgbSwapped()
            
            # Tüm mevcut widget'ları temizle
            for i in reversed(range(self.kamera_besleme_duzen.count())): 
                self.kamera_besleme_duzen.itemAt(i).widget().setParent(None)
                
            # Resim etiketini oluştur ve ekle
            resim_etiket = QLabel()
            resim_etiket.setPixmap(QPixmap.fromImage(qImg).scaled(
                self.kamera_besleme_konteyner.width() - 40,  # Kenar boşluklarını hesaba kat
                self.kamera_besleme_konteyner.height() - 40, 
                Qt.KeepAspectRatio
            ))
            resim_etiket.setAlignment(Qt.AlignCenter)
            self.kamera_besleme_duzen.addWidget(resim_etiket)
    
    def kamerayi_ac_kapat(self):
        """Kamerayı açıp kapatma"""
        if self.kamera_yoneticisi.kamera_acik:
            self.kamerayi_durdur()
        else:
            self.kamerayi_baslat()
            
    def kamerayi_baslat(self):
        """İzinleri kontrol ettikten sonra kamerayı başlat"""
        if not self.kamera_yoneticisi.kamera_acik:
            # Kaydedilmiş izin tercihini kontrol et
            if self.kamera_izni == "granted":
                # İzin zaten verildi, kamerayı doğrudan başlat
                self.kamera_baslatma_islemi()
            elif self.kamera_izni == "denied":                # İzin zaten reddedildi
                self.durum_cubugu.showMessage(tr.get_text("camera_permission_denied"))
            else:
                # İzin sor
                kamera_izin_arayuzunu_goster(
                    self, 
                    self.kamera_besleme_duzen,
                    self.kamera_izni_verildiginde,
                    self.kamera_izni_reddedildiginde
                )
