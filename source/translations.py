class Translations:
    """
    Manages translations for the ColorVisionAid application.
    Allows easy switching between different languages.
    """
    # List of available languages
    LANGUAGES = {
        "en": "English",
        "tr": "Türkçe"
    }
    
    def __init__(self, default_language="en"):
        """Initialize with default language"""
        self.current_language = default_language
        
        # Dictionary containing all translations
        self._translations = {
            # Application title and status messages
            "app_title": {
                "en": "Whisper of Colors",
                "tr": "Renklerin Fısıltısı"
            },
            "camera_initializing": {
                "en": "Camera initializing...",
                "tr": "Kamera başlatılıyor..."
            },
            "camera_stopped": {
                "en": "Camera stopped",
                "tr": "Kamera durduruldu"
            },
            "camera_ready": {
                "en": "Click the \"Start\" button to activate the camera",
                "tr": "Kamerayı etkinleştirmek için \"Başlat\" düğmesine tıklayın"
            },
            "camera_start_message": {
                "en": "Click the \"Start\" button to begin color detection",
                "tr": "Renk tespitini başlatmak için \"Başlat\" düğmesine tıklayın"
            },
            "ready": {
                "en": "Ready",
                "tr": "Hazır"
            },
            
            # Button texts
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
                "en": "App Gallery",
                "tr": "Uygulama Galerisi"
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
            
            # Settings
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
            
            # Image settings
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
            "interface": {
                "en": "Interface",
                "tr": "Arayüz"
            },
            "language": {
                "en": "Language",
                "tr": "Dil"
            },
            "theme": {
                "en": "Theme",
                "tr": "Tema"
            },
            "dark": {
                "en": "Dark",
                "tr": "Koyu"
            },
            "light": {
                "en": "Light",
                "tr": "Aydınlık"
            },
            "theme_tooltip": {
                "en": "Choose application appearance",
                "tr": "Uygulama görünümünü seçin"
            },
            
            # About
            "about": {
                "en": "About",
                "tr": "Hakkında"
            },
            "about_text": {
                "en": "Whisper of Colors\nVersion 1.1\n\nRemove the barriers, reveal your color.",
                "tr": "Renklerin Fısıltısı\nSürüm 1.1\n\nSınırları kaldır, rengini belli et."
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
            
            # Dialog texts
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
            
            # Color names
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
            },
            
            # Permissions
            "camera_permission_title": {
                "en": "Camera Permission",
                "tr": "Kamera İzni"
            },
            "camera_permission_text": {
                "en": "ColorVisionAid needs access to your camera to detect colors.",
                "tr": "ColorVisionAid renkleri algılamak için kamera erişimine ihtiyaç duyar."
            },
            
            # Camera permission buttons
            "grant_permission": {
                "en": "Allow Access",
                "tr": "Erişime İzin Ver"
            },
            "deny_permission": {
                "en": "Deny Access",
                "tr": "Erişimi Reddet"
            },
            "camera_permission_denied": {
                "en": "Camera access denied",
                "tr": "Kamera erişimi reddedildi"
            },
            "remember_decision": {
                "en": "Remember my decision",
                "tr": "Kararımı hatırla"
            },
            "permission_reset": {
                "en": "Camera permission reset successfully",
                "tr": "Kamera izinleri başarıyla sıfırlandı"
            },
            "reset_camera_permission": {
                "en": "Reset Camera Permission",
                "tr": "Kamera İznini Sıfırla"
            },
            "camera_settings": {
                "en": "Camera Settings",
                "tr": "Kamera Ayarları"
            },
            "camera_settings_info": {
                "en": "Control how the app accesses your camera.",
                "tr": "Uygulamanın kameranıza nasıl erişeceğini kontrol edin."
            },
            "current_permission_status": {
                "en": "Current status",
                "tr": "Mevcut durum"
            },
            "permission_status_granted": {
                "en": "Access granted",
                "tr": "Erişim izni verildi"
            },
            "permission_status_denied": {
                "en": "Access denied",
                "tr": "Erişim reddedildi"
            },
            "permission_status_ask": {
                "en": "Ask each time",
                "tr": "Her seferinde sor"
            },
            
            # Button tooltips
            "start_tooltip": {
                "en": "Start the camera to begin detecting colors",
                "tr": "Renk algılamaya başlamak için kamerayı başlatın"
            },
            "stop_tooltip": {
                "en": "Stop the camera and color detection",
                "tr": "Kamerayı ve renk algılamayı durdurun"
            },
            "snapshot_tooltip": {
                "en": "Take a snapshot of the current camera view",
                "tr": "Mevcut kamera görüntüsünün ekran görüntüsünü alın"
            },
            "gallery_tooltip": {
                "en": "View your saved snapshots",
                "tr": "Kayıtlı ekran görüntülerinizi görüntüleyin"
            },
            "load_file": {
                "en": "Upload Photo",
                "tr": "Fotoğraf Yükle"
            },
            "load_file_tooltip": {
                "en": "Load and analyze colors in an image file",
                "tr": "Bir resim dosyası yükleyin ve renklerini analiz edin"
            },
            "select_image_file": {
                "en": "Select Image File",
                "tr": "Resim Dosyası Seçin"
            },
            "file_load_failed": {
                "en": "Failed to load the selected file",
                "tr": "Seçilen dosya yüklenemedi"
            },
            "analyzing_file": {
                "en": "Analyzing File",
                "tr": "Dosya Analiz Ediliyor"
            },
            "file_analysis_complete": {
                "en": "File analysis completed",
                "tr": "Dosya analizi tamamlandı"
            },
            
            # Checkbox tooltips
            "red_checkbox_tooltip": {
                "en": "Enable red color detection",
                "tr": "Kırmızı renk algılamayı etkinleştir"
            },
            "green_checkbox_tooltip": {
                "en": "Enable green color detection",
                "tr": "Yeşil renk algılamayı etkinleştir"
            },
            "blue_checkbox_tooltip": {
                "en": "Enable blue color detection",
                "tr": "Mavi renk algılamayı etkinleştir"
            },
            "yellow_checkbox_tooltip": {
                "en": "Enable yellow color detection",
                "tr": "Sarı renk algılamayı etkinleştir"
            },
            
            # Slider tooltips
            "sensitivity_tooltip": {
                "en": "Adjust how sensitive the detection is",
                "tr": "Algılamanın ne kadar hassas olacağını ayarlayın"
            },
            
            # Permission button tooltips
            "grant_permission_tooltip": {
                "en": "Allow camera access for color detection",
                "tr": "Renk tespiti için kamera erişimine izin ver"
            },
            "deny_permission_tooltip": {
                "en": "Deny camera access (color detection will not work)",
                "tr": "Kamera erişimini reddet (renk tespiti çalışmayacak)"
            },
            "remember_decision_tooltip": {
                "en": "Save this choice for future sessions",
                "tr": "Bu seçimi gelecek oturumlar için kaydet"
            },
            
            # Color blindness types
            "color_blindness_type": {
                "en": "Color Blindness Type",
                "tr": "Renk Körlüğü Türü"
            },
            "color_blindness_type_tooltip": {
                "en": "Select your type of color blindness for optimal detection",
                "tr": "En iyi algılama için renk körlüğü türünüzü seçin"
            },
            "protanopia": {
                "en": "Protanopia (Red Vision Deficiency)",
                "tr": "Protanopi (Kırmızı Görme Zorluğu)"
            },
            "deuteranopia": {
                "en": "Deuteranopia (Green Vision Deficiency)",
                "tr": "Deuteranopi (Yeşil Görme Zorluğu)"
            },
            "tritanopia": {
                "en": "Tritanopia (Blue Vision Deficiency)",
                "tr": "Tritanopi (Mavi Görme Zorluğu)"
            },
            "red_green_colorblind": {
                "en": "Red-Green Color Vision Deficiency",
                "tr": "Kırmızı-Yeşil Renk Körlüğü"
            },
            "blue_yellow_colorblind": {
                "en": "Blue-Yellow Color Vision Deficiency", 
                "tr": "Mavi-Sarı Renk Körlüğü"
            },
            "complete_colorblind": {
                "en": "Complete Color Vision Deficiency",
                "tr": "Tam Renk Körlüğü"
            },
            "custom_colors": {
                "en": "Custom Colors",
                "tr": "Özel Renkler"
            },
            
            # Advanced settings
            "advanced_settings": {
                "en": "Advanced Settings",
                "tr": "Gelişmiş Ayarlar"
            },
            "advanced_settings_tooltip": {
                "en": "Open advanced color detection and sensitivity settings",
                "tr": "Gelişmiş renk algılama ve hassasiyet ayarlarını aç"
            },
            "debug_mode": {
                "en": "Debug Mode",
                "tr": "Debug Modu"
            },
            "debug_mode_tooltip": {
                "en": "Show skin tone filtering debug information",
                "tr": "Ten rengi filtreleme debug bilgilerini göster"
            },
            "manual_color_selection": {
                "en": "Manual Color Selection",
                "tr": "Manuel Renk Seçimi"
            },
            "detection_parameters": {
                "en": "Detection Parameters",
                "tr": "Algılama Parametreleri"
            },
            
            # Short tab titles (to prevent overflow)
            "color_selection_short": {
                "en": "Colors",
                "tr": "Renkler"
            },
            "parameters_short": {
                "en": "Settings", 
                "tr": "Ayarlar"
            },
            "filtering_short": {
                "en": "Filters",
                "tr": "Filtreler"
            },
            
            "real_world_sensitivity": {
                "en": "Detection Sensitivity",
                "tr": "Algılama Hassasiyeti"
            },
            "real_world_sensitivity_tooltip": {
                "en": "Higher values detect distant objects better, lower values provide more stability",
                "tr": "Yüksek değerler uzak nesneleri daha iyi algılar, düşük değerler daha kararlılık sağlar"
            },
            "color_filtering": {
                "en": "Color Filtering",
                "tr": "Renk Filtreleme"
            },
            "skin_tone_filtering": {
                "en": "Skin Tone Filtering",
                "tr": "Ten Rengi Filtreleme"
            },
            "skin_tone_filtering_tooltip": {
                "en": "Prevents skin tones from being detected as red colors",
                "tr": "Ten renklerinin kırmızı renk olarak algılanmasını engeller"
            },
            "stability_enhancement": {
                "en": "Stability Enhancement",
                "tr": "Kararlılık Geliştirme"
            },
            "stability_enhancement_tooltip": {
                "en": "Reduces flickering and improves detection consistency",
                "tr": "Titreşimi azaltır ve algılama tutarlılığını artırır"
            },
            
            # Dialog buttons
            "apply": {
                "en": "Apply",
                "tr": "Uygula"
            },
            "ok": {
                "en": "OK",
                "tr": "Tamam"
            },
            "save": {
                "en": "Save",
                "tr": "Kaydet"
            },
            "cancel": {
                "en": "Cancel",
                "tr": "İptal"
            },
            
            # Advanced settings descriptions
            "manual_color_selection_desc": {
                "en": "Manually select which colors you want to detect. This gives you full control over color detection.",
                "tr": "Algılamak istediğiniz renkleri manuel olarak seçin. Bu size renk algılama üzerinde tam kontrol verir."
            },
            "detection_parameters_desc": {
                "en": "Adjust detection sensitivity for optimal performance. Higher values detect distant objects better.",
                "tr": "Optimal performans için algılama hassasiyetini ayarlayın. Yüksek değerler uzak nesneleri daha iyi algılar."
            },
            "color_filtering_desc": {
                "en": "Configure advanced filtering options to reduce false detections and improve accuracy.",
                "tr": "Yanlış algılamaları azaltmak ve doğruluğu artırmak için gelişmiş filtreleme seçeneklerini yapılandırın."
            },
            "select_colors_to_detect": {
                "en": "Select Colors to Detect",
                "tr": "Algılanacak Renkleri Seçin"
            },
            "enable_skin_tone_filtering": {
                "en": "Enable skin tone filtering",
                "tr": "Ten rengi filtrelemeyi etkinleştir"
            },
            "enable_stability_enhancement": {
                "en": "Enable stability enhancement",
                "tr": "Kararlılık geliştirmeyi etkinleştir"
            },
            "skin_tone_filtering_explanation": {
                "en": "Prevents skin tones from being detected as red colors. Highly recommended for accurate red detection.",
                "tr": "Ten renklerinin kırmızı renk olarak algılanmasını engeller. Doğru kırmızı algılama için şiddetle tavsiye edilir."
            },
            "stability_enhancement_explanation": {
                "en": "Reduces flickering and improves detection consistency, especially for distant objects.",
                "tr": "Titreşimi azaltır ve özellikle uzak nesneler için algılama tutarlılığını artırır."
            },
            "low": {
                "en": "Low",
                "tr": "Düşük"
            },
            "high": {
                "en": "High",
                "tr": "Yüksek"
            },
            "low_sensitivity_desc": {
                "en": "Very stable detection, only close and clear objects. Best for reducing false detections.",
                "tr": "Çok kararlı algılama, sadece yakın ve net nesneler. Yanlış algılamaları azaltmak için en iyisi."
            },
            "medium_sensitivity_desc": {
                "en": "Balanced detection for everyday use. Good compromise between stability and range.",
                "tr": "Günlük kullanım için dengeli algılama. Kararlılık ve menzil arasında iyi bir denge."
            },
            "high_sensitivity_desc": {
                "en": "Detects distant and small objects. May have more false detections but catches everything.",
                "tr": "Uzak ve küçük nesneleri algılar. Daha fazla yanlış algılama olabilir ama her şeyi yakalar."
            }
        }
    
    def set_language(self, language_code):
        if language_code in self.LANGUAGES:
            self.current_language = language_code
            return True
        return False
    
    def get_text(self, key, *arguments):
        if key in self._translations and self.current_language in self._translations[key]:
            text = self._translations[key][self.current_language]
            if arguments:
                return text.format(*arguments)
            return text        
        # Fallback to English if translation not found
        if key in self._translations and "en" in self._translations[key]:
            text = self._translations[key]["en"]
            if arguments:
                return text.format(*arguments)
            return text
        
        # Return the key as a last resort
        return key
# Create a global instance for easy access
translator = Translations()
