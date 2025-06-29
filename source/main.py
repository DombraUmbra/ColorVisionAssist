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
from .ui_components import (kamera_kontrolleri_olustur, renk_korlugu_turu_grubu_olustur,
                          kamera_ayarlari_grubu_olustur,
                          dil_grubu_olustur, hakkinda_grubu_olustur, koyu_tema_uygula, GelismisAyarlarDialog)

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
        # Responsive genişlik - Ekran boyutuna göre ayarla
        from PyQt5.QtWidgets import QApplication
        ekran = QApplication.desktop().screenGeometry()
        min_genislik = min(280, max(250, int(ekran.width() * 0.25)))
        max_genislik = min(350, int(ekran.width() * 0.35))
        
        self.ayarlar_paneli.setMinimumWidth(min_genislik)
        self.ayarlar_paneli.setMaximumWidth(max_genislik)
        
        self.ayarlar_duzen = QVBoxLayout(self.ayarlar_paneli)
        self.ayarlar_duzen.setSpacing(8)
        self.ayarlar_duzen.setContentsMargins(5, 5, 5, 5)
          # UI Components modülünden grupları oluştur
        self.renk_korlugu_grubu = renk_korlugu_turu_grubu_olustur(self)
        self.kamera_ayarlari_grubu = kamera_ayarlari_grubu_olustur(self)
        self.dil_grubu = dil_grubu_olustur(self)
        self.hakkinda_grubu = hakkinda_grubu_olustur(self)
        
        # Ayar gruplarını panele ekle
        self.ayarlar_duzen.addWidget(self.renk_korlugu_grubu)
        self.ayarlar_duzen.addWidget(self.kamera_ayarlari_grubu)
        self.ayarlar_duzen.addWidget(self.dil_grubu)
        self.ayarlar_duzen.addWidget(self.hakkinda_grubu)
        self.ayarlar_duzen.addStretch()
        
        # Varsayılan renk seçimi checkbox'ları (gelişmiş ayarlar için)
        # Bu checkbox'lar sadece gelişmiş ayarlarda görünür olacak
        from PyQt5.QtWidgets import QCheckBox
        self.kirmizi_onay_kutu = QCheckBox(tr.get_text("detect_red"))
        self.yesil_onay_kutu = QCheckBox(tr.get_text("detect_green"))
        self.mavi_onay_kutu = QCheckBox(tr.get_text("detect_blue"))
        self.sari_onay_kutu = QCheckBox(tr.get_text("detect_yellow"))
        
        # Varsayılan seçili renkler (Kırmızı-Yeşil renk körlüğü)
        self.kirmizi_onay_kutu.setChecked(True)
        self.yesil_onay_kutu.setChecked(True)
        
        # Filtreleme ayarları
        self.ten_rengi_filtreleme_aktif = True  # Ten rengi filtreleme varsayılan aktif
        self.kararlilik_gelistirme_aktif = True  # Kararlılık geliştirme varsayılan aktif
        
        # Hassasiyet ve kontrast değerleri için varsayılan değerler (gelişmiş ayarlarda kullanılacak)
        self.hassasiyet_degeri = 5
        self.kontrast_degeri = 5
        
        # Gelişmiş ayarlar için gizli slider (sadece değer tutmak için)
        from PyQt5.QtWidgets import QSlider
        self.hassasiyet_kaydirici = QSlider(Qt.Horizontal)
        self.hassasiyet_kaydirici.setRange(1, 10)
        self.hassasiyet_kaydirici.setValue(5)
        self.hassasiyet_kaydirici.setVisible(False)  # Görünmez

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

        # Grupları güncelle (yeni UI yapısı)
        self.renk_korlugu_grubu.setTitle(tr.get_text("color_blindness_type"))
        self.kamera_ayarlari_grubu.setTitle(tr.get_text("camera_settings"))
        self.dil_grubu.setTitle(tr.get_text("language"))
        self.hakkinda_grubu.setTitle(tr.get_text("about"))
        
        # Renk körlüğü combo box'ını güncelle
        self.renk_korlugu_combo.clear()
        self.renk_korlugu_combo.addItem(tr.get_text("red_green_colorblind"), "red_green")
        self.renk_korlugu_combo.addItem(tr.get_text("blue_yellow_colorblind"), "blue_yellow")
        self.renk_korlugu_combo.addItem(tr.get_text("protanopia"), "protanopia")
        self.renk_korlugu_combo.addItem(tr.get_text("deuteranopia"), "deuteranopia")
        self.renk_korlugu_combo.addItem(tr.get_text("tritanopia"), "tritanopia")
        self.renk_korlugu_combo.addItem(tr.get_text("complete_colorblind"), "complete")
        self.renk_korlugu_combo.addItem(tr.get_text("custom_colors"), "custom")
        
        # Gelişmiş ayarlar butonunu güncelle
        self.gelismis_ayarlar_buton.setText(tr.get_text("advanced_settings"))
        
        # Onay kutularını güncelle (sadece dahili kullanım için)
        self.kirmizi_onay_kutu.setText(tr.get_text("detect_red"))
        self.yesil_onay_kutu.setText(tr.get_text("detect_green"))
        self.mavi_onay_kutu.setText(tr.get_text("detect_blue"))
        self.sari_onay_kutu.setText(tr.get_text("detect_yellow"))
        
        # Etiketleri güncelle
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
                'skin': True,  # Ten rengi arkaplanda çalışır (görünmez)
                'red': self.kirmizi_onay_kutu.isChecked(),
                'green': self.yesil_onay_kutu.isChecked(),
                'blue': self.mavi_onay_kutu.isChecked(),
                'yellow': self.sari_onay_kutu.isChecked()
            }
            
            # Çevrilmiş renk isimleri (ten rengi dahil değil - görünmez)
            cevrilmis_renk_isimleri = {
                'red': tr.get_text("red"),
                'green': tr.get_text("green"),
                'blue': tr.get_text("blue"),
                'yellow': tr.get_text("yellow")
            }
            
            # Renk körlüğü türünü al
            renk_korlugu_turu = self.renk_korlugu_combo.currentData() or 'red_green'
            
            # Renk detektörü ile kareyi işle
            birlestirilmis_sonuc = self.renk_algilayici.kareyi_isle(
                kare, 
                secili_renkler,
                self.hassasiyet_kaydirici.value(),
                self.kontrast_degeri,  # Sabit kontrast değeri kullan
                cevrilmis_renk_isimleri,
                self.ten_rengi_filtreleme_aktif,
                self.kararlilik_gelistirme_aktif,
                renk_korlugu_turu  # Renk körlüğü türünü gönder
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

    def renk_korlugu_turu_degisti(self, indeks):
        """Renk körlüğü türü değiştiğinde otomatik renk seçimi"""
        tür_kodu = self.renk_korlugu_combo.itemData(indeks)
        
        # Tüm renkleri önce kapat
        self.kirmizi_onay_kutu.setChecked(False)
        self.yesil_onay_kutu.setChecked(False)
        self.mavi_onay_kutu.setChecked(False)
        self.sari_onay_kutu.setChecked(False)
        
        # Seçilen türe göre uygun renkleri aç
        if tür_kodu == "red_green":
            # Kırmızı-Yeşil renk körlüğü
            self.kirmizi_onay_kutu.setChecked(True)
            self.yesil_onay_kutu.setChecked(True)
        elif tür_kodu == "blue_yellow":
            # Mavi-Sarı renk körlüğü
            self.mavi_onay_kutu.setChecked(True)
            self.sari_onay_kutu.setChecked(True)
        elif tür_kodu == "protanopia":
            # Protanopi (Kırmızı körlüğü) - Kırmızı ve yeşil ayrımı zor
            self.kirmizi_onay_kutu.setChecked(True)
            self.yesil_onay_kutu.setChecked(True)
            self.mavi_onay_kutu.setChecked(True)  # Mavi net görülür
        elif tür_kodu == "deuteranopia":
            # Deuteranopi (Yeşil körlüğü) - Kırmızı ve yeşil ayrımı zor
            self.kirmizi_onay_kutu.setChecked(True)
            self.yesil_onay_kutu.setChecked(True)
            self.mavi_onay_kutu.setChecked(True)  # Mavi net görülür
        elif tür_kodu == "tritanopia":
            # Tritanopi (Mavi körlüğü) - Mavi ve sarı ayrımı zor
            self.mavi_onay_kutu.setChecked(True)
            self.sari_onay_kutu.setChecked(True)
            self.kirmizi_onay_kutu.setChecked(True)  # Kırmızı net görülür
        elif tür_kodu == "complete":
            # Tam renk körlüğü - Tüm renkler
            self.kirmizi_onay_kutu.setChecked(True)
            self.yesil_onay_kutu.setChecked(True)
            self.mavi_onay_kutu.setChecked(True)
            self.sari_onay_kutu.setChecked(True)
        elif tür_kodu == "custom":
            # Özel renk seçimi - Gelişmiş ayarları aç
            self.gelismis_ayarlar_ac()

    def gelismis_ayarlar_ac(self):
        """Gelişmiş ayarlar dialog'unu aç"""
        dialog = GelismisAyarlarDialog(self)
        dialog.exec_()
