"""
Camera selector component for ColorVisionAid
Provides dropdown selection for available cameras
"""

from PyQt5.QtWidgets import (
    QComboBox, QLabel, QHBoxLayout, QVBoxLayout, 
    QWidget, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from ..translations import translator as tr


class CameraSelector(QWidget):
    """
    Camera selection widget with dropdown and refresh functionality
    """
    # Signal emitted when camera selection changes
    camera_changed = pyqtSignal(int)
    
    def __init__(self, camera_manager, parent=None):
        """
        Initialize camera selector
        
        Args:
            camera_manager: Instance of CameraManager
            parent: Parent widget
        """
        super().__init__(parent)
        self.camera_manager = camera_manager
        self.parent_window = parent
        self.setup_ui()
        self.update_camera_list()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # Camera label
        self.camera_label = QLabel(tr.get_text("select_camera"))
        self.camera_label.setMinimumWidth(80)
        
        # Camera dropdown
        self.camera_combo = QComboBox()
        self.camera_combo.setMinimumWidth(200)
        self.camera_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.camera_combo.currentIndexChanged.connect(self.on_camera_changed)
        
        # Refresh button
        self.refresh_button = QPushButton(tr.get_text("refresh"))
        self.refresh_button.setMaximumWidth(80)
        self.refresh_button.clicked.connect(self.refresh_cameras)
        self.refresh_button.setToolTip(tr.get_text("refresh_camera_list"))
        
        # Add widgets to layout
        main_layout.addWidget(self.camera_label)
        main_layout.addWidget(self.camera_combo)
        main_layout.addWidget(self.refresh_button)
        
        # Apply theme styling
        self.apply_theme_styling()
        
    def apply_theme_styling(self):
        """Apply theme-aware styling to components"""
        try:
            theme = getattr(self.parent_window, 'theme', 'dark').lower()
            
            if theme == 'light':
                # Light theme styling
                label_style = "color: #222; font-size: 11pt;"
                combo_style = """
                    QComboBox {
                        background-color: white;
                        color: #222;
                        border: 2px solid #ccc;
                        border-radius: 5px;
                        padding: 5px;
                        font-size: 11pt;
                    }
                    QComboBox:hover {
                        border-color: #0078d4;
                    }
                    QComboBox::drop-down {
                        border: none;
                        width: 20px;
                    }
                    QComboBox::down-arrow {
                        width: 12px;
                        height: 12px;
                        margin: 2px;
                    }
                """
                button_style = """
                    QPushButton {
                        background-color: #0078d4;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 6px 12px;
                        font-size: 10pt;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #106ebe;
                    }
                    QPushButton:pressed {
                        background-color: #005a9e;
                    }
                """
            else:
                # Dark theme styling
                label_style = "color: white; font-size: 11pt;"
                combo_style = """
                    QComboBox {
                        background-color: #2d2d30;
                        color: white;
                        border: 2px solid #555;
                        border-radius: 5px;
                        padding: 5px;
                        font-size: 11pt;
                    }
                    QComboBox:hover {
                        border-color: #0078d4;
                    }
                    QComboBox::drop-down {
                        border: none;
                        width: 20px;
                    }
                    QComboBox::down-arrow {
                        width: 12px;
                        height: 12px;
                        margin: 2px;
                    }
                    QComboBox QAbstractItemView {
                        background-color: #2d2d30;
                        color: white;
                        selection-background-color: #0078d4;
                    }
                """
                button_style = """
                    QPushButton {
                        background-color: #0078d4;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 6px 12px;
                        font-size: 10pt;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #106ebe;
                    }
                    QPushButton:pressed {
                        background-color: #005a9e;
                    }
                """
            
            self.camera_label.setStyleSheet(label_style)
            self.camera_combo.setStyleSheet(combo_style)
            self.refresh_button.setStyleSheet(button_style)
            
        except Exception:
            # Fallback to basic styling if theme detection fails
            pass
    
    def update_camera_list(self):
        """Update the camera dropdown with available cameras"""
        # Clear existing items
        self.camera_combo.clear()
        
        # Get available cameras
        cameras = self.camera_manager.get_available_cameras()
        
        # Add cameras to dropdown
        for index, name in cameras:
            self.camera_combo.addItem(name, index)
        
        # Set current selection to match camera manager's selected camera
        current_index = self.camera_manager.selected_camera_index
        for i in range(self.camera_combo.count()):
            if self.camera_combo.itemData(i) == current_index:
                self.camera_combo.setCurrentIndex(i)
                break
    
    def refresh_cameras(self):
        """Refresh the list of available cameras"""
        # Refresh camera manager's camera list
        self.camera_manager.refresh_cameras()
        
        # Update the dropdown
        self.update_camera_list()
        
        # Show feedback message
        if hasattr(self.parent_window, 'status_bar'):
            self.parent_window.status_bar.showMessage(tr.get_text("cameras_refreshed"))
    
    def on_camera_changed(self, combo_index):
        """Handle camera selection change"""
        if combo_index >= 0:
            # Get the actual camera index from the combo box data
            camera_index = self.camera_combo.itemData(combo_index)
            if camera_index is not None:
                # Set the camera in the manager
                self.camera_manager.set_camera_index(camera_index)
                
                # Emit signal for other components
                self.camera_changed.emit(camera_index)
                
                # Show feedback message
                if hasattr(self.parent_window, 'status_bar'):
                    camera_name = self.camera_combo.currentText()
                    self.parent_window.status_bar.showMessage(
                        f"{tr.get_text('camera_selected')}: {camera_name}"
                    )
    
    def update_current_camera_name(self):
        """Update the current camera name with real-time resolution info"""
        current_index = self.camera_combo.currentIndex()
        if current_index >= 0:
            camera_index = self.camera_combo.itemData(current_index)
            if camera_index is not None:
                # Get updated camera name from manager
                updated_name = self.camera_manager.get_current_camera_name()
                # Update the combo box item text
                self.camera_combo.setItemText(current_index, updated_name)
    
    def get_current_camera_index(self):
        """Get the currently selected camera index"""
        current_index = self.camera_combo.currentIndex()
        if current_index >= 0:
            return self.camera_combo.itemData(current_index)
        return 0
    
    def set_current_camera_index(self, camera_index):
        """Set the current camera selection by index"""
        for i in range(self.camera_combo.count()):
            if self.camera_combo.itemData(i) == camera_index:
                self.camera_combo.setCurrentIndex(i)
                break
    
    def update_theme(self, theme):
        """Update the theme styling"""
        self.apply_theme_styling()
        
    def retranslate_ui(self):
        """Update UI text when language changes"""
        self.camera_label.setText(tr.get_text("select_camera"))
        self.refresh_button.setText(tr.get_text("refresh"))
        self.refresh_button.setToolTip(tr.get_text("refresh_camera_list"))