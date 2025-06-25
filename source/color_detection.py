import cv2
import numpy as np
from .utils import draw_text_with_utf8

class ColorDetector:
    def __init__(self):
        # Renk aralıkları tanımla
        self.renk_araliklarini_baslat()
        self.min_kontur_alani = 80  # Gürültüyü azaltmak için artırıldı
        # Temporal smoothing için önceki konturları sakla
        self.onceki_konturlar = {}
        self.kontur_kararliligi = 3  # Kaç frame boyunca kontur görülmeli
        
    def renk_araliklarini_baslat(self):
        """HSV renk uzayında tespit edilecek renklerin aralıklarını tanımlar"""
        self.renk_araliklari = {
            'red1': (
                np.array([0, 100, 30]),  # Uzaktaki kırmızı nesneler için daha düşük eşik
                np.array([10, 255, 255])
            ),
            'red2': (
                np.array([170, 100, 30]),  # Uzaktaki kırmızı nesneler için daha düşük eşik
                np.array([180, 255, 255])
            ),
            'green': (
                np.array([45, 40, 30]),  # Sarıdan ayrılması için daha dar aralık
                np.array([75, 255, 255])  # Üst sınır düşürüldü
            ),            
            'blue': (
                np.array([85, 60, 40]),  # Daha seçici eşikler (sadece gerçek maviler)
                np.array([130, 255, 255])  # Aralık daraltıldı
            ),            
            'dark_blue': (
                np.array([95, 40, 25]),  # Çok daha sınırlı aralık (sadece gerçek koyu maviler)
                np.array([115, 120, 80])  # Dar aralık ve düşük değerler
            ),
            'yellow': (
                np.array([15, 60, 40]),  # Yeşilden ayrılması için daha dar aralık
                np.array([40, 255, 255])  # Üst sınır artırıldı
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
          # BGR'dan HSV'ye dönüştürme (öncesinde kontrast artırma)
        # Uzaktaki nesneler için kontrast artırma
        kare_kontrast = cv2.convertScaleAbs(kare, alpha=1.2, beta=10)
        hsv = cv2.cvtColor(kare_kontrast, cv2.COLOR_BGR2HSV)
          # Seçilen renkler için maskeler oluştur
        maskeler = {}
        
        if secili_renkler.get('red', False):
            kirmizi_maske1 = cv2.inRange(hsv, self.renk_araliklari['red1'][0], self.renk_araliklari['red1'][1])
            kirmizi_maske2 = cv2.inRange(hsv, self.renk_araliklari['red2'][0], self.renk_araliklari['red2'][1])
            maskeler['red'] = kirmizi_maske1 | kirmizi_maske2
        
        if secili_renkler.get('green', False):
            maskeler['green'] = cv2.inRange(hsv, self.renk_araliklari['green'][0], self.renk_araliklari['green'][1])
        
        if secili_renkler.get('blue', False):
            mavi_maske1 = cv2.inRange(hsv, self.renk_araliklari['blue'][0], self.renk_araliklari['blue'][1])
            mavi_maske2 = cv2.inRange(hsv, self.renk_araliklari['dark_blue'][0], self.renk_araliklari['dark_blue'][1])
            
            # Koyu mavi maskesini daha da filtrele (çok küçük alanları kaldır)
            cekirdek_temizlik = np.ones((3, 3), np.uint8)
            mavi_maske2 = cv2.morphologyEx(mavi_maske2, cv2.MORPH_OPEN, cekirdek_temizlik, iterations=2)
            
            maskeler['blue'] = mavi_maske1 | mavi_maske2
        
        if secili_renkler.get('yellow', False):
            maskeler['yellow'] = cv2.inRange(hsv, self.renk_araliklari['yellow'][0], self.renk_araliklari['yellow'][1])
        
        # Tüm maskeleri birleştir
        birlestirilmis_maske = np.zeros_like(hsv[:, :, 0])
        for renk, maske in maskeler.items():
            birlestirilmis_maske = birlestirilmis_maske | maske
        
        # Gürültü azaltma işlemleri (uzaktaki nesneler için minimal filtreleme)
        # 1. Çok hafif Gaussian blur (uzaktaki nesneleri korumak için)
        birlestirilmis_maske = cv2.GaussianBlur(birlestirilmis_maske, (3, 3), 0)
        birlestirilmis_maske = cv2.threshold(birlestirilmis_maske, 80, 255, cv2.THRESH_BINARY)[1]  # Daha düşük threshold
        
        # 2. Minimal morphological işlemler
        cekirdek_temizlik = np.ones((2, 2), np.uint8)
        birlestirilmis_maske = cv2.morphologyEx(birlestirilmis_maske, cv2.MORPH_CLOSE, cekirdek_temizlik, iterations=1)
        
        # 3. Çok hafif genişletme
        cekirdek = np.ones((2, 2), np.uint8)  # Daha küçük kernel
        birlestirilmis_maske = cv2.dilate(birlestirilmis_maske, cekirdek, iterations=1)
        
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
            'yellow': (0, 255, 255) if secili_renkler.get('yellow', False) else None        }
        
        # Önce dikdörtgenleri çiz (kararlı kontur algılama ile)
        for renk_adi, maske in maskeler.items():
            if renkler[renk_adi] is not None:
                konturlar, _ = cv2.findContours(maske, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                # Kararlı konturları al
                karali_konturlar = self.kontur_kararliligi_kontrol(renk_adi, konturlar)
                
                for kontur in karali_konturlar:
                    x, y, g, y_yukseklik = cv2.boundingRect(kontur)
                    # Dikdörtgen çiz (kalınlığı biraz artır)
                    cv2.rectangle(birlestirilmis_sonuc, (x, y), (x + g, y + y_yukseklik), renkler[renk_adi], 3)
          # Sonra metni çiz (kararlı konturlar ile)
        for renk_adi, maske in maskeler.items():
            if renkler[renk_adi] is not None:
                konturlar, _ = cv2.findContours(maske, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                # Kararlı konturları al (aynı konturları kullan)
                karali_konturlar = self.kontur_kararliligi_kontrol(renk_adi, konturlar)
                
                for kontur in karali_konturlar:
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
                        metin_rengi=renkler[renk_adi],
                        font_boyutu=16,
                        dis_cizgi_rengi=(0, 0, 0),  # Siyah dış çizgi
                        dis_cizgi_kalinligi=1                    )
                            
        return birlestirilmis_sonuc
    
    def kontur_kararliligi_kontrol(self, renk_adi, konturlar):
        """
        Gelişmiş kontur kararlılığı kontrolü - çerçevelerin sabit kalmasını sağlar
        
        Args:
            renk_adi: Renk adı ('red', 'blue', vb.)
            konturlar: Mevcut frame'deki konturlar
            
        Returns:
            Kararlı ve yumuşatılmış konturlar
        """
        if renk_adi not in self.onceki_konturlar:
            self.onceki_konturlar[renk_adi] = []
        
        # Geçerli konturları filtrele ve kaydet
        gecerli_konturlar = []
        for kontur in konturlar:
            if cv2.contourArea(kontur) > self.min_kontur_alani:
                x, y, w, h = cv2.boundingRect(kontur)
                merkez_x, merkez_y = x + w//2, y + h//2
                alan = cv2.contourArea(kontur)
                gecerli_konturlar.append({
                    'kontur': kontur,
                    'bbox': (x, y, w, h),
                    'merkez': (merkez_x, merkez_y),
                    'alan': alan,
                    'stabilite_sayaci': 1
                })
        
        # Önceki konturlarla karşılaştır ve kararlı olanları bul
        karali_konturlar = []
        
        if len(self.onceki_konturlar[renk_adi]) > 0:
            onceki_konturlar = self.onceki_konturlar[renk_adi][-1]
            
            for gecerli in gecerli_konturlar:
                en_yakin_onceki = None
                en_kucuk_mesafe = float('inf')
                
                # En yakın önceki konturu bul
                for onceki in onceki_konturlar:
                    mesafe = np.sqrt((gecerli['merkez'][0] - onceki['merkez'][0])**2 + 
                                   (gecerli['merkez'][1] - onceki['merkez'][1])**2)
                    
                    if mesafe < en_kucuk_mesafe and mesafe < 30:  # 30 piksel tolerance
                        en_kucuk_mesafe = mesafe
                        en_yakin_onceki = onceki
                
                if en_yakin_onceki is not None:
                    # Kontur kararlı - önceki konumla ortalama al (yumuşak geçiş)
                    eski_bbox = en_yakin_onceki['bbox']
                    yeni_bbox = gecerli['bbox']
                    
                    # %70 eski pozisyon, %30 yeni pozisyon (daha az hareket)
                    yumusak_x = int(eski_bbox[0] * 0.7 + yeni_bbox[0] * 0.3)
                    yumusak_y = int(eski_bbox[1] * 0.7 + yeni_bbox[1] * 0.3)
                    yumusak_w = int(eski_bbox[2] * 0.7 + yeni_bbox[2] * 0.3)
                    yumusak_h = int(eski_bbox[3] * 0.7 + yeni_bbox[3] * 0.3)
                    
                    # Yumuşatılmış bbox'tan yeni kontur oluştur
                    yumusak_kontur = np.array([
                        [[yumusak_x, yumusak_y]],
                        [[yumusak_x + yumusak_w, yumusak_y]],
                        [[yumusak_x + yumusak_w, yumusak_y + yumusak_h]],
                        [[yumusak_x, yumusak_y + yumusak_h]]
                    ])
                    
                    gecerli['kontur'] = yumusak_kontur
                    gecerli['bbox'] = (yumusak_x, yumusak_y, yumusak_w, yumusak_h)
                    gecerli['merkez'] = (yumusak_x + yumusak_w//2, yumusak_y + yumusak_h//2)
                    gecerli['stabilite_sayaci'] = en_yakin_onceki['stabilite_sayaci'] + 1
                    
                    # Sadece en az 2 frame stabil olan konturları kabul et
                    if gecerli['stabilite_sayaci'] >= 2:
                        karali_konturlar.append(gecerli['kontur'])
                else:
                    # Yeni kontur - ilk görülüyor, 1 frame bekle
                    pass
        
        # Mevcut konturları kaydet
        self.onceki_konturlar[renk_adi] = [gecerli_konturlar]
        
        # Son 5 frame'i sakla (daha uzun hafıza)
        if len(self.onceki_konturlar[renk_adi]) > 5:
            self.onceki_konturlar[renk_adi].pop(0)
        
        return karali_konturlar