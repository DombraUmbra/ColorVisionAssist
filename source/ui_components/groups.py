"""
UI group components for ColorVisionAid
Contains group box creation functions for various settings
"""

import os
from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QGroupBox, 
                           QComboBox, QCheckBox, QHBoxLayout, QListView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from ..translations import translator as tr
from .buttons import create_button

class HiddenCurrentCombo(QComboBox):
    """QComboBox that hides the currently selected item from the popup list.
    This improves UX by not showing the already-selected option in the dropdown.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Ensure we have a view instance to manipulate rows
        self.setView(QListView())

    def showPopup(self):
        try:
            # Hide the currently selected row in the popup view
            current = self.currentIndex()
            if current >= 0 and self.view() is not None:
                # First unhide all rows in case of previous state
                for i in range(self.count()):
                    self.view().setRowHidden(i, False)
                self.view().setRowHidden(current, True)
        except Exception:
            pass
        super().showPopup()

    def hidePopup(self):
        try:
            # Restore all rows visibility when popup closes
            if self.view() is not None:
                for i in range(self.count()):
                    self.view().setRowHidden(i, False)
        except Exception:
            pass
        super().hidePopup()

def _apply_combo_theme(combo_box, parent):
    """Apply a unified, theme-aware styling to a QComboBox using external SVG files."""
    theme = getattr(parent, 'theme', 'dark') if parent else 'dark'
    
    # Define paths for icons, ensuring they are correct
    # Go up two levels to reach project root where 'icons' folder resides
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dark_icon_path = os.path.join(base_path, 'icons', 'dropdown_arrow_dark.svg').replace('\\', '/')
    light_icon_path = os.path.join(base_path, 'icons', 'dropdown_arrow_light.svg').replace('\\', '/')
    
    icon_path = light_icon_path if theme == 'dark' else dark_icon_path

    common_style = f"""
        QComboBox {{
            padding: 5px 28px 5px 8px; /* Right padding to not overlap icon */
            font-size: 10pt;
            border-radius: 4px;
        }}
        QComboBox:hover {{
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left-style: solid;
            border-left-width: 1px;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
            background-color: transparent;
        }}
        QComboBox::down-arrow {{
            image: url({icon_path});
            width: 10px;
            height: 6px;
        }}
    """

    if theme == 'light':
        combo_box.setStyleSheet(f"""
            {common_style}
            QComboBox {{
                border: 1px solid #CCCCCC;
                background-color: white;
                color: #333;
            }}
            QComboBox:hover {{
                border: 1px solid #2196F3;
            }}
            QComboBox::drop-down {{
                border-left-color: #CCCCCC;
            }}
        """)
    else:  # dark theme
        combo_box.setStyleSheet(f"""
            {common_style}
            QComboBox {{
                border: 1px solid #555;
                background-color: #2b2b2b;
                color: #EEE;
            }}
            QComboBox:hover {{
                border: 1px solid #64B5F6;
            }}
            QComboBox::drop-down {{
                border-left-color: #555;
            }}
            QComboBox QAbstractItemView {{
                background-color: #2b2b2b;
                color: #EEE;
                selection-background-color: #64B5F6;
                border: 1px solid #555;
                outline: none;
            }}
        """)

def update_combo_themes(parent):
    """Update all combo box themes when theme changes"""
    if hasattr(parent, 'color_blindness_combo'):
        _apply_combo_theme(parent.color_blindness_combo, parent)
    if hasattr(parent, 'language_combo'):
        _apply_combo_theme(parent.language_combo, parent)
    if hasattr(parent, 'theme_combo'):
        _apply_combo_theme(parent.theme_combo, parent)

def create_color_blindness_type_group(parent):
    """Create color blindness type selection group"""
    color_blindness_group = QGroupBox(tr.get_text("color_blindness_type"))
    color_blindness_layout = QVBoxLayout()
    color_blindness_layout.setSpacing(10)
    
    # Color blindness type selection
    parent.color_blindness_combo = HiddenCurrentCombo()
    parent.color_blindness_combo.addItem(tr.get_text("red_green_colorblind"), "red_green")
    parent.color_blindness_combo.addItem(tr.get_text("blue_yellow_colorblind"), "blue_yellow")
    parent.color_blindness_combo.addItem(tr.get_text("protanopia"), "protanopia")
    parent.color_blindness_combo.addItem(tr.get_text("deuteranopia"), "deuteranopia")
    parent.color_blindness_combo.addItem(tr.get_text("tritanopia"), "tritanopia")
    parent.color_blindness_combo.addItem(tr.get_text("complete_colorblind"), "complete")
    parent.color_blindness_combo.addItem(tr.get_text("custom_colors"), "custom")
    
    # Apply theme-aware styling to combo box
    _apply_combo_theme(parent.color_blindness_combo, parent)
    
    parent.color_blindness_combo.setToolTip(tr.get_text("color_blindness_type_tooltip"))
    parent.color_blindness_combo.currentIndexChanged.connect(parent.color_blindness_type_changed)
    
    color_blindness_layout.addWidget(parent.color_blindness_combo)
    
    # Advanced settings button
    parent.advanced_settings_button = create_button(
        tr.get_text("advanced_settings"),
        tr.get_text("advanced_settings_tooltip"),
        "default",
        parent.open_advanced_settings
    )
    
    color_blindness_layout.addWidget(parent.advanced_settings_button)
    color_blindness_group.setLayout(color_blindness_layout)
    
    return color_blindness_group

def create_color_detection_group(parent):
    """Create color detection settings group (for advanced settings)"""
    color_group = QGroupBox(tr.get_text("manual_color_selection"))
    color_layout = QVBoxLayout()
    
    parent.red_checkbox = QCheckBox(tr.get_text("detect_red"))
    parent.green_checkbox = QCheckBox(tr.get_text("detect_green"))
    parent.blue_checkbox = QCheckBox(tr.get_text("detect_blue"))
    parent.yellow_checkbox = QCheckBox(tr.get_text("detect_yellow"))
    
    # Default selected colors
    parent.red_checkbox.setChecked(True)
    parent.green_checkbox.setChecked(True)
    
    # Tooltips
    parent.red_checkbox.setToolTip(tr.get_text("red_checkbox_tooltip"))
    parent.green_checkbox.setToolTip(tr.get_text("green_checkbox_tooltip"))
    parent.blue_checkbox.setToolTip(tr.get_text("blue_checkbox_tooltip"))
    parent.yellow_checkbox.setToolTip(tr.get_text("yellow_checkbox_tooltip"))
    
    # Add to layout
    color_layout.addWidget(parent.red_checkbox)
    color_layout.addWidget(parent.green_checkbox)
    color_layout.addWidget(parent.blue_checkbox)
    color_layout.addWidget(parent.yellow_checkbox)
    color_group.setLayout(color_layout)
    
    return color_group

def create_camera_settings_group(parent):
    """Create camera settings group"""
    camera_settings_group = QGroupBox(tr.get_text("camera_settings"))
    camera_layout = QVBoxLayout()
    camera_layout.setSpacing(8)
    
    # Information about camera permissions
    parent.camera_info_label = QLabel(tr.get_text("camera_settings_info"))
    parent.camera_info_label.setWordWrap(True)
    parent.camera_info_label.setStyleSheet("""
        QLabel {
            color: #CCC; 
            font-size: 9pt; 
            padding: 10px;
            line-height: 1.5;
            background-color: #3A3A3A;
            border-radius: 5px;
            border-left: 3px solid #64B5F6;
            max-height: 80px;
        }
    """)
    parent.camera_info_label.setMinimumHeight(60)
    parent.camera_info_label.setMaximumHeight(100)
    camera_layout.addWidget(parent.camera_info_label)
    
    # Show current permission status
    permission_status_text = ""
    if parent.camera_permission == "granted":
        permission_status_text = tr.get_text("permission_status_granted")
    elif parent.camera_permission == "denied":
        permission_status_text = tr.get_text("permission_status_denied")
    else:
        permission_status_text = tr.get_text("permission_status_ask")
        
    parent.permission_status_label = QLabel(f"{tr.get_text('current_permission_status')}: {permission_status_text}")
    parent.permission_status_label.setWordWrap(True)
    parent.permission_status_label.setStyleSheet("""
        color: #2196F3; 
        font-size: 9pt;
        font-weight: bold;
        margin-top: 8px;
        padding: 4px;
    """)
    camera_layout.addWidget(parent.permission_status_label)
    
    # Camera permission reset button
    permission_reset_button = QPushButton(tr.get_text("reset_camera_permission"))
    
    # Apply theme-aware button styling to match profile selector
    theme = getattr(parent, 'theme', 'dark')
    if theme == 'light':
        permission_reset_button.setStyleSheet("""
            QPushButton {
                background-color: #F8F9FA;
                color: #495057;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
                padding: 8px 12px;
                min-height: 20px;
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
        permission_reset_button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: #CCC;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
                padding: 8px 12px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
                color: #64B5F6;
            }
            QPushButton:pressed {
                background-color: #5A5A5A;
            }
        """)
    
    # Add icon to button - update icon path
    reset_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'icons', 'reset_icon.png').replace('\\', '/')
    if os.path.exists(reset_icon_path):
        permission_reset_button.setIcon(QIcon(reset_icon_path))
    
    permission_reset_button.clicked.connect(parent.reset_camera_permission)
    parent.permission_reset_button = permission_reset_button
    camera_layout.addWidget(permission_reset_button)
    
    camera_settings_group.setLayout(camera_layout)
    
    return camera_settings_group

def create_language_group(parent):
    """Create language settings group"""
    language_group = QGroupBox(tr.get_text("interface"))
    language_layout = QVBoxLayout()
    
    # Language label with blue color
    language_label = QLabel(tr.get_text("language"))
    language_label.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 9pt;")
    language_layout.addWidget(language_label)
    
    # Language selection
    parent.language_combo = HiddenCurrentCombo()
    for code, name in tr.LANGUAGES.items():
        parent.language_combo.addItem(name, code)
    
    # Set current language
    current_index = 0
    language = parent.settings.value("language", "en")
    for i in range(parent.language_combo.count()):
        if parent.language_combo.itemData(i) == language:
            current_index = i
            break
    parent.language_combo.setCurrentIndex(current_index)
    parent.language_combo.currentIndexChanged.connect(parent.change_language)
    
    # Apply theme to language combo
    _apply_combo_theme(parent.language_combo, parent)
    
    language_layout.addWidget(parent.language_combo)

    # Theme label with blue color
    theme_label = QLabel(tr.get_text("theme"))
    theme_label.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 9pt;")
    parent.theme_combo = HiddenCurrentCombo()
    parent.theme_combo.addItem(tr.get_text("dark"), "dark")
    parent.theme_combo.addItem(tr.get_text("light"), "light")
    parent.theme_combo.setToolTip(tr.get_text("theme_tooltip"))
    # Set current theme
    theme_value = parent.settings.value("theme", "dark")
    theme_index = 0
    for i in range(parent.theme_combo.count()):
        if parent.theme_combo.itemData(i) == theme_value:
            theme_index = i
            break
    parent.theme_combo.setCurrentIndex(theme_index)
    parent.theme_combo.currentIndexChanged.connect(parent.change_theme)
    
    # Apply theme to theme combo
    _apply_combo_theme(parent.theme_combo, parent)
    
    language_layout.addWidget(theme_label)
    language_layout.addWidget(parent.theme_combo)
    
    language_group.setLayout(language_layout)
    
    return language_group

def create_about_group(parent):
    """Create about section group"""
    about_group = QGroupBox(tr.get_text("about"))
    about_layout = QVBoxLayout()
    about_layout.setContentsMargins(10, 10, 10, 10)
    
    parent.about_label = QLabel(tr.get_text("about_text"))
    parent.about_label.setAlignment(Qt.AlignCenter)
    parent.about_label.setWordWrap(True)
    parent.about_label.setStyleSheet("""
        QLabel {
            font-size: 9pt;
            line-height: 1.4;
            padding: 8px;
            color: #CCC;
        }
    """)
    about_layout.addWidget(parent.about_label)

    # Contributors list
    contributors_title = QLabel(tr.get_text("contributors"))
    contributors_title.setAlignment(Qt.AlignCenter)
    contributors_title.setStyleSheet("color: #2196F3; font-weight: bold; margin-top: 6px;")
    about_layout.addWidget(contributors_title)

    contributors = [
        "Ammar Yasir Bayır",
        "İrem Duman",
        "İpek Deniz Özcan",
        "Hayat Pınar Polat",
        "Efraim Bayır",
    ]
    contributors_label = QLabel("\n".join(contributors))
    contributors_label.setAlignment(Qt.AlignCenter)
    contributors_label.setWordWrap(True)
    contributors_label.setStyleSheet("QLabel { font-size: 9pt; color: #888; }")
    about_layout.addWidget(contributors_label)
    about_group.setLayout(about_layout)
    
    return about_group
