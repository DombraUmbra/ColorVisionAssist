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
        
        # Update icon path
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'gallery_icon.png')
        self.setWindowIcon(QIcon(icon_path))
        
        # Main layout
        layout = QVBoxLayout()
        
        # Info label
        self.info_label = QLabel(tr.get_text("saved_screenshots"))
        layout.addWidget(self.info_label)
        
        # Create a scroll area for the gallery
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.gallery_layout = QGridLayout(scroll_widget)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        # Add buttons
        self.refresh_button = QPushButton(tr.get_text("refresh"))
        self.refresh_button.clicked.connect(self.load_screenshots)
        
        self.delete_button = QPushButton(tr.get_text("delete_selected"))
        self.delete_button.clicked.connect(self.delete_selected)
        self.delete_button.setEnabled(False)
        
        self.export_button = QPushButton(tr.get_text("export"))
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
        
        # Apply the dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #333;
                color: #EEE;
            }
            QLabel {
                color: #EEE;
            }
            QPushButton {
                background-color: #555;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #777;
            }
            QPushButton:disabled {
                background-color: #444;
                color: #888;
            }
            QScrollArea {
                border: 1px solid #555;
                background-color: #444;
            }
        """)
    
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
            label.setPixmap(thumbnail)
            label.setAlignment(Qt.AlignCenter)
            label.setToolTip(file_path)
            label.setStyleSheet("border: 2px solid #555; margin: 5px; background-color: #222; padding: 5px;")
            label.setFixedSize(QSize(180, 180))
            label.mousePressEvent = lambda event, idx=i: self.select_screenshot(idx)
            
            row, column = i // column_count, i % column_count
            self.gallery_layout.addWidget(label, row, column)
            self.thumbnail_labels.append(label)
        
        # Update info text
        self.info_label.setText(f"{tr.get_text('saved_screenshots')} {len(screenshot_files)}")

    def select_screenshot(self, index):
        # Deselect the previous selection
        if 0 <= self.selected_index < len(self.thumbnail_labels):
            self.thumbnail_labels[self.selected_index].setStyleSheet("border: 2px solid #555; margin: 5px; background-color: #222; padding: 5px;")
        
        # Select the new one
        self.selected_index = index
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
                    self.parent().status_bar.showMessage(tr.get_text("file_exported", export_path))
                except Exception as e:
                    QMessageBox.critical(self, tr.get_text("error"), tr.get_text("export_failed", str(e)))
