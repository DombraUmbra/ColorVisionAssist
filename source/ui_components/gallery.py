import os
import glob
import cv2
import re
from datetime import datetime
from PyQt5.QtWidgets import (QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                           QWidget, QGridLayout, QScrollArea, QMessageBox, QFileDialog, QSizePolicy, QComboBox)
from PyQt5.QtCore import Qt, QSize, QTimer, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor

from ..translations import translator as tr
from .groups import _apply_combo_theme, HiddenCurrentCombo
from .buttons import update_button_theme
from .styles import get_colorblind_friendly_colors, adjust_color_brightness


def natural_sort_key(text):
    """
    Generate a key for natural sorting that handles numbers correctly.
    Handles both old format (screenshot_1.png) and new format (screenshot_31-12-2024_15-30-45_001.png)
    Converts numbers in strings to integers for proper numeric sorting.
    Example: '1.png' < '2.png' < '10.png' instead of '1.png' < '10.png' < '2.png'
    """
    def convert(chunk):
        return int(chunk) if chunk.isdigit() else chunk.lower()
    
    return [convert(chunk) for chunk in re.split(r'(\d+)', text)]


def extract_date_from_filename(file_path):
    """
    Extract date information from filename or file modification time.
    Returns formatted date string in dd/mm/yyyy format.
    """
    filename = os.path.basename(file_path)
    
    # Try to extract date from new format filename: screenshot_dd-mm-yyyy_hh-mm-ss_001.png
    if filename.startswith("screenshot_") and filename.endswith(".png"):
        parts = filename[11:-4].split("_")  # Remove "screenshot_" prefix and ".png" suffix
        if len(parts) >= 2:  # At least date and time parts
            try:
                date_part = parts[0]  # dd-mm-yyyy
                time_part = parts[1]  # hh-mm-ss
                
                # Parse and reformat to dd/mm/yyyy
                day, month, year = map(int, date_part.split("-"))
                hour, minute, second = map(int, time_part.split("-"))
                
                return f"{day:02d}/{month:02d}/{year}", f"{hour:02d}:{minute:02d}"
            except (ValueError, IndexError):
                pass  # Fall back to file modification time
    
    # Fall back to file modification time for old format files
    try:
        mod_time = os.path.getmtime(file_path)
        file_datetime = datetime.fromtimestamp(mod_time)
        date_str = file_datetime.strftime("%d/%m/%Y")
        time_str = file_datetime.strftime("%H:%M")
        return date_str, time_str
    except OSError:
        return "Unknown", "Unknown"


def extract_number_from_filename(filename):
    """
    Extract a display number from filename for caption.
    For new format: extracts the sequence number
    For old format: extracts the main number
    """
    if filename.startswith("screenshot_") and filename.endswith(".png"):
        parts = filename[11:-4].split("_")  # Remove "screenshot_" prefix and ".png" suffix
        
        # New format: screenshot_dd-mm-yyyy_hh-mm-ss_001.png
        if len(parts) >= 3:
            try:
                return int(parts[-1])  # Last part is the sequence number
            except ValueError:
                pass
        
        # Old format: screenshot_123.png
        if len(parts) == 1:
            try:
                return int(parts[0])
            except ValueError:
                pass
    
    # Fallback: extract any numbers from filename
    numbers = ''.join(filter(str.isdigit, filename))
    try:
        return int(numbers) if numbers else 0
    except ValueError:
        return 0


def date_sort_key(file_path):
    """
    Generate a sort key based on date information in filename or file modification time.
    Prioritizes date from filename if available, falls back to file modification time.
    """
    filename = os.path.basename(file_path)
    
    # Try to extract date from new format filename: screenshot_dd-mm-yyyy_hh-mm-ss_001.png
    if filename.startswith("screenshot_") and filename.endswith(".png"):
        parts = filename[11:-4].split("_")  # Remove "screenshot_" prefix and ".png" suffix
        if len(parts) >= 2:  # At least date and time parts
            try:
                date_part = parts[0]  # dd-mm-yyyy
                time_part = parts[1]  # hh-mm-ss
                
                # Parse date: dd-mm-yyyy
                day, month, year = map(int, date_part.split("-"))
                # Parse time: hh-mm-ss
                hour, minute, second = map(int, time_part.split("-"))
                
                # Create datetime object for sorting
                file_datetime = datetime(year, month, day, hour, minute, second)
                return file_datetime.timestamp()
            except (ValueError, IndexError):
                pass  # Fall back to file modification time
    
    # Fall back to file modification time for old format or unparseable files
    try:
        return os.path.getmtime(file_path)
    except OSError:
        return 0  # Default for files that can't be accessed


