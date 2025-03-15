import os
from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                           QWidget, QSlider, QCheckBox, QGroupBox, QGridLayout, QComboBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

# Paketin kendi modüllerini import et
from .translations import translator as tr

def create_button(text, tooltip, style_class="default", callback=None):
    """Standart stilli buton oluştur"""
    button = QPushButton(text)
    button.setToolTip(tooltip)
    
    style_dict = {
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
    
    button.setStyleSheet(style_dict.get(style_class, style_dict["default"]))
    
    if callback:
        button.clicked.connect(callback)
    
    return button

def create_camera_controls(parent):
    """Kamera kontrol butonlarını oluştur"""
    button_layout = QHBoxLayout()
    
    # Kamera aç/kapa butonu
    toggle_camera_button = create_button(
        tr.get_text("start"), 
        tr.get_text("start_tooltip"),
        "start",
        parent.toggle_camera
    )
    parent.toggle_camera_button = toggle_camera_button
    
    # Ekran görüntüsü ve galeri butonları
    snapshot_button = create_button(
        tr.get_text("take_screenshot"),
        tr.get_text("snapshot_tooltip"),
        "snapshot",
        parent.take_snapshot
    )
    # Kamera kapalıyken görünmez yap
    snapshot_button.setVisible(parent.camera_manager.camera_on)
    parent.snapshot_button = snapshot_button
    
    gallery_button = create_button(
        tr.get_text("gallery"),
        tr.get_text("gallery_tooltip"),
        "gallery",
        parent.open_gallery
    )
    parent.gallery_button = gallery_button
    
    button_layout.addWidget(toggle_camera_button)
    button_layout.addWidget(snapshot_button)
    button_layout.addWidget(gallery_button)
    
    return button_layout

def create_color_detection_group(parent):
    """Renk algılama ayarları grubu oluştur"""
    color_group = QGroupBox(tr.get_text("color_detection"))
    color_layout = QVBoxLayout()
    
    parent.red_checkbox = QCheckBox(tr.get_text("detect_red"))
    parent.green_checkbox = QCheckBox(tr.get_text("detect_green"))
    parent.blue_checkbox = QCheckBox(tr.get_text("detect_blue"))
    parent.yellow_checkbox = QCheckBox(tr.get_text("detect_yellow"))
    
    # Varsayılan seçili renkler
    parent.red_checkbox.setChecked(True)
    parent.green_checkbox.setChecked(True)
    
    # İpuçları
    parent.red_checkbox.setToolTip(tr.get_text("red_checkbox_tooltip"))
    parent.green_checkbox.setToolTip(tr.get_text("green_checkbox_tooltip"))
    parent.blue_checkbox.setToolTip(tr.get_text("blue_checkbox_tooltip"))
    parent.yellow_checkbox.setToolTip(tr.get_text("yellow_checkbox_tooltip"))
    
    # Düzene ekle
    color_layout.addWidget(parent.red_checkbox)
    color_layout.addWidget(parent.green_checkbox)
    color_layout.addWidget(parent.blue_checkbox)
    color_layout.addWidget(parent.yellow_checkbox)
    color_group.setLayout(color_layout)
    
    return color_group

def create_display_settings_group(parent):
    """Görüntüleme ayarları grubu oluştur"""
    display_group = QGroupBox(tr.get_text("display_settings"))
    display_layout = QGridLayout()
    
    # Duyarlılık ayarı
    parent.detection_sensitivity_label = QLabel(tr.get_text("detection_sensitivity"))
    display_layout.addWidget(parent.detection_sensitivity_label, 0, 0)
    parent.sensitivity_slider = QSlider(Qt.Horizontal)
    parent.sensitivity_slider.setRange(1, 10)
    parent.sensitivity_slider.setValue(5)
    parent.sensitivity_slider.setToolTip(tr.get_text("sensitivity_tooltip"))
    display_layout.addWidget(parent.sensitivity_slider, 0, 1)
    
    # Kontrast ayarı
    parent.contrast_label = QLabel(tr.get_text("contrast"))
    display_layout.addWidget(parent.contrast_label, 1, 0)
    parent.contrast_slider = QSlider(Qt.Horizontal)
    parent.contrast_slider.setRange(1, 10)
    parent.contrast_slider.setValue(5)
    parent.contrast_slider.setToolTip(tr.get_text("contrast_tooltip"))
    display_layout.addWidget(parent.contrast_slider, 1, 1)
    
    # Görüntü modu
    parent.display_mode_label = QLabel(tr.get_text("display_mode"))
    display_layout.addWidget(parent.display_mode_label, 2, 0)
    parent.display_mode = QComboBox()
    parent.display_mode.addItems(["Normal", "Deuteranopia", "Protanopia", "Tritanopia"])
    parent.display_mode.setToolTip(tr.get_text("display_mode_tooltip"))
    display_layout.addWidget(parent.display_mode, 2, 1)
    
    display_group.setLayout(display_layout)
    
    return display_group

def create_camera_settings_group(parent):
    """Kamera ayarları grubu oluştur"""
    camera_settings_group = QGroupBox(tr.get_text("camera_settings"))
    camera_layout = QVBoxLayout()
    
    # Kamera izinleri hakkında bilgi
    parent.camera_info_label = QLabel(tr.get_text("camera_settings_info"))
    parent.camera_info_label.setWordWrap(True)
    parent.camera_info_label.setStyleSheet("color: #CCC; font-size: 9pt;")
    camera_layout.addWidget(parent.camera_info_label)
    
    # Mevcut izin durumunu göster
    permission_status_text = ""
    if parent.camera_permission == "granted":
        permission_status_text = tr.get_text("permission_status_granted")
    elif parent.camera_permission == "denied":
        permission_status_text = tr.get_text("permission_status_denied")
    else:
        permission_status_text = tr.get_text("permission_status_ask")
        
    parent.permission_status_label = QLabel(f"{tr.get_text('current_permission_status')}: {permission_status_text}")
    parent.permission_status_label.setStyleSheet("color: #2196F3; margin-top: 8px;")
    camera_layout.addWidget(parent.permission_status_label)
    
    # Kamera izinlerini sıfırlama butonu
    reset_permission_button = QPushButton(tr.get_text("reset_camera_permission"))
    reset_permission_button.setStyleSheet("""
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
    reset_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'reset_icon.png')
    if os.path.exists(reset_icon_path):
        reset_permission_button.setIcon(QIcon(reset_icon_path))
    
    reset_permission_button.clicked.connect(parent.reset_camera_permission)
    parent.reset_permission_button = reset_permission_button
    camera_layout.addWidget(reset_permission_button)
    
    camera_settings_group.setLayout(camera_layout)
    
    return camera_settings_group

def create_language_group(parent):
    """Dil ayarları grubu oluştur"""
    language_group = QGroupBox(tr.get_text("language"))
    language_layout = QVBoxLayout()
    
    # Dil seçimi
    parent.language_combo = QComboBox()
    for code, name in tr.LANGUAGES.items():
        parent.language_combo.addItem(name, code)
    
    # Mevcut dili ayarla
    current_index = 0
    language = parent.settings.value("language", "en")
    for i in range(parent.language_combo.count()):
        if parent.language_combo.itemData(i) == language:
            current_index = i
            break
    parent.language_combo.setCurrentIndex(current_index)
    parent.language_combo.currentIndexChanged.connect(parent.change_language)
    
    language_layout.addWidget(parent.language_combo)
    language_group.setLayout(language_layout)
    
    return language_group

def create_about_group(parent):
    """Hakkında bölümü grubu oluştur"""
    about_group = QGroupBox(tr.get_text("about"))
    about_layout = QVBoxLayout()
    
    parent.about_label = QLabel(tr.get_text("about_text"))
    parent.about_label.setAlignment(Qt.AlignCenter)
    about_layout.addWidget(parent.about_label)
    about_group.setLayout(about_layout)
    
    return about_group

def apply_dark_theme(widget):
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
