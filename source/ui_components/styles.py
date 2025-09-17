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
    """Create compact camera interface with start message"""
    # Clear previous widgets
    for i in reversed(range(layout.count())):
        child = layout.takeAt(i).widget()
        if child:
            child.setParent(None)
    
    # Calculate responsive sizes based on window size
    window_width = parent.width() if hasattr(parent, 'width') else 1000
    
    # Smaller, more compact responsive sizes for start message
    base_icon_size = max(24, min(48, int(window_width * 0.04)))  # Reduced from 0.08
    base_message_size = max(9, min(14, int(window_width * 0.012)))  # Reduced from 0.015
    responsive_margin = max(5, min(20, int(window_width * 0.015)))  # Reduced from 0.025
    
    # Start message
    start_widget = QWidget()
    start_layout = QVBoxLayout()
    start_layout.setContentsMargins(responsive_margin, responsive_margin//2, responsive_margin, responsive_margin//2)  # Reduce vertical margins
    
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
                margin: {responsive_margin//2}px;
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
                margin: {responsive_margin//2}px;
                font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji';
            }}
        """)
    camera_icon.setAlignment(Qt.AlignCenter)
    start_layout.addWidget(camera_icon)
    
    # Start message with responsive sizing
    start_message = QLabel(tr.get_text("camera_start_message"))
    responsive_padding = max(3, min(10, int(window_width * 0.008)))  # Reduced padding
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

def get_colorblind_friendly_colors(color_blindness_type="none"):
    """
    Get color mapping for color blindness accessibility
    Returns dictionary mapping original colors to accessible alternatives
    """
    color_maps = {
        "none": {
            # No changes for normal vision
            "green": "#4CAF50",
            "red": "#f44336", 
            "blue": "#2196F3",
            "orange": "#FF9800",
            "purple": "#9C27B0"
        },
        "protanopia": {  # Red-green color blindness (no red receptors)
            "green": "#0F2080",   # Green → Dark Blue for contrast
            "red": "#D8D210",     # Red → Amber/Yellow
            "blue": "#1880D5",    # Blue stays blue
            "orange": "#46453F",  # Load file (orange class) → Lighter Yellow
            "purple": "#80711D"    # Gallery (purple class) → Gold
        },
        "deuteranopia": {  # Red-green color blindness (no green receptors)
            "green": "#0F2080",   # Green → Dark Blue for contrast
            "red": "#D8D210",     # Red → Amber/Yellow
            "blue": "#1880D5",    # Blue stays blue
            "orange": "#46453F",  # Load file (orange class) → Lighter Yellow
            "purple": "#80711D"    # Gallery (purple class) → Gold
        },
        "tritanopia": {  # Blue-yellow color blindness (no blue receptors)
            "green": "#64B5F6",   # Any green-class button -> Light Blue
            "red": "#E91E63",     # Any red/orange/purple-class button -> Pink
            "blue": "#F2C6E6",    # Blue-class -> Light Blue
            "orange": "#E0E0E0",  # Orange-class -> Light Gray (for neutral look)
            "purple": "#E91E63"   # Purple-class -> Pink
        }
    }
    
    return color_maps.get(color_blindness_type, color_maps["none"])

def apply_colorblind_friendly_button_style(button, original_style_class, color_blindness_type="none", theme="dark"):
    """
    Apply color blind friendly styling to buttons based on color blindness type
    """
    color_map = get_colorblind_friendly_colors(color_blindness_type)
    
    # Map original style classes to their base colors
    style_color_mapping = {
        "start": "green",
        "stop": "red", 
        "snapshot": "blue",
        "gallery": "purple",
        "load_file": "orange"
    }
    
    base_color = style_color_mapping.get(original_style_class, "blue")
    accessible_color = color_map[base_color]
    
    # Generate hover and pressed colors (lighter and darker variants)
    hover_color = adjust_color_brightness(accessible_color, 1.2)
    pressed_color = adjust_color_brightness(accessible_color, 0.8)

    # Decide readable text color based on background brightness
    def _contrasting_text_color(bg_hex: str) -> str:
        try:
            hx = bg_hex.lstrip('#')
            if len(hx) != 6:
                return "#FFFFFF"
            r = int(hx[0:2], 16)
            g = int(hx[2:4], 16)
            b = int(hx[4:6], 16)
            # Perceived brightness (YIQ approximation)
            brightness = (299 * r + 587 * g + 114 * b) / 1000
            return "#222222" if brightness >= 170 else "#FFFFFF"
        except Exception:
            return "#FFFFFF"

    text_color = _contrasting_text_color(accessible_color)
    
    if theme == "dark":
        style = f"""
            QPushButton {{
                background-color: {accessible_color};
                color: {text_color};
                padding: 8px 6px;
                border-radius: 5px;
                font-size: 9pt;
                min-height: 25px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border: 2px solid {adjust_color_brightness(accessible_color, 1.4)};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """
    else:  # light theme
        style = f"""
            QPushButton {{
                background-color: {accessible_color};
                color: {text_color};
                padding: 8px 6px;
                border-radius: 5px;
                font-size: 9pt;
                min-height: 25px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """
    
    button.setStyleSheet(style)

def adjust_color_brightness(hex_color, factor):
    """
    Adjust the brightness of a hex color by a factor
    factor > 1 makes it brighter, factor < 1 makes it darker
    """
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Convert hex to RGB
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Adjust brightness
    adjusted_rgb = tuple(min(255, max(0, int(component * factor))) for component in rgb)
    
    # Convert back to hex
    return f"#{adjusted_rgb[0]:02x}{adjusted_rgb[1]:02x}{adjusted_rgb[2]:02x}"
