import os
from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                           QWidget, QSlider, QCheckBox, QGroupBox, QGridLayout, QComboBox, QDialog, QTabWidget)
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
                padding: 8px 6px;
                border-radius: 5px;
                font-size: 9pt;
                min-height: 25px;
                text-align: center;
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
        """,
        "stop": """
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
        """,
        "snapshot": """
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 6px;
                border-radius: 5px;
                font-size: 9pt;
                min-height: 25px;
                text-align: center;
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
                padding: 8px 6px;
                border-radius: 5px;
                font-size: 9pt;
                min-height: 25px;
                text-align: center;
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

def renk_korlugu_turu_grubu_olustur(ebeveyn):
    """Renk körlüğü türü seçimi grubu oluştur"""
    renk_korlugu_grubu = QGroupBox(tr.get_text("color_blindness_type"))
    renk_korlugu_duzen = QVBoxLayout()
    renk_korlugu_duzen.setSpacing(10)
    
    # Renk körlüğü türü seçimi
    ebeveyn.renk_korlugu_combo = QComboBox()
    ebeveyn.renk_korlugu_combo.addItem(tr.get_text("red_green_colorblind"), "red_green")
    ebeveyn.renk_korlugu_combo.addItem(tr.get_text("blue_yellow_colorblind"), "blue_yellow")
    ebeveyn.renk_korlugu_combo.addItem(tr.get_text("protanopia"), "protanopia")
    ebeveyn.renk_korlugu_combo.addItem(tr.get_text("deuteranopia"), "deuteranopia")
    ebeveyn.renk_korlugu_combo.addItem(tr.get_text("tritanopia"), "tritanopia")
    ebeveyn.renk_korlugu_combo.addItem(tr.get_text("complete_colorblind"), "complete")
    ebeveyn.renk_korlugu_combo.addItem(tr.get_text("custom_colors"), "custom")
    
    # Özel ComboBox stili
    ebeveyn.renk_korlugu_combo.setStyleSheet("""
        QComboBox {
            background-color: #555;
            color: white;
            padding: 6px 8px;
            border-radius: 3px;
            font-size: 9pt;
            min-height: 22px;
            border: 1px solid #666;
        }
        QComboBox:hover {
            background-color: #666;
            border: 1px solid #2196F3;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: #666;
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
            background-color: #555;
        }
        QComboBox::down-arrow {
            width: 8px;
            height: 8px;
            margin: 2px;
        }
        QComboBox QAbstractItemView {
            background-color: #555;
            color: white;
            selection-background-color: #2196F3;
            border: 1px solid #666;
            outline: none;
        }
    """)
    
    ebeveyn.renk_korlugu_combo.setToolTip(tr.get_text("color_blindness_type_tooltip"))
    ebeveyn.renk_korlugu_combo.currentIndexChanged.connect(ebeveyn.renk_korlugu_turu_degisti)
    
    renk_korlugu_duzen.addWidget(ebeveyn.renk_korlugu_combo)
    
    # Gelişmiş ayarlar butonu
    ebeveyn.gelismis_ayarlar_buton = buton_olustur(
        tr.get_text("advanced_settings"),
        tr.get_text("advanced_settings_tooltip"),
        "default",
        ebeveyn.gelismis_ayarlar_ac
    )
    
    renk_korlugu_duzen.addWidget(ebeveyn.gelismis_ayarlar_buton)
    renk_korlugu_grubu.setLayout(renk_korlugu_duzen)
    
    return renk_korlugu_grubu
def renk_algilama_grubu_olustur(ebeveyn):
    """Renk algılama ayarları grubu oluştur (Gelişmiş ayarlar için)"""
    renk_grubu = QGroupBox(tr.get_text("manual_color_selection"))
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

