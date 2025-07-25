"""
Theme and styling utilities for ColorVisionAid
Contains dark theme application and interface creation functions
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
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: #666;
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
            background-color: #555;
        }
        QComboBox::down-arrow {
            width: 10px;
            height: 10px;
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #666, stop: 1 #333);
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
