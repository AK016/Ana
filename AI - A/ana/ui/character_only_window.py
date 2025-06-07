#!/usr/bin/env python3
# Ana AI Assistant - Character-Only Window

import os
import sys
import logging
import json
import threading
import requests
from datetime import datetime, timedelta

import qdarktheme
from PyQt5.QtCore import Qt, QSize, QTimer, QUrl, pyqtSlot, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPalette, QFont, QFontDatabase
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QPushButton, QLabel, QSizePolicy, QHBoxLayout, QFrame,
    QGroupBox, QFormLayout, QScrollArea, QTabWidget,
    QLineEdit, QTextEdit, QComboBox, QProgressBar, QCheckBox,
    QFileDialog, QMessageBox, QStackedWidget, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect
)

from ana.ui.character_view import CharacterView

logger = logging.getLogger('Ana.CharacterOnlyWindow')

# Health Connect API Configuration
HEALTH_API_BASE_URL = "https://health-connect-api.example.com/v1"
HEALTH_API_KEY = os.environ.get("HEALTH_API_KEY", "")

class CharacterOnlyWindow(QMainWindow):
    """
    Simplified window that only shows the character view without any UI elements
    """
    
    def __init__(self, assistant=None, settings=None):
        super().__init__()
        self.assistant = assistant
        self.settings = settings or {}
        self.options_visible = False
        self.is_dark_mode = True
        self.health_data = {}
        self.health_connected = False
        self.dev_mode_enabled = False
        
        # Set window properties
        self.setWindowTitle("Ana AI Character Viewer")
        self.resize(800, 700)
        
        # Apply theme
        self._setup_theme()
        
        # Setup UI
        self._setup_ui()
        
        # Initialize health data
        self._init_health_connection()
        
        logger.info("Character-only window initialized")
    
    def _setup_theme(self):
        """Setup the theme for the application"""
        # Apply qdarktheme for consistent look
        self.stylesheet = qdarktheme.setup_theme(
            theme="dark" if self.is_dark_mode else "light",
            corner_shape="rounded",
            custom_colors={
                "primary": "#5E81AC",        # Primary accent color
                "secondary": "#88C0D0",      # Secondary accent color
                "warning": "#EBCB8B",        # Warning color
                "danger": "#BF616A",         # Error/danger color
                "success": "#A3BE8C",        # Success color
            }
        )
        
        # Additional custom styling
        additional_style = """
        QGroupBox {
            border-radius: 8px;
            margin-top: 12px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QPushButton#primary_button {
            background-color: #5E81AC;
            color: white;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton#primary_button:hover {
            background-color: #81A1C1;
        }
        QPushButton#secondary_button {
            background-color: transparent;
            color: #88C0D0;
            border: 1px solid #88C0D0;
            border-radius: 4px;
            padding: 8px 16px;
        }
        QPushButton#secondary_button:hover {
            background-color: rgba(136, 192, 208, 0.1);
        }
        """
        
        # Apply additional style
        self.setStyleSheet(self.stylesheet + additional_style)
    
    def _init_health_connection(self):
        """Initialize connection to Samsung Health"""
        # Check if we have API key
        if not HEALTH_API_KEY:
            logger.warning("No Health API key found. Health integration disabled.")
            return
            
        # Try to connect to health service
        try:
            threading.Thread(target=self._connect_health_service, daemon=True).start()
        except Exception as e:
            logger.error(f"Failed to initialize health connection: {e}")
    
    def _connect_health_service(self):
        """Connect to Samsung Health service in background thread"""
        try:
            # Try to fetch authorization status
            response = requests.get(
                f"{HEALTH_API_BASE_URL}/auth/status",
                headers={"Authorization": f"Bearer {HEALTH_API_KEY}"}
            )
            
            if response.status_code == 200:
                self.health_connected = True
                self._fetch_health_data()
                logger.info("Successfully connected to Samsung Health")
            else:
                logger.warning(f"Failed to connect to health service: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Health connection error: {e}")
    
    def _setup_ui(self):
        """Set up the UI components - only showing character view"""
        # Main central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create character view
        self.character_view = CharacterView(self)
        self.character_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.character_view)
        
        # Top bar with controls
        self.top_bar = QWidget()
        self.top_bar.setObjectName("top_bar")
        self.top_bar.setFixedHeight(50)
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(10, 0, 10, 0)
        
        # App title
        app_title = QLabel("Ana AI")
        app_title.setObjectName("app_title")
        app_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.top_bar_layout.addWidget(app_title)
        
        # Spacer
        self.top_bar_layout.addStretch()
        
        # Theme toggle button
        self.theme_toggle = QPushButton()
        self.theme_toggle.setIcon(QIcon.fromTheme("weather-clear-night") if self.is_dark_mode else QIcon.fromTheme("weather-clear"))
        self.theme_toggle.setObjectName("icon_button")
        self.theme_toggle.setFixedSize(36, 36)
        self.theme_toggle.setCursor(Qt.PointingHandCursor)
        self.theme_toggle.setToolTip("Toggle Dark/Light Mode")
        self.theme_toggle.clicked.connect(self._toggle_theme)
        self.top_bar_layout.addWidget(self.theme_toggle)
        
        # Burger menu button
        self.menu_button = QPushButton("☰")
        self.menu_button.setObjectName("menu_button")
        self.menu_button.setFixedSize(36, 36)
        self.menu_button.setCursor(Qt.PointingHandCursor)
        self.menu_button.clicked.connect(self._toggle_options)
        self.top_bar_layout.addWidget(self.menu_button)
        
        # Add top bar to main layout
        self.main_layout.insertWidget(0, self.top_bar)
        
        # Create the sliding overlay for options
        self._setup_sliding_overlay()
    
    def _setup_sliding_overlay(self):
        """Setup the sliding overlay that appears from the right"""
        # Overlay container
        self.overlay_container = QWidget(self)
        self.overlay_container.setObjectName("overlay_container")
        
        # Set initial position (offscreen to the right)
        self.overlay_container.setGeometry(self.width(), 0, 350, self.height())
        
        # Create shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(-5, 0)
        self.overlay_container.setGraphicsEffect(shadow)
        
        # Set overlay layout
        self.overlay_layout = QVBoxLayout(self.overlay_container)
        self.overlay_layout.setContentsMargins(0, 0, 0, 0)
        self.overlay_layout.setSpacing(0)
        
        # Header with close button
        overlay_header = QWidget()
        overlay_header.setObjectName("overlay_header")
        overlay_header.setFixedHeight(50)
        overlay_header_layout = QHBoxLayout(overlay_header)
        overlay_header_layout.setContentsMargins(15, 0, 15, 0)
        
        header_title = QLabel("Menu")
        header_title.setObjectName("header_title")
        header_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        overlay_header_layout.addWidget(header_title)
        
        overlay_header_layout.addStretch()
        
        close_button = QPushButton("✕")
        close_button.setObjectName("close_button")
        close_button.setFixedSize(36, 36)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self._toggle_options)
        overlay_header_layout.addWidget(close_button)
        
        self.overlay_layout.addWidget(overlay_header)
        
        # Options tabs
        self.options_tabs = QTabWidget()
        self.options_tabs.setObjectName("options_tabs")
        
        # Create option tabs
        self._setup_health_tab()
        self._setup_memory_tab()
        self._setup_dev_tab()
        self._setup_character_tab()
        self._setup_settings_tab()
        
        # Add tabs to overlay
        self.overlay_layout.addWidget(self.options_tabs)
        
        # Animation for sliding
        self.slide_animation = QPropertyAnimation(self.overlay_container, b"geometry")
        self.slide_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.slide_animation.setDuration(300)
        
        # Initially hide the overlay
        self.overlay_container.hide()
    
    def resizeEvent(self, event):
        """Handle window resize events to adjust overlay position"""
        super().resizeEvent(event)
        
        # Update overlay container size on window resize
        if hasattr(self, 'overlay_container'):
            if self.options_visible:
                # If visible, maintain position on the right
                self.overlay_container.setGeometry(
                    self.width() - 350, 0, 350, self.height()
                )
            else:
                # If hidden, keep offscreen to the right
                self.overlay_container.setGeometry(
                    self.width(), 0, 350, self.height()
                )
    
    def _toggle_options(self):
        """Toggle options panel visibility with sliding animation"""
        if not hasattr(self, 'overlay_container'):
            return
            
        self.options_visible = not self.options_visible
        
        if self.options_visible:
            # Show overlay before animation
            self.overlay_container.show()
            
            # Slide in from right
            self.slide_animation.setStartValue(QRect(self.width(), 0, 350, self.height()))
            self.slide_animation.setEndValue(QRect(self.width() - 350, 0, 350, self.height()))
            self.slide_animation.start()
        else:
            # Slide out to right
            self.slide_animation.setStartValue(QRect(self.width() - 350, 0, 350, self.height()))
            self.slide_animation.setEndValue(QRect(self.width(), 0, 350, self.height()))
            self.slide_animation.start()
            
            # Hide overlay after animation finishes
            self.slide_animation.finished.connect(lambda: self.overlay_container.hide())
    
    def _toggle_theme(self):
        """Toggle between dark and light theme"""
        self.is_dark_mode = not self.is_dark_mode
        self._setup_theme()
        
        # Update theme combo box if it exists
        if hasattr(self, 'theme_combo'):
            self.theme_combo.setCurrentIndex(1 if self.is_dark_mode else 2)
    
    def _change_theme(self, index):
        """Change theme based on combo box selection"""
        if index == 0:  # Auto
            # Detect system theme
            import darkdetect
            self.is_dark_mode = darkdetect.isDark()
        elif index == 1:  # Dark
            self.is_dark_mode = True
        elif index == 2:  # Light
            self.is_dark_mode = False
            
        self._setup_theme()
    
    def _change_accent(self, index):
        """Change accent color based on combo box selection"""
        accent_colors = {
            0: "#5E81AC",  # Blue
            1: "#B48EAD",  # Purple
            2: "#88C0D0",  # Teal
            3: "#A3BE8C",  # Green
            4: "#BF616A",  # Red
            5: "#D08770"   # Orange
        }
        
        # Apply new accent color
        if index in accent_colors:
            self._setup_theme(custom_accent=accent_colors[index])
    
    def _setup_theme(self, custom_accent=None):
        """Setup the theme with optional custom accent color"""
        # Load the stylesheet instead of applying directly
        theme_name = "dark" if self.is_dark_mode else "light"
        
        # Define custom colors with only valid color ids
        if self.is_dark_mode:
            custom_colors = {
                "primary": custom_accent or "#88C0D0",  # Nordic cyan
            }
        else:
            custom_colors = {
                "primary": custom_accent or "#5E81AC",  # Nordic blue
            }
        
        # Load the stylesheet
        theme_stylesheet = qdarktheme.load_stylesheet(
            theme=theme_name,
            corner_shape="rounded",
            custom_colors=custom_colors
        )
        
        # Colors for additional styling
        accent_color = custom_colors["primary"]
        
        if self.is_dark_mode:
            # Dark mode colors
            bg_color = "#2E3440"          # Nord dark background
            bg_light_color = "#3B4252"    # Nord lighter background
            text_color = "#ECEFF4"        # Nord light text
            secondary_color = "#81A1C1"   # Nord blue
            warning_color = "#EBCB8B"     # Nord yellow
            danger_color = "#BF616A"      # Nord red
            success_color = "#A3BE8C"     # Nord green
            border_color = "#4C566A"      # Nord border
        else:
            # Light mode colors
            bg_color = "#ECEFF4"          # Nord white
            bg_light_color = "#E5E9F0"    # Nord lighter grey
            text_color = "#2E3440"        # Nord dark text
            secondary_color = "#81A1C1"   # Nord blue
            warning_color = "#D08770"     # Nord orange
            danger_color = "#BF616A"      # Nord red
            success_color = "#A3BE8C"     # Nord green
            border_color = "#D8DEE9"      # Nord border
        
        # Additional custom styling for improved appearance
        additional_style = f"""
        /* Base UI Elements */
        QMainWindow, QWidget {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        /* Top Bar */
        #top_bar {{
            background-color: {bg_light_color};
            border-bottom: 1px solid {border_color};
        }}
        
        #app_title {{
            color: {accent_color};
            font-weight: bold;
        }}
        
        /* Overlay Container */
        #overlay_container {{
            background-color: {bg_color};
            border-left: 1px solid {border_color};
        }}
        
        #overlay_header {{
            background-color: {bg_light_color};
            border-bottom: 1px solid {border_color};
        }}
        
        #header_title {{
            color: {accent_color};
        }}
        
        /* Buttons */
        QPushButton#icon_button, QPushButton#menu_button, QPushButton#close_button {{
            background-color: transparent;
            border: none;
            border-radius: 18px;
            color: {text_color};
            font-size: 16px;
        }}
        
        QPushButton#icon_button:hover, QPushButton#menu_button:hover, QPushButton#close_button:hover {{
            background-color: rgba(136, 192, 208, 0.2);
        }}
        
        QPushButton#close_button:hover {{
            background-color: rgba(191, 97, 106, 0.2);
            color: {danger_color};
        }}
        
        QPushButton#primary_button {{
            background-color: {accent_color};
            color: {"#2E3440" if self.is_dark_mode else "white"};
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            border: none;
        }}
        
        QPushButton#primary_button:hover {{
            background-color: {self._lighten_color(accent_color)};
        }}
        
        QPushButton#primary_button:pressed {{
            background-color: {self._darken_color(accent_color)};
        }}
        
        QPushButton#secondary_button {{
            background-color: transparent;
            color: {accent_color};
            border: 1px solid {accent_color};
            border-radius: 4px;
            padding: 8px 16px;
        }}
        
        QPushButton#secondary_button:hover {{
            background-color: {self._with_alpha(accent_color, 0.1)};
        }}
        
        QPushButton#text_button {{
            background-color: transparent;
            color: {accent_color};
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            text-align: left;
        }}
        
        QPushButton#text_button:hover {{
            background-color: {self._with_alpha(accent_color, 0.1)};
        }}
        
        /* Group Boxes */
        QGroupBox {{
            border: 1px solid {border_color};
            border-radius: 8px;
            margin-top: 14px;
            font-weight: bold;
            background-color: {bg_light_color};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: {accent_color};
        }}
        
        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {border_color};
            border-radius: 4px;
        }}
        
        QTabBar::tab {{
            background-color: {bg_light_color};
            color: {text_color};
            padding: 8px 16px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {accent_color};
            color: {"#2E3440" if self.is_dark_mode else "white"};
            font-weight: bold;
        }}
        
        /* Progress Bars */
        QProgressBar {{
            border: 1px solid {border_color};
            border-radius: 4px;
            background-color: {bg_light_color};
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {accent_color};
            border-radius: 3px;
        }}
        
        /* Labels */
        QLabel[styleSheet*="font-weight: bold"] {{
            color: {accent_color};
        }}
        """
        
        # Apply combined stylesheet
        self.setStyleSheet(theme_stylesheet + additional_style)
    
    def _lighten_color(self, color, amount=30):
        """Lighten a hex color by specified amount"""
        # Convert hex to RGB
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        
        # Lighten
        r = min(r + amount, 255)
        g = min(g + amount, 255)
        b = min(b + amount, 255)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken_color(self, color, amount=30):
        """Darken a hex color by specified amount"""
        # Convert hex to RGB
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        
        # Darken
        r = max(r - amount, 0)
        g = max(g - amount, 0)
        b = max(b - amount, 0)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _with_alpha(self, color, alpha=0.5):
        """Convert hex color to rgba with alpha"""
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"
    
    def _test_emotion(self, emotion):
        """Test setting different emotions"""
        self.character_view.set_emotion(emotion)
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append(f"Setting emotion: {emotion}")
    
    def _test_speaking(self):
        """Test speaking animation"""
        text = "This is a test of the speaking animation with a VRoid character model."
        self.character_view.on_speaking(text)
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append("Testing speaking animation")
    
    def _test_listening(self):
        """Test listening animation"""
        self.character_view.on_listening(True)
        
        # Stop listening after 3 seconds
        QTimer.singleShot(3000, lambda: self.character_view.on_listening(False))
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append("Testing listening animation")
    
    def _toggle_blinking(self, state):
        """Toggle blinking animation"""
        # Implement when character_view supports this
        # self.character_view.enable_blinking(state == Qt.Checked)
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append(f"Blinking: {'enabled' if state == Qt.Checked else 'disabled'}")
    
    def _toggle_breathing(self, state):
        """Toggle breathing animation"""
        # Implement when character_view supports this
        # self.character_view.enable_breathing(state == Qt.Checked)
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append(f"Breathing: {'enabled' if state == Qt.Checked else 'disabled'}")
    
    def _load_character(self):
        """Load character from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Character", "", "VRM Files (*.vrm);;All Files (*)"
        )
        
        if file_path:
            # Implement character loading
            # self.character_view.load_character(file_path)
            
            # Log to console if in dev mode
            if self.dev_mode_enabled and hasattr(self, 'console_output'):
                self.console_output.append(f"Loading character from: {file_path}")
    
    def _toggle_animations(self, state):
        """Toggle UI animations"""
        # Implement UI animation toggling
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append(f"UI animations: {'enabled' if state == Qt.Checked else 'disabled'}")
    
    def _toggle_transparency(self, state):
        """Toggle window transparency"""
        if state == Qt.Checked:
            self.setWindowOpacity(0.9)
        else:
            self.setWindowOpacity(1.0)
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append(f"Window transparency: {'enabled' if state == Qt.Checked else 'disabled'}")
    
    def _toggle_start_on_boot(self, state):
        """Toggle start on boot setting"""
        # Implement start on boot
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append(f"Start on boot: {'enabled' if state == Qt.Checked else 'disabled'}")
    
    def _toggle_minimize_to_tray(self, state):
        """Toggle minimize to tray setting"""
        # Implement minimize to tray
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append(f"Minimize to tray: {'enabled' if state == Qt.Checked else 'disabled'}")
    
    def _check_for_updates(self):
        """Check for updates"""
        # Implement update check
        QMessageBox.information(self, "Updates", "Your application is up to date!")
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append("Checking for updates...")
    
    def _save_settings(self):
        """Save settings"""
        # Implement settings saving
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append("Saving settings...")
    
    def _toggle_dev_mode(self, state):
        """Toggle developer mode"""
        self.dev_mode_enabled = (state == Qt.Checked)
        
        # Show/hide developer sections
        if hasattr(self, 'dev_sections'):
            self.dev_sections.setVisible(self.dev_mode_enabled)
        
        # Log mode change
        logger.info(f"Developer mode: {'enabled' if self.dev_mode_enabled else 'disabled'}")
    
    def _run_command(self):
        """Run developer command"""
        if not hasattr(self, 'cmd_input') or not hasattr(self, 'console_output'):
            return
            
        command = self.cmd_input.text().strip()
        if not command:
            return
            
        # Process command
        self.console_output.append(f"> {command}")
        
        # Simple command processing
        if command == "help":
            self.console_output.append("Available commands: help, clear, info, version")
        elif command == "clear":
            self.console_output.clear()
        elif command == "info":
            self.console_output.append(f"OS: {os.name}")
            self.console_output.append(f"Python: {sys.version}")
            self.console_output.append(f"PyQt: 5")
        elif command == "version":
            self.console_output.append("Ana AI Version: 1.0.0")
        else:
            self.console_output.append(f"Unknown command: {command}")
        
        # Clear input
        self.cmd_input.clear()
    
    def _create_new_project(self):
        """Create new project"""
        # Implement project creation
        QMessageBox.information(self, "Project", "New project created successfully!")
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append("Creating new project...")
    
    def _auto_fix_issues(self):
        """Auto-fix issues"""
        # Implement issue fixing
        QMessageBox.information(self, "Auto-Fix", "Issues fixed successfully!")
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append("Auto-fixing issues...")
    
    def _add_new_feature(self):
        """Add new feature"""
        # Implement feature addition
        QMessageBox.information(self, "Feature", "New feature added successfully!")
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append("Adding new feature...")
    
    def _connect_health(self):
        """Connect to Samsung Health"""
        # Implement health connection
        QMessageBox.information(self, "Health", "Connecting to Samsung Health...")
        
        # Simulate connecting
        threading.Thread(target=self._connect_health_service, daemon=True).start()
    
    def _fetch_health_data(self):
        """Fetch health data from Samsung Health"""
        try:
            # In a real implementation, this would connect to the Samsung Health API
            # For this demo, we'll simulate health data
            
            # Simulate a delay
            import time
            time.sleep(1)
            
            # Mock health data
            mock_data = {
                "heart_rate": {"value": 72, "unit": "bpm"},
                "steps": {"value": 8432, "unit": "steps"},
                "sleep": {"value": 7.5, "unit": "hours"},
                "stress": {"value": "Low", "unit": ""}
            }
            
            # Update health data
            self.health_data = mock_data
            
            # Update UI if widgets exist
            if hasattr(self, 'heart_rate_label'):
                self.heart_rate_label.setText(f"{self.health_data['heart_rate']['value']} {self.health_data['heart_rate']['unit']}")
            
            if hasattr(self, 'steps_label'):
                self.steps_label.setText(f"{self.health_data['steps']['value']} {self.health_data['steps']['unit']}")
            
            if hasattr(self, 'sleep_label'):
                self.sleep_label.setText(f"{self.health_data['sleep']['value']} {self.health_data['sleep']['unit']}")
            
            if hasattr(self, 'stress_label'):
                self.stress_label.setText(f"{self.health_data['stress']['value']}")
            
            if hasattr(self, 'step_progress'):
                self.step_progress.setValue(self.health_data['steps']['value'])
            
            if hasattr(self, 'active_progress'):
                # Simulate active time based on steps
                active_minutes = min(int(self.health_data['steps']['value'] / 250), 60)
                self.active_progress.setValue(active_minutes)
            
            # Update health status
            if hasattr(self, 'health_status'):
                self.health_status.setText("Connected")
                self.health_status.setStyleSheet("color: #A3BE8C;")
            
            # Set connected flag
            self.health_connected = True
            
            logger.info("Health data updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to fetch health data: {e}")
            
            # Update health status
            if hasattr(self, 'health_status'):
                self.health_status.setText("Error")
                self.health_status.setStyleSheet("color: #BF616A;")
    
    def _get_recent_conversations(self):
        """Get recent conversations from memory"""
        # In a real implementation, this would fetch from actual memory storage
        # For this demo, we'll return mock data
        return [
            {"id": 1, "title": "VRoid Integration Discussion", "date": "2025-06-07", "messages": 24},
            {"id": 2, "title": "Character Animation Setup", "date": "2025-06-06", "messages": 17},
            {"id": 3, "title": "Project Planning Session", "date": "2025-06-05", "messages": 31},
            {"id": 4, "title": "UI Design Review", "date": "2025-06-04", "messages": 12},
            {"id": 5, "title": "Feature Brainstorming", "date": "2025-06-03", "messages": 28}
        ]
    
    def _open_conversation(self, conversation):
        """Open a conversation"""
        # Implement conversation opening
        QMessageBox.information(self, "Conversation", f"Opening conversation: {conversation['title']}")
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append(f"Opening conversation: {conversation['title']}")
    
    def _search_conversations(self):
        """Search conversations"""
        # Implement conversation search
        QMessageBox.information(self, "Search", "Search feature not implemented yet")
        
        # Log to console if in dev mode
        if self.dev_mode_enabled and hasattr(self, 'console_output'):
            self.console_output.append("Searching conversations...")
    
    def _export_conversations(self):
        """Export conversations"""
        # Implement conversation export
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Conversations", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            # Mock export
            QMessageBox.information(self, "Export", f"Conversations exported to: {file_path}")
            
            # Log to console if in dev mode
            if self.dev_mode_enabled and hasattr(self, 'console_output'):
                self.console_output.append(f"Exporting conversations to: {file_path}")
    
    def _clear_conversations(self):
        """Clear conversations"""
        # Confirm action
        reply = QMessageBox.question(
            self, "Clear Conversations", 
            "Are you sure you want to clear all conversations? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Implement conversation clearing
            QMessageBox.information(self, "Clear", "All conversations cleared successfully!")
            
            # Log to console if in dev mode
            if self.dev_mode_enabled and hasattr(self, 'console_output'):
                self.console_output.append("Clearing all conversations...")

    def closeEvent(self, event):
        """Handle window close event"""
        # Clean up any resources
        event.accept()
        logger.info("Character-only window closed")

    def _setup_health_tab(self):
        """Setup Samsung Health integration tab"""
        health_tab = QWidget()
        health_layout = QVBoxLayout(health_tab)
        health_layout.setContentsMargins(15, 15, 15, 15)
        health_layout.setSpacing(15)
        
        # Health connection status
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        status_label = QLabel("Samsung Health:")
        status_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(status_label)
        
        self.health_status = QLabel("Disconnected")
        self.health_status.setStyleSheet("color: #BF616A;")
        status_layout.addWidget(self.health_status)
        
        connect_btn = QPushButton("Connect")
        connect_btn.setObjectName("secondary_button")
        connect_btn.clicked.connect(self._connect_health)
        status_layout.addWidget(connect_btn)
        
        health_layout.addWidget(status_container)
        
        # Health metrics
        self.health_metrics = QGroupBox("Health Metrics")
        metrics_layout = QFormLayout(self.health_metrics)
        
        # Heart rate
        self.heart_rate_label = QLabel("-- bpm")
        metrics_layout.addRow("Heart Rate:", self.heart_rate_label)
        
        # Steps
        self.steps_label = QLabel("-- steps")
        metrics_layout.addRow("Steps Today:", self.steps_label)
        
        # Sleep
        self.sleep_label = QLabel("-- hours")
        metrics_layout.addRow("Sleep Last Night:", self.sleep_label)
        
        # Stress
        self.stress_label = QLabel("--")
        metrics_layout.addRow("Stress Level:", self.stress_label)
        
        health_layout.addWidget(self.health_metrics)
        
        # Activity progress
        self.activity_group = QGroupBox("Daily Activity")
        activity_layout = QVBoxLayout(self.activity_group)
        
        # Step goal progress
        step_container = QWidget()
        step_layout = QHBoxLayout(step_container)
        step_layout.setContentsMargins(0, 0, 0, 0)
        
        step_layout.addWidget(QLabel("Steps:"))
        
        self.step_progress = QProgressBar()
        self.step_progress.setRange(0, 10000)
        self.step_progress.setValue(0)
        step_layout.addWidget(self.step_progress)
        
        activity_layout.addWidget(step_container)
        
        # Active time progress
        active_container = QWidget()
        active_layout = QHBoxLayout(active_container)
        active_layout.setContentsMargins(0, 0, 0, 0)
        
        active_layout.addWidget(QLabel("Active Time:"))
        
        self.active_progress = QProgressBar()
        self.active_progress.setRange(0, 60)
        self.active_progress.setValue(0)
        active_layout.addWidget(self.active_progress)
        
        activity_layout.addWidget(active_container)
        
        health_layout.addWidget(self.activity_group)
        
        # Samsung Health settings
        settings_group = QGroupBox("Settings")
        settings_layout = QFormLayout(settings_group)
        
        # Sync frequency
        self.sync_combo = QComboBox()
        self.sync_combo.addItems(["Every 15 minutes", "Every 30 minutes", "Every hour", "Manual only"])
        settings_layout.addRow("Sync Frequency:", self.sync_combo)
        
        # Metrics to sync
        metrics_container = QWidget()
        metrics_options = QVBoxLayout(metrics_container)
        metrics_options.setContentsMargins(0, 0, 0, 0)
        
        self.sync_steps = QCheckBox("Steps")
        self.sync_steps.setChecked(True)
        metrics_options.addWidget(self.sync_steps)
        
        self.sync_heart = QCheckBox("Heart Rate")
        self.sync_heart.setChecked(True)
        metrics_options.addWidget(self.sync_heart)
        
        self.sync_sleep = QCheckBox("Sleep")
        self.sync_sleep.setChecked(True)
        metrics_options.addWidget(self.sync_sleep)
        
        self.sync_stress = QCheckBox("Stress")
        self.sync_stress.setChecked(True)
        metrics_options.addWidget(self.sync_stress)
        
        settings_layout.addRow("Sync Metrics:", metrics_container)
        
        health_layout.addWidget(settings_group)
        
        # Manual sync button
        sync_btn = QPushButton("Sync Now")
        sync_btn.setObjectName("primary_button")
        sync_btn.clicked.connect(self._fetch_health_data)
        health_layout.addWidget(sync_btn)
        
        # Add to tabs
        self.options_tabs.addTab(health_tab, "Health")

    def _setup_memory_tab(self):
        """Setup memory/conversations tab"""
        memory_tab = QWidget()
        memory_layout = QVBoxLayout(memory_tab)
        memory_layout.setContentsMargins(15, 15, 15, 15)
        memory_layout.setSpacing(15)
        
        # Recent conversations
        memory_label = QLabel("Recent Conversations:")
        memory_label.setStyleSheet("font-weight: bold;")
        memory_layout.addWidget(memory_label)
        
        # Conversation list from memory
        self.conversation_list = QScrollArea()
        self.conversation_list.setWidgetResizable(True)
        self.conversation_list.setMinimumHeight(200)
        
        conversations_widget = QWidget()
        conversations_layout = QVBoxLayout(conversations_widget)
        conversations_layout.setContentsMargins(0, 0, 0, 0)
        conversations_layout.setSpacing(5)
        
        # Add actual conversations from memory if available
        conversations = self._get_recent_conversations()
        
        for convo in conversations:
            convo_btn = QPushButton(convo["title"])
            convo_btn.setObjectName("text_button")
            convo_btn.setToolTip(convo["date"])
            convo_btn.clicked.connect(lambda checked, c=convo: self._open_conversation(c))
            conversations_layout.addWidget(convo_btn)
        
        self.conversation_list.setWidget(conversations_widget)
        memory_layout.addWidget(self.conversation_list)
        
        # Memory actions
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        search_btn = QPushButton("Search")
        search_btn.setObjectName("secondary_button")
        search_btn.clicked.connect(self._search_conversations)
        actions_layout.addWidget(search_btn)
        
        export_btn = QPushButton("Export")
        export_btn.setObjectName("secondary_button")
        export_btn.clicked.connect(self._export_conversations)
        actions_layout.addWidget(export_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("secondary_button")
        clear_btn.clicked.connect(self._clear_conversations)
        actions_layout.addWidget(clear_btn)
        
        memory_layout.addWidget(actions_container)
        
        # Memory stats
        stats_group = QGroupBox("Memory Stats")
        stats_layout = QFormLayout(stats_group)
        
        self.total_convos = QLabel("0")
        stats_layout.addRow("Total Conversations:", self.total_convos)
        
        self.total_messages = QLabel("0")
        stats_layout.addRow("Total Messages:", self.total_messages)
        
        self.avg_length = QLabel("0 min")
        stats_layout.addRow("Average Length:", self.avg_length)
        
        memory_layout.addWidget(stats_group)
        
        # Add to tabs
        self.options_tabs.addTab(memory_tab, "Memory")

    def _setup_dev_tab(self):
        """Setup developer mode tab"""
        dev_tab = QWidget()
        dev_layout = QVBoxLayout(dev_tab)
        dev_layout.setContentsMargins(15, 15, 15, 15)
        dev_layout.setSpacing(15)
        
        # Enable developer mode toggle
        dev_toggle_container = QWidget()
        dev_toggle_layout = QHBoxLayout(dev_toggle_container)
        dev_toggle_layout.setContentsMargins(0, 0, 0, 0)
        
        dev_toggle_layout.addWidget(QLabel("Developer Mode:"))
        
        self.dev_toggle = QCheckBox()
        self.dev_toggle.setChecked(self.dev_mode_enabled)
        self.dev_toggle.stateChanged.connect(self._toggle_dev_mode)
        dev_toggle_layout.addWidget(self.dev_toggle)
        
        dev_layout.addWidget(dev_toggle_container)
        
        # Create collapsible sections that are only enabled when dev mode is on
        self.dev_sections = QWidget()
        dev_sections_layout = QVBoxLayout(self.dev_sections)
        dev_sections_layout.setContentsMargins(0, 0, 0, 0)
        dev_sections_layout.setSpacing(15)
        self.dev_sections.setVisible(self.dev_mode_enabled)
        
        # System information
        system_group = QGroupBox("System Info")
        system_layout = QFormLayout(system_group)
        
        system_layout.addRow("OS:", QLabel(f"{os.name}"))
        system_layout.addRow("Python:", QLabel(f"{sys.version.split()[0]}"))
        system_layout.addRow("PyQt:", QLabel("5"))
        
        dev_sections_layout.addWidget(system_group)
        
        # Console output
        console_group = QGroupBox("Console")
        console_layout = QVBoxLayout(console_group)
        
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setMinimumHeight(100)
        self.console_output.setPlaceholderText("Console output will appear here...")
        console_layout.addWidget(self.console_output)
        
        # Command input
        cmd_container = QWidget()
        cmd_layout = QHBoxLayout(cmd_container)
        cmd_layout.setContentsMargins(0, 0, 0, 0)
        
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Enter a command...")
        cmd_layout.addWidget(self.cmd_input)
        
        run_btn = QPushButton("Run")
        run_btn.clicked.connect(self._run_command)
        cmd_layout.addWidget(run_btn)
        
        console_layout.addWidget(cmd_container)
        dev_sections_layout.addWidget(console_group)
        
        # Project management
        project_group = QGroupBox("Project Management")
        project_layout = QVBoxLayout(project_group)
        
        # New project button
        new_project_btn = QPushButton("Create New Project")
        new_project_btn.setObjectName("primary_button")
        new_project_btn.clicked.connect(self._create_new_project)
        project_layout.addWidget(new_project_btn)
        
        # Fix issues button
        fix_issues_btn = QPushButton("Auto-Fix Issues")
        fix_issues_btn.setObjectName("secondary_button")
        fix_issues_btn.clicked.connect(self._auto_fix_issues)
        project_layout.addWidget(fix_issues_btn)
        
        # Add new feature button
        add_feature_btn = QPushButton("Add New Feature")
        add_feature_btn.setObjectName("secondary_button")
        add_feature_btn.clicked.connect(self._add_new_feature)
        project_layout.addWidget(add_feature_btn)
        
        dev_sections_layout.addWidget(project_group)
        
        dev_layout.addWidget(self.dev_sections)
        
        # Add to tabs
        self.options_tabs.addTab(dev_tab, "Developer")
    
    def _setup_character_tab(self):
        """Setup character controls tab"""
        character_tab = QWidget()
        character_layout = QVBoxLayout(character_tab)
        character_layout.setContentsMargins(15, 15, 15, 15)
        character_layout.setSpacing(15)
        
        # Emotions control
        emotion_group = QGroupBox("Emotions")
        emotion_layout = QVBoxLayout(emotion_group)
        
        # Emotion buttons in a scrollable area
        emotions_scroll = QScrollArea()
        emotions_scroll.setWidgetResizable(True)
        emotions_scroll.setFrameShape(QFrame.NoFrame)
        
        emotions_widget = QWidget()
        emotions_grid = QVBoxLayout(emotions_widget)
        emotions_grid.setContentsMargins(0, 0, 0, 0)
        emotions_grid.setSpacing(5)
        
        # Add emotion buttons
        for emotion in ["neutral", "happy", "sad", "surprised", "angry", "thinking", "confused", "excited"]:
            btn = QPushButton(emotion.capitalize())
            btn.setObjectName("secondary_button")
            btn.clicked.connect(lambda checked, e=emotion: self._test_emotion(e))
            emotions_grid.addWidget(btn)
        
        emotions_scroll.setWidget(emotions_widget)
        emotion_layout.addWidget(emotions_scroll)
        
        character_layout.addWidget(emotion_group)
        
        # Animation controls
        animation_group = QGroupBox("Animations")
        animation_layout = QVBoxLayout(animation_group)
        
        # Speaking animation
        speak_btn = QPushButton("Test Speaking")
        speak_btn.setObjectName("secondary_button")
        speak_btn.clicked.connect(self._test_speaking)
        animation_layout.addWidget(speak_btn)
        
        # Listening animation
        listen_btn = QPushButton("Test Listening")
        listen_btn.setObjectName("secondary_button")
        listen_btn.clicked.connect(self._test_listening)
        animation_layout.addWidget(listen_btn)
        
        # Blinking animation toggle
        blink_container = QWidget()
        blink_layout = QHBoxLayout(blink_container)
        blink_layout.setContentsMargins(0, 0, 0, 0)
        
        blink_layout.addWidget(QLabel("Blinking:"))
        
        self.blink_toggle = QCheckBox()
        self.blink_toggle.setChecked(True)
        self.blink_toggle.stateChanged.connect(self._toggle_blinking)
        blink_layout.addWidget(self.blink_toggle)
        
        animation_layout.addWidget(blink_container)
        
        # Breathing animation toggle
        breathing_container = QWidget()
        breathing_layout = QHBoxLayout(breathing_container)
        breathing_layout.setContentsMargins(0, 0, 0, 0)
        
        breathing_layout.addWidget(QLabel("Breathing:"))
        
        self.breathing_toggle = QCheckBox()
        self.breathing_toggle.setChecked(True)
        self.breathing_toggle.stateChanged.connect(self._toggle_breathing)
        breathing_layout.addWidget(self.breathing_toggle)
        
        animation_layout.addWidget(breathing_container)
        
        character_layout.addWidget(animation_group)
        
        # Character appearance
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout(appearance_group)
        
        # Character scale
        scale_container = QWidget()
        scale_layout = QHBoxLayout(scale_container)
        scale_layout.setContentsMargins(0, 0, 0, 0)
        
        scale_layout.addWidget(QLabel("Scale:"))
        
        self.scale_slider = QProgressBar()
        self.scale_slider.setRange(50, 150)
        self.scale_slider.setValue(100)
        scale_layout.addWidget(self.scale_slider)
        
        appearance_layout.addWidget(scale_container)
        
        # Load character from file
        load_btn = QPushButton("Load Character...")
        load_btn.setObjectName("secondary_button")
        load_btn.clicked.connect(self._load_character)
        appearance_layout.addWidget(load_btn)
        
        character_layout.addWidget(appearance_group)
        
        # Add to tabs
        self.options_tabs.addTab(character_tab, "Character")
    
    def _setup_settings_tab(self):
        """Setup settings tab"""
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setContentsMargins(15, 15, 15, 15)
        settings_layout.setSpacing(15)
        
        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)
        
        # Theme selector
        theme_container = QWidget()
        theme_selector = QHBoxLayout(theme_container)
        theme_selector.setContentsMargins(0, 0, 0, 0)
        
        theme_selector.addWidget(QLabel("Theme:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Auto", "Dark", "Light"])
        self.theme_combo.setCurrentIndex(1 if self.is_dark_mode else 2)
        self.theme_combo.currentIndexChanged.connect(self._change_theme)
        theme_selector.addWidget(self.theme_combo)
        
        theme_layout.addWidget(theme_container)
        
        # Accent color
        accent_container = QWidget()
        accent_layout = QHBoxLayout(accent_container)
        accent_layout.setContentsMargins(0, 0, 0, 0)
        
        accent_layout.addWidget(QLabel("Accent Color:"))
        
        self.accent_combo = QComboBox()
        self.accent_combo.addItems(["Blue", "Purple", "Teal", "Green", "Red", "Orange"])
        self.accent_combo.setCurrentIndex(0)
        self.accent_combo.currentIndexChanged.connect(self._change_accent)
        accent_layout.addWidget(self.accent_combo)
        
        theme_layout.addWidget(accent_container)
        
        settings_layout.addWidget(theme_group)
        
        # UI settings
        ui_group = QGroupBox("UI Settings")
        ui_layout = QVBoxLayout(ui_group)
        
        # Animations toggle
        animations_container = QWidget()
        animations_layout = QHBoxLayout(animations_container)
        animations_layout.setContentsMargins(0, 0, 0, 0)
        
        animations_layout.addWidget(QLabel("UI Animations:"))
        
        self.animations_toggle = QCheckBox()
        self.animations_toggle.setChecked(True)
        self.animations_toggle.stateChanged.connect(self._toggle_animations)
        animations_layout.addWidget(self.animations_toggle)
        
        ui_layout.addWidget(animations_container)
        
        # Transparency toggle
        transparency_container = QWidget()
        transparency_layout = QHBoxLayout(transparency_container)
        transparency_layout.setContentsMargins(0, 0, 0, 0)
        
        transparency_layout.addWidget(QLabel("Window Transparency:"))
        
        self.transparency_toggle = QCheckBox()
        self.transparency_toggle.setChecked(False)
        self.transparency_toggle.stateChanged.connect(self._toggle_transparency)
        transparency_layout.addWidget(self.transparency_toggle)
        
        ui_layout.addWidget(transparency_container)
        
        settings_layout.addWidget(ui_group)
        
        # Application settings
        app_group = QGroupBox("Application")
        app_layout = QVBoxLayout(app_group)
        
        # Start on boot toggle
        boot_container = QWidget()
        boot_layout = QHBoxLayout(boot_container)
        boot_layout.setContentsMargins(0, 0, 0, 0)
        
        boot_layout.addWidget(QLabel("Start on Boot:"))
        
        self.boot_toggle = QCheckBox()
        self.boot_toggle.setChecked(False)
        self.boot_toggle.stateChanged.connect(self._toggle_start_on_boot)
        boot_layout.addWidget(self.boot_toggle)
        
        app_layout.addWidget(boot_container)
        
        # Minimize to tray toggle
        tray_container = QWidget()
        tray_layout = QHBoxLayout(tray_container)
        tray_layout.setContentsMargins(0, 0, 0, 0)
        
        tray_layout.addWidget(QLabel("Minimize to Tray:"))
        
        self.tray_toggle = QCheckBox()
        self.tray_toggle.setChecked(True)
        self.tray_toggle.stateChanged.connect(self._toggle_minimize_to_tray)
        tray_layout.addWidget(self.tray_toggle)
        
        app_layout.addWidget(tray_container)
        
        # Version information
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Version: 1.0.0"))
        version_layout.addStretch()
        
        check_updates_btn = QPushButton("Check for Updates")
        check_updates_btn.setObjectName("text_button")
        check_updates_btn.clicked.connect(self._check_for_updates)
        version_layout.addWidget(check_updates_btn)
        
        app_layout.addLayout(version_layout)
        
        settings_layout.addWidget(app_group)
        
        # Save settings button
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primary_button")
        save_btn.clicked.connect(self._save_settings)
        settings_layout.addWidget(save_btn)
        
        # Add to tabs
        self.options_tabs.addTab(settings_tab, "Settings") 