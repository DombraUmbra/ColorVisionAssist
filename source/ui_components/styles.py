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
        QComboBox::drop-down {
            width: 0px;
            border: none;
            background: transparent;
        }
        QComboBox::down-arrow {
            image: none;
            border: none;
            background: transparent;
            width: 0px;
            height: 0px;
        }
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
        QComboBox::drop-down {
            width: 0px;
            border: none;
            background: transparent;
        }
        QComboBox::down-arrow {
            image: none;
            border: none;
            background: transparent;
            width: 0px;
            height: 0px;
        }
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
    
    # Start message
    start_widget = QWidget()
    start_layout = QVBoxLayout()
    start_layout.setContentsMargins(20, 20, 20, 20)
    
    # Icon/Placeholder
    camera_icon = QLabel("📷")
    # Theme-aware styling for camera icon and message
    theme = getattr(parent, 'theme', 'dark').lower()
    if theme == 'light':
        camera_icon.setStyleSheet("""
            QLabel {
                font-size: 60pt;
                color: #999;
                text-align: center;
            }
        """)
    else:
        camera_icon.setStyleSheet("""
            QLabel {
                font-size: 60pt;
                color: #666;
                text-align: center;
            }
        """)
    camera_icon.setAlignment(Qt.AlignCenter)
    start_layout.addWidget(camera_icon)
    
    # Start message
    start_message = QLabel(tr.get_text("camera_start_message"))
    if theme == 'light':
        start_message.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                color: #555;
                text-align: center;
                margin: 10px;
                padding: 10px;
            }
        """)
    else:
        start_message.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                color: #CCC;
                text-align: center;
                margin: 10px;
                padding: 10px;
            }
        """)
    start_message.setAlignment(Qt.AlignCenter)
    start_message.setWordWrap(True)
    start_layout.addWidget(start_message)
    
    start_widget.setLayout(start_layout)
    layout.addWidget(start_widget)
