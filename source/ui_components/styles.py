"""
Theme and styling utilities for ColorVisionAid
Contains dark/light theme application and interface creation functions
"""

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from ..translations import translator as tr

def apply_dark_theme(widget):
    """Apply dark theme style"""
    widget.setStyleSheet("""
        QMainWindow {
            background-color: #333;
        }
        QLabel, QCheckBox, QGroupBox, QPushButton {
            color: #EEE;
            font-size: 10pt;
        }
        QCheckBox:hover {
            color: #2196F3;
        }
        QGroupBox {
            border: 2px solid #555;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: #444;
            font-size: 9pt;
            color: #EEE;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            padding: 0 5px;
            color: #2196F3;
            font-size: 10pt;
            font-weight: bold;
        }
        QGroupBox:hover {
            border: 2px solid #2196F3;
        }
        QSlider::groove:horizontal {
            height: 8px;
            background: #333;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #2196F3;
            border: 1px solid #2196F3;
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }
        QSlider::handle:horizontal:hover {
            background: #64B5F6;
            border: 1px solid #90CAF9;
            width: 20px;
            margin: -3px 0;
        }
        QComboBox {
            background-color: #555;
            color: white;
            padding: 5px;
            border-radius: 3px;
            font-size: 9pt;
            min-height: 20px;
            border: 1px solid #666;
        }
        QComboBox:hover {
            background-color: #666;
            border: 1px solid #2196F3;
        }
    /* Drop-down/arrow styling is handled per-component for better control */
        QComboBox QAbstractItemView {
            background-color: #555;
            color: white;
            selection-background-color: #2196F3;
            border: 1px solid #666;
        }
        QToolTip {
            background-color: #444;
            color: white;
            border: 1px solid #2196F3;
            padding: 2px;
            border-radius: 3px;
            opacity: 200;
        }
    """)

def apply_light_theme(widget):
    """Apply light theme style"""
    widget.setStyleSheet("""
        QMainWindow {
            background-color: #F5F5F7;
        }
        QLabel, QCheckBox, QGroupBox, QPushButton {
            color: #222;
            font-size: 10pt;
        }
        QCheckBox:hover {
            color: #1976D2;
        }
        QGroupBox {
            border: 2px solid #DDD;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: #FFFFFF;
            font-size: 9pt;
            color: #222;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            padding: 0 5px;
            color: #1976D2;
            font-size: 10pt;
            font-weight: bold;
        }
        QGroupBox:hover {
            border: 2px solid #1976D2;
        }
        QSlider::groove:horizontal {
            height: 8px;
            background: #E0E0E0;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #1976D2;
            border: 1px solid #1976D2;
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }
        QSlider::handle:horizontal:hover {
            background: #42A5F5;
            border: 1px solid #90CAF9;
            width: 20px;
            margin: -3px 0;
        }
        QComboBox {
            background-color: #FFFFFF;
            color: #222;
            padding: 5px;
            border-radius: 3px;
            font-size: 9pt;
            min-height: 20px;
            border: 1px solid #CCC;
        }
        QComboBox:hover {
            background-color: #FAFAFA;
            border: 1px solid #1976D2;
        }
    /* Drop-down/arrow styling is handled per-component for better control */
        QComboBox QAbstractItemView {
            background-color: #FFFFFF;
            color: #222;
            selection-background-color: #BBDEFB;
            border: 1px solid #CCC;
        }
        QToolTip {
            background-color: #FFFFFF;
            color: #222;
            border: 1px solid #1976D2;
            padding: 2px;
            border-radius: 3px;
            opacity: 240;
        }
    """)

def apply_theme(widget, theme: str):
    """Apply theme by name ('dark' or 'light'). Defaults to dark."""
    if (theme or '').lower() == 'light':
        apply_light_theme(widget)
    else:
        apply_dark_theme(widget)

def create_camera_interface(parent, layout):
    """Create camera interface with start message"""
    # Clear previous widgets
    for i in reversed(range(layout.count())):
        child = layout.takeAt(i).widget()
        if child:
            child.setParent(None)
    
    # Calculate responsive sizes based on window size
    window_width = parent.width() if hasattr(parent, 'width') else 1000
    window_height = parent.height() if hasattr(parent, 'height') else 600
    
    # Calculate responsive icon size (minimum 40pt, maximum 120pt)
    base_icon_size = max(40, min(120, int(window_width * 0.08)))
    
    # Calculate responsive message size (minimum 10pt, maximum 18pt)
    base_message_size = max(10, min(18, int(window_width * 0.015)))
    
    # Calculate responsive margins
    responsive_margin = max(10, min(40, int(window_width * 0.025)))
    
    # Start message
    start_widget = QWidget()
    start_layout = QVBoxLayout()
    start_layout.setContentsMargins(responsive_margin, responsive_margin, responsive_margin, responsive_margin)
    
    # Icon/Placeholder - Use a camera icon with fallback
    try:
        camera_icon = QLabel("🎥")  # Video camera icon - widely supported
    except:
        try:
            camera_icon = QLabel("📷")  # Fallback to photo camera
        except:
            camera_icon = QLabel("📹")  # Alternative camera symbol
        
    # Additional fallback in case of encoding issues
    if not camera_icon.text() or len(camera_icon.text()) == 0:
        camera_icon.setText("●REC")  # Simple text fallback
        
    # Theme-aware styling for camera icon and message with responsive sizing
    theme = getattr(parent, 'theme', 'dark').lower()
    if theme == 'light':
        camera_icon.setStyleSheet(f"""
            QLabel {{
                font-size: {base_icon_size}pt;
                color: #333;
                text-align: center;
                background-color: transparent;
                border: none;
                margin: {responsive_margin}px;
                font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji';
            }}
        """)
    else:
        camera_icon.setStyleSheet(f"""
            QLabel {{
                font-size: {base_icon_size}pt;
                color: #BBB;
                text-align: center;
                background-color: transparent;
                border: none;
                margin: {responsive_margin}px;
                font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji';
            }}
        """)
    camera_icon.setAlignment(Qt.AlignCenter)
    start_layout.addWidget(camera_icon)
    
    # Start message with responsive sizing
    start_message = QLabel(tr.get_text("camera_start_message"))
    responsive_padding = max(5, min(15, int(window_width * 0.012)))
    if theme == 'light':
        start_message.setStyleSheet(f"""
            QLabel {{
                font-size: {base_message_size}pt;
                color: #222;
                text-align: center;
                margin: {responsive_padding}px;
                padding: {responsive_padding}px;
            }}
        """)
    else:
        start_message.setStyleSheet(f"""
            QLabel {{
                font-size: {base_message_size}pt;
                color: #CCC;
                text-align: center;
                margin: {responsive_padding}px;
                padding: {responsive_padding}px;
            }}
        """)
    start_message.setAlignment(Qt.AlignCenter)
    start_message.setWordWrap(True)
    start_layout.addWidget(start_message)
    
    start_widget.setLayout(start_layout)
    layout.addWidget(start_widget)
