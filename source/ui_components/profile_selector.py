"""
Auto-saving profile selector widget for ColorVisionAid
Simple dropdown that automatically saves changes to current profile
"""

from PyQt5.QtWidgets import (QGroupBox, QVBoxLayout, QComboBox, QPushButton, 
                           QHBoxLayout, QMessageBox, QInputDialog, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from .groups import _apply_combo_theme
from ..profile_manager import ProfileManager, UserProfile
from ..translations import translator as tr
from datetime import datetime


class ProfileSelector(QGroupBox):
    """Auto-saving profile selector widget"""
    
    profile_changed = pyqtSignal(str)  # Signal when profile changes
    
    def __init__(self, parent=None):
        super().__init__(tr.get_text("current_profile"), parent)
        self.parent_window = parent
        self.profile_manager = ProfileManager()
        self._auto_save_enabled = True
        self.setup_ui()
        self.load_profiles()
        self.apply_theme()
        
    def setup_ui(self):
        """Setup the profile selector UI"""
        layout = QVBoxLayout(self)
        
        # Profile selector with dropdown menu
        selector_layout = QHBoxLayout()
        
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumHeight(35)
        self.profile_combo.currentTextChanged.connect(self.on_profile_selected)
        
        # Add profile button (+ icon)
        self.add_profile_btn = QPushButton("➕")
        self.add_profile_btn.setMaximumWidth(32)
        self.add_profile_btn.setMinimumHeight(32)
        self.add_profile_btn.setToolTip(tr.get_text("create_new_profile"))
        self.add_profile_btn.clicked.connect(self.create_new_profile)
        
        # Profile menu button (⚙ icon - more visible than ⋮)
        self.menu_btn = QPushButton("⚙")
        self.menu_btn.setMaximumWidth(32)
        self.menu_btn.setMinimumHeight(32)
        self.menu_btn.setToolTip(tr.get_text("profile_options"))
        self.menu_btn.clicked.connect(self.show_profile_menu)
        
        selector_layout.addWidget(self.profile_combo)
        selector_layout.addWidget(self.add_profile_btn)
        selector_layout.addWidget(self.menu_btn)
        
        layout.addLayout(selector_layout)
        
    def load_profiles(self):
        """Load all profiles into the dropdown"""
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        
        profiles = self.profile_manager.get_all_profiles()
        
        if not profiles:
            # No profiles exist, show create option
            self.profile_combo.addItem(tr.get_text("create_first_profile"))
        else:
            # Add all profiles
            for profile_name in profiles:
                self.profile_combo.addItem(profile_name)
            
            # Set current profile
            if hasattr(self.parent_window, 'current_profile') and self.parent_window.current_profile:
                current_name = self.parent_window.current_profile.name
                index = self.profile_combo.findText(current_name)
                if index >= 0:
                    self.profile_combo.setCurrentIndex(index)
        
        self.profile_combo.blockSignals(False)
        
    def on_profile_selected(self, profile_name):
        """Handle profile selection from dropdown"""
        if not profile_name or profile_name == tr.get_text("create_first_profile"):
            self.create_new_profile()
            return
            
        # Load the selected profile
        profile = self.profile_manager.load_profile(profile_name)
        if profile:
            self.apply_profile_to_main_window(profile)
            self.profile_changed.emit(profile_name)
            
            # Update status
            if hasattr(self.parent_window, 'status_bar'):
                self.parent_window.status_bar.showMessage(
                    tr.get_text("profile_loaded_successfully", profile_name), 2000
                )
    
    def create_new_profile(self):
        """Create a new profile from current settings"""
        # Get new profile name from user
        name, ok = QInputDialog.getText(
            self, 
            tr.get_text("create_new_profile"),
            tr.get_text("enter_profile_name") + ":"
        )
        
        if ok and name.strip():
            name = name.strip()
            
            # Check if profile already exists
            existing_profiles = self.profile_manager.get_all_profiles()
            if name in existing_profiles:
                QMessageBox.warning(
                    self, 
                    tr.get_text("profile_exists"), 
                    tr.get_text("profile_name_already_exists", name)
                )
                return
            
            # Create profile from current settings
            profile = self.create_profile_from_current_settings(name)
            if profile and self.profile_manager.save_profile(profile):
                # Update current profile
                self.parent_window.current_profile = profile
                
                # Reload profiles and select the new one
                self.load_profiles()
                index = self.profile_combo.findText(name)
                if index >= 0:
                    self.profile_combo.setCurrentIndex(index)
                
                self.profile_changed.emit(name)
                QMessageBox.information(
                    self, 
                    tr.get_text("success"), 
                    tr.get_text("profile_created_successfully", name)
                )
            else:
                QMessageBox.critical(
                    self, 
                    tr.get_text("error"), 
                    tr.get_text("failed_to_create_profile")
                )
    
    def show_profile_menu(self):
        """Show profile management menu"""
        menu = QMenu(self)
        
        current_profile_name = self.profile_combo.currentText()
        
        # Rename profile
        if current_profile_name and current_profile_name != tr.get_text("create_first_profile"):
            rename_action = menu.addAction("✏️ " + tr.get_text("rename_profile"))
            rename_action.triggered.connect(lambda: self.rename_profile(current_profile_name))
            
            # Delete profile (only if more than one exists)
            profiles = self.profile_manager.get_all_profiles()
            if len(profiles) > 1:
                delete_action = menu.addAction("🗑️ " + tr.get_text("delete_profile"))
                delete_action.triggered.connect(lambda: self.delete_profile(current_profile_name))
        
        # Duplicate profile
        if current_profile_name and current_profile_name != tr.get_text("create_first_profile"):
            menu.addSeparator()
            duplicate_action = menu.addAction("📋 " + tr.get_text("duplicate_profile"))
            duplicate_action.triggered.connect(lambda: self.duplicate_profile(current_profile_name))
        
        menu.exec_(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))
    
    def rename_profile(self, old_name):
        """Rename current profile"""
        new_name, ok = QInputDialog.getText(
            self, 
            tr.get_text("rename_profile"),
            tr.get_text("enter_new_profile_name") + ":",
            text=old_name
        )
        
        if ok and new_name.strip() and new_name.strip() != old_name:
            new_name = new_name.strip()
            
            # Check if new name already exists
            existing_profiles = self.profile_manager.get_all_profiles()
            if new_name in existing_profiles:
                QMessageBox.warning(
                    self, 
                    tr.get_text("profile_exists"), 
                    tr.get_text("profile_name_already_exists", new_name)
                )
                return
            
            # Rename profile
            if self.profile_manager.rename_profile(old_name, new_name):
                # Update current profile reference
                if hasattr(self.parent_window, 'current_profile') and self.parent_window.current_profile:
                    self.parent_window.current_profile.name = new_name
                
                # Reload and select renamed profile
                self.load_profiles()
                index = self.profile_combo.findText(new_name)
                if index >= 0:
                    self.profile_combo.setCurrentIndex(index)
                
                QMessageBox.information(
                    self, 
                    tr.get_text("success"), 
                    tr.get_text("profile_renamed_successfully", old_name, new_name)
                )
            else:
                QMessageBox.critical(
                    self, 
                    tr.get_text("error"), 
                    tr.get_text("failed_to_rename_profile")
                )
    
    def delete_profile(self, profile_name):
        """Delete current profile"""
        reply = QMessageBox.question(
            self, 
            tr.get_text("confirm_deletion"), 
            tr.get_text("are_you_sure_delete_profile", profile_name)
        )
        
        if reply == QMessageBox.Yes:
            if self.profile_manager.delete_profile(profile_name):
                # Load first available profile or create default
                profiles = self.profile_manager.get_all_profiles()
                if profiles:
                    # Load first available profile
                    first_profile = self.profile_manager.load_profile(profiles[0])
                    if first_profile:
                        self.apply_profile_to_main_window(first_profile)
                else:
                    # Create default profile
                    default_profile = self.profile_manager.create_profile("Default Profile")
                    self.profile_manager.save_profile(default_profile)
                    self.apply_profile_to_main_window(default_profile)
                
                self.load_profiles()
                QMessageBox.information(
                    self, 
                    tr.get_text("success"), 
                    tr.get_text("profile_deleted_successfully")
                )
            else:
                QMessageBox.critical(
                    self, 
                    tr.get_text("error"), 
                    tr.get_text("failed_to_delete_profile")
                )
    
    def duplicate_profile(self, profile_name):
        """Duplicate current profile"""
        new_name, ok = QInputDialog.getText(
            self, 
            tr.get_text("duplicate_profile"),
            tr.get_text("enter_profile_name") + ":",
            text=f"{profile_name} Copy"
        )
        
        if ok and new_name.strip():
            new_name = new_name.strip()
            
            # Check if new name already exists
            existing_profiles = self.profile_manager.get_all_profiles()
            if new_name in existing_profiles:
                QMessageBox.warning(
                    self, 
                    tr.get_text("profile_exists"), 
                    tr.get_text("profile_name_already_exists", new_name)
                )
                return
            
            # Load original profile and duplicate
            original_profile = self.profile_manager.load_profile(profile_name)
            if original_profile:
                # Create copy with new name
                duplicate_profile = UserProfile(
                    name=new_name,
                    color_blindness_type=original_profile.color_blindness_type,
                    language=original_profile.language,
                    theme=original_profile.theme,
                    window_width=original_profile.window_width,
                    window_height=original_profile.window_height,
                    window_x=original_profile.window_x,
                    window_y=original_profile.window_y,
                    is_maximized=original_profile.is_maximized,
                    camera_permission=original_profile.camera_permission,
                    detection_sensitivity=original_profile.detection_sensitivity,
                    color_enhancement=original_profile.color_enhancement,
                    voice_feedback=original_profile.voice_feedback,
                    auto_detection=original_profile.auto_detection,
                    filter_strength=original_profile.filter_strength,
                    created_date=datetime.now().isoformat(),
                    last_used_date=datetime.now().isoformat()
                )
                
                if self.profile_manager.save_profile(duplicate_profile):
                    self.load_profiles()
                    index = self.profile_combo.findText(new_name)
                    if index >= 0:
                        self.profile_combo.setCurrentIndex(index)
                    
                    QMessageBox.information(
                        self, 
                        tr.get_text("success"), 
                        tr.get_text("profile_duplicated_successfully", new_name)
                    )
                else:
                    QMessageBox.critical(
                        self, 
                        tr.get_text("error"), 
                        tr.get_text("failed_to_duplicate_profile")
                    )
    
    def create_profile_from_current_settings(self, name):
        """Create a profile from current main window settings"""
        if not self.parent_window:
            return None
            
        profile = UserProfile(
            name=name,
            created_date=datetime.now().isoformat(),
            last_used_date=datetime.now().isoformat()
        )
        
        # Get color blindness type
        if hasattr(self.parent_window, 'color_blindness_combo'):
            cb_index = self.parent_window.color_blindness_combo.currentIndex()
            cb_types = ["none", "protanopia", "deuteranopia", "tritanopia"]
            if 0 <= cb_index < len(cb_types):
                profile.color_blindness_type = cb_types[cb_index]
        
        # Get language
        if hasattr(self.parent_window, 'language_combo'):
            lang_index = self.parent_window.language_combo.currentIndex()
            lang_codes = ["en", "tr"]
            if 0 <= lang_index < len(lang_codes):
                profile.language = lang_codes[lang_index]
        
        # Get theme
        profile.theme = getattr(self.parent_window, 'theme', 'dark')
        
        # Get window properties
        profile.window_width = self.parent_window.width()
        profile.window_height = self.parent_window.height()
        profile.window_x = self.parent_window.x()
        profile.window_y = self.parent_window.y()
        profile.is_maximized = self.parent_window.isMaximized()
        
        # Get camera permission
        profile.camera_permission = getattr(self.parent_window, 'camera_permission', 'ask')
        
        # Get advanced settings
        settings = self.parent_window.settings
        profile.detection_sensitivity = float(settings.value("detection_sensitivity", 0.5))
        profile.color_enhancement = settings.value("color_enhancement", True, type=bool)
        profile.voice_feedback = settings.value("voice_feedback", False, type=bool)
        profile.auto_detection = settings.value("auto_detection", True, type=bool)
        profile.filter_strength = float(settings.value("filter_strength", 1.0))
        
        return profile
    
    def apply_profile_to_main_window(self, profile):
        """Apply profile settings to main window"""
        if not self.parent_window:
            return
        
        # Update current profile
        self.parent_window.current_profile = profile
        
        # Apply to QSettings
        self.profile_manager.apply_profile_to_settings(profile)
        
        # Temporarily disable auto-save to prevent infinite loop
        self._auto_save_enabled = False
        
        try:
            # Update UI elements
            # Language
            if hasattr(self.parent_window, 'language_combo'):
                lang_codes = ["en", "tr"]
                if profile.language in lang_codes:
                    index = lang_codes.index(profile.language)
                    self.parent_window.language_combo.blockSignals(True)
                    self.parent_window.language_combo.setCurrentIndex(index)
                    self.parent_window.language_combo.blockSignals(False)
                    
                    # Apply language change
                    tr.set_language(profile.language)
                    self.parent_window.update_ui_language()
            
            # Theme
            if hasattr(self.parent_window, 'theme_combo'):
                themes = ["dark", "light"]
                if profile.theme in themes:
                    index = themes.index(profile.theme)
                    self.parent_window.theme_combo.blockSignals(True)
                    self.parent_window.theme_combo.setCurrentIndex(index)
                    self.parent_window.theme_combo.blockSignals(False)
                    
                    # Apply theme change
                    self.parent_window.theme = profile.theme
                    self.parent_window._apply_window_theme()
                    from ..ui_components import apply_theme
                    apply_theme(self.parent_window, self.parent_window.theme)
                    if hasattr(self.parent_window, 'apply_theme_to_components'):
                        self.parent_window.apply_theme_to_components()
                    
                    # Force refresh all group boxes to apply new theme
                    if hasattr(self.parent_window, '_force_refresh_group_boxes'):
                        self.parent_window._force_refresh_group_boxes()
                    
                    # Update profile selector theme
                    self.apply_theme()
            
            # Color blindness type
            if hasattr(self.parent_window, 'color_blindness_combo'):
                cb_types = ["none", "protanopia", "deuteranopia", "tritanopia"]
                if profile.color_blindness_type in cb_types:
                    index = cb_types.index(profile.color_blindness_type)
                    self.parent_window.color_blindness_combo.blockSignals(True)
                    self.parent_window.color_blindness_combo.setCurrentIndex(index)
                    self.parent_window.color_blindness_combo.blockSignals(False)
            
            # DON'T change window position/size when switching profiles
            # Window properties will only be applied on application startup
            
            # Camera permission
            self.parent_window.camera_permission = profile.camera_permission
            
        finally:
            # Re-enable auto-save
            self._auto_save_enabled = True
    
    def auto_save_current_profile(self):
        """Automatically save current settings to active profile"""
        if not self._auto_save_enabled:
            return
            
        if not hasattr(self.parent_window, 'current_profile') or not self.parent_window.current_profile:
            return
        
        # Update current profile with latest settings
        profile = self.create_profile_from_current_settings(self.parent_window.current_profile.name)
        if profile:
            # Keep original creation date
            profile.created_date = self.parent_window.current_profile.created_date
            profile.last_used_date = datetime.now().isoformat()
            
            # Save profile
            self.profile_manager.save_profile(profile)
            self.parent_window.current_profile = profile
    
    def apply_theme(self):
        """Apply current theme to profile selector"""
        # Get theme from parent window or current profile or default
        theme = "dark"  # Default theme
        
        if hasattr(self.parent_window, 'theme') and self.parent_window.theme:
            theme = self.parent_window.theme
        elif hasattr(self.parent_window, 'current_profile') and self.parent_window.current_profile:
            theme = self.parent_window.current_profile.theme
        elif hasattr(self.parent_window, 'settings'):
            theme = self.parent_window.settings.value("theme", "dark")
        
        if theme == "light":
            # Apply only group and button styles at the container level; combo gets its own theme below
            self.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #E0E0E0;
                    border-radius: 5px;
                    margin: 8px 0px;
                    padding-top: 10px;
                    background-color: #FAFAFA;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px 0 8px;
                    color: #1976D2;
                }
                QPushButton {
                    background-color: #F8F9FA;
                    color: #495057;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12pt;
                    padding: 1px;
                }
                QPushButton:hover {
                    background-color: #E9ECEF;
                    color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #DEE2E6;
                }
            """)
        else:
            # Apply only group and button styles at the container level; combo gets its own theme below
            self.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #444;
                    border-radius: 5px;
                    margin: 8px 0px;
                    padding-top: 10px;
                    background-color: #333;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px 0 8px;
                    color: #64B5F6;
                }
                QPushButton {
                    background-color: #3A3A3A;
                    color: #CCC;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12pt;
                    padding: 1px;
                }
                QPushButton:hover {
                    background-color: #4A4A4A;
                    color: #64B5F6;
                }
                QPushButton:pressed {
                    background-color: #5A5A5A;
                }
            """)
        
        # Apply consistent, theme-aware combo styling with SVG arrow icon
        if hasattr(self, 'profile_combo'):
            _apply_combo_theme(self.profile_combo, self.parent_window)
            self.profile_combo.update()
            self.profile_combo.repaint()
        
        # Force update the buttons to apply new styles immediately
        if hasattr(self, 'add_profile_btn'):
            self.add_profile_btn.update()
            self.add_profile_btn.repaint()
        if hasattr(self, 'menu_btn'):
            self.menu_btn.update()
            self.menu_btn.repaint()
        
        # Force update the entire widget
        self.update()
        self.repaint()
