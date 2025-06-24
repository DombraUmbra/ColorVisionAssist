import cv2
import numpy as np
from .utils import draw_text_with_utf8

class ColorDetector:
    def __init__(self):
        # Renk aralıkları tanımla
        self.renk_araliklarini_baslat()
        self.min_kontur_alani = 500
        
    def renk_araliklarini_baslat(self):
        """HSV renk uzayında tespit edilecek renklerin aralıklarını tanımlar"""
        self.renk_araliklari = {
            'red1': (
                np.array([0, 150, 70]),
                np.array([10, 255, 255])
            ),
            'red2': (
                np.array([170, 150, 70]),
                np.array([180, 255, 255])
            ),
            'green': (
                np.array([35, 70, 70]),
                np.array([85, 255, 255])
            ),
            'blue': (
                np.array([90, 70, 70]),
                np.array([130, 255, 255])
            ),
            'yellow': (
                np.array([20, 100, 100]),
                np.array([35, 255, 255])
            )
        }
    
    def kareyi_isle(self, kare, secili_renkler, hassasiyet=5, kontrast=5, renk_cevirileri=None):
        """
        Video karesini işler ve seçilen renkleri tespit eder
        
        Args:
            kare: OpenCV BGR formatında video karesi
            secili_renkler: Dictionary (key=renk adı, value=bool seçili mi)
            hassasiyet: 1-10 arasında duyarlılık değeri
            kontrast: 1-10 arasında kontrast değeri
            renk_cevirileri: Çevrilen renk isimlerini içeren sözlük
            
        Returns:
            İşlenmiş video karesi
        """
        # Boş çeviri sözlüğü oluştur
        if renk_cevirileri is None:
            renk_cevirileri = {
                'red': 'Red',
                'green': 'Green',
                'blue': 'Blue',
                'yellow': 'Yellow'
            }
        
        # BGR'dan HSV'ye dönüştürme
        hsv = cv2.cvtColor(kare, cv2.COLOR_BGR2HSV)
        
        # Seçilen renkler için maskeler oluştur
        maskeler = {}
        if secili_renkler.get('red', False):
            kirmizi_maske1 = cv2.inRange(hsv, self.renk_araliklari['red1'][0], self.renk_araliklari['red1'][1])
            kirmizi_maske2 = cv2.inRange(hsv, self.renk_araliklari['red2'][0], self.renk_araliklari['red2'][1])
            maskeler['red'] = kirmizi_maske1 | kirmizi_maske2
        
        if secili_renkler.get('green', False):
            maskeler['green'] = cv2.inRange(hsv, self.renk_araliklari['green'][0], self.renk_araliklari['green'][1])
        
        if secili_renkler.get('blue', False):
            maskeler['blue'] = cv2.inRange(hsv, self.renk_araliklari['blue'][0], self.renk_araliklari['blue'][1])
        
        if secili_renkler.get('yellow', False):
            maskeler['yellow'] = cv2.inRange(hsv, self.renk_araliklari['yellow'][0], self.renk_araliklari['yellow'][1])
        
        # Tüm maskeleri birleştir
        birlestirilmis_maske = np.zeros_like(hsv[:, :, 0])
        for renk, maske in maskeler.items():
            birlestirilmis_maske = birlestirilmis_maske | maske
        
        # Maskeleri genişlet
        cekirdek = np.ones((5, 5), np.uint8)
        birlestirilmis_maske = cv2.dilate(birlestirilmis_maske, cekirdek, iterations=2)
        
        # Renkleri filtrele
        sonuc = cv2.bitwise_and(kare, kare, mask=birlestirilmis_maske)
        
        # Maskelenmiş renklerin canlılığını duyarlılığa göre ayarla
        hassasiyet = hassasiyet * 20 + 40  # 1-10 değerlerini 60-240 aralığına eşle
        sonuc[np.where((sonuc != [0, 0, 0]).all(axis=2))] = [hassasiyet, hassasiyet, hassasiyet]
        
        # Orijinal kareyi koyulaştır
        kontrast_degeri = kontrast / 10  # 1-10 değerlerini 0.1-1.0 aralığına eşle
        koyulastirilmis_kare = cv2.addWeighted(kare, kontrast_degeri, np.zeros_like(kare), 1-kontrast_degeri, 0)
        
        # Sonuçları birleştir
        birlestirilmis_sonuc = cv2.addWeighted(koyulastirilmis_kare, 0.7, sonuc, 0.3, 0)
        
        # BGR formatında renk değerleri
        renkler = {
            'red': (0, 0, 255) if secili_renkler.get('red', False) else None,
            'green': (0, 255, 0) if secili_renkler.get('green', False) else None,
            'blue': (255, 0, 0) if secili_renkler.get('blue', False) else None,
            'yellow': (0, 255, 255) if secili_renkler.get('yellow', False) else None
        }
        
        # Önce dikdörtgenleri çiz
        for renk_adi, maske in maskeler.items():
            if renkler[renk_adi] is not None:
                konturlar, _ = cv2.findContours(maske, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for kontur in konturlar:
                    if cv2.contourArea(kontur) > self.min_kontur_alani:
                        x, y, g, y_yukseklik = cv2.boundingRect(kontur)
                        # Dikdörtgen çiz
                        cv2.rectangle(birlestirilmis_sonuc, (x, y), (x + g, y + y_yukseklik), renkler[renk_adi], 2)
        
        # Sonra metni çiz
        for renk_adi, maske in maskeler.items():
            if renkler[renk_adi] is not None:
                konturlar, _ = cv2.findContours(maske, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for kontur in konturlar:
                    if cv2.contourArea(kontur) > self.min_kontur_alani:
                        x, y, g, y_yukseklik = cv2.boundingRect(kontur)
                        maske_kontur = maske[y:y+y_yukseklik, x:x+g]
                        kontur_alani = cv2.contourArea(kontur)
                        maske_alani = np.sum(maske_kontur > 0)
                        dogruluk = min((maske_alani / kontur_alani) * 100, 100)
                        
                        # Renk adı ve doğruluk yüzdesi metni oluştur
                        metin = f"{renk_cevirileri.get(renk_adi, renk_adi)} ({dogruluk:.1f}%)"
                        
                        # UTF-8 metin çizim fonksiyonunu kullan
                        birlestirilmis_sonuc = draw_text_with_utf8(
                            birlestirilmis_sonuc,
                            metin,
                            (x, y - 25),  # Metni dikdörtgenin üzerinde konumlandır
                            text_color=renkler[renk_adi],
                            font_size=16,
                            stroke_color=(0, 0, 0),  # Siyah dış çizgi
                            stroke_width=1
                        )
                            
        return birlestirilmis_sonuc
