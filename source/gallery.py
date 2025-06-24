import os
import glob
import cv2
import sys
from PyQt5.QtWidgets import (QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                           QWidget, QGridLayout, QScrollArea, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon

# Modülün doğru import edilebilmesi için source klasörünü ekleme
mevcut_dizin = os.path.dirname(os.path.abspath(__file__))
if mevcut_dizin not in sys.path:
    sys.path.append(mevcut_dizin)

from .translations import translator as tr

class ScreenshotGallery(QDialog):
    def __init__(self, ebeveyn=None):
        super().__init__(ebeveyn)
        self.setWindowTitle(tr.get_text("gallery_title"))
        self.setGeometry(200, 200, 800, 600)
        
        # Icon yolunu güncelle
        ikon_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'gallery_icon.png')
        self.setWindowIcon(QIcon(ikon_yolu))
        
        # Main layout
        duzen = QVBoxLayout()
        
        # Info label
        self.bilgi_etiket = QLabel(tr.get_text("saved_screenshots"))
        duzen.addWidget(self.bilgi_etiket)
        
        # Create a scroll area for the gallery
        kaydirma_alani = QScrollArea()
        kaydirma_alani.setWidgetResizable(True)
        kaydirma_widget = QWidget()
        self.galeri_duzen = QGridLayout(kaydirma_widget)
        
        kaydirma_alani.setWidget(kaydirma_widget)
        duzen.addWidget(kaydirma_alani)
        
        # Buttons layout
        buton_duzen = QHBoxLayout()
        
        # Add buttons
        self.yenile_buton = QPushButton(tr.get_text("refresh"))
        self.yenile_buton.clicked.connect(self.ekran_goruntulerini_yukle)
        
        self.sil_buton = QPushButton(tr.get_text("delete_selected"))
        self.sil_buton.clicked.connect(self.secileni_sil)
        self.sil_buton.setEnabled(False)
        
        self.disari_aktar_buton = QPushButton(tr.get_text("export"))
        self.disari_aktar_buton.clicked.connect(self.secileni_disari_aktar)
        self.disari_aktar_buton.setEnabled(False)
        
        buton_duzen.addWidget(self.yenile_buton)
        buton_duzen.addWidget(self.sil_buton)
        buton_duzen.addWidget(self.disari_aktar_buton)
        
        duzen.addLayout(buton_duzen)
        self.setLayout(duzen)
        
        # Variables
        self.ekran_goruntuler = []
        self.secili_indeks = -1
        self.kucuk_resim_etiketler = []
        
        # Load screenshots
        self.ekran_goruntulerini_yukle()
        
        # Apply the dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #333;
                color: #EEE;
            }
            QLabel {
                color: #EEE;
            }
            QPushButton {
                background-color: #555;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #777;
            }
            QPushButton:disabled {
                background-color: #444;
                color: #888;
            }
            QScrollArea {
                border: 1px solid #555;
                background-color: #444;
            }
        """)
    
    def ekran_goruntulerini_yukle(self):
        # Clear existing thumbnails
        for etiket in self.kucuk_resim_etiketler:
            self.galeri_duzen.removeWidget(etiket)
            etiket.deleteLater()
        
        self.kucuk_resim_etiketler = []
        self.ekran_goruntuler = []
        
        # Ensure screenshots directory exists - ana klasör yerine source klasörünün üstünü kullan
        kok_dizin = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ekran_goruntu_dizin = os.path.join(kok_dizin, "screenshots")
        if not os.path.exists(ekran_goruntu_dizin):
            os.makedirs(ekran_goruntu_dizin)
        
        # Find all PNG files in the screenshots directory that start with "screenshot_"
        ekran_goruntu_dosyalar = glob.glob(os.path.join(ekran_goruntu_dizin, "screenshot_*.png"))
        
        if not ekran_goruntu_dosyalar:
            self.bilgi_etiket.setText(tr.get_text("no_screenshots"))
            self.secili_indeks = -1
            self.sil_buton.setEnabled(False)
            self.disari_aktar_buton.setEnabled(False)
            return
        
        # Sort files by creation time (newest first)
        ekran_goruntu_dosyalar.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        self.ekran_goruntuler = ekran_goruntu_dosyalar
        
        # Display thumbnails in a grid (4 columns)
        sutun_sayisi = 4
        for i, dosya_yolu in enumerate(ekran_goruntu_dosyalar):
            # Create thumbnail
            piksel_harita = QPixmap(dosya_yolu)
            kucuk_resim = piksel_harita.scaled(QSize(150, 150), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Create label and add to layout
            etiket = QLabel()
            etiket.setPixmap(kucuk_resim)
            etiket.setAlignment(Qt.AlignCenter)
            etiket.setToolTip(dosya_yolu)
            etiket.setStyleSheet("border: 2px solid #555; margin: 5px; background-color: #222; padding: 5px;")
            etiket.setFixedSize(QSize(180, 180))
            etiket.mousePressEvent = lambda event, idx=i: self.ekran_goruntusu_sec(idx)
            
            satir, sutun = i // sutun_sayisi, i % sutun_sayisi
            self.galeri_duzen.addWidget(etiket, satir, sutun)
            self.kucuk_resim_etiketler.append(etiket)
        
        # Update info text
        self.bilgi_etiket.setText(f"{tr.get_text('saved_screenshots')} {len(ekran_goruntu_dosyalar)}")

    def ekran_goruntusu_sec(self, indeks):
        # Deselect the previous selection
        if 0 <= self.secili_indeks < len(self.kucuk_resim_etiketler):
            self.kucuk_resim_etiketler[self.secili_indeks].setStyleSheet("border: 2px solid #555; margin: 5px; background-color: #222; padding: 5px;")
        
        # Select the new one
        self.secili_indeks = indeks
        self.kucuk_resim_etiketler[indeks].setStyleSheet("border: 2px solid #2196F3; margin: 5px; background-color: #333; padding: 5px;")
        
        # Enable buttons
        self.sil_buton.setEnabled(True)
        self.disari_aktar_buton.setEnabled(True)
    
    def secileni_sil(self):
        if 0 <= self.secili_indeks < len(self.ekran_goruntuler):
            silinecek_dosya = self.ekran_goruntuler[self.secili_indeks]
            
            # Confirm deletion
            cevap = QMessageBox.question(
                self, 
                tr.get_text("delete_confirmation"), 
                tr.get_text("delete_confirm_text", silinecek_dosya),
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if cevap == QMessageBox.Yes:
                try:
                    os.remove(silinecek_dosya)
                    self.ekran_goruntulerini_yukle()  # Refresh the gallery
                    self.parent().durum_cubugu.showMessage(tr.get_text("file_deleted", silinecek_dosya))
                except Exception as e:
                    QMessageBox.critical(self, tr.get_text("error"), tr.get_text("delete_failed", str(e)))
    
    def secileni_disari_aktar(self):
        if 0 <= self.secili_indeks < len(self.ekran_goruntuler):
            disari_aktarilacak_dosya = self.ekran_goruntuler[self.secili_indeks]
            
            # Open file dialog to choose export location
            disari_aktarma_yolu, _ = QFileDialog.getSaveFileName(
                self, 
                tr.get_text("export_title"), 
                os.path.basename(disari_aktarilacak_dosya),
                "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*.*)"
            )
            
            if disari_aktarma_yolu:
                try:
                    # Read the original image
                    resim = cv2.imread(disari_aktarilacak_dosya)
                    
                    # Save to the selected path
                    cv2.imwrite(disari_aktarma_yolu, resim)
                    self.parent().durum_cubugu.showMessage(tr.get_text("file_exported", disari_aktarma_yolu))
                except Exception as e:
                    QMessageBox.critical(self, tr.get_text("error"), tr.get_text("export_failed", str(e)))
