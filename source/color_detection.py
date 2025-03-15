import cv2
import numpy as np
from utils import draw_text_with_utf8

class ColorDetector:
    def __init__(self):
        # Renk aralıkları tanımla
        self.initialize_color_ranges()
        self.min_contour_area = 500
        
    def initialize_color_ranges(self):
        """HSV renk uzayında tespit edilecek renklerin aralıklarını tanımlar"""
        self.color_ranges = {
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
    
    def process_frame(self, frame, selected_colors, sensitivity=5, contrast=5, color_translations=None):
        """
        Video karesini işler ve seçilen renkleri tespit eder
        
        Args:
            frame: OpenCV BGR formatında video karesi
            selected_colors: Dictionary (key=renk adı, value=bool seçili mi)
            sensitivity: 1-10 arasında duyarlılık değeri
            contrast: 1-10 arasında kontrast değeri
            color_translations: Çevrilen renk isimlerini içeren sözlük
            
        Returns:
            İşlenmiş video karesi
        """
        # Boş çeviri sözlüğü oluştur
        if color_translations is None:
            color_translations = {
                'red': 'Red',
                'green': 'Green',
                'blue': 'Blue',
                'yellow': 'Yellow'
            }
        
        # BGR'dan HSV'ye dönüştürme
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Seçilen renkler için maskeler oluştur
        masks = {}
        if selected_colors.get('red', False):
            mask_red1 = cv2.inRange(hsv, self.color_ranges['red1'][0], self.color_ranges['red1'][1])
            mask_red2 = cv2.inRange(hsv, self.color_ranges['red2'][0], self.color_ranges['red2'][1])
            masks['red'] = mask_red1 | mask_red2
        
        if selected_colors.get('green', False):
            masks['green'] = cv2.inRange(hsv, self.color_ranges['green'][0], self.color_ranges['green'][1])
        
        if selected_colors.get('blue', False):
            masks['blue'] = cv2.inRange(hsv, self.color_ranges['blue'][0], self.color_ranges['blue'][1])
        
        if selected_colors.get('yellow', False):
            masks['yellow'] = cv2.inRange(hsv, self.color_ranges['yellow'][0], self.color_ranges['yellow'][1])
        
        # Tüm maskeleri birleştir
        mask_combined = np.zeros_like(hsv[:, :, 0])
        for color, mask in masks.items():
            mask_combined = mask_combined | mask
        
        # Maskeleri genişlet
        kernel = np.ones((5, 5), np.uint8)
        mask_combined = cv2.dilate(mask_combined, kernel, iterations=2)
        
        # Renkleri filtrele
        result = cv2.bitwise_and(frame, frame, mask=mask_combined)
        
        # Maskelenmiş renklerin canlılığını duyarlılığa göre ayarla
        sensitivity = sensitivity * 20 + 40  # 1-10 değerlerini 60-240 aralığına eşle
        result[np.where((result != [0, 0, 0]).all(axis=2))] = [sensitivity, sensitivity, sensitivity]
        
        # Orijinal kareyi koyulaştır
        contrast_value = contrast / 10  # 1-10 değerlerini 0.1-1.0 aralığına eşle
        darkened_frame = cv2.addWeighted(frame, contrast_value, np.zeros_like(frame), 1-contrast_value, 0)
        
        # Sonuçları birleştir
        combined_result = cv2.addWeighted(darkened_frame, 0.7, result, 0.3, 0)
        
        # BGR formatında renk değerleri
        colors = {
            'red': (0, 0, 255) if selected_colors.get('red', False) else None,
            'green': (0, 255, 0) if selected_colors.get('green', False) else None,
            'blue': (255, 0, 0) if selected_colors.get('blue', False) else None,
            'yellow': (0, 255, 255) if selected_colors.get('yellow', False) else None
        }
        
        # Önce dikdörtgenleri çiz
        for color_name, mask in masks.items():
            if colors[color_name] is not None:
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    if cv2.contourArea(contour) > self.min_contour_area:
                        x, y, w, h = cv2.boundingRect(contour)
                        # Dikdörtgen çiz
                        cv2.rectangle(combined_result, (x, y), (x + w, y + h), colors[color_name], 2)
        
        # Sonra metni çiz
        for color_name, mask in masks.items():
            if colors[color_name] is not None:
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    if cv2.contourArea(contour) > self.min_contour_area:
                        x, y, w, h = cv2.boundingRect(contour)
                        mask_contour = mask[y:y+h, x:x+w]
                        contour_area = cv2.contourArea(contour)
                        mask_area = np.sum(mask_contour > 0)
                        accuracy = min((mask_area / contour_area) * 100, 100)
                        
                        # Renk adı ve doğruluk yüzdesi metni oluştur
                        text = f"{color_translations.get(color_name, color_name)} ({accuracy:.1f}%)"
                        
                        # UTF-8 metin çizim fonksiyonunu kullan
                        combined_result = draw_text_with_utf8(
                            combined_result,
                            text,
                            (x, y - 25),  # Metni dikdörtgenin üzerinde konumlandır
                            text_color=colors[color_name],
                            font_size=16,
                            stroke_color=(0, 0, 0),  # Siyah dış çizgi
                            stroke_width=1
                        )
                            
        return combined_result
