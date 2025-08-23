"""
Button creation and styling utilities for ColorVisionAid
Contains standardized button styles and creation functions
"""

from PyQt5.QtWidgets import QPushButton, QHBoxLayout
from ..translations import translator as tr

def update_button_theme(button: QPushButton, style_class: str, theme: str = 'dark'):
    """Apply style to button based on style_class and theme ('dark'|'light')."""
    style_dict_dark = {
        "default": """
            QPushButton {
                background-color: #555;
                color: white;
                padding: 8px 6px;
                border-radius: 5px;
                font-size: 9pt;
                min-height: 25px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #777;
                border: 1px solid #999;
            }
            QPushButton:pressed {
                background-color: #444;
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
                background-color: #E0E0E0;
                color: #222;
                padding: 8px 6px;
                border-radius: 5px;
                font-size: 9pt;
                min-height: 25px;
                text-align: center;
                border: 1px solid #C7C7C7;
            }
            QPushButton:hover {
                background-color: #EEEEEE;
                border: 1px solid #1976D2;
            }
            QPushButton:pressed {
                background-color: #D5D5D5;
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
def create_button(text, tooltip, style_class="default", callback=None):
    """Create standard styled button"""
    button = QPushButton(text)
    button.setToolTip(tooltip)
    # Default to dark until refreshed by window on theme application
    update_button_theme(button, style_class, theme='dark')
    
    if callback:
        button.clicked.connect(callback)
    
    return button

def create_camera_controls(parent):
    """Create camera control buttons"""
    button_layout = QHBoxLayout()
    
    # Camera toggle button
    camera_toggle_button = create_button(
        tr.get_text("start"), 
        tr.get_text("start_tooltip"),
        "start",
        parent.toggle_camera
    )
    parent.camera_toggle_button = camera_toggle_button
    
    # Screenshot and gallery buttons
    screenshot_button = create_button(
        tr.get_text("take_screenshot"),
        tr.get_text("snapshot_tooltip"),
        "snapshot",
        parent.take_screenshot
    )
    # Hide when camera is off
    screenshot_button.setVisible(parent.camera_manager.camera_open)
    parent.screenshot_button = screenshot_button
    
    # File upload button (will be placed before gallery to swap positions)
    load_file_button = create_button(
        tr.get_text("load_file"),
        tr.get_text("load_file_tooltip"),
        "load_file",
        parent.load_file
    )
    parent.load_file_button = load_file_button
    
    gallery_button = create_button(
        tr.get_text("gallery"),
        tr.get_text("gallery_tooltip"),
        "gallery",
        parent.open_gallery
    )
    parent.gallery_button = gallery_button
    
    button_layout.addWidget(camera_toggle_button)
    button_layout.addWidget(screenshot_button)
    button_layout.addWidget(load_file_button)
    button_layout.addWidget(gallery_button)
    
    return button_layout
