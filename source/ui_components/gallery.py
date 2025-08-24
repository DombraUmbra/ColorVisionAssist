import os
import glob
import cv2
from PyQt5.QtWidgets import (QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                           QWidget, QGridLayout, QScrollArea, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon

from ..translations import translator as tr

class ScreenshotGallery(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr.get_text("gallery_title"))
        self.setGeometry(200, 200, 800, 600)
        
        # Remove question mark button from title bar
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Get theme early
        self.theme = getattr(parent, 'theme', 'dark') if parent else 'dark'
        
        # Apply title bar theme immediately before showing window
        self._apply_gallery_title_bar(self.theme)
        
        # Update icon path to use main app icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "icons", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Main layout
        layout = QVBoxLayout()
        
        # Info label
        self.info_label = QLabel(tr.get_text("saved_screenshots"))
        self.info_label.setObjectName("infoLabel")
        layout.addWidget(self.info_label)
        
        # Create a scroll area for the gallery
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("galleryScrollArea")
        
        scroll_widget = QWidget()
        scroll_widget.setObjectName("galleryScrollWidget")
        self.gallery_layout = QGridLayout(scroll_widget)
        
        # Store references for theme application
        self.scroll_area = scroll_area
        self.scroll_widget = scroll_widget
        
        # Apply initial background colors immediately
        self._set_initial_colors()
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        # Add buttons
        self.refresh_button = QPushButton(tr.get_text("refresh"))
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.load_screenshots)
        
        self.delete_button = QPushButton(tr.get_text("delete_selected"))
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_selected)
        self.delete_button.setEnabled(False)
        
        self.export_button = QPushButton("Kaydet")  # Changed from tr.get_text("export")
        self.export_button.setObjectName("saveButton")
        self.export_button.clicked.connect(self.export_selected)
        self.export_button.setEnabled(False)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.export_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Variables
        self.screenshots = []
        self.selected_index = -1
        self.thumbnail_labels = []
        
        # Load screenshots
        self.load_screenshots()
        
        # Apply theme and styling at the very end
        self.apply_gallery_theme(self.theme)
        self._force_scroll_area_background(self.theme)
        self._force_scroll_area_update()
        
        # Apply title bar theme immediately
        self._apply_gallery_title_bar(self.theme)
        
        # Also apply with small delay as backup
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(50, lambda: self._apply_gallery_title_bar(self.theme))
    
    def _set_initial_colors(self):
        """Set initial colors to prevent white flash"""
        from PyQt5.QtGui import QPalette, QColor
        from PyQt5.QtCore import Qt
        
        if (self.theme or 'dark').lower() == 'light':
            # Light theme colors
            bg_color = QColor(255, 255, 255)  # White
            dialog_bg = "#F5F5F7"
        else:
            # Dark theme colors  
            bg_color = QColor(43, 43, 43)  # #2b2b2b
            dialog_bg = "#333"
        
        # Set dialog background immediately
        if (self.theme or 'dark').lower() == 'light':
            self.setStyleSheet(f"""
                QDialog {{ 
                    background-color: {dialog_bg}; 
                }}
                QScrollArea {{
                    background-color: #FFF !important;
                    border: 1px solid #CCC;
                }}
                QScrollArea QScrollBar:vertical {{
                    background-color: #F0F0F0 !important;
                    width: 12px;
                }}
                QScrollArea QScrollBar::handle:vertical {{
                    background-color: #CCC !important;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QDialog {{ 
                    background-color: {dialog_bg}; 
                }}
                QScrollArea {{
                    background-color: #2b2b2b !important;
                    border: 1px solid #555;
                }}
                QScrollArea QScrollBar:vertical {{
                    background-color: #444 !important;
                    width: 12px;
                }}
                QScrollArea QScrollBar::handle:vertical {{
                    background-color: #666 !important;
                }}
                QScrollArea QScrollBar:horizontal {{
                    background-color: #444 !important;
                    height: 12px;
                }}
                QScrollArea QScrollBar::handle:horizontal {{
                    background-color: #666 !important;
                }}
            """)
        
        # Set scroll area initial colors immediately
        if hasattr(self, 'scroll_area') and hasattr(self, 'scroll_widget'):
            # Method 1: Direct stylesheet
            if (self.theme or 'dark').lower() == 'light':
                self.scroll_area.setStyleSheet("QScrollArea { background-color: #FFF; border: 1px solid #CCC; }")
                self.scroll_widget.setStyleSheet("QWidget { background-color: #FFF; }")
            else:
                self.scroll_area.setStyleSheet("QScrollArea { background-color: #2b2b2b; border: 1px solid #555; }")
                self.scroll_widget.setStyleSheet("QWidget { background-color: #2b2b2b; }")
            
            # Method 2: QPalette
            palette = self.scroll_area.palette()
            palette.setColor(QPalette.Window, bg_color)
            palette.setColor(QPalette.Base, bg_color)
            self.scroll_area.setPalette(palette)
            self.scroll_area.setAutoFillBackground(True)
            
            widget_palette = self.scroll_widget.palette()
            widget_palette.setColor(QPalette.Window, bg_color)
            widget_palette.setColor(QPalette.Base, bg_color)
            self.scroll_widget.setPalette(widget_palette)
            self.scroll_widget.setAutoFillBackground(True)
            
            # Force immediate repaint
            self.scroll_area.update()
            self.scroll_widget.update()
    
    def _apply_button_styles(self):
        """Apply direct styles to buttons to ensure they work"""
        # Refresh button - Blue
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056CC;
            }
        """)
        
        # Delete button - Red
        if self.delete_button.isEnabled():
            self.delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #FF3B30;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #D70015;
                }
            """)
        else:
            self.delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFB3B3;
                    color: #999;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                }
            """)
        
        # Save button - Green
        if self.export_button.isEnabled():
            self.export_button.setStyleSheet("""
                QPushButton {
                    background-color: #34C759;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #248A3D;
                }
            """)
        else:
            self.export_button.setStyleSheet("""
                QPushButton {
                    background-color: #B3E6C7;
                    color: #999;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                }
            """)
        
        # Force scroll area theme using QPalette
        if hasattr(self, 'scroll_area'):
            try:
                from PyQt5.QtGui import QPalette, QColor
                palette = self.scroll_area.palette()
                
                if (self.theme or 'dark').lower() == 'light':
                    bg_color = QColor(255, 255, 255)
                else:
                    bg_color = QColor(45, 45, 45)
                
                palette.setColor(QPalette.Window, bg_color)
                palette.setColor(QPalette.Base, bg_color)
                palette.setColor(QPalette.Background, bg_color)
                self.scroll_area.setPalette(palette)
                self.scroll_area.setAutoFillBackground(True)
                
                # Also apply to scroll area widget
                if self.scroll_area.widget():
                    widget_palette = self.scroll_area.widget().palette()
                    widget_palette.setColor(QPalette.Window, bg_color)
                    widget_palette.setColor(QPalette.Base, bg_color)
                    widget_palette.setColor(QPalette.Background, bg_color)
                    self.scroll_area.widget().setPalette(widget_palette)
                    self.scroll_area.widget().setAutoFillBackground(True)
            except Exception as e:
                print(f"Error applying scroll area palette: {e}")
        
        # Force scroll area update
        self._force_scroll_area_update()
    
    def _update_info_label_style(self):
        """Update info label style with complete reset to prevent font accumulation"""
        if hasattr(self, 'info_label'):
            # Complete style reset - clear all inherited styles
            self.info_label.setStyleSheet("")
            self.info_label.setFont(self.info_label.font())  # Reset font to default
            
            # Apply clean styling based on theme
            is_light = (self.theme or 'dark').lower() == 'light'
            
            if is_light:
                style = """
                QLabel {
                    color: #222222;
                    font-weight: normal;
                    font-size: 12px;
                    padding: 5px;
                    border: none;
                    background: transparent;
                }
                """
            else:
                style = """
                QLabel {
                    color: #FFFFFF;
                    font-weight: normal;
                    font-size: 12px;
                    padding: 5px;
                    border: none;
                    background: transparent;
                }
                """
            
            self.info_label.setStyleSheet(style)
            # Force immediate update
            self.info_label.update()
            self.info_label.repaint()
    
    def _force_scroll_area_update(self):
        """Force scroll area to update its appearance"""
        if hasattr(self, 'scroll_area'):
            try:
                # Force repaint
                self.scroll_area.repaint()
                self.scroll_area.update()
                if self.scroll_area.widget():
                    self.scroll_area.widget().repaint()
                    self.scroll_area.widget().update()
                    
                # Force style update
                self.scroll_area.style().unpolish(self.scroll_area)
                self.scroll_area.style().polish(self.scroll_area)
                if self.scroll_area.widget():
                    self.scroll_area.widget().style().unpolish(self.scroll_area.widget())
                    self.scroll_area.widget().style().polish(self.scroll_area.widget())
            except Exception as e:
                print(f"Error forcing scroll area update: {e}")
    
    def apply_gallery_theme(self, theme: str = 'dark'):
        """Apply theme for gallery window"""
        if (theme or 'dark').lower() == 'light':
            self.setStyleSheet("""
                QDialog {
                    background-color: #F5F5F7;
                    color: #222;
                }
                QLabel {
                    color: #222;
                }
                /* Refresh Button - Blue theme */
                QPushButton#refreshButton {
                    background-color: #007AFF !important;
                    color: white !important;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton#refreshButton:hover {
                    background-color: #0056CC !important;
                }
                
                /* Delete Button - Red theme */
                QPushButton#deleteButton {
                    background-color: #FF3B30 !important;
                    color: white !important;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton#deleteButton:hover {
                    background-color: #D70015 !important;
                }
                QPushButton#deleteButton:disabled {
                    background-color: #FFB3B3 !important;
                    color: #999 !important;
                }
                
                /* Save Button - Green theme */
                QPushButton#saveButton {
                    background-color: #34C759 !important;
                    color: white !important;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton#saveButton:hover {
                    background-color: #248A3D !important;
                }
                QPushButton#saveButton:disabled {
                    background-color: #B3E6C7 !important;
                    color: #999 !important;
                }
                
                QScrollArea {
                    border: 1px solid #CCC;
                    background-color: #FFF;
                }
                QScrollArea#galleryScrollArea {
                    background-color: #FFF;
                }
                QScrollArea#galleryScrollArea > QWidget {
                    background-color: #FFF;
                }
                QScrollArea#galleryScrollArea QWidget {
                    background-color: #FFF;
                }
                QScrollArea::corner {
                    background-color: #FFF;
                }
                QWidget#galleryScrollWidget {
                    background-color: #FFF;
                }
                QScrollArea QScrollBar:vertical {
                    background-color: #F0F0F0;
                    width: 12px;
                    border-radius: 6px;
                    border: 1px solid #DDD;
                }
                QScrollArea QScrollBar::handle:vertical {
                    background-color: #CCC;
                    border-radius: 5px;
                    border: 1px solid #BBB;
                }
                QScrollArea QScrollBar::handle:vertical:hover {
                    background-color: #AAA;
                }
                QScrollArea QScrollBar::add-line:vertical,
                QScrollArea QScrollBar::sub-line:vertical {
                    background: none;
                    border: none;
                }
                QScrollArea QScrollBar::add-page:vertical,
                QScrollArea QScrollBar::sub-page:vertical {
                    background: none;
                }
                
                /* Specific styling for gallery content to ensure white background */
                QGridLayout {
                    background-color: #FFF;
                }
                QFrame {
                    background-color: #FFF;
                }
                QLabel[objectName="thumbnail"] {
                    background-color: #FFF;
                }
                
                /* Dialog level widgets - keep light theme */
                QDialog > QWidget {
                    background-color: #F5F5F7;
                }
                /* Override for scroll widget specifically */
                QDialog QScrollArea QWidget {
                    background-color: #FFF !important;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #333;
                    color: #EEE;
                }
                QLabel {
                    color: #EEE;
                }
                /* Refresh Button - Blue theme */
                QPushButton#refreshButton {
                    background-color: #0A84FF !important;
                    color: white !important;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton#refreshButton:hover {
                    background-color: #409CFF !important;
                }
                
                /* Delete Button - Red theme */
                QPushButton#deleteButton {
                    background-color: #FF453A !important;
                    color: white !important;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton#deleteButton:hover {
                    background-color: #FF6961 !important;
                }
                QPushButton#deleteButton:disabled {
                    background-color: #5C2B2B !important;
                    color: #888 !important;
                }
                
                /* Save Button - Green theme */
                QPushButton#saveButton {
                    background-color: #32D74B !important;
                    color: white !important;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton#saveButton:hover {
                    background-color: #64E478 !important;
                }
                QPushButton#saveButton:disabled {
                    background-color: #2B4A2F !important;
                    color: #888 !important;
                }
                
                QScrollArea {
                    border: 1px solid #555;
                    background-color: #2b2b2b;
                }
                QScrollArea#galleryScrollArea {
                    background-color: #2b2b2b;
                }
                QScrollArea#galleryScrollArea > QWidget {
                    background-color: #2b2b2b;
                }
                QScrollArea#galleryScrollArea QWidget {
                    background-color: #2b2b2b;
                }
                QScrollArea::corner {
                    background-color: #2b2b2b;
                }
                QWidget#galleryScrollWidget {
                    background-color: #2b2b2b;
                }
                QScrollArea QScrollBar:vertical {
                    background-color: #444 !important;
                    width: 12px;
                    border-radius: 6px;
                    border: 1px solid #555;
                }
                QScrollArea QScrollBar::handle:vertical {
                    background-color: #666 !important;
                    border-radius: 5px;
                    border: 1px solid #555;
                }
                QScrollArea QScrollBar::handle:vertical:hover {
                    background-color: #888 !important;
                }
                QScrollArea QScrollBar::add-line:vertical,
                QScrollArea QScrollBar::sub-line:vertical {
                    background: #444 !important;
                    border: none;
                    height: 0px;
                }
                QScrollArea QScrollBar::add-page:vertical,
                QScrollArea QScrollBar::sub-page:vertical {
                    background: #444 !important;
                }
                QScrollArea QScrollBar:horizontal {
                    background-color: #444 !important;
                    height: 12px;
                    border-radius: 6px;
                    border: 1px solid #555;
                }
                QScrollArea QScrollBar::handle:horizontal {
                    background-color: #666 !important;
                    border-radius: 5px;
                    border: 1px solid #555;
                }
                QScrollArea QScrollBar::handle:horizontal:hover {
                    background-color: #888 !important;
                }
                QScrollArea QScrollBar::add-line:horizontal,
                QScrollArea QScrollBar::sub-line:horizontal {
                    background: #444 !important;
                    border: none;
                    width: 0px;
                }
                QScrollArea QScrollBar::add-page:vertical,
                QScrollArea QScrollBar::sub-page:vertical {
                    background: none;
                }
                
                /* Specific styling for gallery content to ensure dark background */
                QGridLayout {
                    background-color: #2b2b2b;
                }
                QFrame {
                    background-color: #2b2b2b;
                }
                QLabel[objectName="thumbnail"] {
                    background-color: #2b2b2b;
                }
                
                /* Dialog level widgets - keep dark theme */
                QDialog > QWidget {
                    background-color: #333;
                }
                /* Override for scroll widget specifically */
                QDialog QScrollArea QWidget {
                    background-color: #2b2b2b !important;
                }
            """)
        
        # Update info label with dedicated method to prevent font accumulation
        self._update_info_label_style()

    def _apply_gallery_title_bar(self, theme: str):
        """Apply theme-appropriate title bar for gallery"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Get window handle
            hwnd = int(self.winId())
            
            # DWMWA_USE_IMMERSIVE_DARK_MODE
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            
            # Set dark/light mode for title bar
            mode_value = 1 if (theme or 'dark').lower() == 'dark' else 0
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(mode_value)),
                ctypes.sizeof(ctypes.c_int)
            )
        except Exception as e:
            # Fallback - just print error, don't crash
            print(f"Could not apply gallery title bar theme: {e}")
    
    def _force_scroll_area_background(self, theme: str):
        """Force scroll area background color using multiple methods"""
        from PyQt5.QtGui import QPalette
        from PyQt5.QtCore import Qt
        
        if hasattr(self, 'scroll_area') and hasattr(self, 'scroll_widget'):
            if (theme or 'dark').lower() == 'light':
                # Light theme colors
                bg_color = "#FFFFFF"
                scrollbar_bg = "#F0F0F0"
                scrollbar_handle = "#CCCCCC"
                
                # Method 1: Direct StyleSheet with !important
                self.scroll_area.setStyleSheet(f"""
                    QScrollArea {{
                        background-color: {bg_color} !important;
                        border: 1px solid #CCCCCC !important;
                    }}
                    QScrollArea > QWidget {{
                        background-color: {bg_color} !important;
                    }}
                    QScrollArea QWidget {{
                        background-color: {bg_color} !important;
                    }}
                    QScrollArea::corner {{
                        background-color: {bg_color} !important;
                    }}
                    QScrollArea QScrollBar:vertical {{
                        background-color: {scrollbar_bg} !important;
                        width: 12px;
                        border-radius: 6px;
                        border: 1px solid #DDDDDD;
                    }}
                    QScrollArea QScrollBar::handle:vertical {{
                        background-color: {scrollbar_handle} !important;
                        border-radius: 5px;
                        border: 1px solid #BBBBBB;
                        min-height: 20px;
                    }}
                    QScrollArea QScrollBar::handle:vertical:hover {{
                        background-color: #AAAAAA !important;
                    }}
                    QScrollArea QScrollBar::add-line:vertical,
                    QScrollArea QScrollBar::sub-line:vertical {{
                        background: transparent !important;
                        height: 0px;
                        border: none;
                    }}
                    QScrollArea QScrollBar::add-page:vertical,
                    QScrollArea QScrollBar::sub-page:vertical {{
                        background: {scrollbar_bg};
                    }}
                """)
                
                self.scroll_widget.setStyleSheet(f"""
                    QWidget {{
                        background-color: {bg_color};
                    }}
                """)
                
                # Method 2: QPalette
                palette = self.scroll_area.palette()
                palette.setColor(QPalette.Window, Qt.white)
                palette.setColor(QPalette.Base, Qt.white)
                palette.setColor(QPalette.Background, Qt.white)
                self.scroll_area.setPalette(palette)
                self.scroll_area.setAutoFillBackground(True)
                
                widget_palette = self.scroll_widget.palette()
                widget_palette.setColor(QPalette.Window, Qt.white)
                widget_palette.setColor(QPalette.Base, Qt.white)
                widget_palette.setColor(QPalette.Background, Qt.white)
                self.scroll_widget.setPalette(widget_palette)
                self.scroll_widget.setAutoFillBackground(True)
                
            else:
                # Dark theme colors
                bg_color = "#2b2b2b"
                scrollbar_bg = "#444444"
                scrollbar_handle = "#666666"
                
                # Method 1: Direct StyleSheet with !important
                self.scroll_area.setStyleSheet(f"""
                    QScrollArea {{
                        background-color: {bg_color} !important;
                        border: 1px solid #555555 !important;
                    }}
                    QScrollArea > QWidget {{
                        background-color: {bg_color} !important;
                    }}
                    QScrollArea QWidget {{
                        background-color: {bg_color} !important;
                    }}
                    QScrollArea::corner {{
                        background-color: {bg_color} !important;
                    }}
                    QScrollArea QScrollBar:vertical {{
                        background-color: {scrollbar_bg} !important;
                        width: 12px;
                        border-radius: 6px;
                        border: 1px solid #555555;
                    }}
                    QScrollArea QScrollBar::handle:vertical {{
                        background-color: {scrollbar_handle} !important;
                        border-radius: 5px;
                        border: 1px solid #555555;
                        min-height: 20px;
                    }}
                    QScrollArea QScrollBar::handle:vertical:hover {{
                        background-color: #888888 !important;
                    }}
                    QScrollArea QScrollBar::add-line:vertical,
                    QScrollArea QScrollBar::sub-line:vertical {{
                        background: transparent !important;
                        height: 0px;
                        border: none;
                    }}
                    QScrollArea QScrollBar::add-page:vertical,
                    QScrollArea QScrollBar::sub-page:vertical {{
                        background: {scrollbar_bg};
                    }}
                """)
                
                self.scroll_widget.setStyleSheet(f"""
                    QWidget {{
                        background-color: {bg_color};
                    }}
                """)
                
                # Method 2: QPalette
                from PyQt5.QtGui import QColor
                dark_color = QColor(43, 43, 43)  # #2b2b2b
                
                palette = self.scroll_area.palette()
                palette.setColor(QPalette.Window, dark_color)
                palette.setColor(QPalette.Base, dark_color)
                palette.setColor(QPalette.Background, dark_color)
                self.scroll_area.setPalette(palette)
                self.scroll_area.setAutoFillBackground(True)
                
                widget_palette = self.scroll_widget.palette()
                widget_palette.setColor(QPalette.Window, dark_color)
                widget_palette.setColor(QPalette.Base, dark_color)
                widget_palette.setColor(QPalette.Background, dark_color)
                self.scroll_widget.setPalette(widget_palette)
                self.scroll_widget.setAutoFillBackground(True)
            
            # Force repaint
            self.scroll_area.update()
            self.scroll_widget.update()
            self.scroll_area.repaint()
            self.scroll_widget.repaint()
    
    def load_screenshots(self):
        # Clear existing thumbnails
        for label in self.thumbnail_labels:
            self.gallery_layout.removeWidget(label)
            label.deleteLater()
        
        self.thumbnail_labels = []
        self.screenshots = []
        
        # Ensure screenshots directory exists - use repository root (parent of 'source' folder)
        # __file__ is .../source/ui_components/gallery.py -> go up 3 levels to reach repo root
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        screenshots_dir = os.path.join(root_dir, "screenshots")
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
        
        # Find all PNG files in the screenshots directory that start with "screenshot_"
        screenshot_files = glob.glob(os.path.join(screenshots_dir, "screenshot_*.png"))
        
        if not screenshot_files:
            self.info_label.setText(tr.get_text("no_screenshots"))
            self.selected_index = -1
            self.delete_button.setEnabled(False)
            self.export_button.setEnabled(False)
            return
        
        # Sort files by creation time (newest first)
        screenshot_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        self.screenshots = screenshot_files
        
        # Display thumbnails in a grid (4 columns)
        column_count = 4
        for i, file_path in enumerate(screenshot_files):
            # Create thumbnail
            pixmap = QPixmap(file_path)
            thumbnail = pixmap.scaled(QSize(150, 150), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Create label and add to layout
            label = QLabel()
            label.setObjectName("thumbnail")
            label.setPixmap(thumbnail)
            label.setAlignment(Qt.AlignCenter)
            label.setToolTip(file_path)
            
            # Apply theme-appropriate styling
            if (self.theme or 'dark').lower() == 'light':
                label.setStyleSheet("border: 2px solid #CCC; margin: 5px; background-color: #FFF; padding: 5px;")
            else:
                label.setStyleSheet("border: 2px solid #555; margin: 5px; background-color: #222; padding: 5px;")
                
            label.setFixedSize(QSize(180, 180))
            label.mousePressEvent = lambda event, idx=i: self.select_screenshot(idx)
            
            row, column = i // column_count, i % column_count
            self.gallery_layout.addWidget(label, row, column)
            self.thumbnail_labels.append(label)
        
        # Update info text
        self.info_label.setText(f"{tr.get_text('saved_screenshots')} {len(screenshot_files)}")
        
        # Update button styles after loading
        self._apply_button_styles()

    def select_screenshot(self, index):
        # Update button colors first  
        self._apply_button_styles()
        
        # Deselect the previous selection
        if 0 <= self.selected_index < len(self.thumbnail_labels):
            if (self.theme or 'dark').lower() == 'light':
                self.thumbnail_labels[self.selected_index].setStyleSheet("border: 2px solid #CCC; margin: 5px; background-color: #FFF; padding: 5px;")
            else:
                self.thumbnail_labels[self.selected_index].setStyleSheet("border: 2px solid #555; margin: 5px; background-color: #222; padding: 5px;")
        
        # Select the new one
        self.selected_index = index
        if (self.theme or 'dark').lower() == 'light':
            self.thumbnail_labels[index].setStyleSheet("border: 2px solid #007AFF; margin: 5px; background-color: #F0F8FF; padding: 5px;")
        else:
            self.thumbnail_labels[index].setStyleSheet("border: 2px solid #2196F3; margin: 5px; background-color: #333; padding: 5px;")
        
        # Enable buttons
        self.delete_button.setEnabled(True)
        self.export_button.setEnabled(True)
    
    def delete_selected(self):
        if 0 <= self.selected_index < len(self.screenshots):
            file_to_delete = self.screenshots[self.selected_index]
            
            # Confirm deletion
            reply = QMessageBox.question(
                self, 
                tr.get_text("delete_confirmation"), 
                tr.get_text("delete_confirm_text", file_to_delete),
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    os.remove(file_to_delete)
                    self.load_screenshots()  # Refresh the gallery
                    self._apply_button_styles()  # Update button colors after refresh
                    self.parent().status_bar.showMessage(tr.get_text("file_deleted", file_to_delete))
                except Exception as e:
                    QMessageBox.critical(self, tr.get_text("error"), tr.get_text("delete_failed", str(e)))
    
    def export_selected(self):
        if 0 <= self.selected_index < len(self.screenshots):
            file_to_export = self.screenshots[self.selected_index]
            
            # Open file dialog to choose export location
            export_path, _ = QFileDialog.getSaveFileName(
                self, 
                tr.get_text("export_title"), 
                os.path.basename(file_to_export),
                "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*.*)"
            )
            
            if export_path:
                try:
                    # Read the original image
                    image = cv2.imread(file_to_export)
                    
                    # Save to the selected path
                    cv2.imwrite(export_path, image)
                    self._apply_button_styles()  # Update button colors after export
                    self.parent().status_bar.showMessage(tr.get_text("file_exported", export_path))
                except Exception as e:
                    QMessageBox.critical(self, tr.get_text("error"), tr.get_text("export_failed", str(e)))