def kamera_ayarlari_grubu_olustur(ebeveyn):
    """Kamera ayarları grubu oluştur"""
    kamera_ayarlari_grubu = QGroupBox(tr.get_text("camera_settings"))
    kamera_duzen = QVBoxLayout()
    kamera_duzen.setSpacing(8)
    
    # Kamera izinleri hakkında bilgi
    ebeveyn.kamera_bilgi_etiket = QLabel(tr.get_text("camera_settings_info"))
    ebeveyn.kamera_bilgi_etiket.setWordWrap(True)
    ebeveyn.kamera_bilgi_etiket.setStyleSheet("""
        QLabel {
            color: #CCC; 
            font-size: 9pt; 
            padding: 10px;
            line-height: 1.5;
            background-color: #3A3A3A;
            border-radius: 5px;
            border-left: 3px solid #64B5F6;
            max-height: 80px;
        }
    """)
    ebeveyn.kamera_bilgi_etiket.setMinimumHeight(60)
    ebeveyn.kamera_bilgi_etiket.setMaximumHeight(100)
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
    ebeveyn.izin_durum_etiket.setWordWrap(True)
    ebeveyn.izin_durum_etiket.setStyleSheet("""
        color: #2196F3; 
        font-size: 9pt;
        font-weight: bold;
        margin-top: 8px;
        padding: 4px;
    """)
    kamera_duzen.addWidget(ebeveyn.izin_durum_etiket)
    
    # Kamera izinlerini sıfırlama butonu
    izin_sifirlama_buton = QPushButton(tr.get_text("reset_camera_permission"))
    izin_sifirlama_buton.setStyleSheet("""
        QPushButton {
            background-color: #555;
            color: white;
            padding: 8px 10px;
            border-radius: 5px;
            text-align: center;
            font-size: 9pt;
            min-height: 25px;
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
    hakkinda_duzen.setContentsMargins(10, 10, 10, 10)
    
    ebeveyn.hakkinda_etiket = QLabel(tr.get_text("about_text"))
    ebeveyn.hakkinda_etiket.setAlignment(Qt.AlignCenter)
    ebeveyn.hakkinda_etiket.setWordWrap(True)
    ebeveyn.hakkinda_etiket.setStyleSheet("""
        QLabel {
            font-size: 9pt;
            line-height: 1.4;
            padding: 8px;
            color: #CCC;
        }
    """)
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
            font-size: 9pt;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            padding: 0 5px;
            color: #2196F3;
            font-size: 10pt;
            font-weight: bold;
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
            font-size: 9pt;
            min-height: 20px;
            border: 1px solid #666;
        }
        QComboBox:hover {
            background-color: #666;
            border: 1px solid #2196F3;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: #666;
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
            background-color: #555;
        }
        QComboBox::down-arrow {
            width: 10px;
            height: 10px;
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #666, stop: 1 #333);
        }
        QComboBox QAbstractItemView {
            background-color: #555;
            color: white;
            selection-background-color: #2196F3;
            border: 1px solid #666;
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

class GelismisAyarlarDialog(QDialog):
    """Gelişmiş ayarlar dialog'u - Ana uygulama ile uyumlu tasarım"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(tr.get_text("advanced_settings"))
        self.setModal(True)
        
        # Responsive boyutlandırma - Ekran boyutuna göre uyum
        from PyQt5.QtWidgets import QApplication
        ekran = QApplication.desktop().screenGeometry()
        genislik = min(max(650, int(ekran.width() * 0.65)), 900)
        yukseklik = min(max(700, int(ekran.height() * 0.75)), 950)
        
        self.setMinimumSize(genislik, yukseklik)
        self.setMaximumSize(genislik + 150, yukseklik + 150)
        self.resize(genislik, yukseklik)
        
        # Dialog'un checkbox'larını başlat
        self.kirmizi_onay_kutu = None
        self.yesil_onay_kutu = None
        self.mavi_onay_kutu = None
        self.sari_onay_kutu = None
        
        self.kurulum()
        
    def kurulum(self):
        """Dialog layout'unu kur - Ana uygulama temayla uyumlu"""
        ana_duzen = QVBoxLayout(self)
        ana_duzen.setSpacing(12)
        ana_duzen.setContentsMargins(20, 20, 20, 20)
        
        # Tab widget oluştur - Ana tema ile uyumlu
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #555;
                border-radius: 5px;
                background-color: #444;
                padding: 10px;
                margin-top: 5px;
            }
            QTabBar::tab {
                background-color: #555;
                color: #EEE;
                padding: 12px 14px;
                margin: 1px;
                border-radius: 3px;
                font-size: 9pt;
                min-width: 70px;
                max-width: 120px;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background-color: #666;
            }
        """)
        
        # Renk seçimi sekmesi
        renk_sekmesi = self.renk_sekmesi_olustur()
        tab_widget.addTab(renk_sekmesi, tr.get_text("color_selection_short"))
        
        # Algılama parametreleri sekmesi
        parametre_sekmesi = self.parametre_sekmesi_olustur()
        tab_widget.addTab(parametre_sekmesi, tr.get_text("parameters_short"))
        
        # Filtreleme sekmesi
        filtreleme_sekmesi = self.filtreleme_sekmesi_olustur()
        tab_widget.addTab(filtreleme_sekmesi, tr.get_text("filtering_short"))
        
        ana_duzen.addWidget(tab_widget)
        
        # Butonlar - Ana uygulama buton stili
        buton_duzen = self.buton_duzen_olustur()
        ana_duzen.addLayout(buton_duzen)
        
        # Ana tema uygula - Dialog için özel stil
        self.dialog_teması_uygula()
        
    def dialog_teması_uygula(self):
        """Dialog için ana tema uygulaması"""
        self.setStyleSheet("""
            QDialog {
                background-color: #333;
                color: #EEE;
            }
            QWidget {
                background-color: #333;
                color: #EEE;
            }
            QScrollArea {
                background-color: #333;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #333;
            }
        """)
        
    def renk_sekmesi_olustur(self):
        """Renk seçimi sekmesini oluştur - Ana tema uyumlu"""
        renk_sekmesi = QWidget()
        renk_duzen = QVBoxLayout(renk_sekmesi)
        renk_duzen.setSpacing(12)
        renk_duzen.setContentsMargins(10, 10, 10, 10)
        
        # Açıklama - Ana uygulama stili
        aciklama = QLabel(tr.get_text("manual_color_selection_desc"))
        aciklama.setWordWrap(True)
        aciklama.setStyleSheet("""
            QLabel {
                color: #CCC;
                font-size: 9pt;
                padding: 10px;
                background-color: #3A3A3A;
                border-radius: 5px;
                border-left: 4px solid #2196F3;
                line-height: 1.4;
            }
        """)
        renk_duzen.addWidget(aciklama)
        
        # Renk seçimi grubu - Ana uygulama GroupBox stili
        renk_grubu = QGroupBox(tr.get_text("select_colors_to_detect"))
        renk_grubu.setStyleSheet("""
            QGroupBox {
                color: #EEE;
                font-size: 10pt;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: #444;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 8px;
                color: #2196F3;
                font-size: 10pt;
                font-weight: bold;
            }
            QGroupBox:hover {
                border: 2px solid #2196F3;
            }
        """)
        
        renk_duzen_ic = QVBoxLayout()
        renk_duzen_ic.setSpacing(10)
        renk_duzen_ic.setContentsMargins(15, 10, 15, 15)
        
        # Checkbox'ları oluştur - Ana uygulama stili
        self.kirmizi_onay_kutu = QCheckBox(tr.get_text("detect_red"))
        self.yesil_onay_kutu = QCheckBox(tr.get_text("detect_green"))
        self.mavi_onay_kutu = QCheckBox(tr.get_text("detect_blue"))
        self.sari_onay_kutu = QCheckBox(tr.get_text("detect_yellow"))
        
        # Ana pencereden değerleri al
        self.kirmizi_onay_kutu.setChecked(self.parent.kirmizi_onay_kutu.isChecked())
        self.yesil_onay_kutu.setChecked(self.parent.yesil_onay_kutu.isChecked())
        self.mavi_onay_kutu.setChecked(self.parent.mavi_onay_kutu.isChecked())
        self.sari_onay_kutu.setChecked(self.parent.sari_onay_kutu.isChecked())
        
        # Ana uygulama checkbox stili
        checkbox_stil = """
            QCheckBox {
                color: #EEE;
                font-size: 10pt;
                spacing: 10px;
                padding: 8px;
                background-color: #3A3A3A;
                border-radius: 4px;
                margin: 2px 0;
            }
            QCheckBox:hover {
                color: #2196F3;
                background-color: #454545;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid #666;
                background-color: #333;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border: 2px solid #2196F3;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #64B5F6;
            }
        """
        
        for checkbox in [self.kirmizi_onay_kutu, self.yesil_onay_kutu, self.mavi_onay_kutu, self.sari_onay_kutu]:
            checkbox.setStyleSheet(checkbox_stil)
        
        # İpuçları
        self.kirmizi_onay_kutu.setToolTip(tr.get_text("red_checkbox_tooltip"))
        self.yesil_onay_kutu.setToolTip(tr.get_text("green_checkbox_tooltip"))
        self.mavi_onay_kutu.setToolTip(tr.get_text("blue_checkbox_tooltip"))
        self.sari_onay_kutu.setToolTip(tr.get_text("yellow_checkbox_tooltip"))
        
        # Checkbox'ları ekle
        renk_duzen_ic.addWidget(self.kirmizi_onay_kutu)
        renk_duzen_ic.addWidget(self.yesil_onay_kutu)
        renk_duzen_ic.addWidget(self.mavi_onay_kutu)
        renk_duzen_ic.addWidget(self.sari_onay_kutu)
        
        renk_grubu.setLayout(renk_duzen_ic)
        renk_duzen.addWidget(renk_grubu)
        
        renk_duzen.addStretch()
        return renk_sekmesi
    
    def parametre_sekmesi_olustur(self):
        """Algılama parametreleri sekmesini oluştur - Ana tema uyumlu"""
        parametre_sekmesi = QWidget()
        parametre_duzen = QVBoxLayout(parametre_sekmesi)
        parametre_duzen.setSpacing(15)
        
        # Açıklama
        aciklama = QLabel(tr.get_text("detection_parameters_desc"))
        aciklama.setWordWrap(True)
        aciklama.setStyleSheet("""
            QLabel {
                color: #CCC;
                font-size: 9pt;
                padding: 8px;
                background-color: #3A3A3A;
                border-radius: 3px;
                border-left: 3px solid #2196F3;
            }
        """)
        parametre_duzen.addWidget(aciklama)
        
        # Hassasiyet grubu - Ana uygulama stili
        hassasiyet_grubu = QGroupBox(tr.get_text("real_world_sensitivity"))
        hassasiyet_grubu.setStyleSheet("""
            QGroupBox {
                color: #EEE;
                font-size: 10pt;
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
        """)
        
        hassasiyet_duzen = QVBoxLayout()
        
        # Hassasiyet slider'ı - Ana uygulama stili
        slider_duzen = QHBoxLayout()
        
        self.hassasiyet_kaydirici = QSlider(Qt.Horizontal)
        self.hassasiyet_kaydirici.setRange(1, 10)
        self.hassasiyet_kaydirici.setValue(self.parent.hassasiyet_kaydirici.value())
        
        # Ana uygulama slider stili
        self.hassasiyet_kaydirici.setStyleSheet("""
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
        """)
        
        slider_duzen.addWidget(self.hassasiyet_kaydirici)
        
        # Değer etiketi
        self.hassasiyet_deger_etiket = QLabel(str(self.hassasiyet_kaydirici.value()))
        self.hassasiyet_deger_etiket.setStyleSheet("""
            QLabel {
                color: #2196F3;
                font-size: 12pt;
                font-weight: bold;
                padding: 2px 8px;
                background-color: #555;
                border-radius: 3px;
                min-width: 20px;
            }
        """)
        self.hassasiyet_deger_etiket.setAlignment(Qt.AlignCenter)
        slider_duzen.addWidget(self.hassasiyet_deger_etiket)
        
        self.hassasiyet_kaydirici.valueChanged.connect(self.hassasiyet_degisti)
        hassasiyet_duzen.addLayout(slider_duzen)
        
        # Hassasiyet açıklaması
        self.hassasiyet_aciklama = QLabel(self.hassasiyet_aciklama_al(self.hassasiyet_kaydirici.value()))
        self.hassasiyet_aciklama.setWordWrap(True)
        self.hassasiyet_aciklama.setStyleSheet("""
            QLabel {
                color: #BBB;
                font-size: 9pt;
                padding: 8px;
                background-color: #3A3A3A;
                border-radius: 3px;
                margin-top: 5px;
            }
        """)
        hassasiyet_duzen.addWidget(self.hassasiyet_aciklama)
        
        hassasiyet_grubu.setLayout(hassasiyet_duzen)
        parametre_duzen.addWidget(hassasiyet_grubu)
        
        parametre_duzen.addStretch()
        return parametre_sekmesi
    
    def filtreleme_sekmesi_olustur(self):
        """Filtreleme sekmesini oluştur - Ana tema uyumlu"""
        filtreleme_sekmesi = QWidget()
        filtreleme_duzen = QVBoxLayout(filtreleme_sekmesi)
        filtreleme_duzen.setSpacing(15)
        
        # Açıklama
        aciklama = QLabel(tr.get_text("color_filtering_desc"))
        aciklama.setWordWrap(True)
        aciklama.setStyleSheet("""
            QLabel {
                color: #CCC;
                font-size: 9pt;
                padding: 8px;
                background-color: #3A3A3A;
                border-radius: 3px;
                border-left: 3px solid #2196F3;
            }
        """)
        filtreleme_duzen.addWidget(aciklama)
        
        # Ten rengi filtreleme grubu - Ana uygulama stili
        ten_rengi_grubu = QGroupBox(tr.get_text("skin_tone_filtering"))
        ten_rengi_grubu.setStyleSheet("""
            QGroupBox {
                color: #EEE;
                font-size: 10pt;
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
        """)
        
        ten_rengi_duzen = QVBoxLayout()
        
        self.ten_rengi_filtreleme = QCheckBox(tr.get_text("enable_skin_tone_filtering"))
        self.ten_rengi_filtreleme.setChecked(self.parent.ten_rengi_filtreleme_aktif)  # Ana uygulamadan mevcut değeri yükle
        self.ten_rengi_filtreleme.setToolTip(tr.get_text("skin_tone_filtering_tooltip"))
        self.ten_rengi_filtreleme.setStyleSheet("""
            QCheckBox {
                color: #EEE;
                font-size: 10pt;
                spacing: 8px;
                padding: 5px;
            }
            QCheckBox:hover {
                color: #2196F3;
            }
        """)
        ten_rengi_duzen.addWidget(self.ten_rengi_filtreleme)
        
        # Ten rengi açıklaması
        ten_rengi_aciklama = QLabel(tr.get_text("skin_tone_filtering_explanation"))
        ten_rengi_aciklama.setWordWrap(True)
        ten_rengi_aciklama.setStyleSheet("""
            QLabel {
                color: #BBB;
                font-size: 9pt;
                padding: 8px;
                background-color: #3A3A3A;
                border-radius: 3px;
            }
        """)
        ten_rengi_duzen.addWidget(ten_rengi_aciklama)
        
        ten_rengi_grubu.setLayout(ten_rengi_duzen)
        filtreleme_duzen.addWidget(ten_rengi_grubu)
        
        # Kararlılık grubu - Ana uygulama stili
        kararlilik_grubu = QGroupBox(tr.get_text("stability_enhancement"))
        kararlilik_grubu.setStyleSheet("""
            QGroupBox {
                color: #EEE;
                font-size: 10pt;
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
        """)
        
        kararlilik_duzen = QVBoxLayout()
        
        self.kararlilik_gelistirme = QCheckBox(tr.get_text("enable_stability_enhancement"))
        self.kararlilik_gelistirme.setChecked(self.parent.kararlilik_gelistirme_aktif)  # Ana uygulamadan mevcut değeri yükle
        self.kararlilik_gelistirme.setToolTip(tr.get_text("stability_enhancement_tooltip"))
        self.kararlilik_gelistirme.setStyleSheet("""
            QCheckBox {
                color: #EEE;
                font-size: 10pt;
                spacing: 8px;
                padding: 5px;
            }
            QCheckBox:hover {
                color: #2196F3;
            }
        """)
        kararlilik_duzen.addWidget(self.kararlilik_gelistirme)
        
        # Kararlılık açıklaması
        kararlilik_aciklama = QLabel(tr.get_text("stability_enhancement_explanation"))
        kararlilik_aciklama.setWordWrap(True)
        kararlilik_aciklama.setStyleSheet("""
            QLabel {
                color: #BBB;
                font-size: 9pt;
                padding: 8px;
                background-color: #3A3A3A;
                border-radius: 3px;
            }
        """)
        kararlilik_duzen.addWidget(kararlilik_aciklama)
        
        kararlilik_grubu.setLayout(kararlilik_duzen)
        filtreleme_duzen.addWidget(kararlilik_grubu)
        
        filtreleme_duzen.addStretch()
        return filtreleme_sekmesi
    
    def buton_duzen_olustur(self):
        """Buton düzenini oluştur - Ana uygulama buton stili"""
        buton_duzen = QHBoxLayout()
        buton_duzen.addStretch()
        
        # İptal butonu - Ana uygulama stili
        iptal_buton = QPushButton(tr.get_text("cancel"))
        iptal_buton.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                padding: 8px;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #777;
                border: 1px solid #999;
            }
            QPushButton:pressed {
                background-color: #444;
            }
        """)
        iptal_buton.clicked.connect(self.reject)
        buton_duzen.addWidget(iptal_buton)
        
        # Kaydet butonu - Ana uygulama stili (eski "Tamam" butonu)
        kaydet_buton = QPushButton(tr.get_text("save"))
        kaydet_buton.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #66BB6A;
                border: 2px solid #81C784;
            }
            QPushButton:pressed {
                background-color: #43A047;
            }
        """)
        kaydet_buton.clicked.connect(self.ayarlari_kaydet_ve_kapat)
        buton_duzen.addWidget(kaydet_buton)
        
        return buton_duzen
    
    def hassasiyet_degisti(self, deger):
        """Hassasiyet değiştiğinde çağrılır"""
        self.hassasiyet_deger_etiket.setText(str(deger))
        self.hassasiyet_aciklama.setText(self.hassasiyet_aciklama_al(deger))
    
    def hassasiyet_aciklama_al(self, deger):
        """Hassasiyet değerine göre açıklama döndür"""
        if deger <= 3:
            return tr.get_text("low_sensitivity_desc")
        elif deger <= 7:
            return tr.get_text("medium_sensitivity_desc")
        else:
            return tr.get_text("high_sensitivity_desc")
        
    def ayarlari_kaydet_ve_kapat(self):
        """Ayarları kaydet ve dialog'u kapat"""
        # Renk seçimlerini güncelle
        self.parent.kirmizi_onay_kutu.setChecked(self.kirmizi_onay_kutu.isChecked())
        self.parent.yesil_onay_kutu.setChecked(self.yesil_onay_kutu.isChecked())
        self.parent.mavi_onay_kutu.setChecked(self.mavi_onay_kutu.isChecked())
        self.parent.sari_onay_kutu.setChecked(self.sari_onay_kutu.isChecked())
        
        # Hassasiyet değerini güncelle
        if hasattr(self, 'hassasiyet_kaydirici'):
            self.parent.hassasiyet_kaydirici.setValue(self.hassasiyet_kaydirici.value())
        
        # Filtreleme ayarlarını ana uygulamada sakla
        if hasattr(self, 'ten_rengi_filtreleme'):
            self.parent.ten_rengi_filtreleme_aktif = self.ten_rengi_filtreleme.isChecked()
        if hasattr(self, 'kararlilik_gelistirme'):
            self.parent.kararlilik_gelistirme_aktif = self.kararlilik_gelistirme.isChecked()
        
        # Renk körlüğü combo'sunu "Özel Renkler" olarak ayarla - SINYAL ENGELLEYEREKk
        self.parent.renk_korlugu_combo.blockSignals(True)  # Sinyalleri geçici engelle
        for i in range(self.parent.renk_korlugu_combo.count()):
            if self.parent.renk_korlugu_combo.itemData(i) == "custom":
                self.parent.renk_korlugu_combo.setCurrentIndex(i)
                break
        self.parent.renk_korlugu_combo.blockSignals(False)  # Sinyalleri yeniden etkinleştir
        
        # Dialog'u kapat
        self.accept()
    
    def ayarlari_uygula_ve_kapat(self):
        """Eski fonksiyon - geriye dönük uyumluluk için"""
        self.ayarlari_kaydet_ve_kapat()