class ScreenshotGallery(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Give the dialog a stable object name for targeted styling
        self.setObjectName("screenshotGalleryDialog")
        self.setWindowTitle(tr.get_text("gallery_title"))
        self.setGeometry(200, 200, 800, 600)
        # Non-modal dialog with standard window frame including maximize button
        self.setWindowFlags(
            Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint |
            Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint |
            Qt.WindowSystemMenuHint
        )
        self.setModal(False)

        # Ensure proper window behavior for minimize
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        self.setAttribute(Qt.WA_DeleteOnClose, False)

        # Theme
        self.theme = getattr(parent, 'theme', 'dark') if parent else 'dark'

        # App icon
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "icons", "app_icon.png",
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Root layout
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Header: info + sort controls
        self.header_widget = QWidget()
        # Ensure stylesheet backgrounds are painted for this container
        try:
            self.header_widget.setAttribute(Qt.WA_StyledBackground, True)
        except Exception:
            pass
        self.header_widget.setObjectName("galleryHeader")
        info_sort_layout = QHBoxLayout(self.header_widget)
        info_sort_layout.setContentsMargins(8, 6, 8, 6)
        info_sort_layout.setSpacing(10)

        self.info_label = QLabel(tr.get_text("saved_screenshots"))
        self.info_label.setObjectName("infoLabel")

        self.sort_label = QLabel(tr.get_text("sort_by") + ":")
        self.sort_label.setObjectName("sortLabel")

        self.sort_combo = HiddenCurrentCombo()
        self.sort_combo.setObjectName("sortCombo")
        self.sort_combo.addItem(tr.get_text("sort_by_name_asc"), "name_asc")
        self.sort_combo.addItem(tr.get_text("sort_by_name_desc"), "name_desc")
        self.sort_combo.addItem(tr.get_text("sort_by_date_asc"), "date_asc")
        self.sort_combo.addItem(tr.get_text("sort_by_date_desc"), "date_desc")
        self.sort_combo.currentTextChanged.connect(self.sort_screenshots)
        try:
            _apply_combo_theme(self.sort_combo, self)
        except Exception:
            pass

        info_sort_layout.addWidget(self.info_label)
        info_sort_layout.addStretch()
        info_sort_layout.addWidget(self.sort_label)
        info_sort_layout.addWidget(self.sort_combo)
        layout.addWidget(self.header_widget)

        # Scroll area and content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("galleryScrollArea")
        scroll_area.setContentsMargins(0, 0, 0, 0)

        scroll_widget = QWidget()
        # Ensure stylesheet backgrounds are painted for the scroll content widget
        try:
            scroll_widget.setAttribute(Qt.WA_StyledBackground, True)
        except Exception:
            pass
        scroll_widget.setObjectName("galleryScrollWidget")
        scroll_widget.setContentsMargins(0, 0, 0, 0)
        self.gallery_layout = QGridLayout(scroll_widget)
        self.gallery_layout.setSpacing(4)
        self.gallery_layout.setContentsMargins(0, 0, 0, 0)
        scroll_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.scroll_area = scroll_area
        self.scroll_widget = scroll_widget
        self._set_initial_colors()

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Footer: buttons container
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(8, 6, 8, 6)
        button_layout.setSpacing(10)
        self.refresh_button = QPushButton(tr.get_text("refresh"))
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.refresh_gallery)
        self.delete_button = QPushButton(tr.get_text("delete"))
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_selected)
        self.delete_button.setEnabled(False)
        self.export_button = QPushButton(tr.get_text("save"))
        self.export_button.setObjectName("saveButton")
        self.export_button.clicked.connect(self.export_selected)
        self.export_button.setEnabled(False)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.export_button)

        self.footer_widget = QWidget()
        # Ensure stylesheet backgrounds are painted for this container
        try:
            self.footer_widget.setAttribute(Qt.WA_StyledBackground, True)
        except Exception:
            pass
        self.footer_widget.setObjectName("galleryFooter")
        self.footer_widget.setLayout(button_layout)
        layout.addWidget(self.footer_widget)

        self.setLayout(layout)

        # Fullscreen state
        self.is_fullscreen = False
        self.normal_geometry = None

        # Selection state
        self.screenshots = []
        self.selected_index = -1
        self.last_selected_index = -1
        self.thumbnail_labels = []
        self._thumb_labels = []
        self.selected_indices = set()

        # Load and theme
        self.load_screenshots()
        self.apply_gallery_theme(self.theme)
        self._force_scroll_area_background(self.theme)
        self._force_scroll_area_update()
        
        # Force complete theme application
        self._force_complete_theme_application(self.theme)

        # Title bar theme immediate + delayed
        self._apply_gallery_title_bar(self.theme)
        QTimer.singleShot(50, lambda: self._apply_gallery_title_bar(self.theme))

    def showEvent(self, event):
        try:
            self._sync_theme_from_parent()
            # Force immediate theme reapplication when shown
            QTimer.singleShot(10, lambda: self._force_complete_theme_application(self.theme))
            QTimer.singleShot(50, lambda: self.apply_gallery_theme(self.theme))
            # Restore last geometry from current profile if available
            try:
                parent = self.parent()
                profile = getattr(parent, 'current_profile', None)
                if profile:
                    gx = int(getattr(profile, 'gallery_x', -1))
                    gy = int(getattr(profile, 'gallery_y', -1))
                    gw = int(getattr(profile, 'gallery_width', -1))
                    gh = int(getattr(profile, 'gallery_height', -1))
                    # Apply only if values are valid and within current screen
                    if gw > 100 and gh > 100 and gx >= 0 and gy >= 0:
                        try:
                            scr = self.screen().availableGeometry() if hasattr(self, 'screen') and self.screen() else None
                        except Exception:
                            scr = None
                        if not scr or (gx < scr.right() and gy < scr.bottom()):
                            # Basic sanity: apply geometry
                            self.setGeometry(gx, gy, gw, gh)
            except Exception:
                pass
        except Exception:
            pass
        super().showEvent(event)

    def changeEvent(self, event):
        try:
            if event.type() in (QEvent.PaletteChange, QEvent.StyleChange):
                self._sync_theme_from_parent()
                # Immediately reapply theme on any change
                QTimer.singleShot(10, lambda: self._force_complete_theme_application(self.theme))
        except Exception:
            pass
        super().changeEvent(event)

    def _sync_theme_from_parent(self):
        """Ensure gallery reflects parent's current theme (fixes stale dark UI in light mode)."""
        parent_theme = getattr(self.parent(), 'theme', getattr(self, 'theme', 'dark')) if self.parent() else getattr(self, 'theme', 'dark')
        parent_theme = (parent_theme or 'dark').lower()
        if getattr(self, 'theme', 'dark').lower() != parent_theme:
            self.theme = parent_theme
        # Re-apply gallery theming consistently
        self.apply_gallery_theme(self.theme)
        self._force_scroll_area_background(self.theme)
        self._update_info_label_style()
        self._apply_sort_styles(self.theme)
        self._apply_gallery_title_bar(self.theme)
        self._force_complete_theme_application(self.theme)

    def _force_complete_theme_application(self, theme: str):
        """Force theme to every single widget in the gallery to eliminate dark areas"""
        from PyQt5.QtGui import QPalette, QColor
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QWidget
        
        is_light = (theme or 'dark').lower() == 'light'
        
        if is_light:
            bg_color = QColor(245, 245, 247)  # #F5F5F7
            text_color = QColor(34, 34, 34)   # #222222
            window_color = QColor(255, 255, 255)  # #FFFFFF
        else:
            bg_color = QColor(51, 51, 51)     # #333333
            text_color = QColor(238, 238, 238) # #EEEEEE
            window_color = QColor(43, 43, 43)  # #2b2b2b
        
        # Force palette on main dialog
        main_palette = self.palette()
        main_palette.setColor(QPalette.Window, bg_color)
        main_palette.setColor(QPalette.WindowText, text_color)
        main_palette.setColor(QPalette.Base, window_color)
        main_palette.setColor(QPalette.AlternateBase, bg_color)
        main_palette.setColor(QPalette.Text, text_color)
        main_palette.setColor(QPalette.Button, bg_color)
        main_palette.setColor(QPalette.ButtonText, text_color)
        self.setPalette(main_palette)
        self.setAutoFillBackground(True)
        
        # Apply to all child widgets recursively
        def apply_to_widget(widget):
            try:
                # Skip buttons as they have their own styling
                if not widget.objectName().endswith('Button'):
                    palette = widget.palette()
                    palette.setColor(QPalette.Window, bg_color)
                    palette.setColor(QPalette.WindowText, text_color)
                    palette.setColor(QPalette.Base, window_color)
                    palette.setColor(QPalette.Text, text_color)
                    widget.setPalette(palette)
                    widget.setAutoFillBackground(True)
                
                # Recursively apply to children
                for child in widget.findChildren(QWidget):
                    apply_to_widget(child)
            except Exception:
                pass
        
        apply_to_widget(self)
        
        # Force specific styles on header and footer again with stronger selectors
        if is_light:
            global_style = f"""
                /* Main dialog and all child widgets - force light theme */
                QDialog#screenshotGalleryDialog, QDialog#screenshotGalleryDialog > QWidget {{
                    background-color: {bg_color.name()} !important;
                    color: {text_color.name()} !important;
                }}
                QDialog#screenshotGalleryDialog QWidget#galleryHeader, QDialog#screenshotGalleryDialog QWidget#galleryHeader * {{
                    background-color: #F5F5F7 !important;
                    color: #222222 !important;
                }}
                QDialog#screenshotGalleryDialog QWidget#galleryFooter, QDialog#screenshotGalleryDialog QWidget#galleryFooter * {{
                    background-color: #F5F5F7 !important;
                    color: #222222 !important;
                }}
                /* ScrollArea and all related components - force white */
                QDialog#screenshotGalleryDialog QScrollArea, QDialog#screenshotGalleryDialog QScrollArea QWidget {{
                    background-color: {window_color.name()} !important;
                }}
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar {{
                    background-color: #F0F0F0 !important;
                }}
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::handle {{
                    background-color: #CCC !important;
                }}
                /* Button containers and margins */
                QDialog#screenshotGalleryDialog QHBoxLayout, QDialog#screenshotGalleryDialog QVBoxLayout {{
                    background-color: transparent !important;
                }}
                /* Force dialog frame background */
                QDialog#screenshotGalleryDialog {{
                    background-color: #F5F5F7 !important;
                    border: 1px solid #E0E0E0 !important;
                }}
            """
        else:
            global_style = f"""
                /* Main dialog and all child widgets - force dark theme */
                QDialog#screenshotGalleryDialog, QDialog#screenshotGalleryDialog > QWidget {{
                    background-color: {bg_color.name()} !important;
                    color: {text_color.name()} !important;
                }}
                QDialog#screenshotGalleryDialog QWidget#galleryHeader, QDialog#screenshotGalleryDialog QWidget#galleryHeader * {{
                    background-color: #333333 !important;
                    color: #EEEEEE !important;
                }}
                QDialog#screenshotGalleryDialog QWidget#galleryFooter, QDialog#screenshotGalleryDialog QWidget#galleryFooter * {{
                    background-color: #333333 !important;
                    color: #EEEEEE !important;
                }}
                /* ScrollArea and all related components - force dark */
                QDialog#screenshotGalleryDialog QScrollArea, QDialog#screenshotGalleryDialog QScrollArea QWidget {{
                    background-color: {window_color.name()} !important;
                }}
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar {{
                    background-color: #444 !important;
                }}
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::handle {{
                    background-color: #666 !important;
                }}
                /* Button containers and margins */
                QDialog#screenshotGalleryDialog QHBoxLayout, QDialog#screenshotGalleryDialog QVBoxLayout {{
                    background-color: transparent !important;
                }}
                /* Force dialog frame background */
                QDialog#screenshotGalleryDialog {{
                    background-color: #333333 !important;
                    border: 1px solid #444444 !important;
                }}
            """
        
        # Apply global style to override any lingering dark areas
        self.setStyleSheet(self.styleSheet() + global_style)
        
        # Force update
        self.update()
        self.repaint()

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
                QDialog#screenshotGalleryDialog {{ 
                    background-color: {dialog_bg} !important; 
                    border: 1px solid #E0E0E0 !important;
                }}
                QDialog#screenshotGalleryDialog QScrollArea {{
                    background-color: #FFF !important;
                    border: 1px solid #CCC !important;
                }}
                QDialog#screenshotGalleryDialog QAbstractScrollArea::viewport {{
                    background-color: #FFF !important;
                }}
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar:vertical {{
                    background-color: #F0F0F0 !important;
                    width: 12px;
                }}
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::handle:vertical {{
                    background-color: #CCC !important;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QDialog#screenshotGalleryDialog {{ 
                    background-color: {dialog_bg} !important; 
                    border: 1px solid #444444 !important;
                }}
                QDialog#screenshotGalleryDialog QScrollArea {{
                    background-color: #2b2b2b !important;
                    border: 1px solid #555 !important;
                }}
                QDialog#screenshotGalleryDialog QAbstractScrollArea::viewport {{
                    background-color: #2b2b2b !important;
                }}
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar:vertical {{
                    background-color: #444 !important;
                    width: 12px;
                }}
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::handle:vertical {{
                    background-color: #666 !important;
                }}
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar:horizontal {{
                    background-color: #444 !important;
                    height: 12px;
                }}
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::handle:horizontal {{
                    background-color: #666 !important;
                }}
            """)
        
        # Set scroll area initial colors immediately
        if hasattr(self, 'scroll_area') and hasattr(self, 'scroll_widget'):
            # Method 1: Direct stylesheet
            if (self.theme or 'dark').lower() == 'light':
                self.scroll_area.setStyleSheet("QScrollArea { background-color: #FFF; border: 1px solid #CCC; }")
                self.scroll_widget.setStyleSheet("QWidget { background-color: #FFF; }")
                try:
                    self.scroll_area.viewport().setStyleSheet("QWidget { background-color: #FFF; }")
                except Exception:
                    pass
            else:
                self.scroll_area.setStyleSheet("QScrollArea { background-color: #2b2b2b; border: 1px solid #555; }")
                self.scroll_widget.setStyleSheet("QWidget { background-color: #2b2b2b; }")
                try:
                    self.scroll_area.viewport().setStyleSheet("QWidget { background-color: #2b2b2b; }")
                except Exception:
                    pass
            
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

            # Also set viewport palette
            try:
                vp = self.scroll_area.viewport()
                vp_palette = vp.palette()
                vp_palette.setColor(QPalette.Window, bg_color)
                vp_palette.setColor(QPalette.Base, bg_color)
                vp.setPalette(vp_palette)
                vp.setAutoFillBackground(True)
            except Exception:
                pass
            
            # Force immediate repaint
            self.scroll_area.update()
            self.scroll_widget.update()
    
    def _apply_button_styles(self):
        """Apply direct styles to buttons to ensure they work and eliminate dark background areas"""
        # Get current theme
        is_light = (self.theme or 'dark').lower() == 'light'
        theme = (self.theme or 'dark')
        # Resolve color blindness type from parent (prefer live combobox state, fallback to profile)
        cb_type = 'none'
        try:
            parent = self.parent()
            if parent is not None:
                # Prefer most recent combobox value if available
                if hasattr(parent, 'color_blindness_combo') and parent.color_blindness_combo is not None:
                    current = parent.color_blindness_combo.currentData()
                    if current and current != 'category':
                        cb_type = current
                # Fallback to persisted profile value
                if cb_type == 'none' and hasattr(parent, 'current_profile') and parent.current_profile is not None:
                    cb_type = getattr(parent.current_profile, 'color_blindness_type', 'none') or 'none'
        except Exception:
            cb_type = 'none'
        # Get accessible color map for disabled states
        color_map = get_colorblind_friendly_colors(cb_type)
        # Base colors for logical classes
        base_stop = color_map.get('red', '#f44336')   # delete
        base_start = color_map.get('green', '#4CAF50')  # save
        disabled_stop = adjust_color_brightness(base_stop.lstrip('#'), 1.6) if base_stop.startswith('#') else base_stop
        disabled_start = adjust_color_brightness(base_start.lstrip('#'), 1.6) if base_start.startswith('#') else base_start
        # adjust_color_brightness expects hex without '#', wrap outputs
        if not disabled_stop.startswith('#'):
            disabled_stop = f"#{disabled_stop}"
        if not disabled_start.startswith('#'):
            disabled_start = f"#{disabled_start}"
        
        # Refresh button - use unified theming (blue style) and compact metrics
        update_button_theme(self.refresh_button, 'snapshot', theme, cb_type)
        try:
            self.refresh_button.setStyleSheet(self.refresh_button.styleSheet() + """
                QPushButton { padding: 6px 8px; min-height: 22px; border-radius: 4px; font-size: 8.5pt; }
            """)
        except Exception:
            pass
        
        # Delete button - use unified theming when enabled; keep disabled style
        if self.delete_button.isEnabled():
            update_button_theme(self.delete_button, 'stop', theme, cb_type)
            try:
                self.delete_button.setStyleSheet(self.delete_button.styleSheet() + """
                    QPushButton { padding: 6px 8px; min-height: 22px; border-radius: 4px; font-size: 8.5pt; }
                """)
            except Exception:
                pass
        else:
            self.delete_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {disabled_stop};
                    color: #999;
                    padding: 6px 8px;
                    border-radius: 4px;
                    font-size: 8.5pt;
                    min-height: 22px;
                    text-align: center;
                }}
            """)
        
        # Save button - use unified theming when enabled; keep disabled style
        if self.export_button.isEnabled():
            update_button_theme(self.export_button, 'start', theme, cb_type)
            try:
                self.export_button.setStyleSheet(self.export_button.styleSheet() + """
                    QPushButton { padding: 6px 8px; min-height: 22px; border-radius: 4px; font-size: 8.5pt; }
                """)
            except Exception:
                pass
        else:
            self.export_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {disabled_start};
                    color: #999;
                    padding: 6px 8px;
                    border-radius: 4px;
                    font-size: 8.5pt;
                    min-height: 22px;
                    text-align: center;
                }}
            """)
        
        # Force button container (footer) background
        if hasattr(self, 'footer_widget'):
            from PyQt5.QtGui import QPalette, QColor
            from PyQt5.QtWidgets import QWidget
            
            if is_light:
                bg_color = QColor(245, 245, 247)  # #F5F5F7
                text_color = QColor(34, 34, 34)   # #222222
            else:
                bg_color = QColor(51, 51, 51)     # #333333
                text_color = QColor(238, 238, 238) # #EEEEEE
            
            # Apply background to footer widget and all its children
            footer_palette = self.footer_widget.palette()
            footer_palette.setColor(QPalette.Window, bg_color)
            footer_palette.setColor(QPalette.Base, bg_color)
            footer_palette.setColor(QPalette.WindowText, text_color)
            self.footer_widget.setPalette(footer_palette)
            self.footer_widget.setAutoFillBackground(True)
            
            # Apply to all child widgets to eliminate dark areas
            for child in self.footer_widget.findChildren(QWidget):
                if not child.objectName().endswith('Button'):
                    child_palette = child.palette()
                    child_palette.setColor(QPalette.Window, bg_color)
                    child_palette.setColor(QPalette.Base, bg_color)
                    child_palette.setColor(QPalette.WindowText, text_color)
                    child.setPalette(child_palette)
                    child.setAutoFillBackground(True)
        
        # Force scroll area theme using QPalette
        if hasattr(self, 'scroll_area'):
            try:
                from PyQt5.QtGui import QPalette, QColor
                palette = self.scroll_area.palette()
                
                if is_light:
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
            # Get current theme
            is_light = (self.theme or 'dark').lower() == 'light'
            
            # Complete style and palette reset - clear all inherited styles
            self.info_label.setStyleSheet("")
            
            # Force palette update first
            from PyQt5.QtGui import QPalette, QColor
            label_palette = self.info_label.palette()
            if is_light:
                text_color = QColor(34, 34, 34)  # #222222
                bg_color = QColor(245, 245, 247)  # #F5F5F7
            else:
                text_color = QColor(255, 255, 255)  # #FFFFFF
                bg_color = QColor(51, 51, 51)  # #333333
                
            label_palette.setColor(QPalette.WindowText, text_color)
            label_palette.setColor(QPalette.Text, text_color)
            label_palette.setColor(QPalette.Window, bg_color)
            label_palette.setColor(QPalette.Base, bg_color)
            self.info_label.setPalette(label_palette)
            self.info_label.setAutoFillBackground(True)
            
            # Reset font to default
            self.info_label.setFont(self.info_label.font())
            
            # Dynamic font size based on fullscreen mode - compact for mobile-like
            font_size = "13px" if self.is_fullscreen else "12px"
            padding = "6px" if self.is_fullscreen else "5px"
            
            if is_light:
                style = f"""
                QLabel {{
                    color: #222222 !important;
                    font-weight: normal;
                    font-size: {font_size};
                    padding: {padding};
                    border: none;
                    background: transparent;
                }}
                """
            else:
                style = f"""
                QLabel {{
                    color: #FFFFFF !important;
                    font-weight: normal;
                    font-size: {font_size};
                    padding: {padding};
                    border: none;
                    background: transparent;
                }}
                """
            
            self.info_label.setStyleSheet(style)
            
            # Force complete widget refresh
            try:
                self.info_label.style().unpolish(self.info_label)
                self.info_label.style().polish(self.info_label)
            except Exception:
                pass
                
            # Force immediate update
            self.info_label.update()
            self.info_label.repaint()
    
    def _update_info_label_style_with_theme(self, theme):
        """Update info label style with specific theme - for widget recreation"""
        if hasattr(self, 'info_label'):
            # Get theme parameter directly
            is_light = (theme or 'dark').lower() == 'light'
            
            # Complete style and palette reset - clear all inherited styles
            self.info_label.setStyleSheet("")
            
            # Force palette update first
            from PyQt5.QtGui import QPalette, QColor
            label_palette = self.info_label.palette()
            if is_light:
                text_color = QColor(34, 34, 34)  # #222222
                bg_color = QColor(245, 245, 247)  # #F5F5F7
            else:
                text_color = QColor(255, 255, 255)  # #FFFFFF
                bg_color = QColor(51, 51, 51)  # #333333
                
            label_palette.setColor(QPalette.WindowText, text_color)
            label_palette.setColor(QPalette.Text, text_color)
            label_palette.setColor(QPalette.Window, bg_color)
            label_palette.setColor(QPalette.Base, bg_color)
            self.info_label.setPalette(label_palette)
            self.info_label.setAutoFillBackground(True)
            
            # Reset font to default
            self.info_label.setFont(self.info_label.font())
            
            # Dynamic font size based on fullscreen mode - compact for mobile-like
            font_size = "13px" if self.is_fullscreen else "12px"
            padding = "6px" if self.is_fullscreen else "5px"
            
            if is_light:
                style = f"""
                QLabel {{
                    color: #222222 !important;
                    font-weight: normal;
                    font-size: {font_size};
                    padding: {padding};
                    border: none;
                    background: transparent;
                }}
                """
            else:
                style = f"""
                QLabel {{
                    color: #FFFFFF !important;
                    font-weight: normal;
                    font-size: {font_size};
                    padding: {padding};
                    border: none;
                    background: transparent;
                }}
                """
            
            self.info_label.setStyleSheet(style)
            
            # Force complete widget refresh
            try:
                self.info_label.style().unpolish(self.info_label)
                self.info_label.style().polish(self.info_label)
            except Exception:
                pass
                
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
    
    def _force_complete_theme_application(self, theme):
        """Force complete theme application to all components."""
        # Force main dialog palette
        palette = self.palette()
        if theme == 'light':
            palette.setColor(QPalette.Window, QColor('#FFFFFF'))
            palette.setColor(QPalette.WindowText, QColor('#000000'))
            palette.setColor(QPalette.Base, QColor('#FFFFFF'))
            palette.setColor(QPalette.AlternateBase, QColor('#F0F0F0'))
            palette.setColor(QPalette.Text, QColor('#000000'))
            palette.setColor(QPalette.Button, QColor('#F0F0F0'))
            palette.setColor(QPalette.ButtonText, QColor('#000000'))
        else:
            palette.setColor(QPalette.Window, QColor('#2B2B2B'))
            palette.setColor(QPalette.WindowText, QColor('#FFFFFF'))
            palette.setColor(QPalette.Base, QColor('#1E1E1E'))
            palette.setColor(QPalette.AlternateBase, QColor('#404040'))
            palette.setColor(QPalette.Text, QColor('#FFFFFF'))
            palette.setColor(QPalette.Button, QColor('#404040'))
            palette.setColor(QPalette.ButtonText, QColor('#FFFFFF'))
        
        self.setPalette(palette)
        
        # Force update all child widgets
        for child in self.findChildren(QWidget):
            child.setPalette(palette)
            if hasattr(child, 'setAutoFillBackground'):
                child.setAutoFillBackground(True)
        
        # Force dropdown theme update with complete reset
        try:
            if hasattr(self, 'sort_combo'):
                # Extreme approach: recreate the combo box
                self._recreate_sort_combo(theme)
        except Exception as e:
            print(f"Error updating dropdown in force theme: {e}")
        
        # Force info label theme update with complete reset
        try:
            if hasattr(self, 'info_label'):
                # Extreme approach: recreate the info label with direct theme
                self._recreate_info_label(theme)
        except Exception as e:
            print(f"Error updating info label in force theme: {e}")
        
            # Force complete widget hierarchy update
        try:
            # Update self
            self.update()
            self.repaint()
            
            # Force style re-polish for all widgets
            for child in self.findChildren(QWidget):
                child.setPalette(palette)
                if hasattr(child, 'setAutoFillBackground'):
                    child.setAutoFillBackground(True)
                # Force style system refresh
                try:
                    child.style().unpolish(child)
                    child.style().polish(child)
                    child.update()
                    child.repaint()
                except Exception:
                    pass
        except Exception:
            pass
    
    def _recreate_sort_combo(self, theme):
        """Recreate sort combo box with proper theme"""
        if not hasattr(self, 'sort_combo') or not hasattr(self, 'header_widget'):
            return
            
        # Get current selection before recreating
        current_data = self.sort_combo.currentData() if self.sort_combo.currentIndex() >= 0 else "name_asc"
        
        # Get layout
        layout = self.header_widget.layout()
        if not layout:
            return
            
        # Remove old combo
        layout.removeWidget(self.sort_combo)
        self.sort_combo.deleteLater()
        
        # Create new combo
        self.sort_combo = HiddenCurrentCombo()
        self.sort_combo.setObjectName("sortCombo")
        self.sort_combo.addItem(tr.get_text("sort_by_name_asc"), "name_asc")
        self.sort_combo.addItem(tr.get_text("sort_by_name_desc"), "name_desc")
        self.sort_combo.addItem(tr.get_text("sort_by_date_asc"), "date_asc")
        self.sort_combo.addItem(tr.get_text("sort_by_date_desc"), "date_desc")
        self.sort_combo.currentTextChanged.connect(self.sort_screenshots)
        
        # Apply theme to new combo - use direct theme application
        if theme == 'light':
            self._apply_light_combo_theme(self.sort_combo)
        else:
            self._apply_dark_combo_theme(self.sort_combo)
        
        # Restore selection
        for i in range(self.sort_combo.count()):
            if self.sort_combo.itemData(i) == current_data:
                self.sort_combo.setCurrentIndex(i)
                break
        
        # Add back to layout
        layout.addWidget(self.sort_combo)
    
    def _recreate_info_label(self, theme):
        """Recreate info label with proper theme"""
        if not hasattr(self, 'info_label') or not hasattr(self, 'header_widget'):
            return
            
        # Get current text before recreating
        current_text = self.info_label.text()
        
        # Get layout
        layout = self.header_widget.layout()
        if not layout:
            return
            
        # Remove old label
        layout.removeWidget(self.info_label)
        self.info_label.deleteLater()
        
        # Create new label
        self.info_label = QLabel(current_text)
        self.info_label.setObjectName("infoLabel")
        
        # Apply theme to new label - pass theme directly
        self._update_info_label_style_with_theme(theme)
        
        # Add back to layout (at the beginning)
        layout.insertWidget(0, self.info_label)
    
    def _apply_light_combo_theme(self, combo_box):
        """Apply light theme directly to combo box"""
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        dark_icon_path = os.path.join(base_path, 'icons', 'dropdown_arrow_dark.svg').replace('\\', '/')
        
        combo_box.setStyleSheet(f"""
            QComboBox {{
                padding: 5px 28px 5px 8px;
                font-size: 10pt;
                border-radius: 4px;
                border: 1px solid #CCCCCC;
                background-color: white;
                color: #333;
            }}
            QComboBox:hover {{
                border: 1px solid #2196F3;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-style: solid;
                border-left-width: 1px;
                border-left-color: #CCCCCC;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-color: transparent;
            }}
            QComboBox::down-arrow {{
                image: url({dark_icon_path});
                width: 10px;
                height: 6px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #FFFFFF;
                color: #222;
                selection-background-color: #E9ECEF;
                border: 1px solid #DDD;
                outline: none;
            }}
        """)
        
        # Also style the view directly
        try:
            view = combo_box.view()
            if view:
                view.setStyleSheet("""
                    QListView {
                        background-color: #FFFFFF;
                        color: #222;
                        selection-background-color: #E9ECEF;
                        border: 1px solid #DDD;
                        outline: none;
                    }
                    QListView::item:selected {
                        color: #111;
                        background-color: #E9ECEF;
                    }
                """)
        except Exception:
            pass
    
    def _apply_dark_combo_theme(self, combo_box):
        """Apply dark theme directly to combo box"""
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        light_icon_path = os.path.join(base_path, 'icons', 'dropdown_arrow_light.svg').replace('\\', '/')
        
        combo_box.setStyleSheet(f"""
            QComboBox {{
                padding: 5px 28px 5px 8px;
                font-size: 10pt;
                border-radius: 4px;
                border: 1px solid #555;
                background-color: #444;
                color: #EEE;
            }}
            QComboBox:hover {{
                border: 1px solid #666;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-style: solid;
                border-left-width: 1px;
                border-left-color: #555;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-color: transparent;
            }}
            QComboBox::down-arrow {{
                image: url({light_icon_path});
                width: 10px;
                height: 6px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #444;
                color: #EEE;
                selection-background-color: #555;
                border: 1px solid #666;
                outline: none;
            }}
        """)
        
        # Also style the view directly
        try:
            view = combo_box.view()
            if view:
                view.setStyleSheet("""
                    QListView {
                        background-color: #444;
                        color: #EEE;
                        selection-background-color: #555;
                        border: 1px solid #666;
                        outline: none;
                    }
                    QListView::item:selected {
                        color: #FFF;
                        background-color: #555;
                    }
                """)
        except Exception:
            pass
    
    def apply_gallery_theme(self, theme: str = 'dark'):
        """Apply theme for gallery window"""
        # Clear previous stylesheet to avoid rule accumulation from parent/main window
        try:
            self.setStyleSheet("")
        except Exception:
            pass
        
        # Force dialog palette immediately
        from PyQt5.QtGui import QPalette, QColor
        dialog_palette = self.palette()
        if (theme or 'dark').lower() == 'light':
            dialog_palette.setColor(QPalette.Window, QColor(245, 245, 247))
            dialog_palette.setColor(QPalette.Base, QColor(255, 255, 255))
            dialog_palette.setColor(QPalette.WindowText, QColor(34, 34, 34))
            dialog_palette.setColor(QPalette.Text, QColor(34, 34, 34))
        else:
            dialog_palette.setColor(QPalette.Window, QColor(51, 51, 51))
            dialog_palette.setColor(QPalette.Base, QColor(43, 43, 43))
            dialog_palette.setColor(QPalette.WindowText, QColor(238, 238, 238))
            dialog_palette.setColor(QPalette.Text, QColor(238, 238, 238))
        
        self.setPalette(dialog_palette)
        self.setAutoFillBackground(True)
        
        if (theme or 'dark').lower() == 'light':
            self.setStyleSheet("""
                /* Main dialog styling - force light theme */
                QDialog#screenshotGalleryDialog {
                    background-color: #F5F5F7 !important;
                    color: #222222 !important;
                }
                
                /* All labels in dialog */
                QDialog#screenshotGalleryDialog QLabel {
                    color: #222222 !important;
                    background-color: transparent !important;
                }
                
                /* Header and Footer containers - force light background with stronger selectors */
                QDialog#screenshotGalleryDialog QWidget#galleryHeader {
                    background-color: #F5F5F7 !important;
                    border-bottom: 1px solid #E0E0E0 !important;
                    padding: 6px 8px;
                }
                QDialog#screenshotGalleryDialog QWidget#galleryFooter {
                    background-color: #F5F5F7 !important;
                    border-top: 1px solid #E0E0E0 !important;
                    padding: 6px 8px;
                }
                
                /* Scroll area and viewport - force white */
                QDialog#screenshotGalleryDialog QScrollArea {
                    background-color: #FFFFFF !important;
                    border: 1px solid #CCCCCC !important;
                }
                QDialog#screenshotGalleryDialog QAbstractScrollArea::viewport {
                    background-color: #FFFFFF !important;
                }
                /* Refresh Button - Blue theme with proper spacing and container background */
                QDialog#screenshotGalleryDialog QPushButton#refreshButton {
                    background-color: #007AFF !important;
                    color: white !important;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                    margin: 2px;
                }
                QDialog#screenshotGalleryDialog QPushButton#refreshButton:hover {
                    background-color: #0056CC !important;
                }
                
                /* Delete Button - Red theme with proper spacing and container background */
                QDialog#screenshotGalleryDialog QPushButton#deleteButton {
                    background-color: #FF3B30 !important;
                    color: white !important;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                    margin: 2px;
                }
                QDialog#screenshotGalleryDialog QPushButton#deleteButton:hover {
                    background-color: #D70015 !important;
                }
                QDialog#screenshotGalleryDialog QPushButton#deleteButton:disabled {
                    background-color: #FFB3B3 !important;
                    color: #999 !important;
                }
                
                /* Save Button - Green theme with proper spacing and container background */
                QDialog#screenshotGalleryDialog QPushButton#saveButton {
                    background-color: #34C759 !important;
                    color: white !important;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                    margin: 2px;
                }
                QDialog#screenshotGalleryDialog QPushButton#saveButton:hover {
                    background-color: #248A3D !important;
                }
                QDialog#screenshotGalleryDialog QPushButton#saveButton:disabled {
                    background-color: #B3E6C7 !important;
                    color: #999 !important;
                }
                
                /* Sort ComboBox and Label - use main app styles */
                QDialog#screenshotGalleryDialog QLabel#sortLabel {
                    color: #222 !important;
                    font-weight: bold !important;
                    padding: 0 5px !important;
                    font-size: 10pt !important;
                }
                
                /* ComboBox style is applied via shared _apply_combo_theme to ensure consistency */
                
                /* Force all scroll area components to light theme */
                QDialog#screenshotGalleryDialog QScrollArea {
                    border: 1px solid #CCC !important;
                    background-color: #FFF !important;
                }
                QDialog#screenshotGalleryDialog QScrollArea#galleryScrollArea {
                    background-color: #FFF !important;
                }
                QDialog#screenshotGalleryDialog QScrollArea#galleryScrollArea > QWidget {
                    background-color: #FFF !important;
                }
                QDialog#screenshotGalleryDialog QScrollArea#galleryScrollArea QWidget {
                    background-color: #FFF !important;
                }
                QDialog#screenshotGalleryDialog QScrollArea::corner {
                    background-color: #FFF !important;
                }
                QDialog#screenshotGalleryDialog QWidget#galleryScrollWidget {
                    background-color: #FFF !important;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar:vertical {
                    background-color: #F0F0F0 !important;
                    width: 12px;
                    border-radius: 6px;
                    border: 1px solid #DDD;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::handle:vertical {
                    background-color: #CCC !important;
                    border-radius: 5px;
                    border: 1px solid #BBB;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::handle:vertical:hover {
                    background-color: #AAA !important;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::add-line:vertical,
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::sub-line:vertical {
                    background: #F0F0F0 !important;
                    border: none;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::add-page:vertical,
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::sub-page:vertical {
                    background: #F8F8F8 !important;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar:horizontal {
                    background-color: #F0F0F0 !important;
                    height: 12px;
                    border-radius: 6px;
                    border: 1px solid #DDD;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::handle:horizontal {
                    background-color: #CCC !important;
                    border-radius: 5px;
                    border: 1px solid #BBB;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::handle:horizontal:hover {
                    background-color: #AAA !important;
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
                QDialog#screenshotGalleryDialog > QWidget {
                    background-color: #F5F5F7;
                }
                /* Override for scroll widget specifically */
                QDialog#screenshotGalleryDialog QScrollArea QWidget {
                    background-color: #FFF !important;
                }
            """)
        else:
            self.setStyleSheet("""
                /* Main dialog styling - force dark theme */
                QDialog#screenshotGalleryDialog {
                    background-color: #333333 !important;
                    color: #EEEEEE !important;
                }
                
                /* All labels in dialog */
                QDialog#screenshotGalleryDialog QLabel {
                    color: #EEEEEE !important;
                    background-color: transparent !important;
                }
                
                /* Header and Footer containers - force dark background with stronger selectors */
                QDialog#screenshotGalleryDialog QWidget#galleryHeader {
                    background-color: #333333 !important;
                    border-bottom: 1px solid #444444 !important;
                    padding: 6px 8px;
                }
                QDialog#screenshotGalleryDialog QWidget#galleryFooter {
                    background-color: #333333 !important;
                    border-top: 1px solid #444444 !important;
                    padding: 6px 8px;
                }
                
                /* Scroll area and viewport - force dark */
                QDialog#screenshotGalleryDialog QScrollArea {
                    background-color: #2b2b2b !important;
                    border: 1px solid #555555 !important;
                }
                QDialog#screenshotGalleryDialog QAbstractScrollArea::viewport {
                    background-color: #2b2b2b !important;
                }
                QDialog#screenshotGalleryDialog QPushButton#refreshButton {
                    background-color: #0A84FF !important;
                    color: white !important;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                    margin: 2px;
                }
                QDialog#screenshotGalleryDialog QPushButton#refreshButton:hover {
                    background-color: #409CFF !important;
                }
                
                /* Delete Button - Red theme with proper spacing */
                QDialog#screenshotGalleryDialog QPushButton#deleteButton {
                    background-color: #FF453A !important;
                    color: white !important;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                    margin: 2px;
                }
                QDialog#screenshotGalleryDialog QPushButton#deleteButton:hover {
                    background-color: #FF6961 !important;
                }
                QDialog#screenshotGalleryDialog QPushButton#deleteButton:disabled {
                    background-color: #5C2B2B !important;
                    color: #888 !important;
                }
                
                /* Save Button - Green theme with proper spacing */
                QDialog#screenshotGalleryDialog QPushButton#saveButton {
                    background-color: #32D74B !important;
                    color: white !important;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    font-weight: bold;
                    margin: 2px;
                }
                QDialog#screenshotGalleryDialog QPushButton#saveButton:hover {
                    background-color: #64E478 !important;
                }
                QDialog#screenshotGalleryDialog QPushButton#saveButton:disabled {
                    background-color: #2B4A2F !important;
                    color: #888 !important;
                }
                
                /* Sort ComboBox and Label - use main app styles */
                QDialog#screenshotGalleryDialog QLabel#sortLabel {
                    color: white !important;
                    font-weight: bold !important;
                    padding: 0 5px !important;
                    font-size: 10pt !important;
                }
                
                /* ComboBox style is applied via shared _apply_combo_theme to ensure consistency */
                
                /* Force all scroll area components to dark theme */
                QDialog#screenshotGalleryDialog QScrollArea {
                    border: 1px solid #555 !important;
                    background-color: #2b2b2b !important;
                }
                QDialog#screenshotGalleryDialog QScrollArea#galleryScrollArea {
                    background-color: #2b2b2b !important;
                }
                QDialog#screenshotGalleryDialog QScrollArea#galleryScrollArea > QWidget {
                    background-color: #2b2b2b !important;
                }
                QDialog#screenshotGalleryDialog QScrollArea#galleryScrollArea QWidget {
                    background-color: #2b2b2b !important;
                }
                QDialog#screenshotGalleryDialog QScrollArea::corner {
                    background-color: #2b2b2b !important;
                }
                QDialog#screenshotGalleryDialog QWidget#galleryScrollWidget {
                    background-color: #2b2b2b !important;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar:vertical {
                    background-color: #444 !important;
                    width: 12px;
                    border-radius: 6px;
                    border: 1px solid #555;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::handle:vertical {
                    background-color: #666 !important;
                    border-radius: 5px;
                    border: 1px solid #555;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::handle:vertical:hover {
                    background-color: #888 !important;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::add-line:vertical,
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::sub-line:vertical {
                    background: #444 !important;
                    border: none;
                    height: 0px;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::add-page:vertical,
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::sub-page:vertical {
                    background: #444 !important;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar:horizontal {
                    background-color: #444 !important;
                    height: 12px;
                    border-radius: 6px;
                    border: 1px solid #555;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::handle:horizontal {
                    background-color: #666 !important;
                    border-radius: 5px;
                    border: 1px solid #555;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::handle:horizontal:hover {
                    background-color: #888 !important;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::add-line:horizontal,
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::sub-line:horizontal {
                    background: #444 !important;
                    border: none;
                    width: 0px;
                }
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::add-page:vertical,
                QDialog#screenshotGalleryDialog QScrollArea QScrollBar::sub-page:vertical {
                    background: none;
                }
                
                /* Specific styling for gallery content to ensure dark background */
                QDialog#screenshotGalleryDialog QGridLayout {
                    background-color: #2b2b2b;
                }
                QDialog#screenshotGalleryDialog QFrame {
                    background-color: #2b2b2b;
                }
                QDialog#screenshotGalleryDialog QLabel[objectName="thumbnail"] {
                    background-color: #2b2b2b;
                }
                
                /* Dialog level widgets - keep dark theme */
                QDialog#screenshotGalleryDialog > QWidget {
                    background-color: #333;
                }
                /* Override for scroll widget specifically */
                QDialog#screenshotGalleryDialog QScrollArea QWidget {
                    background-color: #2b2b2b !important;
                }
            """)
        
        # Also force header/footer widget styles directly with palette and ensure all child widgets follow
        try:
            from PyQt5.QtGui import QPalette, QColor
            from PyQt5.QtCore import Qt
            from PyQt5.QtWidgets import QWidget
            
            if (theme or 'dark').lower() == 'light':
                # Light theme colors for header/footer
                light_color = QColor(245, 245, 247)  # #F5F5F7
                text_color = QColor(34, 34, 34)   # #222222
                
                # Force header background and all its children
                if hasattr(self, 'header_widget'):
                    # Apply to header widget itself
                    header_palette = self.header_widget.palette()
                    header_palette.setColor(QPalette.Window, light_color)
                    header_palette.setColor(QPalette.Base, light_color)
                    header_palette.setColor(QPalette.Button, light_color)
                    header_palette.setColor(QPalette.WindowText, text_color)
                    header_palette.setColor(QPalette.Text, text_color)
                    header_palette.setColor(QPalette.ButtonText, text_color)
                    self.header_widget.setPalette(header_palette)
                    self.header_widget.setAutoFillBackground(True)
                    # Force immediate stylesheet
                    self.header_widget.setStyleSheet("""
                        QWidget#galleryHeader {
                            background-color: #F5F5F7 !important;
                            color: #222222 !important;
                            border-bottom: 1px solid #E0E0E0 !important;
                            padding: 6px 8px;
                        }
                        QWidget#galleryHeader * {
                            background-color: #F5F5F7 !important;
                            color: #222222 !important;
                        }
                    """)
                    
                    # Apply to all child widgets recursively
                    for child in self.header_widget.findChildren(QWidget):
                        if not child.objectName().endswith('Button'):  # Skip buttons as they have their own styling
                            child_palette = child.palette()
                            child_palette.setColor(QPalette.Window, light_color)
                            child_palette.setColor(QPalette.Base, light_color)
                            child_palette.setColor(QPalette.WindowText, text_color)
                            child_palette.setColor(QPalette.Text, text_color)
                            child.setPalette(child_palette)
                            child.setAutoFillBackground(True)
                
                # Force footer background and all its children
                if hasattr(self, 'footer_widget'):
                    # Apply to footer widget itself
                    footer_palette = self.footer_widget.palette()
                    footer_palette.setColor(QPalette.Window, light_color)
                    footer_palette.setColor(QPalette.Base, light_color)
                    footer_palette.setColor(QPalette.Button, light_color)
                    footer_palette.setColor(QPalette.WindowText, text_color)
                    footer_palette.setColor(QPalette.Text, text_color)
                    footer_palette.setColor(QPalette.ButtonText, text_color)
                    self.footer_widget.setPalette(footer_palette)
                    self.footer_widget.setAutoFillBackground(True)
                    # Force immediate stylesheet
                    self.footer_widget.setStyleSheet("""
                        QWidget#galleryFooter {
                            background-color: #F5F5F7 !important;
                            color: #222222 !important;
                            border-top: 1px solid #E0E0E0 !important;
                            padding: 6px 8px;
                        }
                        QWidget#galleryFooter * {
                            background-color: #F5F5F7 !important;
                            color: #222222 !important;
                        }
                    """)
                    
                    # Apply to all child widgets recursively
                    for child in self.footer_widget.findChildren(QWidget):
                        if not child.objectName().endswith('Button'):  # Skip buttons as they have their own styling
                            child_palette = child.palette()
                            child_palette.setColor(QPalette.Window, light_color)
                            child_palette.setColor(QPalette.Base, light_color)
                            child_palette.setColor(QPalette.WindowText, text_color)
                            child_palette.setColor(QPalette.Text, text_color)
                            child.setPalette(child_palette)
                            child.setAutoFillBackground(True)
            else:
                # Dark theme colors for header/footer
                dark_color = QColor(51, 51, 51)  # #333333
                text_color = QColor(238, 238, 238) # #EEEEEE
                
                # Force header background and all its children
                if hasattr(self, 'header_widget'):
                    # Apply to header widget itself
                    header_palette = self.header_widget.palette()
                    header_palette.setColor(QPalette.Window, dark_color)
                    header_palette.setColor(QPalette.Base, dark_color)
                    header_palette.setColor(QPalette.Button, dark_color)
                    header_palette.setColor(QPalette.WindowText, text_color)
                    header_palette.setColor(QPalette.Text, text_color)
                    header_palette.setColor(QPalette.ButtonText, text_color)
                    self.header_widget.setPalette(header_palette)
                    self.header_widget.setAutoFillBackground(True)
                    # Force immediate stylesheet
                    self.header_widget.setStyleSheet("""
                        QWidget#galleryHeader {
                            background-color: #333333 !important;
                            color: #EEEEEE !important;
                            border-bottom: 1px solid #444444 !important;
                            padding: 6px 8px;
                        }
                        QWidget#galleryHeader * {
                            background-color: #333333 !important;
                            color: #EEEEEE !important;
                        }
                    """)
                    
                    # Apply to all child widgets recursively
                    for child in self.header_widget.findChildren(QWidget):
                        if not child.objectName().endswith('Button'):  # Skip buttons as they have their own styling
                            child_palette = child.palette()
                            child_palette.setColor(QPalette.Window, dark_color)
                            child_palette.setColor(QPalette.Base, dark_color)
                            child_palette.setColor(QPalette.WindowText, text_color)
                            child_palette.setColor(QPalette.Text, text_color)
                            child.setPalette(child_palette)
                            child.setAutoFillBackground(True)
                
                # Force footer background and all its children
                if hasattr(self, 'footer_widget'):
                    # Apply to footer widget itself
                    footer_palette = self.footer_widget.palette()
                    footer_palette.setColor(QPalette.Window, dark_color)
                    footer_palette.setColor(QPalette.Base, dark_color)
                    footer_palette.setColor(QPalette.Button, dark_color)
                    footer_palette.setColor(QPalette.WindowText, text_color)
                    footer_palette.setColor(QPalette.Text, text_color)
                    footer_palette.setColor(QPalette.ButtonText, text_color)
                    self.footer_widget.setPalette(footer_palette)
                    self.footer_widget.setAutoFillBackground(True)
                    # Force immediate stylesheet
                    self.footer_widget.setStyleSheet("""
                        QWidget#galleryFooter {
                            background-color: #333333 !important;
                            color: #EEEEEE !important;
                            border-top: 1px solid #444444 !important;
                            padding: 6px 8px;
                        }
                        QWidget#galleryFooter * {
                            background-color: #333333 !important;
                            color: #EEEEEE !important;
                        }
                    """)
                    
                    # Apply to all child widgets recursively
                    for child in self.footer_widget.findChildren(QWidget):
                        if not child.objectName().endswith('Button'):  # Skip buttons as they have their own styling
                            child_palette = child.palette()
                            child_palette.setColor(QPalette.Window, dark_color)
                            child_palette.setColor(QPalette.Base, dark_color)
                            child_palette.setColor(QPalette.WindowText, text_color)
                            child_palette.setColor(QPalette.Text, text_color)
                            child.setPalette(child_palette)
                            child.setAutoFillBackground(True)
        except Exception as e:
            print(f"Error applying header/footer palette: {e}")
        
        # Update info label with dedicated method to prevent font accumulation
        self._update_info_label_style()
        
        # Force apply styles programmatically to sort components (shared theme)
        self._apply_sort_styles(theme)
        
        # Ensure scroll area background/palette fully reflects the theme
        try:
            self._force_scroll_area_background(theme)
            self._force_scroll_area_update()
        except Exception:
            pass
        
        # Force repaint of header/footer to ensure colors stick
        try:
            if hasattr(self, 'header_widget'):
                self.header_widget.update()
                self.header_widget.repaint()
            if hasattr(self, 'footer_widget'):
                self.footer_widget.update()
                self.footer_widget.repaint()
        except Exception:
            pass
        
        # Apply button styles to ensure proper theming and eliminate dark backgrounds
        self._apply_button_styles()
        
        # Force scroll area palette
        if hasattr(self, 'scroll_area') and hasattr(self, 'scroll_widget'):
            try:
                from PyQt5.QtGui import QPalette, QColor
                if (theme or 'dark').lower() == 'light':
                    scroll_bg = QColor(255, 255, 255)
                else:
                    scroll_bg = QColor(43, 43, 43)
                
                # Apply to scroll area
                scroll_palette = self.scroll_area.palette()
                scroll_palette.setColor(QPalette.Window, scroll_bg)
                scroll_palette.setColor(QPalette.Base, scroll_bg)
                self.scroll_area.setPalette(scroll_palette)
                self.scroll_area.setAutoFillBackground(True)
                
                # Apply to scroll widget
                widget_palette = self.scroll_widget.palette()
                widget_palette.setColor(QPalette.Window, scroll_bg)
                widget_palette.setColor(QPalette.Base, scroll_bg)
                self.scroll_widget.setPalette(widget_palette)
                self.scroll_widget.setAutoFillBackground(True)
                
                # Apply to viewport
                try:
                    viewport = self.scroll_area.viewport()
                    vp_palette = viewport.palette()
                    vp_palette.setColor(QPalette.Window, scroll_bg)
                    vp_palette.setColor(QPalette.Base, scroll_bg)
                    viewport.setPalette(vp_palette)
                    viewport.setAutoFillBackground(True)
                except Exception:
                    pass
            except Exception:
                pass
        
        # Update dropdown theme after base theme is applied - force complete reset
        try:
            if hasattr(self, 'sort_combo'):
                # Extreme approach: recreate the combo box with new theme
                self._recreate_sort_combo(theme)
        except Exception as e:
            print(f"Error updating dropdown theme: {e}")
        
        # Update info label immediately after theme application - force complete reset
        try:
            if hasattr(self, 'info_label'):
                # Extreme approach: recreate the info label with new theme
                self._recreate_info_label(theme)
        except Exception as e:
            print(f"Error updating info label theme: {e}")
        
        # Force complete widget tree update
        try:
            self.update()
            self.repaint()
            # Update all children
            for child in self.findChildren(QWidget):
                child.update()
                child.repaint()
        except Exception:
            pass
    
    def _apply_sort_styles(self, theme: str):
        """Apply theme-aware styles to sort label and use shared combo theming."""
        is_light = (theme or 'dark').lower() == 'light'
        # Label style only; delegate combo box to shared theming
        if is_light:
            self.sort_label.setStyleSheet(
                """
                QLabel {
                    color: #222;
                    font-weight: bold;
                    padding: 0 5px;
                    font-size: 10pt;
                }
                """
            )
        else:
            self.sort_label.setStyleSheet(
                """
                QLabel {
                    color: #EEE;
                    font-weight: bold;
                    padding: 0 5px;
                    font-size: 10pt;
                }
                """
            )
        # Apply the same theme and arrow icon style as the main app combos
        try:
            _apply_combo_theme(self.sort_combo, self)
        except Exception:
            pass

    def update_ui_language(self):
        """Update UI elements to reflect current language"""
        # Update window title
        self.setWindowTitle(tr.get_text("gallery_title"))
        
        # Update info label
        self.info_label.setText(tr.get_text("saved_screenshots"))
        # Update sort label
        if hasattr(self, 'sort_label'):
            self.sort_label.setText(tr.get_text("sort_by") + ":")
        
        # Update button texts
        self.refresh_button.setText(tr.get_text("refresh"))
        self.delete_button.setText(tr.get_text("delete_selected"))
        self.export_button.setText(tr.get_text("save"))
        
        # Update sort combo items
        current_selection = self.sort_combo.currentData()
        self.sort_combo.clear()
        self.sort_combo.addItem(tr.get_text("sort_by_name_asc"), "name_asc")
        self.sort_combo.addItem(tr.get_text("sort_by_name_desc"), "name_desc")
        self.sort_combo.addItem(tr.get_text("sort_by_date_asc"), "date_asc")
        self.sort_combo.addItem(tr.get_text("sort_by_date_desc"), "date_desc")
        
        # Restore previous selection
        if current_selection:
            for i in range(self.sort_combo.count()):
                if self.sort_combo.itemData(i) == current_selection:
                    self.sort_combo.setCurrentIndex(i)
                    break

    def refresh_button_themes(self):
        """Refresh button styles to reflect current color blindness settings and theme."""
        try:
            self._apply_button_styles()
            # Force repaint to ensure immediate visual update
            for btn in (self.refresh_button, self.delete_button, self.export_button):
                try:
                    btn.update()
                    btn.repaint()
                except Exception:
                    pass
        except Exception:
            pass

    def changeEvent(self, event):
        """React to framework change events (language/theme/custom)."""
        try:
            from PyQt5.QtCore import QEvent
            et = event.type()
            if et == QEvent.LanguageChange:
                # Update all localized texts
                self.update_ui_language()
                # Re-apply sort label/combo theme after text updates
                try:
                    self._apply_sort_styles(getattr(self, 'theme', 'dark'))
                except Exception:
                    pass
                # Refresh gallery to update counts with localized prefix
                try:
                    self.refresh_gallery()
                except Exception:
                    pass
            # Proactively reapply button styles on any palette/style change too
            if et in (QEvent.PaletteChange, QEvent.StyleChange):
                try:
                    self.refresh_button_themes()
                except Exception:
                    pass
        except Exception:
            pass
        # Call base implementation
        try:
            super().changeEvent(event)
        except Exception:
            pass

    def _apply_gallery_title_bar(self, theme: str):
        """Apply theme-appropriate title bar for gallery"""
        try:
            import platform
            if platform.system() == "Windows":
                try:
                    import ctypes
                    from ctypes import wintypes
                    
                    # Get window handle
                    hwnd = int(self.winId())
                    
                    # Windows 10/11 dark title bar - multiple methods for compatibility
                    DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19
                    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                    
                    if (theme or 'dark').lower() == 'dark':
                        value = 1
                    else:
                        value = 0
                        
                    # Try newer API first (Windows 10 20H1+)
                    try:
                        ctypes.windll.dwmapi.DwmSetWindowAttribute(
                            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 
                            ctypes.byref(ctypes.c_int(value)), 
                            ctypes.sizeof(ctypes.c_int)
                        )
                    except Exception:
                        # Fallback to older API
                        try:
                            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1, 
                                ctypes.byref(ctypes.c_int(value)), 
                                ctypes.sizeof(ctypes.c_int)
                            )
                        except Exception:
                            pass
                    
                    # Force window refresh to apply changes
                    try:
                        rect = wintypes.RECT()
                        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                        ctypes.windll.user32.SetWindowPos(
                            hwnd, 0, 0, 0, 0, 0,
                            0x0001 | 0x0002 | 0x0020  # SWP_NOSIZE | SWP_NOMOVE | SWP_FRAMECHANGED
                        )
                    except Exception:
                        pass
                except Exception:
                    pass
        except Exception as e:
            # Fallback - just print error, don't crash
            print(f"Could not apply gallery title bar theme: {e}")

    def _apply_gallery_title_bar_to_dialog(self, dialog_widget, theme: str):
        """Apply the same title bar theme approach from gallery to dialog - exact copy"""
        try:
            import platform
            if platform.system() == "Windows":
                try:
                    import ctypes
                    from ctypes import wintypes
                    
                    # Get window handle
                    hwnd = int(dialog_widget.winId())
                    
                    # Windows 10/11 dark title bar - multiple methods for compatibility
                    DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19
                    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                    
                    if (theme or 'dark').lower() == 'dark':
                        value = 1
                    else:
                        value = 0
                        
                    # Try newer API first (Windows 10 20H1+)
                    try:
                        ctypes.windll.dwmapi.DwmSetWindowAttribute(
                            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 
                            ctypes.byref(ctypes.c_int(value)), 
                            ctypes.sizeof(ctypes.c_int)
                        )
                    except Exception:
                        # Fallback to older API
                        try:
                            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1, 
                                ctypes.byref(ctypes.c_int(value)), 
                                ctypes.sizeof(ctypes.c_int)
                            )
                        except Exception:
                            pass
                    
                    # Force window refresh to apply changes
                    try:
                        rect = wintypes.RECT()
                        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                        ctypes.windll.user32.SetWindowPos(
                            hwnd, 0, 0, 0, 0, 0,
                            0x0001 | 0x0002 | 0x0020  # SWP_NOSIZE | SWP_NOMOVE | SWP_FRAMECHANGED
                        )
                    except Exception:
                        pass
                except Exception:
                    pass
        except Exception as e:
            # Fallback - just print error, don't crash
            print(f"Could not apply dialog title bar theme: {e}")
    
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
        
        # Sort files by creation time (newest first) - default sorting
        screenshot_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        self.screenshots = screenshot_files
        
        # Apply current sort selection
        self.apply_current_sort()

        # Dynamic column count calculation based on window size and mode
        if self.is_fullscreen:
            column_count = 6  # Fixed for fullscreen mode
        else:
            # Calculate optimal column count for current window width
            available_width = self.scroll_area.width() - 20  # Account for scrollbar
            # Fallback to window width if scroll area width is not available
            if available_width <= 20:
                available_width = self.width() - 40
            
            thumbnail_width = 185  # Reduced width per thumbnail for tighter layout
            min_columns = 3  # Minimum columns for readability
            max_columns = 8  # Maximum columns to prevent overcrowding
            
            if available_width > 0:
                calculated_columns = max(min_columns, min(max_columns, available_width // thumbnail_width))
                column_count = calculated_columns
            else:
                column_count = 4  # Default fallback
        
        # Dynamic thumbnail sizes based on fullscreen mode - maximize screen usage
        if self.is_fullscreen:
            # Calculate optimal size based on screen width (6 columns)
            thumbnail_size = QSize(220, 220)
            label_size = QSize(225, 225)
        else:
            thumbnail_size = QSize(150, 150)
            label_size = QSize(180, 150)
        
        for i, file_path in enumerate(screenshot_files):
            # Create thumbnail
            pixmap = QPixmap(file_path)
            thumbnail = pixmap.scaled(thumbnail_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Create label and add to layout inside a cell container
            thumb_label = ClickableLabel(i, self)
            thumb_label.setObjectName("thumbnail")
            thumb_label.setPixmap(thumbnail)
            thumb_label.setAlignment(Qt.AlignCenter)
            thumb_label.setToolTip(file_path)
            # Ultra-minimal styling for maximum density
            if self.is_fullscreen:
                thumb_label.setStyleSheet("margin: 0px; border: none; padding: 0px; background: transparent;")
            else:
                thumb_label.setStyleSheet("margin: 0px; background: transparent; padding: 0px;")
            thumb_label.setFixedSize(label_size)

            # Caption with filename index and date in dd/mm/yyyy format
            base = os.path.basename(file_path)
            num = extract_number_from_filename(base)
            date_str, time_str = extract_date_from_filename(file_path)
            caption = QLabel(f"#{num} • {date_str} {time_str}")
            caption.setAlignment(Qt.AlignCenter)
            
            # Larger font size for enhanced readability
            font_size = "13px" if self.is_fullscreen else "12px"
            margin = "1px 0 2px 0" if self.is_fullscreen else "2px 0 6px 0"
            caption.setStyleSheet(f"QLabel {{ color: #888; font-size: {font_size}; padding: 0px; margin: {margin}; }}")

            # Cell container with reduced margins for tighter layout
            cell = QWidget()
            v = QVBoxLayout(cell)
            # Reduced margins for both modes to bring images closer
            margin = 0 if self.is_fullscreen else 2
            v_margin = 0 if self.is_fullscreen else 0
            spacing = 0 if self.is_fullscreen else 0
            v.setContentsMargins(margin, v_margin, margin, v_margin)
            v.setSpacing(spacing)
            v.addWidget(thumb_label)
            v.addWidget(caption)
            
            # Set cell minimum size based on fullscreen mode - maximize space usage
            if self.is_fullscreen:
                cell.setMinimumSize(225, 225)
                cell.setMaximumSize(225, 225)
            else:
                cell.setMinimumSize(190, 170)
            
            # Set size policy for cell
            cell.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

            row, column = i // column_count, i % column_count
            # Add widgets with top alignment to prevent vertical spreading
            self.gallery_layout.addWidget(cell, row, column, Qt.AlignTop | Qt.AlignLeft)
            # Track widgets to allow clearing later
            self.thumbnail_labels.append(cell)
            self._thumb_labels.append(thumb_label)
        
        # Set minimal stretch factors for ultra-compact layout in fullscreen
        if self.is_fullscreen:
            # Reset all stretch factors to 0 for compact layout
            for col in range(column_count):
                self.gallery_layout.setColumnStretch(col, 0)
            # Set row stretch factors to 0 to prevent vertical expansion
            total_rows = (len(screenshot_files) + column_count - 1) // column_count
            for row in range(total_rows):
                self.gallery_layout.setRowStretch(row, 0)
            # Set scroll widget size policy to minimize vertical space
            self.scroll_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            # Add a spacer to push content to top
            if total_rows > 0:
                spacer = QWidget()
                spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.gallery_layout.addWidget(spacer, total_rows, 0, 1, column_count)
        else:
            # Restore normal size policy for non-fullscreen mode
            self.scroll_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            # Set compact spacing for normal mode too
            self.gallery_layout.setSpacing(3)
        
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
            # Update last selected index only when adding
            self.last_selected_index = index
        # Update visuals
        for i, thumb_label in enumerate(self._thumb_labels):
            if i in self.selected_indices:
                thumb_label.setStyleSheet("margin: 0px; background: rgba(33,150,243,0.3); border: 2px solid #2196F3; padding: 0px;")
            else:
                thumb_label.setStyleSheet("margin: 0px; background: transparent; padding: 0px;")
        # Update button states
        self.delete_button.setEnabled(len(self.selected_indices) > 0)
        self.export_button.setEnabled(len(self.selected_indices) > 0)  # Enable for any selection
        # Update button styles
        self._apply_button_styles()

    def select_range(self, index):
        """Range select support; select from last selected index to current index"""
        if self.last_selected_index == -1:
            # No previous selection, treat as single select
            self.select_single(index)
            return
        
        # Clear current selections
        self.selected_indices.clear()
        
        # Calculate range
        start_index = min(self.last_selected_index, index)
        end_index = max(self.last_selected_index, index)
        
        # Add all indices in range
        for i in range(start_index, end_index + 1):
            if 0 <= i < len(self.screenshots):
                self.selected_indices.add(i)
        
        # Update last selected index
        self.last_selected_index = index
        
        # Update visuals
        for i, thumb_label in enumerate(self._thumb_labels):
            if i in self.selected_indices:
                thumb_label.setStyleSheet("margin: 0px; background: rgba(33,150,243,0.3); border: 2px solid #2196F3; padding: 0px;")
            else:
                thumb_label.setStyleSheet("margin: 0px; background: transparent; padding: 0px;")
        # Update button states
        self.delete_button.setEnabled(len(self.selected_indices) > 0)
        self.export_button.setEnabled(len(self.selected_indices) > 0)  # Enable for any selection
        # Update button styles
        self._apply_button_styles()

    def select_single(self, index):
        """Single-select support; select only the specified index"""
        # Clear all selections
        self.selected_indices.clear()
        # Add the specified index
        self.selected_indices.add(index)
        # Update last selected index
        self.last_selected_index = index
        # Update visuals
        for i, thumb_label in enumerate(self._thumb_labels):
            if i in self.selected_indices:
                thumb_label.setStyleSheet("margin: 0px; background: rgba(33,150,243,0.3); border: 2px solid #2196F3; padding: 0px;")
            else:
                thumb_label.setStyleSheet("margin: 0px; background: transparent; padding: 0px;")
        # Update button states
        self.delete_button.setEnabled(len(self.selected_indices) > 0)
        self.export_button.setEnabled(len(self.selected_indices) > 0)  # Enable for any selection
        # Update button styles
        self._apply_button_styles()

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
            tr.get_text("delete_confirm_text", str(count))
        )
        if reply == QMessageBox.Yes:
            try:
                for idx in sorted(self.selected_indices, reverse=True):
                    if 0 <= idx < len(self.screenshots):
                        os.remove(self.screenshots[idx])
                self.load_screenshots()
                self._apply_button_styles()
                # Check if parent exists before accessing status_bar
                if self.parent() and hasattr(self.parent(), 'status_bar'):
                    self.parent().status_bar.showMessage(tr.get_text("file_deleted", f"{count}"))
            except Exception as e:
                self._themed_critical(tr.get_text("error"), tr.get_text("delete_failed", str(e)))
    
    def export_selected(self):
        if not self.selected_indices:
            return
            
        if len(self.selected_indices) == 1:
            # Single file export - existing behavior with file dialog
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
                    # Check if parent exists before accessing status_bar
                    if self.parent() and hasattr(self.parent(), 'status_bar'):
                        self.parent().status_bar.showMessage(tr.get_text("file_exported", export_path))
                except Exception as e:
                    self._themed_critical(tr.get_text("error"), tr.get_text("export_failed", str(e)))
        else:
            # Multiple files export - choose directory
            export_dir = QFileDialog.getExistingDirectory(
                self,
                tr.get_text("select_export_directory"),
                "",
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
            )
            
            if export_dir:
                try:
                    exported_count = 0
                    failed_count = 0
                    
                    for index in self.selected_indices:
                        if 0 <= index < len(self.screenshots):
                            source_file = self.screenshots[index]
                            source_name = os.path.basename(source_file)
                            export_path = os.path.join(export_dir, source_name)
                            
                            try:
                                # Read and save the image
                                image = cv2.imread(source_file)
                                cv2.imwrite(export_path, image)
                                exported_count += 1
                            except Exception:
                                failed_count += 1
                    
                    self._apply_button_styles()  # Update button colors after export
                    
                    # Show result message
                    if self.parent() and hasattr(self.parent(), 'status_bar'):
                        if failed_count == 0:
                            self.parent().status_bar.showMessage(tr.get_text("files_exported", f"{exported_count}"))
                        else:
                            self.parent().status_bar.showMessage(tr.get_text("files_exported_with_errors", f"{exported_count}", f"{failed_count}"))
                
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
        
        # Set window flags before applying styles for better theme integration
        box.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint)
        box.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        
        self._apply_dialog_stylesheet(box)
        box.setIcon(QMessageBox.Critical)
        box.setWindowTitle(title)
        box.setText(text)
        box.setStandardButtons(QMessageBox.Ok)
        
        # Apply title bar theme exactly like gallery - immediate application
        theme_mode = getattr(self, 'theme', 'dark').lower()
        self._apply_gallery_title_bar_to_dialog(box, theme_mode)
        
        # Show dialog 
        box.show()
        
        # Apply title bar theme again after show - like gallery does
        self._apply_gallery_title_bar_to_dialog(box, theme_mode)
        
        # Also apply delayed like gallery 
        try:
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(50, lambda: self._apply_gallery_title_bar_to_dialog(box, theme_mode))
        except Exception:
            pass
            
        box.exec_()

    def _themed_question(self, title: str, text: str) -> int:
        # Localized Yes/No labels
        box = QMessageBox(self)
        
        # Set window flags before applying styles for better theme integration
        box.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint)
        box.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        
        self._apply_dialog_stylesheet(box)
        box.setIcon(QMessageBox.Question)
        # Use Qt's non-native dialog to ensure the Close (X) button is enabled on Windows
        try:
            box.setOption(QMessageBox.DontUseNativeDialog, True)
        except Exception:
            pass
        box.setWindowTitle(title)
        box.setText(text)
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
        
        # Apply title bar theme exactly like gallery - immediate application
        theme_mode = getattr(self, 'theme', 'dark').lower()
        self._apply_gallery_title_bar_to_dialog(box, theme_mode)
        
        # Show dialog 
        box.show()
        
        # Apply title bar theme again after show - like gallery does
        self._apply_gallery_title_bar_to_dialog(box, theme_mode)
        
        # Also apply delayed like gallery 
        try:
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(50, lambda: self._apply_gallery_title_bar_to_dialog(box, theme_mode))
        except Exception:
            pass
            
        result = box.exec_()
        if box.clickedButton() is yes_btn:
            return QMessageBox.Yes
        return QMessageBox.No

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            # Use maximize instead of direct fullscreen for better integration
            self.setWindowState(Qt.WindowMaximized)

    def enter_fullscreen(self):
        """Enter fullscreen mode"""
        if not self.is_fullscreen:
            # Save current geometry
            self.normal_geometry = self.geometry()
            
            # Set maximized instead of fullscreen to keep window frame
            self.setWindowState(Qt.WindowMaximized)
            self.is_fullscreen = True
            
            # Set ultra-minimal grid spacing for fullscreen mode - maximum density
            self.gallery_layout.setSpacing(-1 if self.is_fullscreen else 0)
            
            # Apply fullscreen-specific styles
            self._apply_fullscreen_styles()
            
            # Reload gallery with new layout
            self.load_screenshots()

    def _update_fullscreen_ui(self):
        """Update UI for fullscreen mode without changing window state"""
        self.is_fullscreen = True
        # Set ultra-minimal grid spacing for fullscreen mode - maximum density
        self.gallery_layout.setSpacing(-1 if self.is_fullscreen else 0)
        # Apply fullscreen-specific styles
        self._apply_fullscreen_styles()
        # Reload gallery with new layout
        self.load_screenshots()

    def _update_normal_ui(self):
        """Update UI for normal mode without changing window state"""
        self.is_fullscreen = False
        # Set grid spacing for normal mode
        self.gallery_layout.setSpacing(8)
        # Restore normal styles
        self._apply_button_styles()
        # Reload gallery with normal layout
        self.load_screenshots()

    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        if self.is_fullscreen:
            # Restore window state
            self.setWindowState(Qt.WindowNoState)
            
            # Restore geometry if available
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            
            self.is_fullscreen = False
            
            # Set grid spacing for normal mode
            self.gallery_layout.setSpacing(8)
            
            # Restore normal styles
            self._apply_button_styles()
            
            # Reload gallery with normal layout
            self.load_screenshots()

    def _apply_fullscreen_styles(self):
        """Apply larger button styles for fullscreen mode"""
        # Refresh button - Blue (larger)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056CC;
            }
        """)
        
        # Delete button - Red (larger)
        if self.delete_button.isEnabled():
            self.delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #FF3B30;
                    color: white;
                    padding: 12px 24px;
                    border-radius: 8px;
                    border: none;
                    font-weight: bold;
                    font-size: 14px;
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
                    padding: 12px 24px;
                    border-radius: 8px;
                    border: none;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
        
        # Save button - Green (larger)
        if self.export_button.isEnabled():
            self.export_button.setStyleSheet("""
                QPushButton {
                    background-color: #34C759;
                    color: white;
                    padding: 12px 24px;
                    border-radius: 8px;
                    border: none;
                    font-weight: bold;
                    font-size: 14px;
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
                    padding: 12px 24px;
                    border-radius: 8px;
                    border: none;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_Escape:
            if self.is_fullscreen:
                self.exit_fullscreen()
            else:
                self.accept()
        elif event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Persist gallery window geometry into current profile on close."""
        try:
            # Don’t save geometry when in fullscreen to avoid storing screen-sized values
            if not getattr(self, 'is_fullscreen', False):
                g = self.geometry()
                parent = self.parent()
                profile = getattr(parent, 'current_profile', None)
                if profile is not None:
                    try:
                        profile.gallery_x = int(g.x())
                        profile.gallery_y = int(g.y())
                        profile.gallery_width = int(g.width())
                        profile.gallery_height = int(g.height())
                    except Exception:
                        pass
                    # Persist to disk via ProfileManager if available
                    pm = getattr(parent, 'profile_manager', None)
                    if pm is not None:
                        try:
                            pm.save_profile(profile)
                            pm.apply_profile_to_settings(profile)
                        except Exception:
                            pass
        except Exception:
            pass
        super().closeEvent(event)

    def changeEvent(self, event):
        """Handle window state changes"""
        if event.type() == event.WindowStateChange:
            # Handle minimize button properly - ensure window goes to taskbar
            if self.windowState() & Qt.WindowMinimized:
                # Force window to actually minimize to taskbar
                self.showMinimized()
                return
            elif self.windowState() & Qt.WindowMaximized:
                if not self.is_fullscreen:
                    self._update_fullscreen_ui()
            elif self.windowState() == Qt.WindowNoState:
                if self.is_fullscreen:
                    self._update_normal_ui()
        super().changeEvent(event)

    def showEvent(self, event):
        """Ensure proper display when window is shown"""
        super().showEvent(event)
        # Make sure window is properly visible and focusable
        self.raise_()
        self.activateWindow()

    def minimizeEvent(self, event):
        """Handle minimize event properly"""
        # Ensure window actually minimizes to taskbar
        self.showMinimized()
        super().minimizeEvent(event) if hasattr(super(), 'minimizeEvent') else None

    def resizeEvent(self, event):
        """Handle window resize events to update column layout dynamically"""
        super().resizeEvent(event)
        # Only reload layout for normal mode (not fullscreen) and if gallery has been loaded
        if not self.is_fullscreen and hasattr(self, 'screenshots') and self.screenshots:
            # Add a small delay to avoid excessive reloading during resize
            if hasattr(self, '_resize_timer'):
                self._resize_timer.stop()
            else:
                from PyQt5.QtCore import QTimer
                self._resize_timer = QTimer()
                self._resize_timer.setSingleShot(True)
                self._resize_timer.timeout.connect(self._delayed_layout_update)
            self._resize_timer.start(200)  # 200ms delay
    
    def _delayed_layout_update(self):
        """Delayed update of gallery layout after resize"""
        if not self.is_fullscreen:
            self.load_screenshots()
    
    def sort_screenshots(self):
        """Sort screenshots based on the selected option"""
        if not self.screenshots:
            return
            
        self.apply_current_sort()
        self.refresh_display()
    
    def apply_current_sort(self):
        """Apply sorting based on current combo box selection"""
        current_data = self.sort_combo.currentData()
        
        if current_data == "name_asc":
            # Sort by filename A-Z with natural numeric ordering
            self.screenshots.sort(key=lambda x: natural_sort_key(os.path.basename(x)))
        elif current_data == "name_desc":
            # Sort by filename Z-A with natural numeric ordering
            self.screenshots.sort(key=lambda x: natural_sort_key(os.path.basename(x)), reverse=True)
        elif current_data == "date_asc":
            # Sort by date oldest first (using enhanced date extraction)
            self.screenshots.sort(key=date_sort_key)
        elif current_data == "date_desc":
            # Sort by date newest first (default, using enhanced date extraction)
            self.screenshots.sort(key=date_sort_key, reverse=True)
    
    def refresh_display(self):
        """Refresh the display of thumbnails without reloading from disk"""
        # Clear existing thumbnails
        for cell in self.thumbnail_labels:
            self.gallery_layout.removeWidget(cell)
            cell.deleteLater()
        self.thumbnail_labels = []
        self._thumb_labels = []
        
        # Clear selection state
        self.selected_indices.clear()
        self.selected_index = -1
        self.last_selected_index = -1
        self.delete_button.setEnabled(False)
        self.export_button.setEnabled(False)
        
        # Re-display thumbnails with current order
        self.load_screenshots()

# Helper clickable label to support multi-select toggling
class ClickableLabel(QLabel):
    def __init__(self, index: int, gallery: ScreenshotGallery):
        super().__init__()
        self._index = index
        self._gallery = gallery

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check modifier keys for different selection modes
            if event.modifiers() & Qt.ControlModifier:
                # Ctrl+Click: Toggle selection (multi-select)
                self._gallery.toggle_select(self._index)
            elif event.modifiers() & Qt.ShiftModifier:
                # Shift+Click: Range selection
                self._gallery.select_range(self._index)
            else:
                # Normal click: Single selection
                self._gallery.select_single(self._index)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._gallery.open_fullscreen(self._index)
        super().mouseDoubleClickEvent(event)
