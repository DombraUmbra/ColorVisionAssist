"""
Dialog windows for ColorVisionAid
Contains advanced settings dialog and other dialog components
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QWidget, QLabel, QCheckBox, QPushButton, QSlider, QGroupBox)
from PyQt5.QtCore import Qt
from ..translations import translator as tr

class AdvancedSettingsDialog(QDialog):
    """Advanced settings dialog - Compatible design with main application"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(tr.get_text("advanced_settings"))
        self.setModal(True)
        
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(tr.get_text("advanced_settings"))
        self.setModal(True)
        
        # Remove context help button for all themes
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # Responsive sizing - Adapt to screen size
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.desktop().screenGeometry()
        width = min(max(650, int(screen.width() * 0.65)), 900)
        height = min(max(700, int(screen.height() * 0.75)), 950)
        
        self.setMinimumSize(width, height)
        self.setMaximumSize(width + 150, height + 150)
        self.resize(width, height)
        
        # Initialize dialog checkboxes
        self.red_checkbox = None
        self.green_checkbox = None
        self.blue_checkbox = None
        self.yellow_checkbox = None
        
        self.setup()

    def _get_theme(self) -> str:
        """Return current theme ('light' or 'dark') inherited from parent if available."""
        return (getattr(self.parent, 'theme', 'dark') if self.parent else 'dark').lower()
        
    def setup(self):
        """Set up dialog layout - Compatible with main application theme"""
        # Create main content layout
        content_layout = QVBoxLayout(self)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create tab widget - Compatible with main theme
        tab_widget = QTabWidget()
        if self._get_theme() == 'light':
            tab_widget.setStyleSheet("""
                QTabWidget::pane { border: 2px solid #DDD; border-radius: 5px; background-color: #FFFFFF; padding: 10px; margin-top: 5px; }
                QTabBar::tab { background-color: #EDEFF1; color: #222; padding: 12px 14px; margin: 1px; border-radius: 3px; font-size: 9pt; min-width: 70px; max-width: 120px; border: 1px solid #D0D4D9; }
                QTabBar::tab:selected { background-color: #1976D2; color: white; font-weight: bold; border: 1px solid #1976D2; }
                QTabBar::tab:hover { background-color: #F5F6F7; }
            """)
        else:
            tab_widget.setStyleSheet("""
                QTabWidget::pane { border: 2px solid #555; border-radius: 5px; background-color: #444; padding: 10px; margin-top: 5px; }
                QTabBar::tab { background-color: #555; color: #EEE; padding: 12px 14px; margin: 1px; border-radius: 3px; font-size: 9pt; min-width: 70px; max-width: 120px; }
                QTabBar::tab:selected { background-color: #2196F3; color: white; font-weight: bold; }
                QTabBar::tab:hover { background-color: #666; }
            """)
        
        # Color selection tab
        color_tab = self.create_color_tab()
        tab_widget.addTab(color_tab, tr.get_text("color_selection_short"))
        
        # Detection parameters tab
        parameters_tab = self.create_parameters_tab()
        tab_widget.addTab(parameters_tab, tr.get_text("parameters_short"))
        
        # Filtering tab
        filtering_tab = self.create_filtering_tab()
        tab_widget.addTab(filtering_tab, tr.get_text("filtering_short"))
        
        content_layout.addWidget(tab_widget)
        
        # Buttons - Main application button style
        button_layout = self.create_button_layout()
        content_layout.addLayout(button_layout)
        
        # Apply main theme - Special style for dialog
        theme = getattr(self.parent, 'theme', 'dark') if self.parent else 'dark'
        self.apply_dialog_theme(theme)
        
    def apply_dialog_theme(self, theme: str = 'dark'):
        """Apply main theme for dialog (dark or light)"""
        if (theme or 'dark').lower() == 'light':
            self.setStyleSheet("""
                QDialog { 
                    background-color: #F5F5F7; 
                    color: #222; 
                }
                QWidget { background-color: #F5F5F7; color: #222; }
                QScrollArea { background-color: #F5F5F7; border: none; }
                QScrollArea > QWidget > QWidget { background-color: #F5F5F7; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { 
                    background-color: #2b2b2b; 
                    color: #EEE; 
                    border: 1px solid #555;
                }
                QWidget { background-color: #2b2b2b; color: #EEE; }
                QScrollArea { background-color: #2b2b2b; border: none; }
                QScrollArea > QWidget > QWidget { background-color: #2b2b2b; }
            """)
        
    def create_color_tab(self):
        """Create color selection tab - Compatible with main theme"""
        color_tab = QWidget()
        color_layout = QVBoxLayout(color_tab)
        color_layout.setSpacing(12)
        color_layout.setContentsMargins(10, 10, 10, 10)
        
        # Description - Main application style
        description = QLabel(tr.get_text("manual_color_selection_desc"))
        description.setWordWrap(True)
        if self._get_theme() == 'light':
            description.setStyleSheet("""
                QLabel { color: #444; font-size: 9pt; padding: 10px; background-color: #F1F3F4; border-radius: 5px; border-left: 4px solid #1976D2; line-height: 1.4; }
            """)
        else:
            description.setStyleSheet("""
                QLabel { color: #CCC; font-size: 9pt; padding: 10px; background-color: #3A3A3A; border-radius: 5px; border-left: 4px solid #2196F3; line-height: 1.4; }
            """)
        color_layout.addWidget(description)
        
        # Color selection group - Main application GroupBox style
        color_group = QGroupBox(tr.get_text("select_colors_to_detect"))
        if self._get_theme() == 'light':
            color_group.setStyleSheet("""
                QGroupBox { color: #222; font-size: 10pt; font-weight: bold; border: 2px solid #DDD; border-radius: 8px; margin-top: 12px; padding-top: 15px; background-color: #FFFFFF; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 8px; color: #1976D2; font-size: 10pt; font-weight: bold; }
                QGroupBox:hover { border: 2px solid #1976D2; }
            """)
        else:
            color_group.setStyleSheet("""
                QGroupBox { color: #EEE; font-size: 10pt; font-weight: bold; border: 2px solid #555; border-radius: 8px; margin-top: 12px; padding-top: 15px; background-color: #444; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 8px; color: #2196F3; font-size: 10pt; font-weight: bold; }
                QGroupBox:hover { border: 2px solid #2196F3; }
            """)
        
        color_layout_inner = QVBoxLayout()
        color_layout_inner.setSpacing(10)
        color_layout_inner.setContentsMargins(15, 10, 15, 15)
        
        # Create checkboxes - Main application style
        self.red_checkbox = QCheckBox(tr.get_text("detect_red"))
        self.green_checkbox = QCheckBox(tr.get_text("detect_green"))
        self.blue_checkbox = QCheckBox(tr.get_text("detect_blue"))
        self.yellow_checkbox = QCheckBox(tr.get_text("detect_yellow"))
        
        # Get values from main window
        self.red_checkbox.setChecked(self.parent.red_checkbox.isChecked())
        self.green_checkbox.setChecked(self.parent.green_checkbox.isChecked())
        self.blue_checkbox.setChecked(self.parent.blue_checkbox.isChecked())
        self.yellow_checkbox.setChecked(self.parent.yellow_checkbox.isChecked())
        
        # Main application checkbox style
        if self._get_theme() == 'light':
            checkbox_stil = """
                QCheckBox { color: #222; font-size: 10pt; spacing: 10px; padding: 8px; background-color: #F5F6F7; border-radius: 4px; margin: 2px 0; }
                QCheckBox:hover { color: #1976D2; background-color: #ECEFF1; }
                QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px; border: 2px solid #BBB; background-color: #FFF; }
                QCheckBox::indicator:checked { background-color: #1976D2; border: 2px solid #1976D2; }
                QCheckBox::indicator:hover { border: 2px solid #64B5F6; }
            """
        else:
            checkbox_stil = """
                QCheckBox { color: #EEE; font-size: 10pt; spacing: 10px; padding: 8px; background-color: #3A3A3A; border-radius: 4px; margin: 2px 0; }
                QCheckBox:hover { color: #2196F3; background-color: #454545; }
                QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px; border: 2px solid #666; background-color: #333; }
                QCheckBox::indicator:checked { background-color: #2196F3; border: 2px solid #2196F3; }
                QCheckBox::indicator:hover { border: 2px solid #64B5F6; }
            """
        
        for checkbox in [self.red_checkbox, self.green_checkbox, self.blue_checkbox, self.yellow_checkbox]:
            checkbox.setStyleSheet(checkbox_stil)
        
        # Tooltips
        self.red_checkbox.setToolTip(tr.get_text("red_checkbox_tooltip"))
        self.green_checkbox.setToolTip(tr.get_text("green_checkbox_tooltip"))
        self.blue_checkbox.setToolTip(tr.get_text("blue_checkbox_tooltip"))
        self.yellow_checkbox.setToolTip(tr.get_text("yellow_checkbox_tooltip"))
        
        # Add checkboxes
        color_layout_inner.addWidget(self.red_checkbox)
        color_layout_inner.addWidget(self.green_checkbox)
        color_layout_inner.addWidget(self.blue_checkbox)
        color_layout_inner.addWidget(self.yellow_checkbox)
        
        color_group.setLayout(color_layout_inner)
        color_layout.addWidget(color_group)
        
        color_layout.addStretch()
        return color_tab
    
    def create_parameters_tab(self):
        """Create detection parameters tab - Compatible with main theme"""
        parameters_tab = QWidget()
        parameters_layout = QVBoxLayout(parameters_tab)
        parameters_layout.setSpacing(15)
        parameters_layout.setContentsMargins(10, 10, 10, 10)
        
        # Description
        description = QLabel(tr.get_text("detection_parameters_desc"))
        description.setWordWrap(True)
        if self._get_theme() == 'light':
            description.setStyleSheet("""
                QLabel { color: #444; font-size: 9pt; padding: 8px; background-color: #F1F3F4; border-radius: 3px; border-left: 3px solid #1976D2; }
            """)
        else:
            description.setStyleSheet("""
                QLabel { color: #CCC; font-size: 9pt; padding: 8px; background-color: #3A3A3A; border-radius: 3px; border-left: 3px solid #2196F3; }
            """)
        parameters_layout.addWidget(description)
        
        # Sensitivity group - Main application style
        sensitivity_group = QGroupBox(tr.get_text("real_world_sensitivity"))
        if self._get_theme() == 'light':
            sensitivity_group.setStyleSheet("""
                QGroupBox { color: #222; font-size: 10pt; border: 2px solid #DDD; border-radius: 5px; margin-top: 10px; padding-top: 10px; background-color: #FFFFFF; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 5px; color: #1976D2; }
                QGroupBox:hover { border: 2px solid #1976D2; }
            """)
        else:
            sensitivity_group.setStyleSheet("""
                QGroupBox { color: #EEE; font-size: 10pt; border: 2px solid #555; border-radius: 5px; margin-top: 10px; padding-top: 10px; background-color: #444; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 5px; color: #2196F3; }
                QGroupBox:hover { border: 2px solid #2196F3; }
            """)
        
        sensitivity_layout = QVBoxLayout()
        
        # Sensitivity slider - Main application style
        slider_layout = QHBoxLayout()
        
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(1, 10)
        self.sensitivity_slider.setValue(self.parent.sensitivity_slider.value())
        
        # Main application slider style
        if self._get_theme() == 'light':
            self.sensitivity_slider.setStyleSheet("""
                QSlider::groove:horizontal { height: 8px; background: #E0E0E0; border-radius: 4px; }
                QSlider::handle:horizontal { background: #1976D2; border: 1px solid #1976D2; width: 18px; margin: -2px 0; border-radius: 9px; }
                QSlider::handle:horizontal:hover { background: #42A5F5; border: 1px solid #90CAF9; width: 20px; margin: -3px 0; }
            """)
        else:
            self.sensitivity_slider.setStyleSheet("""
                QSlider::groove:horizontal { height: 8px; background: #333; border-radius: 4px; }
                QSlider::handle:horizontal { background: #2196F3; border: 1px solid #2196F3; width: 18px; margin: -2px 0; border-radius: 9px; }
                QSlider::handle:horizontal:hover { background: #64B5F6; border: 1px solid #90CAF9; width: 20px; margin: -3px 0; }
            """)
        
        slider_layout.addWidget(self.sensitivity_slider)
        
        # Value label
        self.sensitivity_value_label = QLabel(str(self.sensitivity_slider.value()))
        if self._get_theme() == 'light':
            self.sensitivity_value_label.setStyleSheet("""
                QLabel { color: #1976D2; font-size: 12pt; font-weight: bold; padding: 2px 8px; background-color: #EDEFF1; border-radius: 3px; min-width: 20px; }
            """)
        else:
            self.sensitivity_value_label.setStyleSheet("""
                QLabel { color: #2196F3; font-size: 12pt; font-weight: bold; padding: 2px 8px; background-color: #555; border-radius: 3px; min-width: 20px; }
            """)
        self.sensitivity_value_label.setAlignment(Qt.AlignCenter)
        slider_layout.addWidget(self.sensitivity_value_label)
        
        self.sensitivity_slider.valueChanged.connect(self.sensitivity_changed)
        sensitivity_layout.addLayout(slider_layout)
        
        # Sensitivity description
        self.sensitivity_description = QLabel(self.get_sensitivity_description(self.sensitivity_slider.value()))
        self.sensitivity_description.setWordWrap(True)
        if self._get_theme() == 'light':
            self.sensitivity_description.setStyleSheet("""
                QLabel { color: #555; font-size: 9pt; padding: 8px; background-color: #F1F3F4; border-radius: 3px; margin-top: 5px; }
            """)
        else:
            self.sensitivity_description.setStyleSheet("""
                QLabel { color: #BBB; font-size: 9pt; padding: 8px; background-color: #3A3A3A; border-radius: 3px; margin-top: 5px; }
            """)
        sensitivity_layout.addWidget(self.sensitivity_description)
        
        sensitivity_group.setLayout(sensitivity_layout)
        parameters_layout.addWidget(sensitivity_group)
        
        parameters_layout.addStretch()
        return parameters_tab
    
    def create_filtering_tab(self):
        """Create filtering tab - Compatible with main theme"""
        filtering_tab = QWidget()
        filtering_layout = QVBoxLayout(filtering_tab)
        filtering_layout.setSpacing(15)
        filtering_layout.setContentsMargins(10, 10, 10, 10)
        
        # Description
        description = QLabel(tr.get_text("color_filtering_desc"))
        description.setWordWrap(True)
        if self._get_theme() == 'light':
            description.setStyleSheet("""
                QLabel { color: #444; font-size: 9pt; padding: 8px; background-color: #F1F3F4; border-radius: 3px; border-left: 3px solid #1976D2; }
            """)
        else:
            description.setStyleSheet("""
                QLabel { color: #CCC; font-size: 9pt; padding: 8px; background-color: #3A3A3A; border-radius: 3px; border-left: 3px solid #2196F3; }
            """)
        filtering_layout.addWidget(description)
        
        # Skin tone filtering group - Main application style
        skin_tone_group = QGroupBox(tr.get_text("skin_tone_filtering"))
        if self._get_theme() == 'light':
            skin_tone_group.setStyleSheet("""
                QGroupBox { color: #222; font-size: 10pt; border: 2px solid #DDD; border-radius: 5px; margin-top: 10px; padding-top: 10px; background-color: #FFFFFF; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 5px; color: #1976D2; }
                QGroupBox:hover { border: 2px solid #1976D2; }
            """)
        else:
            skin_tone_group.setStyleSheet("""
                QGroupBox { color: #EEE; font-size: 10pt; border: 2px solid #555; border-radius: 5px; margin-top: 10px; padding-top: 10px; background-color: #444; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 5px; color: #2196F3; }
                QGroupBox:hover { border: 2px solid #2196F3; }
            """)
        
        skin_tone_layout = QVBoxLayout()
        
        self.skin_tone_filtering = QCheckBox(tr.get_text("enable_skin_tone_filtering"))
        self.skin_tone_filtering.setChecked(self.parent.skin_tone_filtering_active)  # Load current value from main application
        self.skin_tone_filtering.setToolTip(tr.get_text("skin_tone_filtering_tooltip"))
        if self._get_theme() == 'light':
            self.skin_tone_filtering.setStyleSheet("""
                QCheckBox { color: #222; font-size: 10pt; spacing: 8px; padding: 5px; }
                QCheckBox:hover { color: #1976D2; }
            """)
        else:
            self.skin_tone_filtering.setStyleSheet("""
                QCheckBox { color: #EEE; font-size: 10pt; spacing: 8px; padding: 5px; }
                QCheckBox:hover { color: #2196F3; }
            """)
        skin_tone_layout.addWidget(self.skin_tone_filtering)
        
        # Skin tone description
        skin_tone_description = QLabel(tr.get_text("skin_tone_filtering_explanation"))
        skin_tone_description.setWordWrap(True)
        if self._get_theme() == 'light':
            skin_tone_description.setStyleSheet("""
                QLabel { color: #555; font-size: 9pt; padding: 8px; background-color: #F1F3F4; border-radius: 3px; }
            """)
        else:
            skin_tone_description.setStyleSheet("""
                QLabel { color: #BBB; font-size: 9pt; padding: 8px; background-color: #3A3A3A; border-radius: 3px; }
            """)
        skin_tone_layout.addWidget(skin_tone_description)
        
        # Debug mode checkbox
        self.debug_mode = QCheckBox(tr.get_text("debug_mode"))
        self.debug_mode.setChecked(self.parent.debug_mode_active)
        self.debug_mode.setToolTip(tr.get_text("debug_mode_tooltip"))
        if self._get_theme() == 'light':
            self.debug_mode.setStyleSheet("""
                QCheckBox { color: #222; font-size: 10pt; spacing: 8px; padding: 5px; }
                QCheckBox:hover { color: #1976D2; }
            """)
        else:
            self.debug_mode.setStyleSheet("""
                QCheckBox { color: #EEE; font-size: 10pt; spacing: 8px; padding: 5px; }
                QCheckBox:hover { color: #2196F3; }
            """)
        skin_tone_layout.addWidget(self.debug_mode)
        
        skin_tone_group.setLayout(skin_tone_layout)
        filtering_layout.addWidget(skin_tone_group)
        
        # Stability group - Main application style
        stability_group = QGroupBox(tr.get_text("stability_enhancement"))
        if self._get_theme() == 'light':
            stability_group.setStyleSheet("""
                QGroupBox { color: #222; font-size: 10pt; border: 2px solid #DDD; border-radius: 5px; margin-top: 10px; padding-top: 10px; background-color: #FFFFFF; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 5px; color: #1976D2; }
                QGroupBox:hover { border: 2px solid #1976D2; }
            """)
        else:
            stability_group.setStyleSheet("""
                QGroupBox { color: #EEE; font-size: 10pt; border: 2px solid #555; border-radius: 5px; margin-top: 10px; padding-top: 10px; background-color: #444; }
                QGroupBox::title { subcontrol-origin: margin; padding: 0 5px; color: #2196F3; }
                QGroupBox:hover { border: 2px solid #2196F3; }
            """)
        
        stability_layout = QVBoxLayout()
        
        self.stability_enhancement = QCheckBox(tr.get_text("enable_stability_enhancement"))
        self.stability_enhancement.setChecked(self.parent.stability_enhancement_active)  # Load current value from main application
        self.stability_enhancement.setToolTip(tr.get_text("stability_enhancement_tooltip"))
        if self._get_theme() == 'light':
            self.stability_enhancement.setStyleSheet("""
                QCheckBox { color: #222; font-size: 10pt; spacing: 8px; padding: 5px; }
                QCheckBox:hover { color: #1976D2; }
            """)
        else:
            self.stability_enhancement.setStyleSheet("""
                QCheckBox { color: #EEE; font-size: 10pt; spacing: 8px; padding: 5px; }
                QCheckBox:hover { color: #2196F3; }
            """)
        stability_layout.addWidget(self.stability_enhancement)
        
        # Stability description
        stability_description = QLabel(tr.get_text("stability_enhancement_explanation"))
        stability_description.setWordWrap(True)
        if self._get_theme() == 'light':
            stability_description.setStyleSheet("""
                QLabel { color: #555; font-size: 9pt; padding: 8px; background-color: #F1F3F4; border-radius: 3px; }
            """)
        else:
            stability_description.setStyleSheet("""
                QLabel { color: #BBB; font-size: 9pt; padding: 8px; background-color: #3A3A3A; border-radius: 3px; }
            """)
        stability_layout.addWidget(stability_description)
        
        stability_group.setLayout(stability_layout)
        filtering_layout.addWidget(stability_group)
        
        filtering_layout.addStretch()
        return filtering_tab
    
    def create_button_layout(self):
        """Create button layout - Main application button style"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Cancel button - Main application style
        cancel_button = QPushButton(tr.get_text("cancel"))
        if self._get_theme() == 'light':
            cancel_button.setStyleSheet("""
                QPushButton { background-color: #E0E0E0; color: #222; padding: 8px 6px; border-radius: 5px; font-size: 9pt; min-height: 25px; text-align: center; min-width: 80px; border: 1px solid #C7C7C7; }
                QPushButton:hover { background-color: #EEEEEE; border: 1px solid #1976D2; }
                QPushButton:pressed { background-color: #D5D5D5; }
            """)
        else:
            cancel_button.setStyleSheet("""
                QPushButton { background-color: #555; color: white; padding: 8px 6px; border-radius: 5px; font-size: 9pt; min-height: 25px; text-align: center; min-width: 80px; }
                QPushButton:hover { background-color: #777; border: 1px solid #999; }
                QPushButton:pressed { background-color: #444; }
            """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # Save button - Main application style (old "OK" button)
        save_button = QPushButton(tr.get_text("save"))
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 6px;
                border-radius: 5px;
                font-size: 9pt;
                min-height: 25px;
                text-align: center;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #66BB6A;
                border: 2px solid #81C784;
            }
            QPushButton:pressed {
                background-color: #43A047;
            }
        """)
        save_button.clicked.connect(self.save_settings_and_close)
        button_layout.addWidget(save_button)
        
        return button_layout
    
    def sensitivity_changed(self, value):
        """Called when sensitivity changes"""
        self.sensitivity_value_label.setText(str(value))
        self.sensitivity_description.setText(self.get_sensitivity_description(value))
    
    def get_sensitivity_description(self, value):
        """Return description based on sensitivity value"""
        if value <= 3:
            return tr.get_text("low_sensitivity_desc")
        elif value <= 7:
            return tr.get_text("medium_sensitivity_desc")
        else:
            return tr.get_text("high_sensitivity_desc")
        
    def save_settings_and_close(self):
        """Save settings and close dialog"""
        # Update color selections
        self.parent.red_checkbox.setChecked(self.red_checkbox.isChecked())
        self.parent.green_checkbox.setChecked(self.green_checkbox.isChecked())
        self.parent.blue_checkbox.setChecked(self.blue_checkbox.isChecked())
        self.parent.yellow_checkbox.setChecked(self.yellow_checkbox.isChecked())
        
        # Update sensitivity value
        if hasattr(self, 'sensitivity_slider'):
            self.parent.sensitivity_slider.setValue(self.sensitivity_slider.value())
        
        # Store filtering settings in main application
        if hasattr(self, 'skin_tone_filtering'):
            self.parent.skin_tone_filtering_active = self.skin_tone_filtering.isChecked()
        if hasattr(self, 'stability_enhancement'):
            self.parent.stability_enhancement_active = self.stability_enhancement.isChecked()
        if hasattr(self, 'debug_mode'):
            self.parent.debug_mode_active = self.debug_mode.isChecked()
        
        # Set color blindness combo to "Custom Colors" - BLOCKING SIGNALS
        self.parent.color_blindness_combo.blockSignals(True)  # Temporarily block signals
        for i in range(self.parent.color_blindness_combo.count()):
            if self.parent.color_blindness_combo.itemData(i) == "custom":
                self.parent.color_blindness_combo.setCurrentIndex(i)
                break
        self.parent.color_blindness_combo.blockSignals(False)  # Re-enable signals
        
        # Close dialog
        self.accept()
    
    def apply_settings_and_close(self):
        """Old function - for backward compatibility"""
        self.save_settings_and_close()
