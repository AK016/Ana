#!/usr/bin/env python3
# Ana AI Assistant - UI Controller Module

import os
import sys
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QStackedWidget,
                            QSplitter, QFrame)
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor

# Import UI components
from .character_view import CharacterView
from .chat_widget import ChatWidget
from .sidebar import Sidebar
from .health_widget import HealthWidget

logger = logging.getLogger('Ana.UIController')

class UIController:
    """Controls the main UI for Ana AI Assistant"""
    
    def __init__(self, ana_core, settings):
        """Initialize UI controller with Ana core"""
        self.ana_core = ana_core
        self.settings = settings
        self.app = None
        self.main_window = None
        
        # Create QApplication instance if not already created
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        
        # Style settings
        self.ui_settings = settings.get("ui", {})
        self.theme = self.ui_settings.get("theme", "cyberpunk")
        self.accent_color = self.ui_settings.get("accent_color", "#00FFCC")
        
        # Create main window
        self.setup_ui()
        
        logger.info("UI Controller initialized")
    
    def setup_ui(self):
        """Set up the main UI components"""
        # Create main window
        self.main_window = QMainWindow()
        self.main_window.setWindowTitle("Ana AI Assistant")
        self.main_window.setMinimumSize(1200, 800)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "images", "ana_icon.png")
        if os.path.exists(icon_path):
            self.main_window.setWindowIcon(QIcon(icon_path))
        
        # Create central widget
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = Sidebar(self.theme, self.accent_color)
        self.sidebar.setFixedWidth(200)
        self.sidebar.button_clicked.connect(self.handle_sidebar_button)
        main_layout.addWidget(self.sidebar)
        
        # Create content area
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create stacked widget for different content pages
        self.stacked_widget = QStackedWidget()
        
        # Create pages
        self.setup_pages()
        
        # Add stacked widget to content layout
        content_layout.addWidget(self.stacked_widget)
        
        # Add content area to main layout
        main_layout.addWidget(content_area)
        
        # Set the cyberpunk theme stylesheet
        self.apply_theme()
        
        logger.info("UI setup completed")
    
    def setup_pages(self):
        """Set up the different content pages"""
        # Main chat page with character visualization
        chat_page = QWidget()
        chat_layout = QVBoxLayout(chat_page)
        
        # Create character view
        self.character_view = CharacterView()
        chat_layout.addWidget(self.character_view, 2)
        
        # Create chat widget
        self.chat_widget = ChatWidget()
        self.chat_widget.message_sent.connect(self.handle_user_message)
        chat_layout.addWidget(self.chat_widget, 1)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(chat_page)
        
        # Tasks page
        tasks_page = QWidget()
        self.stacked_widget.addWidget(tasks_page)
        
        # Memory page
        memory_page = QWidget()
        self.stacked_widget.addWidget(memory_page)
        
        # Calendar page
        calendar_page = QWidget()
        self.stacked_widget.addWidget(calendar_page)
        
        # Health page
        health_page = QWidget()
        health_layout = QVBoxLayout(health_page)
        
        # Create health widget
        self.health_widget = HealthWidget()
        self.health_widget.refresh_requested.connect(self.refresh_health_data)
        health_layout.addWidget(self.health_widget)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(health_page)
        
        # Music page
        music_page = QWidget()
        self.stacked_widget.addWidget(music_page)
        
        # Developer mode page
        dev_page = QWidget()
        self.stacked_widget.addWidget(dev_page)
    
    def apply_theme(self):
        """Apply the selected theme to the UI"""
        if self.theme == "cyberpunk":
            # Cyberpunk theme with neon accents
            self.main_window.setStyleSheet(f"""
                QMainWindow, QWidget {{
                    background-color: #121220;
                    color: #E0E0E0;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }}
                
                QSplitter::handle {{
                    background-color: {self.accent_color};
                    width: 1px;
                }}
                
                QPushButton {{
                    background-color: #1A1A2E;
                    border: 1px solid {self.accent_color};
                    border-radius: 2px;
                    color: {self.accent_color};
                    padding: 5px 10px;
                }}
                
                QPushButton:hover {{
                    background-color: #252538;
                    border: 1px solid #00FFEE;
                    color: #00FFEE;
                }}
                
                QPushButton:pressed {{
                    background-color: #2A2A40;
                    border: 1px solid #00DDCC;
                }}
                
                QLineEdit, QTextEdit {{
                    background-color: #1A1A2E;
                    border: 1px solid #333355;
                    border-radius: 2px;
                    color: #E0E0E0;
                    padding: 5px;
                }}
                
                QLineEdit:focus, QTextEdit:focus {{
                    border: 1px solid {self.accent_color};
                }}
                
                QScrollBar:vertical {{
                    border: none;
                    background: #1A1A2E;
                    width: 8px;
                    margin: 0px;
                }}
                
                QScrollBar::handle:vertical {{
                    background: #333355;
                    min-height: 20px;
                    border-radius: 4px;
                }}
                
                QScrollBar::handle:vertical:hover {{
                    background: {self.accent_color};
                }}
                
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
                
                QScrollBar:horizontal {{
                    border: none;
                    background: #1A1A2E;
                    height: 8px;
                    margin: 0px;
                }}
                
                QScrollBar::handle:horizontal {{
                    background: #333355;
                    min-width: 20px;
                    border-radius: 4px;
                }}
                
                QScrollBar::handle:horizontal:hover {{
                    background: {self.accent_color};
                }}
                
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                    width: 0px;
                }}
            """)
        else:
            # Default theme (can add more themes later)
            pass
    
    def start(self):
        """Start the UI"""
        # Show the main window
        self.main_window.show()
        
        # Initialize health data
        self.refresh_health_data()
        
        logger.info("UI started")
        
        # Note: We don't run app.exec_() here as it should be run by the main thread
    
    def stop(self):
        """Stop the UI"""
        # Close the main window
        if self.main_window:
            self.main_window.close()
            
        logger.info("UI stopped")
    
    def run(self):
        """Run the UI event loop (only for standalone testing)"""
        if self.app and self.main_window:
            return self.app.exec_()
    
    @pyqtSlot(str)
    def handle_sidebar_button(self, button_id):
        """Handle sidebar button clicks"""
        logger.info(f"Sidebar button clicked: {button_id}")
        
        # Map button IDs to stacked widget indices
        button_map = {
            "home": 0,
            "tasks": 1,
            "memory": 2,
            "calendar": 3,
            "health": 4,
            "music": 5,
            "developer": 6
        }
        
        if button_id in button_map:
            self.stacked_widget.setCurrentIndex(button_map[button_id])
            
            # Special case for health button
            if button_id == "health":
                self.refresh_health_data()
    
    @pyqtSlot(str)
    def handle_user_message(self, message):
        """Handle user message from chat widget"""
        logger.info(f"User message: {message}")
        
        # Process message with Ana core
        response = self.ana_core.process_command(message)
        
        # Add response to chat
        self.chat_widget.add_message("Ana", response)
        
        # Trigger character animation for speaking
        self.character_view.animate_speaking(len(response))
    
    def update_state(self, state):
        """Update UI with current state"""
        # Update character state if needed
        if "emotion" in state:
            self.character_view.set_emotion(state["emotion"])
        
        # Update other UI elements based on state
        # ...
    
    @pyqtSlot()
    def refresh_health_data(self):
        """Refresh health data from Ana core"""
        try:
            # Get health summary from Ana core
            health_data = self.ana_core.get_health_data("summary")
            
            # Add interpretation if not already present
            if "interpretation" not in health_data and hasattr(self.ana_core.health_integration, "interpret_health_data"):
                health_data["interpretation"] = self.ana_core.health_integration.interpret_health_data(health_data)
            
            # Update health widget with data
            self.health_widget.update_data(health_data)
            
            logger.info("Health data refreshed")
            
        except Exception as e:
            logger.error(f"Error refreshing health data: {str(e)}")

# For testing the UI independently
if __name__ == "__main__":
    # Create mock Ana core
    class MockAnaCore:
        def process_command(self, command):
            return f"Processing command: {command}"
        
        def get_health_data(self, data_type):
            # Return mock health data
            return {
                "date": "2023-04-15",
                "health_score": 85,
                "steps": {"count": 8500, "distance": 6.2, "calories": 350},
                "sleep": {"duration_minutes": 440, "quality": 75, "deep_sleep_minutes": 110},
                "stress": {"level": 35, "category": "Moderate"},
                "heart_rate": {"average": 72, "max": 110, "min": 60}
            }
    
    # Create and start UI
    ui_controller = UIController(MockAnaCore(), {})
    sys.exit(ui_controller.run()) 