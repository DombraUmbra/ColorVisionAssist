"""
Proje V - Renk körlüğü yardımcı uygulaması
Bu paket, Proje V uygulamasının modüllerini barındırır.

Modüller:
- main: Ana uygulama ve UI mantığı
- camera: Kamera yönetimi ve ilgili UI özellikleri
- color_detection: Renk algılama algoritmaları
- gallery: Ekran görüntüleri galerisi
- translations: Çoklu dil desteği
- utils: Yardımcı fonksiyonlar
- ui_components: UI bileşenleri oluşturma fonksiyonları
"""

# Ana sınıfı doğrudan paketten erişilebilir yapma
from .main import ColorVisionAid

# Sık kullanılan bileşenleri paketten direkt olarak import edilebilir hale getir
from .camera import CameraManager
from .color_detection import ColorDetector
from .translations import translator
