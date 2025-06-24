import os
from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                           QWidget, QSlider, QCheckBox, QGroupBox, QGridLayout, QComboBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

# Paketin kendi modüllerini import et
from .translations import translator as tr

def buton_olustur(metin, ipucu, stil_sinifi="default", callback=None):
    """Standart stilli buton oluştur"""
    buton = QPushButton(metin)
    buton.setToolTip(ipucu)
    
    stil_sozlugu = {
        "default": """
            QPushButton {
                background-color: #555;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #777;
                border: 1px solid #999;
            }
            QPushButton:pressed {
                background-color: #444;
            }
        """,
        "start": """
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
        """,
        "stop": """
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
        """,
        "snapshot": """
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #42A5F5;
                border: 2px solid #64B5F6;
            }
            QPushButton:pressed {
                background-color: #1E88E5;
            }
        """,
        "gallery": """
            QPushButton {
                background-color: #9C27B0;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #AB47BC;
                border: 2px solid #BA68C8;
            }
            QPushButton:pressed {
                background-color: #8E24AA;
            }
        """
    }
    
    buton.setStyleSheet(stil_sozlugu.get(stil_sinifi, stil_sozlugu["default"]))
    
    if callback:
        buton.clicked.connect(callback)
    
    return buton

def kamera_kontrolleri_olustur(ebeveyn):
    """Kamera kontrol butonlarını oluştur"""
    buton_duzen = QHBoxLayout()
    
    # Kamera aç/kapa butonu
    kamera_acma_kapama_buton = buton_olustur(
        tr.get_text("start"), 
        tr.get_text("start_tooltip"),
        "start",
        ebeveyn.kamerayi_ac_kapat
    )
    ebeveyn.kamera_acma_kapama_buton = kamera_acma_kapama_buton
    
    # Ekran görüntüsü ve galeri butonları
    ekran_goruntusu_buton = buton_olustur(
        tr.get_text("take_screenshot"),
        tr.get_text("snapshot_tooltip"),
        "snapshot",
        ebeveyn.ekran_goruntusu_al
    )
    # Kamera kapalıyken görünmez yap
    ekran_goruntusu_buton.setVisible(ebeveyn.kamera_yoneticisi.kamera_acik)
    ebeveyn.ekran_goruntusu_buton = ekran_goruntusu_buton
    
    galeri_buton = buton_olustur(
        tr.get_text("gallery"),
        tr.get_text("gallery_tooltip"),
        "gallery",
        ebeveyn.galeri_ac
    )
    ebeveyn.galeri_buton = galeri_buton
    
    buton_duzen.addWidget(kamera_acma_kapama_buton)
    buton_duzen.addWidget(ekran_goruntusu_buton)
    buton_duzen.addWidget(galeri_buton)
    
    return buton_duzen

def renk_algilama_grubu_olustur(ebeveyn):
    """Renk algılama ayarları grubu oluştur"""
    renk_grubu = QGroupBox(tr.get_text("color_detection"))
    renk_duzen = QVBoxLayout()
    
    ebeveyn.kirmizi_onay_kutu = QCheckBox(tr.get_text("detect_red"))
    ebeveyn.yesil_onay_kutu = QCheckBox(tr.get_text("detect_green"))
    ebeveyn.mavi_onay_kutu = QCheckBox(tr.get_text("detect_blue"))
    ebeveyn.sari_onay_kutu = QCheckBox(tr.get_text("detect_yellow"))
    
    # Varsayılan seçili renkler
    ebeveyn.kirmizi_onay_kutu.setChecked(True)
    ebeveyn.yesil_onay_kutu.setChecked(True)
    
    # İpuçları
    ebeveyn.kirmizi_onay_kutu.setToolTip(tr.get_text("red_checkbox_tooltip"))
    ebeveyn.yesil_onay_kutu.setToolTip(tr.get_text("green_checkbox_tooltip"))
    ebeveyn.mavi_onay_kutu.setToolTip(tr.get_text("blue_checkbox_tooltip"))
    ebeveyn.sari_onay_kutu.setToolTip(tr.get_text("yellow_checkbox_tooltip"))
    
    # Düzene ekle
    renk_duzen.addWidget(ebeveyn.kirmizi_onay_kutu)
    renk_duzen.addWidget(ebeveyn.yesil_onay_kutu)
    renk_duzen.addWidget(ebeveyn.mavi_onay_kutu)
    renk_duzen.addWidget(ebeveyn.sari_onay_kutu)
    renk_grubu.setLayout(renk_duzen)
    
    return renk_grubu

