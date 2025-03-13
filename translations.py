class Translations:
    """
    Manages translations for the ColorVisionAid application.
    Allows easy switching between different languages.
    """
    
    # Available languages
    LANGUAGES = {
        "en": "English",
        "tr": "Türkçe"
    }
    
    def __init__(self, default_language="en"):
        """Initialize with default language"""
        self.current_language = default_language
        
        # Dictionary containing all translations
        self._translations = {
            # Application title and main interface
            "app_title": {
                "en": "ColorVisionAid (CVA)",
                "tr": "ColorVisionAid (CVA)"
            },
            "camera_initializing": {
                "en": "Camera initializing...",
                "tr": "Kamera başlatılıyor..."
            },
            "camera_stopped": {
                "en": "Camera stopped",
                "tr": "Kamera durduruldu"
            },
            "ready": {
                "en": "Ready",
                "tr": "Hazır"
            },
            
            # Button labels
            "start": {
                "en": "Start",
                "tr": "Başlat"
            },
            "stop": {
                "en": "Stop",
                "tr": "Durdur"
            },
            "take_screenshot": {
                "en": "Take Screenshot",
                "tr": "Ekran Görüntüsü Al"
            },
            "gallery": {
                "en": "Gallery",
                "tr": "Galeri"
            },
            "refresh": {
                "en": "Refresh",
                "tr": "Yenile"
            },
            "delete_selected": {
                "en": "Delete Selected",
                "tr": "Seçileni Sil"
            },
            "export": {
                "en": "Export",
                "tr": "Dışa Aktar"
            },
            
            # Settings panel
            "color_detection": {
                "en": "Color Detection",
                "tr": "Renk Tespiti"
            },
            "detect_red": {
                "en": "Detect Red",
                "tr": "Kırmızı Algıla"
            },
            "detect_green": {
                "en": "Detect Green",
                "tr": "Yeşil Algıla"
            },
            "detect_blue": {
                "en": "Detect Blue",
                "tr": "Mavi Algıla"
            },
            "detect_yellow": {
                "en": "Detect Yellow",
                "tr": "Sarı Algıla"
            },
            
            # Display settings
            "display_settings": {
                "en": "Display Settings",
                "tr": "Görüntüleme Ayarları"
            },
            "detection_sensitivity": {
                "en": "Detection Sensitivity:",
                "tr": "Algılama Hassasiyeti:"
            },
            "contrast": {
                "en": "Contrast:",
                "tr": "Kontrast:"
            },
            "display_mode": {
                "en": "Display Mode:",
                "tr": "Gösterim Modu:"
            },
            
            # Language settings
            "language": {
                "en": "Language",
                "tr": "Dil"
            },
            
            # About section
            "about": {
                "en": "About",
                "tr": "Hakkında"
            },
            "about_text": {
                "en": "ColorVisionAid (CVA)\nVersion 1.1\n\nDesigned to assist individuals\nwith color vision deficiency.",
                "tr": "ColorVisionAid (CVA)\nSürüm 1.1\n\nRenk görme zorluğu yaşayan\nbireylere yardımcı olmak için\ntasarlanmıştır."
            },
            
            # Gallery
            "gallery_title": {
                "en": "Screenshot Gallery",
                "tr": "Ekran Görüntüleri Galerisi"
            },
            "saved_screenshots": {
                "en": "Saved screenshots:",
                "tr": "Kaydedilmiş ekran görüntüleri:"
            },
            "no_screenshots": {
                "en": "No screenshots saved yet.",
                "tr": "Henüz kaydedilmiş ekran görüntüsü yok."
            },
            
            # Status messages
            "camera_started": {
                "en": "Camera started",
                "tr": "Kamera başlatıldı"
            },
            "camera_start_failed": {
                "en": "Failed to start camera!",
                "tr": "Kamera başlatılamadı!"
            },
            "screenshot_saved": {
                "en": "Screenshot saved: {}",
                "tr": "Ekran görüntüsü kaydedildi: {}"
            },
            "file_deleted": {
                "en": "{} deleted",
                "tr": "{} silindi"
            },
            "file_exported": {
                "en": "Screenshot exported: {}",
                "tr": "Ekran görüntüsü dışa aktarıldı: {}"
            },
            
            # Dialog messages
            "delete_confirmation": {
                "en": "Delete Confirmation",
                "tr": "Silme Onayı"
            },
            "delete_confirm_text": {
                "en": "Are you sure you want to delete the file {}?",
                "tr": "{} dosyasını silmek istediğinize emin misiniz?"
            },
            "error": {
                "en": "Error",
                "tr": "Hata"
            },
            "delete_failed": {
                "en": "Failed to delete file: {}",
                "tr": "Dosya silinemedi: {}"
            },
            "export_failed": {
                "en": "Export failed: {}",
                "tr": "Dışa aktarma başarısız: {}"
            },
            "export_title": {
                "en": "Export Screenshot",
                "tr": "Ekran Görüntüsünü Dışa Aktar"
            },
            
            # Color names (for detection)
            "red": {
                "en": "Red",
                "tr": "Kırmızı"
            },
            "green": {
                "en": "Green",
                "tr": "Yeşil"
            },
            "blue": {
                "en": "Blue",
                "tr": "Mavi"
            },
            "yellow": {
                "en": "Yellow",
                "tr": "Sarı"
            },
            
            # Language change
            "language_changed": {
                "en": "Language changed",
                "tr": "Dil değiştirildi"
            }
        }
    
    def set_language(self, language_code):
        if language_code in self.LANGUAGES:
            self.current_language = language_code
            return True
        return False
    
    def get_text(self, key, *args):
        if key in self._translations and self.current_language in self._translations[key]:
            text = self._translations[key][self.current_language]
            if args:
                return text.format(*args)
            return text
        
        # Fallback to English if translation not found
        if key in self._translations and "en" in self._translations[key]:
            text = self._translations[key]["en"]
            if args:
                return text.format(*args)
            return text
        
        # Return the key as a last resort
        return key

# Create a global instance for easy access
translator = Translations()
