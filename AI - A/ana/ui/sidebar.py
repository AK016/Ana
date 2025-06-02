#!/usr/bin/env python3
# Ana AI Assistant - Sidebar UI Component

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                            QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont

import os

class SidebarButton(QPushButton):
    """Custom button for sidebar with cyberpunk styling"""
    
    def __init__(self, text, icon_path=None, parent=None, accent_color="#00FFCC"):
        super().__init__(text, parent)
        
        self.accent_color = accent_color
        self.setCheckable(True)
        self.setFlat(True)
        
        # Set fixed height
        self.setFixedHeight(50)
        
        # Set icon if provided
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24))
        
        # Set alignment and style
        self.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 10px 15px;
                border: none;
                border-left: 3px solid transparent;
                background-color: transparent;
                color: #aaaacc;
                font-size: 14px;
            }}
            
            QPushButton:hover {{
                background-color: #202040;
                color: #ffffff;
                border-left: 3px solid {self.accent_color};
            }}
            
            QPushButton:checked {{
                background-color: #202040;
                color: {self.accent_color};
                border-left: 3px solid {self.accent_color};
            }}
        """)

class Sidebar(QWidget):
    """Sidebar navigation component with cyberpunk aesthetic"""
    
    # Signal emitted when a button is clicked
    button_clicked = pyqtSignal(str)
    
    def __init__(self, theme="cyberpunk", accent_color="#00FFCC", parent=None):
        super().__init__(parent)
        
        self.theme = theme
        self.accent_color = accent_color
        self.buttons = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the sidebar UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo and title
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        
        # Logo label
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "..", "resources", "images", "ana_logo.png")
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            # Fallback if logo doesn't exist
            logo_label.setText("ANA")
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setStyleSheet(f"color: {self.accent_color}; font-size: 24px; font-weight: bold;")
        
        title_layout.addWidget(logo_label)
        
        # Title label
        title_label = QLabel("AI ASSISTANT")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {self.accent_color}; font-size: 14px; font-weight: bold;")
        title_layout.addWidget(title_label)
        
        layout.addWidget(title_widget)
        
        # Add separator
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: #333366;")
        layout.addWidget(separator)
        
        # Navigation buttons
        self._add_button("home", "Home", "home.png", layout)
        self._add_button("tasks", "Tasks", "tasks.png", layout)
        self._add_button("memory", "Memory", "memory.png", layout)
        self._add_button("calendar", "Calendar", "calendar.png", layout)
        self._add_button("health", "Health", "health.png", layout)
        self._add_button("music", "Music", "music.png", layout)
        
        # Flexible space
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Developer mode button
        self._add_button("developer", "Developer Mode", "developer.png", layout)
        
        # Version info
        version_label = QLabel("v0.5.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #555577; font-size: 11px; padding: 5px;")
        layout.addWidget(version_label)
        
        # Set the default active button
        if "home" in self.buttons:
            self.buttons["home"].setChecked(True)
        
        # Apply cyberpunk styling to the sidebar
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #151525;
            }}
        """)
    
    def _add_button(self, button_id, text, icon_name, layout):
        """Add a button to the sidebar"""
        # Construct icon path
        icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "images", "icons", icon_name)
        
        # Create button
        button = SidebarButton(text, icon_path, self, self.accent_color)
        
        # Connect signal
        button.clicked.connect(lambda: self._on_button_click(button_id))
        
        # Add to layout
        layout.addWidget(button)
        
        # Store in buttons dictionary
        self.buttons[button_id] = button
    
    def _on_button_click(self, button_id):
        """Handle button click"""
        # Uncheck all other buttons
        for bid, button in self.buttons.items():
            if bid != button_id:
                button.setChecked(False)
        
        # Ensure the clicked button is checked
        self.buttons[button_id].setChecked(True)
        
        # Emit signal with button ID
        self.button_clicked.emit(button_id) 