def gorunum_ayarlari_grubu_olustur(ebeveyn):
    """Görüntüleme ayarları grubu oluştur"""
    gorunum_grubu = QGroupBox(tr.get_text("display_settings"))
    gorunum_duzen = QGridLayout()
    
    # Duyarlılık ayarı
    ebeveyn.algilama_hassasiyet_etiket = QLabel(tr.get_text("detection_sensitivity"))
    gorunum_duzen.addWidget(ebeveyn.algilama_hassasiyet_etiket, 0, 0)
    ebeveyn.hassasiyet_kaydirici = QSlider(Qt.Horizontal)
    ebeveyn.hassasiyet_kaydirici.setRange(1, 10)
    ebeveyn.hassasiyet_kaydirici.setValue(5)
    ebeveyn.hassasiyet_kaydirici.setToolTip(tr.get_text("sensitivity_tooltip"))
    gorunum_duzen.addWidget(ebeveyn.hassasiyet_kaydirici, 0, 1)
    
    # Kontrast ayarı
    ebeveyn.kontrast_etiket = QLabel(tr.get_text("contrast"))
    gorunum_duzen.addWidget(ebeveyn.kontrast_etiket, 1, 0)
    ebeveyn.kontrast_kaydirici = QSlider(Qt.Horizontal)
    ebeveyn.kontrast_kaydirici.setRange(1, 10)
    ebeveyn.kontrast_kaydirici.setValue(5)
    ebeveyn.kontrast_kaydirici.setToolTip(tr.get_text("contrast_tooltip"))
    gorunum_duzen.addWidget(ebeveyn.kontrast_kaydirici, 1, 1)
    
    # Görüntü modu
    ebeveyn.gorunum_modu_etiket = QLabel(tr.get_text("display_mode"))
    gorunum_duzen.addWidget(ebeveyn.gorunum_modu_etiket, 2, 0)
    ebeveyn.gorunum_modu = QComboBox()
    ebeveyn.gorunum_modu.addItems(["Normal", "Deuteranopia", "Protanopia", "Tritanopia"])
    ebeveyn.gorunum_modu.setToolTip(tr.get_text("display_mode_tooltip"))
    gorunum_duzen.addWidget(ebeveyn.gorunum_modu, 2, 1)
    
    gorunum_grubu.setLayout(gorunum_duzen)
    
    return gorunum_grubu

def kamera_ayarlari_grubu_olustur(ebeveyn):
    """Kamera ayarları grubu oluştur"""
    kamera_ayarlari_grubu = QGroupBox(tr.get_text("camera_settings"))
    kamera_duzen = QVBoxLayout()
    
    # Kamera izinleri hakkında bilgi
    ebeveyn.kamera_bilgi_etiket = QLabel(tr.get_text("camera_settings_info"))
    ebeveyn.kamera_bilgi_etiket.setWordWrap(True)
    ebeveyn.kamera_bilgi_etiket.setStyleSheet("color: #CCC; font-size: 9pt;")
    kamera_duzen.addWidget(ebeveyn.kamera_bilgi_etiket)
    
    # Mevcut izin durumunu göster
    izin_durum_metni = ""
    if ebeveyn.kamera_izni == "granted":
        izin_durum_metni = tr.get_text("permission_status_granted")
    elif ebeveyn.kamera_izni == "denied":
        izin_durum_metni = tr.get_text("permission_status_denied")
    else:
        izin_durum_metni = tr.get_text("permission_status_ask")
        
    ebeveyn.izin_durum_etiket = QLabel(f"{tr.get_text('current_permission_status')}: {izin_durum_metni}")
    ebeveyn.izin_durum_etiket.setStyleSheet("color: #2196F3; margin-top: 8px;")
    kamera_duzen.addWidget(ebeveyn.izin_durum_etiket)
    
    # Kamera izinlerini sıfırlama butonu
    izin_sifirlama_buton = QPushButton(tr.get_text("reset_camera_permission"))
    izin_sifirlama_buton.setStyleSheet("""
        QPushButton {
            background-color: #555;
            color: white;
            padding: 8px;
            border-radius: 5px;
            text-align: left;
            padding-left: 30px;
        }
        QPushButton:hover {
            background-color: #777;
            border: 1px solid #999;
        }
        QPushButton:pressed {
            background-color: #444;
        }
    """)
    
    # Butona ikon ekle - ikon yolunu güncelle
    sifirlama_ikon_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'reset_icon.png')
    if os.path.exists(sifirlama_ikon_yolu):
        izin_sifirlama_buton.setIcon(QIcon(sifirlama_ikon_yolu))
    
    izin_sifirlama_buton.clicked.connect(ebeveyn.kamera_iznini_sifirla)
    ebeveyn.izin_sifirlama_buton = izin_sifirlama_buton
    kamera_duzen.addWidget(izin_sifirlama_buton)
    
    kamera_ayarlari_grubu.setLayout(kamera_duzen)
    
    return kamera_ayarlari_grubu

