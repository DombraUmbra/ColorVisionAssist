import cv2
import numpy as np
from utils import draw_text_with_utf8

class ColorDetector:
    def __init__(self):
        # İyileştirilmiş renk aralıkları
        self.renk_araliklari = {
            # TEN RENGİ - Çok geniş ama kararlı aralık
            'skin': [
                (np.array([0, 5, 25]), np.array([45, 95, 255])),        # Maksimum kapsayıcı ten rengi
            ],
            
            # KIRMIZI - Kararlı algılama için optimize edilmiş aralık
            'red': [
                (np.array([0, 70, 45]), np.array([9, 255, 255])),        # Alt kırmızı (daha geniş, kararlı)
                (np.array([171, 70, 45]), np.array([180, 255, 255]))     # Üst kırmızı (daha geniş, kararlı)
            ],
            
            # YEŞİL - Maviden net ayrılan aralık
            'green': [
                (np.array([35, 40, 40]), np.array([75, 255, 255]))       # Daha dar ve yüksek kalite yeşil
            ],
            
            # MAVİ - Yeşilden net ayrılan aralık
            'blue': [
                (np.array([85, 40, 40]), np.array([135, 255, 255]))      # Daha dar ve yüksek kalite mavi
            ],
            
            # SARI - Geniş aralık (eski hali)
            'yellow': [
                (np.array([15, 30, 30]), np.array([35, 255, 255]))
            ]
        }
        
        # Basit minimum kontur alanları (tüm renkler için aynı)
        self.min_alanlar = {
            'skin': 100,    # Ten rengi için biraz daha büyük alan
            'red': 60,      # Kırmızı da diğer renkler gibi
            'green': 60, 
            'blue': 40,
            'yellow': 10
        }

        # Renk körlüğü türlerine göre optimal çerçeve/metin renkleri
        self.renk_korlugu_eşlemeleri = {
            'red_green': {  # Kırmızı-Yeşil renk körlüğü
                'red': (255, 128, 0),      # Parlak mavi (BGR)
                'green': (255, 0, 255),    # Parlak mor (BGR)
                'blue': (0, 255, 255),     # Sarı (BGR)
                'yellow': (0, 0, 255)      # Kırmızı (BGR)
            },
            'blue_yellow': {  # Mavi-Sarı renk körlüğü
                'red': (0, 255, 0),        # Yeşil (BGR)
                'green': (0, 0, 255),      # Kırmızı (BGR)
                'blue': (0, 255, 255),     # Sarı (BGR)
                'yellow': (0, 128, 0)      # Koyu yeşil (BGR)
            },
            'protanopia': {  # Protanopi (Kırmızı körlük)
                'red': (255, 255, 0),      # Cyan (BGR)
                'green': (255, 128, 0),    # Parlak mavi (BGR)
                'blue': (0, 255, 255),     # Sarı (BGR)
                'yellow': (128, 255, 0)    # Açık cyan (BGR)
            },
            'deuteranopia': {  # Deuteranopi (Yeşil körlük)
                'red': (255, 128, 0),      # Parlak mavi (BGR)
                'green': (255, 0, 128),    # Mor (BGR)
                'blue': (0, 255, 255),     # Sarı (BGR)
                'yellow': (255, 0, 255)    # Magenta (BGR)
            },
            'tritanopia': {  # Tritanopi (Mavi körlük)
                'red': (0, 255, 0),        # Yeşil (BGR)
                'green': (0, 0, 255),      # Kırmızı (BGR)
                'blue': (0, 255, 0),       # Yeşil (BGR)
                'yellow': (0, 128, 255)    # Turuncu (BGR)
            },
            'complete': {  # Tam renk körlüğü
                'red': (255, 255, 255),    # Beyaz (BGR)
                'green': (128, 128, 128),  # Gri (BGR)
                'blue': (0, 0, 0),         # Siyah (BGR)
                'yellow': (200, 200, 200)  # Açık gri (BGR)
            }
        }

    def kareyi_isle(self, kare, secili_renkler, hassasiyet=5, kontrast=5, renk_cevirileri=None, ten_rengi_filtreleme=True, kararlilik_gelistirme=True, renk_korlugu_turu='red_green'):
        """
        İyileştirilmiş renk algılama + vurgulama sistemi
        """
        if renk_cevirileri is None:
            renk_cevirileri = {
                'skin': 'Ten Rengi',
                'red': 'Kırmızı',
                'green': 'Yeşil', 
                'blue': 'Mavi',
                'yellow': 'Sarı'
            }
        
        # Basit ön işleme (tüm renkler için aynı)
        alpha = 1.0 + (kontrast - 5) * 0.15  # Etkili kontrast
        kare_iyilesirilmis = cv2.convertScaleAbs(kare, alpha=alpha, beta=5)
        
        # HSV dönüşümü
        hsv = cv2.cvtColor(kare_iyilesirilmis, cv2.COLOR_BGR2HSV)
        
        # Basit gürültü azaltma
        hsv = cv2.bilateralFilter(hsv, 9, 75, 75)
        hsv = cv2.medianBlur(hsv, 3)
        
        # Ten rengi maskesi hazırla (sadece kırmızıdan ayırt etmek için)
        ten_maske = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for alt_sinir, ust_sinir in self.renk_araliklari['skin']:
            ten_maske_temp = cv2.inRange(hsv, alt_sinir, ust_sinir)
            ten_maske = cv2.bitwise_or(ten_maske, ten_maske_temp)
        
        # VURGULAMA SİSTEMİ HAZIRLIĞI
        # Arkaplan karartma için orijinal kareden başla
        sonuc = kare.copy()
        karartilmis_arkaplan = cv2.convertScaleAbs(kare, alpha=0.3, beta=0)  # %30 parlaklık
        
        # HER ZAMAN ARKAPLAN KARARTMA UYGULA
        # Önce tüm kareyi karart
        sonuc = karartilmis_arkaplan.copy()
        
        # Tüm renk maskelerini birleştirmek için
        toplam_maske = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        # Renk bilgilerini sakla (çizim için)
        tespit_edilen_renkler = []
        
        # Her renk için işlem (ten rengi hariç - sadece arkaplanda kullanılır)
        for renk_adi, secili in secili_renkler.items():
            if not secili or renk_adi not in self.renk_araliklari or renk_adi == 'skin':
                continue
                
            # Renk maskesi oluştur
            maske_birlesik = np.zeros(hsv.shape[:2], dtype=np.uint8)
            
            for alt_sinir, ust_sinir in self.renk_araliklari[renk_adi]:
                maske = cv2.inRange(hsv, alt_sinir, ust_sinir)
                maske_birlesik = cv2.bitwise_or(maske_birlesik, maske)
            
            # Sadece kırmızı için basit ten rengi filtresi uygula
            if renk_adi == 'red':
                # Sadece basit ten rengi filtreleme (kararlılık için)
                maske_birlesik = cv2.bitwise_and(maske_birlesik, cv2.bitwise_not(ten_maske))
            
            # Basit morfolojik temizleme (tüm renkler için aynı)
            kernel_kucuk = np.ones((3, 3), np.uint8)
            kernel_orta = np.ones((5, 5), np.uint8)
            
            maske_birlesik = cv2.morphologyEx(maske_birlesik, cv2.MORPH_OPEN, kernel_kucuk)
            maske_birlesik = cv2.morphologyEx(maske_birlesik, cv2.MORPH_CLOSE, kernel_orta)
            maske_birlesik = cv2.medianBlur(maske_birlesik, 5)
            
            # Konturları bul
            konturlar, _ = cv2.findContours(maske_birlesik, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Hassasiyete göre minimum alan ayarla (daha hassas)
            min_alan = self.min_alanlar[renk_adi] * (12 - hassasiyet) / 10
            
            # Renk değeri
            if renk_adi == 'skin':
                renk = (139, 105, 20)  # Kahverengi ton (ten rengi için)
            elif renk_adi == 'red':
                renk = (0, 0, 255)
            elif renk_adi == 'green':
                renk = (0, 255, 0)
            elif renk_adi == 'blue':
                renk = (255, 0, 0)
            elif renk_adi == 'yellow':
                renk = (0, 255, 255)
            
            # Bu renk için geçerli konturları topla
            for kontur in konturlar:
                alan = cv2.contourArea(kontur)
                if alan < min_alan:
                    continue
                
                # Bounding box
                x, y, w, h = cv2.boundingRect(kontur)
                
                # Gelişmiş şekil filtresi
                aspect_ratio = max(w, h) / max(min(w, h), 1)
                if aspect_ratio > 6:  # Biraz daha toleranslı
                    continue
                
                # Kontur kalitesi kontrolü
                peri = cv2.arcLength(kontur, True)
                if peri > 0:
                    compactness = 4 * np.pi * alan / (peri * peri)
                    if compactness < 0.1:  # Çok düzensiz şekilleri atla
                        continue
                
                # Doğruluk hesapla
                roi_maske = maske_birlesik[y:y+h, x:x+w]
                maske_alani = np.sum(roi_maske > 0)
                dogruluk = min(100, (maske_alani / max(alan, 1)) * 100)
                
                # Basit doğruluk kontrolü (tüm renkler için aynı)
                if dogruluk < 30:
                    continue
                
                # Bu konturun maskesini toplam maskeye ekle
                cv2.fillPoly(toplam_maske, [kontur], 255)
                
                # Renk bilgisini sakla
                metin = f"{renk_cevirileri.get(renk_adi, renk_adi)} ({dogruluk:.0f}%)"
                tespit_edilen_renkler.append({
                    'kontur': kontur,
                    'bbox': (x, y, w, h),
                    'renk': renk,
                    'renk_adi': renk_adi,  # Renk adını da sakla
                    'metin': metin
                })
        
        # VURGULAMA SİSTEMİ UYGULA
        if np.sum(toplam_maske) > 0:
            # Maske kenarlarını yumuşat
            toplam_maske_smooth = cv2.GaussianBlur(toplam_maske, (15, 15), 0)
            toplam_maske_smooth = toplam_maske_smooth.astype(np.float32) / 255.0
            
            # 3 kanala genişlet
            maske_3d = np.stack([toplam_maske_smooth] * 3, axis=2)
            
            # Orijinal renkleri algılanan alanlarda geri getir
            sonuc = sonuc.astype(np.float32)
            kare_float = kare.astype(np.float32)
            
            # Yumuşak geçiş ile orijinal renkleri vurgula
            sonuc = sonuc * (1 - maske_3d) + kare_float * maske_3d
            sonuc = sonuc.astype(np.uint8)
            
            # RENK KÖRLÜĞÜ DOSTU VURGU EFEKTI
            # Her renk için optimal çerçeve rengi kullan
            for renk_info in tespit_edilen_renkler:
                kontur = renk_info['kontur']
                renk_adi = renk_info['renk_adi']  # Renk adını da saklayacağız
                
                # Renk körlüğü türüne göre optimal çerçeve rengi seç
                if renk_korlugu_turu in self.renk_korlugu_eşlemeleri:
                    cerceve_rengi = self.renk_korlugu_eşlemeleri[renk_korlugu_turu].get(renk_adi, (255, 255, 255))
                else:
                    cerceve_rengi = (255, 255, 255)  # Varsayılan beyaz
                
                # Bu kontur için maske oluştur
                kontur_maske = np.zeros(hsv.shape[:2], dtype=np.uint8)
                cv2.fillPoly(kontur_maske, [kontur], 255)
                
                # Kontur kenarını genişlet
                vurgu_maske = cv2.dilate(kontur_maske, np.ones((5, 5), np.uint8), iterations=1)
                vurgu_kenar = cv2.bitwise_xor(vurgu_maske, kontur_maske)
                
                # Bu rengin kenarını optimal çerçeve rengiyle çiz
                sonuc[vurgu_kenar > 0] = cerceve_rengi
        
        # RENK KÖRLÜĞÜ DOSTU METİN ÇİZİMİ
        for renk_info in tespit_edilen_renkler:
            x, y, w, h = renk_info['bbox']
            metin = renk_info['metin']
            renk_adi = renk_info['renk_adi']
            
            # Renk körlüğü türüne göre optimal metin rengi seç
            if renk_korlugu_turu in self.renk_korlugu_eşlemeleri:
                metin_rengi = self.renk_korlugu_eşlemeleri[renk_korlugu_turu].get(renk_adi, (255, 255, 255))
            else:
                metin_rengi = (255, 255, 255)  # Varsayılan beyaz
            
            # Merkezi konumu hesapla 
            merkez_x = x + w // 2
            merkez_y = y + h // 2
            
            # Metin boyutunu al
            text_size = cv2.getTextSize(metin, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            # Metni nesnenin üst ortasına yerleştir
            metin_x = merkez_x - text_size[0] // 2
            metin_y = max(y - 10, 20)  # En az 20 piksel yukarıda
            
            # BGR'yi RGB'ye çevir (draw_text_with_utf8 RGB bekler)
            metin_rengi_rgb = (metin_rengi[2], metin_rengi[1], metin_rengi[0])
            
            # Renk körlüğü dostu metin çiz
            sonuc = draw_text_with_utf8(
                sonuc, metin, (metin_x, metin_y),
                metin_rengi=metin_rengi_rgb, font_boyutu=14,
                dis_cizgi_rengi=(0, 0, 0), dis_cizgi_kalinligi=2
            )
        
        return sonuc
