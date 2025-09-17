"""
Button creation and styling utilities for ColorVisionAid
Contains standardized button styles and creation functions
"""

from PyQt5.QtWidgets import QPushButton, QHBoxLayout
from ..translations import translator as tr
from .styles import apply_colorblind_friendly_button_style

def update_button_theme(button: QPushButton, style_class: str, theme: str = 'dark', color_blindness_type: str = "none"):
    """Apply style to button based on style_class, theme ('dark'|'light'), and color blindness type."""
    
    print(f"[DEBUG] update_button_theme: style={style_class}, theme={theme}, cb_type={color_blindness_type}")
    
    # If color blindness support is needed, use the accessible styling
    if color_blindness_type in ["protanopia", "deuteranopia", "tritanopia"]:
        print(f"[DEBUG] Applying colorblind-friendly styling for {color_blindness_type}")
        apply_colorblind_friendly_button_style(button, style_class, color_blindness_type, theme)
        return
    
    print(f"[DEBUG] Applying standard styling (no colorblind support needed)")
    
    # Original styling for normal vision
    style_dict_dark = {
        "default": """
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
        """,
        "start": """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 6px;
                border-radius: 5px;
                font-size: 9pt;
                min-height: 25px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #66BB6A;
                border: 2px solid #81C784;
            }
            QPushButton:pressed {
                background-color: #43A047;
            }
        """,
        "stop": """
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 6px;
                border-radius: 5px;
                font-size: 9pt;
                min-height: 25px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #EF5350;
                border: 2px solid #E57373;
            }
            QPushButton:pressed {
                background-color: #E53935;
            }
        """,
        "snapshot": """
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 6px;
                border-radius: 5px;
                font-size: 9pt;
                min-height: 25px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #42A5F5;
                border: 2px solid #64B5F6;
            }
            QPushButton:pressed {
                background-color: #1E88E5;
            }
        """,
        "gallery": """
            QPushButton {
                background-color: #9C27B0;
                color: white;
                padding: 8px 6px;
                border-radius: 5px;
                font-size: 9pt;
                min-height: 25px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #AB47BC;
                border: 2px solid #BA68C8;
            }
            QPushButton:pressed {
                background-color: #8E24AA;
            }
        """,
        "load_file": """
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 8px 6px;
                border-radius: 5px;
                font-size: 9pt;
                min-height: 25px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #FFB74D;
                border: 2px solid #FFCC02;
            }
            QPushButton:pressed {
                background-color: #F57C00;
            }
        """
    }

    style_dict_light = {
        "default": """
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
        """,
        "start": """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 6px;
                border-radius: 5px;
                font-size: 9pt;
                min-height: 25px;
                text-align: center;
            }
            QPushButton:hover { background-color: #66BB6A; }
            QPushButton:pressed { background-color: #43A047; }
        """,
        "stop": """
            QPushButton { background-color: #f44336; color: white; padding: 8px 6px; border-radius: 5px; font-size: 9pt; min-height: 25px; text-align: center; }
            QPushButton:hover { background-color: #EF5350; }
            QPushButton:pressed { background-color: #E53935; }
        """,
        "snapshot": """
            QPushButton { background-color: #1976D2; color: white; padding: 8px 6px; border-radius: 5px; font-size: 9pt; min-height: 25px; text-align: center; }
            QPushButton:hover { background-color: #1E88E5; }
            QPushButton:pressed { background-color: #1565C0; }
        """,
        "gallery": """
            QPushButton { background-color: #8E24AA; color: white; padding: 8px 6px; border-radius: 5px; font-size: 9pt; min-height: 25px; text-align: center; }
            QPushButton:hover { background-color: #AB47BC; }
            QPushButton:pressed { background-color: #6A1B9A; }
        """,
        "load_file": """
            QPushButton { background-color: #FB8C00; color: white; padding: 8px 6px; border-radius: 5px; font-size: 9pt; min-height: 25px; text-align: center; }
            QPushButton:hover { background-color: #FFA726; }
            QPushButton:pressed { background-color: #F57C00; }
        """
    }

    if (theme or 'dark').lower() == 'light':
        button.setStyleSheet(style_dict_light.get(style_class, style_dict_light["default"]))
    else:
        button.setStyleSheet(style_dict_dark.get(style_class, style_dict_dark["default"]))
def create_button(text, tooltip, style_class="default", callback=None, color_blindness_type="none"):
    """Create standard styled button with color blindness support"""
    button = QPushButton(text)
    button.setToolTip(tooltip)
    # Default to dark until refreshed by window on theme application
    update_button_theme(button, style_class, theme='dark', color_blindness_type=color_blindness_type)
    
    if callback:
        button.clicked.connect(callback)
    
    return button

def create_camera_controls(parent):
    """Create camera control buttons with color blindness support"""
    button_layout = QHBoxLayout()
    
    # Get color blindness type from parent if available
    color_blindness_type = getattr(parent, 'current_profile', None)
    if color_blindness_type and hasattr(color_blindness_type, 'color_blindness_type'):
        cb_type = color_blindness_type.color_blindness_type
    else:
        cb_type = "none"
    
    # Camera toggle button
    camera_toggle_button = create_button(
        tr.get_text("start"), 
        tr.get_text("start_tooltip"),
        "start",
        parent.toggle_camera,
        cb_type
    )
    # Mark for accent-exclusion so global pink mapping won't affect this button
    camera_toggle_button.setObjectName("camera_start_button")
    parent.camera_toggle_button = camera_toggle_button
    
    # Screenshot and gallery buttons
    screenshot_button = create_button(
        tr.get_text("take_screenshot"),
        tr.get_text("snapshot_tooltip"),
        "snapshot",
        parent.take_screenshot,
        cb_type
    )
    # Hide when camera is off
    screenshot_button.setVisible(parent.camera_manager.camera_open)
    parent.screenshot_button = screenshot_button
    
    # File upload button (will be placed before gallery to swap positions)
    load_file_button = create_button(
        tr.get_text("load_file"),
        tr.get_text("load_file_tooltip"),
        "load_file",
        parent.load_file,
        cb_type
    )
    parent.load_file_button = load_file_button
    
    gallery_button = create_button(
        tr.get_text("gallery"),
        tr.get_text("gallery_tooltip"),
        "gallery",
        parent.open_gallery,
        cb_type
    )
    # Mark gallery button to keep its own accessible color (pink under tritanopia)
    gallery_button.setObjectName("gallery_button")
    parent.gallery_button = gallery_button
    
    button_layout.addWidget(camera_toggle_button)
    button_layout.addWidget(screenshot_button)
    button_layout.addWidget(load_file_button)
    button_layout.addWidget(gallery_button)
    
    return button_layout
