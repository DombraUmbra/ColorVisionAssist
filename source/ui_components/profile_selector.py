"""
Auto-saving profile selector widget for ColorVisionAid
Simple dropdown that automatically saves changes to current profile
"""

from PyQt5.QtWidgets import (QGroupBox, QVBoxLayout, QComboBox, QPushButton, 
                           QHBoxLayout, QMessageBox, QInputDialog, QMenu, QDialog, QLineEdit, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from .groups import _apply_combo_theme, HiddenCurrentCombo
from ..profile_manager import ProfileManager, UserProfile
from ..translations import translator as tr
from datetime import datetime
from .buttons import update_button_theme


class ProfileSelector(QGroupBox):
    """Auto-saving profile selector widget"""
    
    profile_changed = pyqtSignal(str)  # Signal when profile changes
    
    def __init__(self, parent=None):
        super().__init__(tr.get_text("current_profile"), parent)
        self.parent_window = parent
        self.profile_manager = ProfileManager()
        # Start with autosave disabled to prevent overwriting during startup
        self._auto_save_enabled = False
        self.setup_ui()
        self.load_profiles()
        self.apply_theme()
        
        # Enable autosave after initialization is complete
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(500, lambda: setattr(self, '_auto_save_enabled', True))
        
    def setup_ui(self):
        """Setup the profile selector UI"""
        layout = QVBoxLayout(self)

        # Profile selector with dropdown menu
        selector_layout = QHBoxLayout()

        self.profile_combo = HiddenCurrentCombo()
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

        selector_layout.addWidget(self.profile_combo, 1)
        selector_layout.addWidget(self.add_profile_btn)
        selector_layout.addWidget(self.menu_btn)

        layout.addLayout(selector_layout)
    
    def _get_theme(self) -> str:
        return (getattr(self.parent_window, 'theme', 'dark') if self.parent_window else 'dark').lower()

    def _apply_dialog_stylesheet(self, widget):
        theme = self._get_theme()
        if theme == 'light':
            widget.setStyleSheet(
                """
                QDialog, QMessageBox { background-color: #F5F5F7; color: #222; }
                QLabel { color: #222; }
                QLineEdit { background-color: #FFFFFF; color: #222; border: 1px solid #CCCCCC; border-radius: 4px; padding: 6px; }
                QPushButton { background-color: #F8F9FA; color: #495057; border: none; border-radius: 4px; font-weight: bold; padding: 6px 10px; }
                QPushButton:hover { background-color: #E9ECEF; color: #1976D2; }
                QPushButton:pressed { background-color: #DEE2E6; }
                """
            )
        else:
            widget.setStyleSheet(
                """
                QDialog, QMessageBox { background-color: #2b2b2b; color: #EEE; }
                QLabel { color: #EEE; }
                QLineEdit { background-color: #333; color: #EEE; border: 1px solid #555; border-radius: 4px; padding: 6px; }
                QPushButton { background-color: #3A3A3A; color: #CCC; border: none; border-radius: 4px; font-weight: bold; padding: 6px 10px; }
                QPushButton:hover { background-color: #4A4A4A; color: #64B5F6; }
                QPushButton:pressed { background-color: #5A5A5A; }
                """
            )

    def _menu_stylesheet(self) -> str:
        theme = self._get_theme()
        if theme == 'light':
            return (
                """
                QMenu { background-color: #FFFFFF; color: #222; border: 1px solid #DDD; }
                QMenu::item { padding: 6px 16px; }
                QMenu::item:selected { background: #E9ECEF; color: #1976D2; }
                QMenu::separator { height: 1px; background: #DDD; margin: 4px 8px; }
                """
            )
        else:
            return (
                """
                QMenu { background-color: #2b2b2b; color: #EEE; border: 1px solid #555; }
                QMenu::item { padding: 6px 16px; }
                QMenu::item:selected { background: #3A3A3A; color: #64B5F6; }
                QMenu::separator { height: 1px; background: #555; margin: 4px 8px; }
                """
            )

    def _message_box(self, icon: QMessageBox.Icon, title: str, text: str, buttons=QMessageBox.Ok) -> int:
        box = QMessageBox(self)
        # Apply themed content stylesheet
        self._apply_dialog_stylesheet(box)
        box.setIcon(icon)
        box.setWindowTitle(title)
        box.setText(text)
        # Prefer non-native dialog so we can style and get a close (X) button reliably
        try:
            box.setOption(QMessageBox.DontUseNativeDialog, True)
        except Exception:
            pass
        # Ensure title/close buttons visible and help button hidden
        try:
            box.setWindowFlags(box.windowFlags() | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            box.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        except Exception:
            pass
        # Apply Windows title bar dark/light mode like in themed_get_text
        try:
            self._apply_title_bar_theme(box)
            # Re-apply after show with a slight delay to survive OS repaint
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(50, lambda: self._apply_title_bar_theme(box))
        except Exception:
            pass
        box.setStandardButtons(buttons)
        return box.exec_()

    def themed_info(self, title: str, text: str):
        self._message_box(QMessageBox.Information, title, text, QMessageBox.Ok)

    def themed_warning(self, title: str, text: str):
        self._message_box(QMessageBox.Warning, title, text, QMessageBox.Ok)

    def themed_error(self, title: str, text: str):
        self._message_box(QMessageBox.Critical, title, text, QMessageBox.Ok)

    def themed_question(self, title: str, text: str) -> int:
        """Themed question dialog with localized Yes/No labels."""
        box = QMessageBox(self)
        self._apply_dialog_stylesheet(box)
        box.setIcon(QMessageBox.Question)
        # Use Qt's non-native dialog to ensure the Close (X) button is enabled on Windows
        try:
            box.setOption(QMessageBox.DontUseNativeDialog, True)
        except Exception:
            pass
        box.setWindowTitle(title)
        box.setText(text)
        # Ensure close (X) button is present and help button hidden
        box.setWindowFlags(box.windowFlags() | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        box.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        box.setStandardButtons(QMessageBox.NoButton)
        # Consistent order: No (left), Yes (right), preserve insertion order
        no_btn = box.addButton(tr.get_text("no"), QMessageBox.ActionRole)
        yes_btn = box.addButton(tr.get_text("yes"), QMessageBox.ActionRole)
        # Make window close (X) behave like No and Enter like Yes
        try:
            box.setEscapeButton(no_btn)
            box.setDefaultButton(yes_btn)
        except Exception:
            pass
        # Apply CB-aware button theming (Yes = 'start', No = 'stop')
        try:
            theme = self._get_theme()
            cb_type = 'none'
            if getattr(self, 'parent_window', None) and getattr(self.parent_window, 'current_profile', None):
                cb_type = getattr(self.parent_window.current_profile, 'color_blindness_type', 'none') or 'none'
            update_button_theme(yes_btn, 'start', theme, cb_type)
            update_button_theme(no_btn, 'stop', theme, cb_type)
            # Keep reasonable minimum widths for readability
            try:
                yes_btn.setMinimumWidth(84)
                no_btn.setMinimumWidth(84)
            except Exception:
                pass
        except Exception:
            pass
        # Apply dark/light title bar on Windows
        try:
            self._apply_title_bar_theme(box)
        except Exception:
            pass
        # If the dialog is closed via (X), treat as No
        box.exec_()
        if box.clickedButton() is yes_btn:
            return QMessageBox.Yes
        return QMessageBox.No

    def themed_get_text(self, title: str, label: str, text: str = ""):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        # Remove '?' button and keep only title + close
        dialog.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        dialog.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        # Make sure the dialog is wide enough for the title to be fully readable
        dialog.setMinimumWidth(560)
        dialog.resize(560, 100)

        # Apply app icon if available
        try:
            import os
            from PyQt5.QtGui import QIcon
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            icon_path = os.path.join(base_dir, "icons", "app_icon.png")
            if os.path.exists(icon_path):
                dialog.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass

        # Apply dark/light themed title bar (Windows) and stylesheet
        self._apply_dialog_stylesheet(dialog)
        # Slightly upscale typography and paddings for this dialog only
        dialog.setStyleSheet(dialog.styleSheet() +
            """
            QLabel { font-size: 13px; }
            QLabel#profileInputLabel { font-size: 16px; font-weight: 600; margin-bottom: 6px; }
            QLineEdit { font-size: 13px; padding: 8px 10px; }
            QPushButton { font-size: 12px; padding: 8px 14px; }
            """
        )
        self._apply_title_bar_theme(dialog)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        lbl = QLabel(label)
        lbl.setObjectName("profileInputLabel")
        # Increase label font slightly
        try:
            lblFont = lbl.font()
            lblFont.setPointSize(max(lblFont.pointSize(), 12))
            lbl.setFont(lblFont)
        except Exception:
            pass
        edit = QLineEdit()
        # Increase input height and font
        try:
            editFont = edit.font()
            editFont.setPointSize(max(editFont.pointSize(), 11))
            edit.setFont(editFont)
        except Exception:
            pass
        edit.setMinimumHeight(36)
        if text:
            edit.setText(text)
            edit.selectAll()
        # Put label and input side-by-side
        form_row = QHBoxLayout()
        form_row.setSpacing(10)
        try:
            lbl.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        except Exception:
            pass
        form_row.addWidget(lbl)
        form_row.addWidget(edit, 1)
        layout.addLayout(form_row)
        btn_row = QHBoxLayout()
        ok_btn = QPushButton(tr.get_text("save"))
        ok_btn.setObjectName("primarySaveButton")
        cancel_btn = QPushButton(tr.get_text("cancel"))
        # Make buttons larger
        for btn in (cancel_btn, ok_btn):
            try:
                btnFont = btn.font()
                btnFont.setPointSize(max(btnFont.pointSize(), 10))
                btn.setFont(btnFont)
            except Exception:
                pass
            btn.setMinimumHeight(36)
            btn.setMinimumWidth(110)
        # Apply color-blind-aware styles using unified button theming
        try:
            theme = self._get_theme()
            cb_type = 'none'
            if getattr(self, 'parent_window', None) and getattr(self.parent_window, 'current_profile', None):
                cb_type = getattr(self.parent_window.current_profile, 'color_blindness_type', 'none') or 'none'
            update_button_theme(ok_btn, 'start', theme, cb_type)
            update_button_theme(cancel_btn, 'stop', theme, cb_type)
        except Exception:
            pass
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        btn_row.setSpacing(10)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)
    # Save button color is handled via update_button_theme above (CB-aware), no extra override needed
        # Re-apply title bar theme after dialog is about to show
        try:
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(50, lambda: self._apply_title_bar_theme(dialog))
        except Exception:
            pass

        result = dialog.exec_()
        return (edit.text(), True) if result == QDialog.Accepted else (text, False)
    
    def _apply_title_bar_theme(self, widget: QDialog):
        """Apply theme-appropriate title bar on Windows for the given dialog widget."""
        try:
            theme = self._get_theme()
            import ctypes
            hwnd = int(widget.winId())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            mode_value = 1 if (theme or 'dark') == 'dark' else 0
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(mode_value)),
                ctypes.sizeof(ctypes.c_int)
            )
        except Exception:
            # Non-Windows or API not available; safely ignore
            pass
        
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
                # Normalize "Default Profile" naming across languages when listing
                current_name = self.parent_window.current_profile.name
                # If the current profile is a localized default, map to actual stored name if needed
                index = self.profile_combo.findText(current_name)
                if index >= 0:
                    self.profile_combo.setCurrentIndex(index)
        
        self.profile_combo.blockSignals(False)

    def update_ui_language(self):
        """Update groupbox title, tooltips and placeholder on language change"""
        # Update group title
        self.setTitle(tr.get_text("current_profile"))

        # Update tooltips
        if hasattr(self, 'add_profile_btn'):
            self.add_profile_btn.setToolTip(tr.get_text("create_new_profile"))
        if hasattr(self, 'menu_btn'):
            self.menu_btn.setToolTip(tr.get_text("profile_options"))

        # Refresh profiles list to localize placeholder text when there are no profiles
        current_text = self.profile_combo.currentText() if hasattr(self, 'profile_combo') else ""
        self.load_profiles()
        # Try restoring previous selection by name if it exists
        if current_text:
            index = self.profile_combo.findText(current_text)
            if index >= 0:
                self.profile_combo.setCurrentIndex(index)
        
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
        # Get new profile name from user (themed)
        name, ok = self.themed_get_text(
            tr.get_text("create_new_profile"),
            tr.get_text("enter_profile_name") + ":"
        )
        
        if ok and name.strip():
            name = name.strip()
            
            # Check if profile already exists
            existing_profiles = self.profile_manager.get_all_profiles()
            if name in existing_profiles:
                self.themed_warning(tr.get_text("profile_exists"), tr.get_text("profile_name_already_exists", name))
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
            else:
                self.themed_error(tr.get_text("error"), tr.get_text("failed_to_create_profile"))
    
    def show_profile_menu(self):
        """Show profile management menu"""
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_stylesheet())

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
        new_name, ok = self.themed_get_text(
            tr.get_text("rename_profile"),
            tr.get_text("enter_new_profile_name") + ":",
            text=old_name
        )
        
        if ok and new_name.strip() and new_name.strip() != old_name:
            new_name = new_name.strip()
            
            # Check if new name already exists
            existing_profiles = self.profile_manager.get_all_profiles()
            if new_name in existing_profiles:
                self.themed_warning(tr.get_text("profile_exists"), tr.get_text("profile_name_already_exists", new_name))
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
                
                # Suppress modal success dialog; provide lightweight feedback via status bar instead
                if hasattr(self.parent_window, 'status_bar'):
                    try:
                        self.parent_window.status_bar.showMessage(
                            tr.get_text("profile_renamed_successfully", old_name, new_name), 2000
                        )
                    except Exception:
                        pass
            else:
                self.themed_error(tr.get_text("error"), tr.get_text("failed_to_rename_profile"))
    
    def delete_profile(self, profile_name):
        """Delete current profile"""
        reply = self.themed_question(tr.get_text("confirm_deletion"), tr.get_text("are_you_sure_delete_profile", profile_name))
        
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
                    default_profile = self.profile_manager.create_profile(tr.get_text("default_profile"))
                    self.profile_manager.save_profile(default_profile)
                    self.apply_profile_to_main_window(default_profile)
                
                self.load_profiles()
                # Show lightweight feedback instead of a modal dialog
                if hasattr(self.parent_window, 'status_bar'):
                    try:
                        self.parent_window.status_bar.showMessage(tr.get_text("profile_deleted_successfully"), 2000)
                    except Exception:
                        pass
            else:
                self.themed_error(tr.get_text("error"), tr.get_text("failed_to_delete_profile"))
    
    def duplicate_profile(self, profile_name):
        """Duplicate current profile"""
        new_name, ok = self.themed_get_text(
            tr.get_text("duplicate_profile"),
            tr.get_text("enter_profile_name") + ":",
            text=f"{profile_name} {tr.get_text('copy_suffix')}"
        )
        
        if ok and new_name.strip():
            new_name = new_name.strip()
            
            # Check if new name already exists
            existing_profiles = self.profile_manager.get_all_profiles()
            if new_name in existing_profiles:
                self.themed_warning(tr.get_text("profile_exists"), tr.get_text("profile_name_already_exists", new_name))
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
                    detect_red=original_profile.detect_red,
                    detect_green=original_profile.detect_green,
                    detect_blue=original_profile.detect_blue,
                    detect_yellow=original_profile.detect_yellow,
                    skin_tone_filtering_active=original_profile.skin_tone_filtering_active,
                    stability_enhancement_active=original_profile.stability_enhancement_active,
                    debug_mode_active=original_profile.debug_mode_active,
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
                    
                    # Show lightweight feedback instead of a modal dialog
                    if hasattr(self.parent_window, 'status_bar'):
                        try:
                            self.parent_window.status_bar.showMessage(tr.get_text("profile_duplicated_successfully", new_name), 2000)
                        except Exception:
                            pass
                else:
                    self.themed_error(tr.get_text("error"), tr.get_text("failed_to_duplicate_profile"))
    
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
            # Use the new currentData method for the new combobox
            color_blindness_type = self.parent_window.color_blindness_combo.currentData()
            if color_blindness_type:
                profile.color_blindness_type = color_blindness_type
        
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
        # Manual color selections from main window checkboxes (if exist)
        try:
            if hasattr(self.parent_window, 'red_checkbox'):
                profile.detect_red = bool(self.parent_window.red_checkbox.isChecked())
            if hasattr(self.parent_window, 'green_checkbox'):
                profile.detect_green = bool(self.parent_window.green_checkbox.isChecked())
            if hasattr(self.parent_window, 'blue_checkbox'):
                profile.detect_blue = bool(self.parent_window.blue_checkbox.isChecked())
            if hasattr(self.parent_window, 'yellow_checkbox'):
                profile.detect_yellow = bool(self.parent_window.yellow_checkbox.isChecked())
        except Exception:
            pass
        # Additional advanced flags from main window state if present
        try:
            profile.skin_tone_filtering_active = bool(getattr(self.parent_window, 'skin_tone_filtering_active', profile.skin_tone_filtering_active))
            profile.stability_enhancement_active = bool(getattr(self.parent_window, 'stability_enhancement_active', profile.stability_enhancement_active))
            profile.debug_mode_active = bool(getattr(self.parent_window, 'debug_mode_active', profile.debug_mode_active))
        except Exception:
            pass
        
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
                    
                    # Update open gallery window if exists
                    if hasattr(self.parent_window, '_gallery_window') and self.parent_window._gallery_window is not None:
                        try:
                            # Force complete theme reset on gallery
                            self.parent_window._gallery_window.theme = self.parent_window.theme
                            # Clear all stylesheets first to prevent conflicts
                            self.parent_window._gallery_window.setStyleSheet("")
                            # Apply themes with forced updates
                            self.parent_window._gallery_window.apply_gallery_theme(self.parent_window.theme)
                            self.parent_window._gallery_window._force_complete_theme_application(self.parent_window.theme)
                            # Force additional update cycle
                            from PyQt5.QtCore import QTimer
                            QTimer.singleShot(50, lambda: self._delayed_gallery_update(self.parent_window._gallery_window, self.parent_window.theme))
                        except Exception as e:
                            print(f"Error updating gallery theme: {e}")
                    
                    # Force refresh all group boxes to apply new theme
                    if hasattr(self.parent_window, '_force_refresh_group_boxes'):
                        self.parent_window._force_refresh_group_boxes()
                    
                    # Update profile selector theme
                    self.apply_theme()
            
            # Color blindness type
            if hasattr(self.parent_window, 'color_blindness_combo'):
                # Use the new setCurrentData method for the new combobox
                self.parent_window.color_blindness_combo.blockSignals(True)
                success = self.parent_window.color_blindness_combo.setCurrentData(profile.color_blindness_type)
                self.parent_window.color_blindness_combo.blockSignals(False)
                
                # Update button colors for accessibility
                if hasattr(self.parent_window, 'update_button_colors_for_accessibility'):
                    self.parent_window.update_button_colors_for_accessibility(profile.color_blindness_type)
            
            # DON'T change window position/size when switching profiles
            # Window properties will only be applied on application startup
            
            # Camera permission
            self.parent_window.camera_permission = profile.camera_permission

            # Detection sensitivity (profile stores 0.1–1.0, slider expects 1–10)
            try:
                if hasattr(self.parent_window, 'sensitivity_slider'):
                    sens = float(getattr(profile, 'detection_sensitivity', 0.5))
                    slider_val = max(1, min(10, int(round(sens * 10))))
                    self.parent_window.sensitivity_slider.blockSignals(True)
                    self.parent_window.sensitivity_slider.setValue(slider_val)
                    self.parent_window.sensitivity_slider.blockSignals(False)
                # Keep QSettings in sync for restart persistence
                if hasattr(self.parent_window, 'settings'):
                    self.parent_window.settings.setValue("detection_sensitivity", float(getattr(profile, 'detection_sensitivity', 0.5)))
            except Exception:
                pass

            # Manual color selections (if checkboxes exist)
            try:
                if hasattr(self.parent_window, 'red_checkbox'):
                    self.parent_window.red_checkbox.blockSignals(True)
                    self.parent_window.red_checkbox.setChecked(bool(profile.detect_red))
                    self.parent_window.red_checkbox.blockSignals(False)
                if hasattr(self.parent_window, 'green_checkbox'):
                    self.parent_window.green_checkbox.blockSignals(True)
                    self.parent_window.green_checkbox.setChecked(bool(profile.detect_green))
                    self.parent_window.green_checkbox.blockSignals(False)
                if hasattr(self.parent_window, 'blue_checkbox'):
                    self.parent_window.blue_checkbox.blockSignals(True)
                    self.parent_window.blue_checkbox.setChecked(bool(profile.detect_blue))
                    self.parent_window.blue_checkbox.blockSignals(False)
                if hasattr(self.parent_window, 'yellow_checkbox'):
                    self.parent_window.yellow_checkbox.blockSignals(True)
                    self.parent_window.yellow_checkbox.setChecked(bool(profile.detect_yellow))
                    self.parent_window.yellow_checkbox.blockSignals(False)
            except Exception:
                pass

            # Advanced flags on main window instance
            try:
                if hasattr(self.parent_window, 'skin_tone_filtering_active'):
                    self.parent_window.skin_tone_filtering_active = bool(profile.skin_tone_filtering_active)
                if hasattr(self.parent_window, 'stability_enhancement_active'):
                    self.parent_window.stability_enhancement_active = bool(profile.stability_enhancement_active)
                if hasattr(self.parent_window, 'debug_mode_active'):
                    self.parent_window.debug_mode_active = bool(profile.debug_mode_active)
            except Exception:
                pass
            
        finally:
            # Re-enable auto-save with a small delay to prevent immediate triggering during startup
            from PyQt5.QtCore import QTimer
            def delayed_autosave_enable():
                self._auto_save_enabled = True
            QTimer.singleShot(100, delayed_autosave_enable)
    
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
            
            # Save profile to file
            self.profile_manager.save_profile(profile)
            self.parent_window.current_profile = profile
            
            # Also sync to QSettings for restart persistence, but only after profile is saved
            try:
                self.profile_manager.apply_profile_to_settings(profile)
            except Exception:
                pass
    
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

        # Determine color blindness type to adapt accent under tritanopia
        cb_type = None
        try:
            if hasattr(self.parent_window, 'color_blindness_combo') and self.parent_window.color_blindness_combo:
                cb_type = self.parent_window.color_blindness_combo.currentData()
            if not cb_type and hasattr(self.parent_window, 'current_profile') and self.parent_window.current_profile:
                cb_type = getattr(self.parent_window.current_profile, 'color_blindness_type', None)
        except Exception:
            cb_type = None

        is_tritanopia = (str(cb_type).lower() == 'tritanopia')

        # Accent colors: always use blue family accents (tritanopia uses Start-button blue too)
        accent_light = '#1976D2'
        accent_dark = '#64B5F6'

        if theme == "light":
            # Apply only group and button styles at the container level; combo gets its own theme below
            css = """
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
                    color: __ACCENT__;
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
                    color: __ACCENT__;
                }
                QPushButton:pressed {
                    background-color: #DEE2E6;
                }
            """
            self.setStyleSheet(css.replace("__ACCENT__", accent_light))
        else:
            # Apply only group and button styles at the container level; combo gets its own theme below
            css = """
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
                    color: __ACCENT__;
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
                    color: __ACCENT__;
                }
                QPushButton:pressed {
                    background-color: #5A5A5A;
                }
            """
            self.setStyleSheet(css.replace("__ACCENT__", accent_dark))

        # In case external accent replacer modified our stylesheet, ensure consistency by re-applying once
        try:
            ss = self.styleSheet() or ""
            # If for any reason our QPushButton rules are stripped, enforce them again without recursion
            if "QPushButton{" not in ss.replace(" ", ""):
                self.setStyleSheet("")
                if theme == "light":
                    css2 = """
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
                            color: __ACCENT__;
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
                            color: __ACCENT__;
                        }
                        QPushButton:pressed {
                            background-color: #DEE2E6;
                        }
                    """
                    self.setStyleSheet(css2.replace("__ACCENT__", accent_light))
                else:
                    css2 = """
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
                            color: __ACCENT__;
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
                            color: __ACCENT__;
                        }
                        QPushButton:pressed {
                            background-color: #5A5A5A;
                        }
                    """
                    self.setStyleSheet(css2.replace("__ACCENT__", accent_dark))
        except Exception:
            pass

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
    
    def _delayed_gallery_update(self, gallery_window, theme):
        """Delayed gallery update to ensure all changes take effect"""
        try:
            if gallery_window and not gallery_window.isHidden():
                # Force another round of updates with complete reset
                gallery_window.setStyleSheet("")
                gallery_window.apply_gallery_theme(theme)
                gallery_window._force_complete_theme_application(theme)
        except Exception:
            pass