def dil_grubu_olustur(ebeveyn):
    """Dil ayarları grubu oluştur"""
    dil_grubu = QGroupBox(tr.get_text("language"))
    dil_duzen = QVBoxLayout()
    
    # Dil seçimi
    ebeveyn.dil_combo = QComboBox()
    for kod, ad in tr.LANGUAGES.items():
        ebeveyn.dil_combo.addItem(ad, kod)
    
    # Mevcut dili ayarla
    mevcut_indeks = 0
    dil = ebeveyn.ayarlar.value("language", "en")
    for i in range(ebeveyn.dil_combo.count()):
        if ebeveyn.dil_combo.itemData(i) == dil:
            mevcut_indeks = i
            break
    ebeveyn.dil_combo.setCurrentIndex(mevcut_indeks)
    ebeveyn.dil_combo.currentIndexChanged.connect(ebeveyn.dil_degistir)
    
    dil_duzen.addWidget(ebeveyn.dil_combo)
    dil_grubu.setLayout(dil_duzen)
    
    return dil_grubu

def hakkinda_grubu_olustur(ebeveyn):
    """Hakkında bölümü grubu oluştur"""
    hakkinda_grubu = QGroupBox(tr.get_text("about"))
    hakkinda_duzen = QVBoxLayout()
    
    ebeveyn.hakkinda_etiket = QLabel(tr.get_text("about_text"))
    ebeveyn.hakkinda_etiket.setAlignment(Qt.AlignCenter)
    hakkinda_duzen.addWidget(ebeveyn.hakkinda_etiket)
    hakkinda_grubu.setLayout(hakkinda_duzen)
    
    return hakkinda_grubu

def koyu_tema_uygula(widget):
    """Koyu tema stilini uygula"""
    widget.setStyleSheet("""
        QMainWindow {
            background-color: #333;
        }
        QLabel, QCheckBox, QGroupBox, QPushButton {
            color: #EEE;
            font-size: 10pt;
        }
        QCheckBox:hover {
            color: #2196F3;
        }
        QGroupBox {
            border: 2px solid #555;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: #444;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            padding: 0 5px;
            color: #2196F3;
        }
        QGroupBox:hover {
            border: 2px solid #2196F3;
        }
        QSlider::groove:horizontal {
            height: 8px;
            background: #333;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #2196F3;
            border: 1px solid #2196F3;
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }
        QSlider::handle:horizontal:hover {
            background: #64B5F6;
            border: 1px solid #90CAF9;
            width: 20px;
            margin: -3px 0;
        }
        QComboBox {
            background-color: #555;
            color: white;
            padding: 5px;
            border-radius: 3px;
        }
        QComboBox:hover {
            background-color: #666;
            border: 1px solid #2196F3;
        }
        QToolTip {
            background-color: #444;
            color: white;
            border: 1px solid #2196F3;
            padding: 2px;
            border-radius: 3px;
            opacity: 200;
        }
    """)
