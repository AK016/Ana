#!/usr/bin/env python3
# Ana AI Assistant - Main Window

import os
import sys
import logging
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSlot, QPropertyAnimation, QRect
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPalette, QLinearGradient, QFont, QFontDatabase
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QSizePolicy, QFrame,
    QLineEdit, QTextEdit, QScrollArea, QTabWidget, QGraphicsDropShadowEffect
)

from ui.chat_tab import ChatTab
from ui.tasks_tab import TasksTab
from ui.calendar_tab import CalendarTab
from ui.music_tab import MusicTab
from ui.health_tab import HealthTab
from ui.settings_tab import SettingsTab
from ui.dev_tab import DeveloperTab
from ui.character_view import CharacterView
from ui.full_screen_character import FullScreenCharacter, BackgroundType

logger = logging.getLogger('Ana.MainWindow')

class MainWindow(QMainWindow):
    """Main window for Ana AI Assistant"""
    
    def __init__(self, assistant, settings):
        super().__init__()
        self.assistant = assistant
        self.settings = settings
        self.fullscreen_character = None
        self._setup_ui()
        self._setup_connections()
        self._load_style()
        self._apply_theme()
        
        logger.info("Main window initialized")
    
    def _setup_ui(self):
        """Set up the UI components"""
        # Window properties
        self.setWindowTitle("Ana AI Assistant")
        self.setMinimumSize(1200, 800)
        self.setWindowIcon(QIcon(os.path.join(
            os.path.dirname(__file__), "..", "assets", "icon.png"
        )))
        
        # Load custom fonts
        self._load_fonts()
        
        # Main central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Setup sidebar
        self._setup_sidebar()
        
        # Setup main content area
        self._setup_content_area()
        
        # Setup status bar
        self.statusBar().showMessage("Ana is ready")
    
    def _load_fonts(self):
        """Load custom fonts for the application"""
        font_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
        if os.path.exists(font_dir):
            for font_file in os.listdir(font_dir):
                if font_file.endswith(('.ttf', '.otf')):
                    font_path = os.path.join(font_dir, font_file)
                    QFontDatabase.addApplicationFont(font_path)
        
        # Set default font
        self.app_font = QFont("Rajdhani", 10)
        QApplication.setFont(self.app_font)
    
    def _setup_sidebar(self):
        """Set up the sidebar with function buttons"""
        # Sidebar container
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(300)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(20, 40, 20, 20)
        self.sidebar_layout.setSpacing(15)
        
        # Add logo at the top
        self.logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
        if os.path.exists(logo_path):
            self.logo_label.setPixmap(QPixmap(logo_path).scaled(
                240, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        else:
            self.logo_label.setText("ANA AI")
            self.logo_label.setAlignment(Qt.AlignCenter)
            self.logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00E5FF;")
        
        self.sidebar_layout.addWidget(self.logo_label)
        self.sidebar_layout.addSpacing(20)
        
        # Function buttons - using cyberpunk style with icons
        self.function_buttons = {}
        
        button_specs = [
            ("tasks", "TASKS", "tasks.png", "Task management"),
            ("memory", "MEMORY", "memory.png", "Memory database"),
            ("calendar", "CALENDAR SYNC", "calendar.png", "Calendar integration"),
            ("health", "HEALTH", "health.png", "Health monitoring"),
            ("music", "MUSIC", "music.png", "Music playback"),
            ("developer", "DEVELOPER MODE", "developer.png", "Developer tools")
        ]
        
        for btn_id, label, icon_file, tooltip in button_specs:
            btn = self._create_sidebar_button(btn_id, label, icon_file, tooltip)
            self.function_buttons[btn_id] = btn
            self.sidebar_layout.addWidget(btn)
        
        # Add spacer at the bottom
        self.sidebar_layout.addStretch()
        
        # Add to main layout
        self.main_layout.addWidget(self.sidebar)
    
    def _create_sidebar_button(self, btn_id, label, icon_file, tooltip):
        """Create a styled sidebar button"""
        btn = QPushButton()
        btn.setObjectName(f"sidebar_btn_{btn_id}")
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(70)
        
        # Button layout for icon and text
        btn_layout = QHBoxLayout(btn)
        btn_layout.setContentsMargins(20, 10, 10, 10)
        btn_layout.setSpacing(15)
        
        # Icon
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", icon_file)
        if os.path.exists(icon_path):
            icon_pixmap = QPixmap(icon_path).scaled(
                30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            icon_label.setPixmap(icon_pixmap)
        else:
            # If icon doesn't exist, use text as placeholder
            icon_label.setText("•")
            icon_label.setStyleSheet("color: #00E5FF; font-size: 24px;")
        
        icon_label.setFixedSize(QSize(30, 30))
        btn_layout.addWidget(icon_label)
        
        # Text
        text_label = QLabel(label)
        text_label.setStyleSheet("color: #00E5FF; font-size: 16px; font-weight: bold;")
        btn_layout.addWidget(text_label)
        btn_layout.addStretch()
        
        # Connect click handler
        btn.clicked.connect(lambda: self._on_sidebar_button_click(btn_id))
        
        return btn
    
    def _setup_content_area(self):
        """Set up the main content area with tabs"""
        # Content container
        self.content_container = QWidget()
        self.content_container.setObjectName("content_container")
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # Stacked widget for different content pages
        self.content_stack = QStackedWidget()
        
        # Create tabs
        self.chat_tab = ChatTab(self.assistant)
        self.tasks_tab = TasksTab(self.assistant)
        self.calendar_tab = CalendarTab(self.assistant)
        self.health_tab = HealthTab(self.assistant)
        self.music_tab = MusicTab(self.assistant)
        self.settings_tab = SettingsTab(self.assistant, self.settings)
        self.dev_tab = DeveloperTab(self.assistant, self.settings)
        
        # Add tabs to stack
        self.content_stack.addWidget(self.chat_tab)  # Index 0
        self.content_stack.addWidget(self.tasks_tab)  # Index 1
        self.content_stack.addWidget(self.calendar_tab)  # Index 2
        self.content_stack.addWidget(self.health_tab)  # Index 3
        self.content_stack.addWidget(self.music_tab)  # Index 4
        self.content_stack.addWidget(self.settings_tab)  # Index 5
        self.content_stack.addWidget(self.dev_tab)  # Index 6
        
        # Add character view to the right side (for chat tab only)
        self.chat_view = QWidget()
        self.chat_view_layout = QHBoxLayout(self.chat_view)
        self.chat_view_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_view_layout.setSpacing(0)
        
        # Left side (content)
        self.chat_view_layout.addWidget(self.content_stack, 1)  # Stretch factor 1
        
        # Right side (character)
        self.character_container = QWidget()
        self.character_container.setObjectName("character_container")
        self.character_container.setMinimumWidth(450)
        self.character_layout = QVBoxLayout(self.character_container)
        self.character_layout.setContentsMargins(0, 0, 0, 0)
        
        # Character view
        self.character_view = CharacterView()
        self.character_layout.addWidget(self.character_view, 1)  # Stretch factor 1
        
        # Full screen button
        self.fullscreen_button = QPushButton("Full Screen Mode")
        self.fullscreen_button.setObjectName("fullscreen_button")
        self.fullscreen_button.setToolTip("Show Ana in full screen mode")
        self.fullscreen_button.setCursor(Qt.PointingHandCursor)
        self.fullscreen_button.setStyleSheet(
            "background-color: rgba(0, 229, 255, 0.2); "
            "color: #FFFFFF; padding: 10px; "
            "border: 1px solid #00E5FF; border-radius: 5px;"
        )
        self.fullscreen_button.clicked.connect(self._show_fullscreen_character)
        
        # Message display
        self.message_display = QLabel("Good evening, Master.\nWhat would you like do to today?")
        self.message_display.setObjectName("message_display")
        self.message_display.setAlignment(Qt.AlignCenter)
        self.message_display.setWordWrap(True)
        self.message_display.setStyleSheet(
            "color: #00E5FF; font-size: 18px; padding: 20px; "
            "background-color: rgba(0, 20, 40, 0.7); border-radius: 15px; "
            "border: 1px solid #00E5FF;"
        )
        self.message_display.setMinimumHeight(100)
        self.message_display.setMaximumHeight(150)
        
        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 5, 10, 5)
        button_layout.addWidget(self.fullscreen_button)
        
        # Add widgets to character layout
        self.character_layout.addWidget(self.message_display)
        self.character_layout.addWidget(button_container)
        
        # Microphone button
        self.mic_button = QPushButton()
        self.mic_button.setObjectName("mic_button")
        self.mic_button.setToolTip("Activate microphone")
        self.mic_button.setCursor(Qt.PointingHandCursor)
        self.mic_button.setMinimumSize(QSize(60, 60))
        self.mic_button.setMaximumSize(QSize(60, 60))
        
        # Add icon to button
        mic_icon_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", "icons", "microphone.png"
        )
        if os.path.exists(mic_icon_path):
            self.mic_button.setIcon(QIcon(mic_icon_path))
            self.mic_button.setIconSize(QSize(30, 30))
        
        # Center the mic button
        mic_container = QWidget()
        mic_layout = QHBoxLayout(mic_container)
        mic_layout.addStretch()
        mic_layout.addWidget(self.mic_button)
        mic_layout.addStretch()
        self.character_layout.addWidget(mic_container)
        self.character_layout.addSpacing(20)
        
        # Add character container to chat view
        self.chat_view_layout.addWidget(self.character_container)
        
        # Add to content layout
        self.content_layout.addWidget(self.chat_view)
        
        # Add to main layout
        self.main_layout.addWidget(self.content_container, 1)  # Stretch factor 1
    
    def _on_sidebar_button_click(self, btn_id):
        """Handle sidebar button clicks"""
        # Map button IDs to stack index
        btn_to_index = {
            "tasks": 1,
            "memory": 0,  # Memory shows chat history
            "calendar": 2,
            "health": 3,
            "music": 4,
            "developer": 6,
            "settings": 5
        }
        
        # Switch to corresponding tab
        if btn_id in btn_to_index:
            index = btn_to_index[btn_id]
            self.content_stack.setCurrentIndex(index)
            
            # Hide character container for non-chat tabs
            if btn_id == "memory":
                self.character_container.show()
            else:
                self.character_container.hide()
    
    def _setup_connections(self):
        """Set up signal connections to the assistant"""
        # Connect assistant events to character animations
        self.assistant.add_callback("wake", self.character_view.on_wake_word)
        self.assistant.add_callback("listen", self.character_view.on_listening)
        self.assistant.add_callback("process", self.character_view.on_processing)
        self.assistant.add_callback("speak", self.character_view.on_speaking)
        self.assistant.add_callback("idle", self.character_view.on_idle)
        
        # Connect assistant speaking to message display
        self.assistant.add_callback("speak", self._on_assistant_speaking)
        
        # Connect microphone button
        self.mic_button.clicked.connect(self._on_mic_button_click)
        
        # Connect face detection
        self.assistant.add_callback("face_detected", self._on_face_detected)
    
    def _on_assistant_speaking(self):
        """Handle assistant speaking event"""
        # Get last assistant message from memory
        last_message = self.assistant.memory.get_last_assistant_message()
        if last_message:
            message_text = last_message["content"]
            self.message_display.setText(message_text)
            
            # Update fullscreen character if active
            if self.fullscreen_character and hasattr(self.fullscreen_character, 'set_message'):
                self.fullscreen_character.set_message(message_text)
                self.fullscreen_character.animate_speaking(len(message_text) * 80)  # Estimate duration based on text length
    
    def _on_mic_button_click(self):
        """Handle microphone button click"""
        # Disable button while listening
        self.mic_button.setEnabled(False)
        self.mic_button.setStyleSheet("background-color: #FF4081;")
        
        # Start listening in a separate thread
        import threading
        threading.Thread(target=self._listen_thread, daemon=True).start()
    
    def _on_face_detected(self):
        """Handle face detection event"""
        # Update UI when face is detected
        # This could show an animation or change status
        self.statusBar().showMessage("User detected")
    
    def _listen_thread(self):
        """Thread for listening to user input"""
        # Tell assistant to listen
        success = self.assistant.listen()
        
        # Re-enable button after listening completes
        self.mic_button.setEnabled(True)
        self.mic_button.setStyleSheet("")
        
        # Update status based on recognition result
        if success:
            self.statusBar().showMessage("Command processed")
        else:
            self.statusBar().showMessage("Listening failed or cancelled")
    
    def _show_fullscreen_character(self):
        """Show the character in full screen mode"""
        # Create fullscreen character if not exists
        if not self.fullscreen_character:
            self.fullscreen_character = FullScreenCharacter(self)
            
            # Connect closed signal to handle cleanup
            self.fullscreen_character.closed.connect(self._on_fullscreen_closed)
            
            # Copy current emotion and message
            emotion = self.character_view.current_emotion
            self.fullscreen_character.set_emotion(emotion)
            
            message = self.message_display.text()
            self.fullscreen_character.set_message(message)
            
            # Set default background - can be customized based on context or weather
            self._set_background_based_on_context()
        
        # Show the fullscreen character
        self.fullscreen_character.show()
    
    def _on_fullscreen_closed(self):
        """Handle fullscreen character being closed"""
        # Clean up reference
        self.fullscreen_character = None
    
    def _set_background_based_on_context(self):
        """Set appropriate background based on context or weather"""
        if not self.fullscreen_character:
            return
            
        # Try to determine time of day
        import datetime
        hour = datetime.datetime.now().hour
        
        if 6 <= hour < 18:
            time_of_day = "day"
        elif 18 <= hour < 20:
            time_of_day = "sunset"
        else:
            time_of_day = "night"
        
        # Try to get weather information if available
        weather_condition = "clear"  # Default
        
        try:
            # Check if weather info is available from assistant
            if hasattr(self.assistant, 'get_weather_info'):
                weather_data = self.assistant.get_weather_info()
                if weather_data and 'condition' in weather_data:
                    weather_condition = weather_data['condition'].lower()
        except Exception as e:
            logger.error(f"Error getting weather info: {str(e)}")
        
        # Set background based on time and weather
        if time_of_day == "night":
            # Night backgrounds
            if weather_condition in ["clear", "few clouds"]:
                self.fullscreen_character.set_background(
                    BackgroundType.CYBERPUNK_CITY, 
                    time_of_day=time_of_day
                )
            else:
                self.fullscreen_character.set_background(
                    BackgroundType.WEATHER, 
                    weather=weather_condition,
                    time_of_day=time_of_day
                )
        else:
            # Day/sunset backgrounds
            self.fullscreen_character.set_background(
                BackgroundType.WEATHER, 
                weather=weather_condition,
                time_of_day=time_of_day
            )
    
    def _load_style(self):
        """Load stylesheet from file"""
        style_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", "style.qss"
        )
        
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
        else:
            # Fallback stylesheet
            self.setStyleSheet("""
                #sidebar {
                    background-color: #0A0E17;
                    border-right: 1px solid #00E5FF;
                }
                
                #sidebar_btn_tasks, #sidebar_btn_memory, #sidebar_btn_calendar,
                #sidebar_btn_health, #sidebar_btn_music, #sidebar_btn_developer {
                    background-color: rgba(0, 20, 40, 0.5);
                    border: 1px solid #00E5FF;
                    border-radius: 10px;
                    text-align: left;
                }
                
                #sidebar_btn_tasks:hover, #sidebar_btn_memory:hover, #sidebar_btn_calendar:hover,
                #sidebar_btn_health:hover, #sidebar_btn_music:hover, #sidebar_btn_developer:hover {
                    background-color: rgba(0, 229, 255, 0.1);
                }
                
                #content_container {
                    background-color: #091428;
                }
                
                #character_container {
                    background-color: rgba(9, 20, 40, 0.9);
                    border-left: 1px solid #00E5FF;
                }
                
                #mic_button {
                    background-color: rgba(0, 229, 255, 0.2);
                    border: 2px solid #00E5FF;
                    border-radius: 30px;
                }
                
                #mic_button:hover {
                    background-color: rgba(0, 229, 255, 0.3);
                }
                
                #fullscreen_button {
                    background-color: rgba(0, 229, 255, 0.2);
                    border: 1px solid #00E5FF;
                    border-radius: 5px;
                    color: #FFFFFF;
                    padding: 10px;
                }
                
                #fullscreen_button:hover {
                    background-color: rgba(0, 229, 255, 0.3);
                }
            """)
    
    def _apply_theme(self):
        """Apply dark theme to the application"""
        # Set dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(9, 20, 40))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(10, 14, 23))
        dark_palette.setColor(QPalette.AlternateBase, QColor(12, 18, 30))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(10, 14, 23))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, QColor(0, 229, 255))
        dark_palette.setColor(QPalette.Highlight, QColor(0, 229, 255))
        dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        dark_palette.setColor(QPalette.Link, QColor(0, 229, 255))
        
        self.setPalette(dark_palette)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Close fullscreen character if open
        if self.fullscreen_character:
            self.fullscreen_character.close()
            
        # Properly shut down the assistant
        self.assistant.shutdown()
        event.accept() 