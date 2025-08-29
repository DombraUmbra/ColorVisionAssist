import os
import glob
import cv2
from PyQt5.QtWidgets import (QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                           QWidget, QGridLayout, QScrollArea, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPixmap, QIcon

from ..translations import translator as tr

class ScreenshotGallery(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr.get_text("gallery_title"))
        self.setGeometry(200, 200, 800, 600)
        # Non-modal dialog with standard window frame
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setModal(False)

        # Theme
        self.theme = getattr(parent, 'theme', 'dark') if parent else 'dark'

        # App icon
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "icons",
            "app_icon.png",
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Layouts
        layout = QVBoxLayout()

        # Info label
        self.info_label = QLabel(tr.get_text("saved_screenshots"))
        self.info_label.setObjectName("infoLabel")
        layout.addWidget(self.info_label)

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("galleryScrollArea")

        scroll_widget = QWidget()
        scroll_widget.setObjectName("galleryScrollWidget")
        self.gallery_layout = QGridLayout(scroll_widget)

        self.scroll_area = scroll_area
        self.scroll_widget = scroll_widget
        self._set_initial_colors()

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Buttons
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton(tr.get_text("refresh"))
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.refresh_gallery)

        self.delete_button = QPushButton(tr.get_text("delete"))
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_selected)
        self.delete_button.setEnabled(False)

        self.export_button = QPushButton(tr.get_text("save"))  # Save
        self.export_button.setObjectName("saveButton")
        self.export_button.clicked.connect(self.export_selected)
        self.export_button.setEnabled(False)

        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.export_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # State
        self.screenshots = []
        self.selected_index = -1
        self.thumbnail_labels = []  # cell QWidget containers for cleanup
        self._thumb_labels = []     # QLabel thumbnails only (index-aligned)
        self.selected_indices = set()

        # Load and theme
        self.load_screenshots()
        self.apply_gallery_theme(self.theme)
        self._force_scroll_area_background(self.theme)
        self._force_scroll_area_update()

        # Title bar theme immediate + delayed
        self._apply_gallery_title_bar(self.theme)
        QTimer.singleShot(50, lambda: self._apply_gallery_title_bar(self.theme))

    def refresh_gallery(self):
        """Briefly clear and reload to show visual feedback for refresh."""
        # Clear grid
        for cell in self.thumbnail_labels:
            self.gallery_layout.removeWidget(cell)
            cell.deleteLater()
        self.thumbnail_labels = []
        self._thumb_labels = []
        self.selected_indices.clear()
        self.delete_button.setEnabled(False)
        self.export_button.setEnabled(False)
        # After a short delay, reload
        QTimer.singleShot(250, self.load_screenshots)
    
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

    def update_ui_language(self):
        """Update UI elements to reflect current language"""
        # Update window title
        self.setWindowTitle(tr.get_text("gallery_title"))
        
        # Update info label
        self.info_label.setText(tr.get_text("saved_screenshots"))
        
        # Update button texts
        self.refresh_button.setText(tr.get_text("refresh"))
        self.delete_button.setText(tr.get_text("delete_selected"))
        self.export_button.setText(tr.get_text("save"))

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
        for cell in self.thumbnail_labels:
            self.gallery_layout.removeWidget(cell)
            cell.deleteLater()
        self.thumbnail_labels = []
        self._thumb_labels = []
        self.screenshots = []
        self.selected_indices.clear()
        
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
            
            # Create label and add to layout inside a cell container
            thumb_label = ClickableLabel(i, self)
            thumb_label.setObjectName("thumbnail")
            thumb_label.setPixmap(thumbnail)
            thumb_label.setAlignment(Qt.AlignCenter)
            thumb_label.setToolTip(file_path)
            # Remove decorative frame; use clean margins only
            thumb_label.setStyleSheet("margin: 0px; background: transparent; padding: 0px;")
            thumb_label.setFixedSize(QSize(180, 150))

            # Caption with filename index and date
            base = os.path.basename(file_path)
            num = ''.join(filter(str.isdigit, os.path.splitext(base)[0]))
            from datetime import datetime as _dt
            date_txt = _dt.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M')
            caption = QLabel(f"#{num} • {date_txt}")
            caption.setAlignment(Qt.AlignCenter)
            caption.setStyleSheet("QLabel { color: #888; font-size: 9px; padding: 0px; margin: 2px 0 8px 0; }")

            # Cell container
            cell = QWidget()
            v = QVBoxLayout(cell)
            v.setContentsMargins(4, 0, 4, 0)
            v.setSpacing(0)
            v.addWidget(thumb_label)
            v.addWidget(caption)

            row, column = i // column_count, i % column_count
            self.gallery_layout.addWidget(cell, row, column)
            # Track widgets to allow clearing later
            self.thumbnail_labels.append(cell)
            self._thumb_labels.append(thumb_label)
        
        # Update info text
        self.info_label.setText(f"{tr.get_text('saved_screenshots')} {len(screenshot_files)}")
        
        # Update button styles after loading
        self._apply_button_styles()

    def toggle_select(self, index):
        # Multi-select support; toggle selection state
        if index in self.selected_indices:
            self.selected_indices.remove(index)
        else:
            self.selected_indices.add(index)
        # Update visuals
        for i, widget in enumerate(self.gallery_widgets()):
            if not isinstance(widget, QLabel) or widget.objectName() != "thumbnail":
                continue
            if i in self.selected_indices:
                widget.setStyleSheet("margin: 4px; background: rgba(33,150,243,0.12);")
            else:
                widget.setStyleSheet("margin: 4px; background: transparent;")
        self.delete_button.setEnabled(len(self.selected_indices) > 0)
        self.export_button.setEnabled(len(self.selected_indices) == 1)

    def select_single(self, index):
        """Single-select support; select only the specified index"""
        # Clear all selections
        self.selected_indices.clear()
        # Add the specified index
        self.selected_indices.add(index)
        # Update visuals
        for i, widget in enumerate(self.gallery_widgets()):
            if not isinstance(widget, QLabel) or widget.objectName() != "thumbnail":
                continue
            if i in self.selected_indices:
                widget.setStyleSheet("margin: 4px; background: rgba(33,150,243,0.12);")
            else:
                widget.setStyleSheet("margin: 4px; background: transparent;")
        self.delete_button.setEnabled(len(self.selected_indices) > 0)
        self.export_button.setEnabled(len(self.selected_indices) == 1)

    def gallery_widgets(self):
        # Helper to iterate added thumbnail QLabel widgets in order
        return list(self._thumb_labels)
    
    def delete_selected(self):
        if not self.selected_indices:
            return
        # Confirm deletion (count)
        count = len(self.selected_indices)
        reply = self._themed_question(
            tr.get_text("confirm_deletion"),
            tr.get_text("delete_confirm_text", f"{count} file(s)")
        )
        if reply == QMessageBox.Yes:
            try:
                for idx in sorted(self.selected_indices, reverse=True):
                    if 0 <= idx < len(self.screenshots):
                        os.remove(self.screenshots[idx])
                self.load_screenshots()
                self._apply_button_styles()
                self.parent().status_bar.showMessage(tr.get_text("file_deleted", f"{count}"))
            except Exception as e:
                self._themed_critical(tr.get_text("error"), tr.get_text("delete_failed", str(e)))
    
    def export_selected(self):
        if len(self.selected_indices) == 1:
            index = next(iter(self.selected_indices))
            file_to_export = self.screenshots[index]
            
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
                    self._themed_critical(tr.get_text("error"), tr.get_text("export_failed", str(e)))

    def open_fullscreen(self, index):
        """Open the specified screenshot in fullscreen mode with overlay controls.

        - Modern circular icon buttons (minimize, close) in the top-right
        - Minimize actually minimizes the fullscreen dialog (does not close)
        - Auto-hide controls and info when mouse is idle; show again on movement
        - Image resizes to always use available space
        """
        if 0 <= index < len(self.screenshots):
            from PyQt5.QtWidgets import (
                QDialog,
                QLabel,
                QVBoxLayout,
                QHBoxLayout,
                QPushButton,
                QWidget,
                QStyle,
            )
            from PyQt5.QtCore import Qt, QTimer, QSize, QEvent
            from PyQt5.QtGui import QPixmap, QIcon
            import os
            from datetime import datetime

            class FullscreenDialog(QDialog):
                """Fullscreen image viewer with auto-hiding overlays."""

                def __init__(self, parent, image_path: str):
                    super().__init__(parent)
                    # Start in fullscreen (frameless)
                    self._is_fullscreen = True
                    self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
                    # Cover the screen initially
                    scr_size = parent.screen().size()
                    self.setGeometry(0, 0, scr_size.width(), scr_size.height())
                    self.setStyleSheet("background-color: black;")
                    # Allow shrinking in windowed mode via minimum size
                    self.setMinimumSize(QSize(160, 120))

                    self.original_pixmap = QPixmap(image_path)
                    self.setMouseTracking(True)

                    # App icon (same as other windows)
                    try:
                        icon_path = os.path.join(
                            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                            "icons",
                            "app_icon.png",
                        )
                        if os.path.exists(icon_path):
                            self.setWindowIcon(QIcon(icon_path))
                    except Exception:
                        pass

                    # Build UI
                    self._build_ui(image_path)
                    self._install_behavior()

                def _build_ui(self, image_path: str):
                    # Layout only contains the image; overlays are floating widgets (no layout impact)
                    self.main_layout = QVBoxLayout(self)
                    self.main_layout.setContentsMargins(0, 0, 0, 0)
                    self.main_layout.setSpacing(0)

                    # Floating Top toolbar
                    self.toolbar_widget = QWidget(self)
                    self.toolbar_widget.setAttribute(Qt.WA_TranslucentBackground, True)
                    toolbar_layout = QHBoxLayout(self.toolbar_widget)
                    toolbar_layout.setContentsMargins(10, 10, 10, 10)
                    toolbar_layout.setSpacing(8)
                    toolbar_layout.addStretch()

                    # Minimize button
                    self.minimize_btn = QPushButton(self.toolbar_widget)
                    self.minimize_btn.setToolTip(tr.get_text("windowed"))
                    self.minimize_btn.setCursor(Qt.PointingHandCursor)
                    self.minimize_btn.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMinButton))
                    self.minimize_btn.setIconSize(QSize(14, 14))
                    self.minimize_btn.setFixedSize(32, 32)
                    self.minimize_btn.setStyleSheet(
                        """
                        QPushButton {
                            background-color: rgba(240, 240, 240, 0.95);
                            border: 1px solid rgba(0, 0, 0, 0.12);
                            border-radius: 16px;
                        }
                        QPushButton:hover { background-color: rgba(245, 245, 245, 0.95); }
                        QPushButton:pressed { background-color: rgba(230, 230, 230, 0.95); }
                        """
                    )
                    toolbar_layout.addWidget(self.minimize_btn)

                    # Close button
                    self.close_btn = QPushButton(self.toolbar_widget)
                    self.close_btn.setToolTip(tr.get_text("close"))
                    self.close_btn.setCursor(Qt.PointingHandCursor)
                    self.close_btn.setIcon(self.style().standardIcon(QStyle.SP_TitleBarCloseButton))
                    self.close_btn.setIconSize(QSize(14, 14))
                    self.close_btn.setFixedSize(32, 32)
                    self.close_btn.setStyleSheet(
                        """
                        QPushButton {
                            background-color: rgba(255, 59, 48, 0.80);
                            border: 1px solid rgba(255, 59, 48, 0.9);
                            border-radius: 16px;
                            color: white;
                        }
                        QPushButton:hover { background-color: rgba(255, 59, 48, 0.92); }
                        QPushButton:pressed { background-color: rgba(255, 59, 48, 1.0); }
                        """
                    )
                    toolbar_layout.addWidget(self.close_btn)

                    # Image area
                    self.image_label = QLabel(self)
                    self.image_label.setAlignment(Qt.AlignCenter)
                    self.image_label.setMouseTracking(True)
                    try:
                        from PyQt5.QtWidgets import QSizePolicy
                        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                        self.image_label.setMinimumSize(1, 1)
                    except Exception:
                        pass
                    self.main_layout.addWidget(self.image_label, 1)

                    # Bottom info bar
                    self.info_widget = QWidget(self)
                    self.info_widget.setAttribute(Qt.WA_TranslucentBackground, True)
                    info_layout = QHBoxLayout(self.info_widget)
                    info_layout.setContentsMargins(12, 8, 12, 12)
                    info_layout.setSpacing(8)

                    file_name = os.path.basename(image_path)
                    try:
                        mod_time = os.path.getmtime(image_path)
                        date_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        date_str = "Unknown"
                    # Keep for window title usage in windowed mode
                    self._file_name = file_name
                    self._date_str = date_str

                    self.info_label = QLabel(f"📁 {file_name}  |  📅 {date_str}", self.info_widget)
                    self.info_label.setStyleSheet(
                        """
                        QLabel {
                            color: rgba(255, 255, 255, 0.88);
                            font-size: 12px;
                            background-color: rgba(0, 0, 0, 0.45);
                            padding: 8px 12px;
                            border-radius: 6px;
                        }
                        """
                    )
                    info_layout.addWidget(self.info_label)
                    info_layout.addStretch()

                    self._update_image()
                    self._update_overlay_positions()
                    # Ensure overlays are on top and visible initially
                    self.toolbar_widget.show()
                    self.info_widget.show()
                    self.toolbar_widget.raise_()
                    self.info_widget.raise_()
                    # Ensure focus/stacking over gallery
                    self.raise_()
                    self.activateWindow()

                def _install_behavior(self):
                    # Button actions
                    self.minimize_btn.clicked.connect(self._toggle_windowed)
                    self.close_btn.clicked.connect(self.accept)

                    # Hover tracking for overlays to prevent idle while hovering
                    self._hover_count = 0
                    self.toolbar_widget.installEventFilter(self)
                    self.info_widget.installEventFilter(self)
                    self.minimize_btn.installEventFilter(self)
                    self.close_btn.installEventFilter(self)
                    self.info_label.installEventFilter(self)

                    # Idle/auto-hide timer
                    self._idle_timer = QTimer(self)
                    self._idle_timer.setInterval(2000)
                    self._idle_timer.timeout.connect(self._on_idle_timeout)

                    # Start with overlays visible, then arm timer
                    self._show_overlays()
                    self._idle_timer.start()

                    # Set correct icon for current mode
                    self._update_minimize_icon()
                    # Ensure initial focus
                    self.raise_()
                    self.activateWindow()

                def _on_idle_timeout(self):
                    # Do not enter idle if hovering controls/info
                    if self._hover_count > 0:
                        self._idle_timer.start()
                        return
                    self._hide_overlays()

                def _hide_overlays(self):
                    # In windowed mode keep overlays hidden anyway; in fullscreen also hide and blank cursor
                    self.toolbar_widget.setVisible(False)
                    self.info_widget.setVisible(False)
                    if self._is_fullscreen:
                        # Hide cursor in idle only in fullscreen
                        self.setCursor(Qt.BlankCursor)
                        self.image_label.setCursor(Qt.BlankCursor)

                def _show_overlays(self):
                    if self._is_fullscreen:
                        self.toolbar_widget.setVisible(True)
                        self.info_widget.setVisible(True)
                    else:
                        self.toolbar_widget.setVisible(False)
                        self.info_widget.setVisible(False)
                    # Restore cursor (never blank outside fullscreen idle)
                    self.setCursor(Qt.ArrowCursor)
                    self.image_label.setCursor(Qt.ArrowCursor)

                def mouseMoveEvent(self, event):
                    # Show overlays and reset idle timer when mouse moves
                    self._show_overlays()
                    self._idle_timer.start()
                    super().mouseMoveEvent(event)

                def mouseDoubleClickEvent(self, event):
                    # Double click to toggle fullscreen/windowed
                    try:
                        if event.button() == Qt.LeftButton:
                            self._toggle_windowed()
                    except Exception:
                        pass
                    super().mouseDoubleClickEvent(event)

                def eventFilter(self, watched, event):
                    if event.type() in (QEvent.Enter, QEvent.HoverEnter):
                        self._hover_count += 1
                        self._show_overlays()
                        self._idle_timer.start()
                    elif event.type() in (QEvent.Leave, QEvent.HoverLeave):
                        self._hover_count = max(0, self._hover_count - 1)
                        # When leaving, restart timer so it can hide later if still idle
                        self._idle_timer.start()
                    return super().eventFilter(watched, event)

                def resizeEvent(self, event):
                    self._update_image()
                    self._update_overlay_positions()
                    # Keep overlays on top
                    self.toolbar_widget.raise_()
                    self.info_widget.raise_()
                    # Avoid geometry loops when maximized/fullscreen/minimized
                    if not (self.windowState() & (Qt.WindowMaximized | Qt.WindowFullScreen | Qt.WindowMinimized)):
                        self._ensure_on_screen()
                    super().resizeEvent(event)

                def showEvent(self, event):
                    # Position and stack overlays once the widget is shown
                    self._update_overlay_positions()
                    self.toolbar_widget.raise_()
                    self.info_widget.raise_()
                    if not (self.windowState() & (Qt.WindowMaximized | Qt.WindowFullScreen | Qt.WindowMinimized)):
                        self._ensure_on_screen()
                    # If already in windowed mode, (re)apply title bar theme
                    if not self._is_fullscreen:
                        self._apply_title_bar_theme()
                        # Hide overlays in windowed mode
                        self.toolbar_widget.hide()
                        self.info_widget.hide()
                    super().showEvent(event)

                def keyPressEvent(self, event):
                    if event.key() == Qt.Key_Escape:
                        self.accept()
                    else:
                        super().keyPressEvent(event)

                def _update_image(self):
                    if self.original_pixmap.isNull():
                        self.image_label.clear()
                        return

                    # Always scale to full client area, independent of overlay visibility
                    avail_w = max(1, self.width())
                    avail_h = max(1, self.height())
                    scaled = self.original_pixmap.scaled(
                        avail_w,
                        avail_h,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                    self.image_label.setPixmap(scaled)

                def _update_overlay_positions(self):
                    # Position toolbar at top-right, info at bottom-left, with margins
                    margin = 12
                    # Ensure proper size based on content
                    tb_size = self.toolbar_widget.sizeHint()
                    self.toolbar_widget.setGeometry(
                        max(0, self.width() - tb_size.width() - margin),
                        margin,
                        tb_size.width(),
                        tb_size.height(),
                    )
                    info_size = self.info_widget.sizeHint()
                    self.info_widget.setGeometry(
                        margin,
                        max(0, self.height() - info_size.height() - margin),
                        min(self.width() - 2 * margin, info_size.width()),
                        info_size.height(),
                    )

                def _toggle_windowed(self):
                    if self._is_fullscreen:
                        # Switch to windowed mode with system frame so user can move/resize
                        self._is_fullscreen = False
                        self.setWindowFlags(
                            Qt.Window
                            | Qt.WindowTitleHint
                            | Qt.WindowSystemMenuHint
                            | Qt.WindowMinMaxButtonsHint
                            | Qt.WindowCloseButtonHint
                        )
                        # Detach from parent to behave as independent window and avoid close on resize/focus
                        try:
                            self.setParent(None)
                        except Exception:
                            pass
                        # Set window title to file name and date
                        try:
                            self.setWindowTitle(f"{self._file_name} — {self._date_str}")
                        except Exception:
                            pass
                        self.show()
                        self.showNormal()
                        # Size to image and keep within screen bounds
                        scr = self.screen().availableGeometry()
                        max_w = int(scr.width() * 0.85)
                        max_h = int(scr.height() * 0.85)
                        img_w = max(1, self.original_pixmap.width())
                        img_h = max(1, self.original_pixmap.height())
                        scale = min(max_w / img_w, max_h / img_h, 1.0)
                        win_w = max(480, int(img_w * scale))
                        win_h = max(360, int(img_h * scale))
                        self.resize(win_w, win_h)
                        x = scr.x() + (scr.width() - win_w) // 2
                        y = scr.y() + (scr.height() - win_h) // 2
                        x = max(scr.x(), min(x, scr.right() - win_w))
                        y = max(scr.y(), min(y, scr.bottom() - win_h))
                        self.move(x, y)
                        self._ensure_on_screen()
                        # Apply themed title bar on Windows (immediate + delayed)
                        self._apply_title_bar_theme()
                        QTimer.singleShot(50, self._apply_title_bar_theme)
                        # Hide overlays and info in windowed mode
                        self.toolbar_widget.hide()
                        self.info_widget.hide()
                    else:
                        # Back to fullscreen frameless
                        self._is_fullscreen = True
                        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
                        self.show()
                        self.showFullScreen()
                        # Show overlays again and restart idle timer
                        self._show_overlays()
                        self._idle_timer.start()
                    self._update_minimize_icon()
                    self._update_overlay_positions()
                    self.raise_()
                    self.activateWindow()

                def changeEvent(self, event):
                    # Prevent getting stuck minimized by restoring and focusing if minimized
                    if event.type() == QEvent.WindowStateChange:
                        # Only auto-restore when in fullscreen; allow minimize in windowed mode
                        if (self.windowState() & Qt.WindowMinimized) and self._is_fullscreen:
                            QTimer.singleShot(0, self._restore_from_minimize)
                        # If user clicks Maximize in windowed mode, switch to our fullscreen view instead
                        elif (self.windowState() & Qt.WindowMaximized) and (not self._is_fullscreen):
                            QTimer.singleShot(0, self._enter_fullscreen_from_maximize)
                    super().changeEvent(event)

                def _restore_from_minimize(self):
                    try:
                        self.showNormal()
                        self.raise_()
                        self.activateWindow()
                    except Exception:
                        pass

                def _enter_fullscreen_from_maximize(self):
                    """Handle system maximize in windowed mode by entering true fullscreen."""
                    try:
                        # Drop maximize, then enter fullscreen frameless
                        self.showNormal()
                        self._is_fullscreen = True
                        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
                        self.show()
                        self.showFullScreen()
                        # Restore overlays and cursor behavior for fullscreen
                        self._update_minimize_icon()
                        self._show_overlays()
                        self._idle_timer.start()
                        self._update_overlay_positions()
                        self.raise_()
                        self.activateWindow()
                    except Exception:
                        pass

                def moveEvent(self, event):
                    # Keep the window within visible screen area when moved
                    if not (self.windowState() & (Qt.WindowMaximized | Qt.WindowFullScreen | Qt.WindowMinimized)):
                        self._ensure_on_screen()
                    super().moveEvent(event)

                def _ensure_on_screen(self):
                    try:
                        scr = self.screen().availableGeometry()
                        g = self.frameGeometry()
                        # Clamp position
                        x = max(scr.x(), min(g.x(), scr.right() - g.width()))
                        y = max(scr.y(), min(g.y(), scr.bottom() - g.height()))
                        if x != g.x() or y != g.y():
                            self.move(x, y)
                    except Exception:
                        pass

                def _apply_title_bar_theme(self):
                    """Apply theme-appropriate Windows title bar color to match app theme (safe no-op elsewhere)."""
                    try:
                        theme = getattr(self.parent(), 'theme', 'dark') if self.parent() is not None else 'dark'
                        import ctypes
                        hwnd = int(self.winId())
                        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                        mode_value = 1 if (theme or 'dark').lower() == 'dark' else 0
                        ctypes.windll.dwmapi.DwmSetWindowAttribute(
                            hwnd,
                            DWMWA_USE_IMMERSIVE_DARK_MODE,
                            ctypes.byref(ctypes.c_int(mode_value)),
                            ctypes.sizeof(ctypes.c_int)
                        )
                    except Exception:
                        # Non-Windows or API unavailable
                        pass

                def _update_minimize_icon(self):
                    if self._is_fullscreen:
                        # Show restore/normal icon to indicate exit fullscreen
                        self.minimize_btn.setIcon(
                            self.style().standardIcon(QStyle.SP_TitleBarNormalButton)
                        )
                        self.minimize_btn.setToolTip(tr.get_text("windowed"))
                    else:
                        # Show maximize icon to indicate go fullscreen
                        self.minimize_btn.setIcon(
                            self.style().standardIcon(QStyle.SP_TitleBarMaxButton)
                        )
                        self.minimize_btn.setToolTip(tr.get_text("fullscreen"))

            # Create and show the dialog non-modally and keep a reference
            # Use WindowStaysOnTop to ensure it appears above the gallery window
            self._active_fullscreen_dialog = FullscreenDialog(self, self.screenshots[index])
            self._active_fullscreen_dialog.show()
            self._active_fullscreen_dialog.raise_()
            self._active_fullscreen_dialog.activateWindow()

    def _apply_dialog_stylesheet(self, widget):
        theme = (self.theme or 'dark').lower()
        if theme == 'light':
            widget.setStyleSheet(
                """
                QDialog, QMessageBox { background-color: #F5F5F7; color: #222; }
                QLabel { color: #222; }
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
                QPushButton { background-color: #3A3A3A; color: #CCC; border: none; border-radius: 4px; font-weight: bold; padding: 6px 10px; }
                QPushButton:hover { background-color: #4A4A4A; color: #64B5F6; }
                QPushButton:pressed { background-color: #5A5A5A; }
                """
            )

    def _themed_critical(self, title: str, text: str):
        box = QMessageBox(self)
        self._apply_dialog_stylesheet(box)
        box.setIcon(QMessageBox.Critical)
        box.setWindowTitle(title)
        box.setText(text)
        box.setStandardButtons(QMessageBox.Ok)
        box.exec_()

    def _themed_question(self, title: str, text: str) -> int:
        # Localized Yes/No labels
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
        # Consistent order: No (left), Yes (right); use ActionRole to preserve order
        no_btn = box.addButton(tr.get_text("no"), QMessageBox.ActionRole)
        yes_btn = box.addButton(tr.get_text("yes"), QMessageBox.ActionRole)
        # Make window close (X) behave like No and Enter like Yes
        try:
            box.setEscapeButton(no_btn)
            box.setDefaultButton(yes_btn)
        except Exception:
            pass
        # Style buttons inline (theme-aware): Yes green, No red
        try:
            theme = getattr(self, 'theme', 'dark').lower()
            if theme == 'light':
                yes_btn.setStyleSheet(
                    """
                    QPushButton { background-color: #34C759; color: white; border: none; border-radius: 4px; padding: 6px 10px; font-weight: bold; }
                    QPushButton:hover { background-color: #248A3D; }
                    """
                )
                no_btn.setStyleSheet(
                    """
                    QPushButton { background-color: #FF3B30; color: white; border: none; border-radius: 4px; padding: 6px 10px; font-weight: bold; }
                    QPushButton:hover { background-color: #D70015; }
                    """
                )
            else:
                yes_btn.setStyleSheet(
                    """
                    QPushButton { background-color: #32D74B; color: white; border: none; border-radius: 4px; padding: 6px 10px; font-weight: bold; }
                    QPushButton:hover { background-color: #64E478; }
                    """
                )
                no_btn.setStyleSheet(
                    """
                    QPushButton { background-color: #FF453A; color: white; border: none; border-radius: 4px; padding: 6px 10px; font-weight: bold; }
                    QPushButton:hover { background-color: #FF6961; }
                    """
                )
        except Exception:
            pass
        box.exec_()
        if box.clickedButton() is yes_btn:
            return QMessageBox.Yes
        return QMessageBox.No

# Helper clickable label to support multi-select toggling
class ClickableLabel(QLabel):
    def __init__(self, index: int, gallery: ScreenshotGallery):
        super().__init__()
        self._index = index
        self._gallery = gallery

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._gallery.select_single(self._index)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._gallery.open_fullscreen(self._index)
        super().mouseDoubleClickEvent(event)
