#!/usr/bin/env python3
# Ana AI Assistant - Main Window UI Module

import os
import sys
import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTextEdit, QSystemTrayIcon,
    QMenu, QAction, QTabWidget, QSplitter, QFrame,
    QGraphicsOpacityEffect, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import (
    Qt, QSize, QTimer, QThread, pyqtSignal, 
    QPropertyAnimation, QEasingCurve, QRect
)
from PyQt5.QtGui import (
    QIcon, QPixmap, QPalette, QColor, QFont, 
    QFontDatabase, QMovie, QPainter, QBrush,
    QLinearGradient, QPen, QRadialGradient
)

# Import UI components
from core.ui.character_widget import CharacterWidget
from core.ui.chat_widget import ChatWidget
from core.ui.task_widget import TaskWidget
from core.ui.settings_widget import SettingsWidget
from core.ui.calendar_widget import CalendarWidget
from core.ui.music_widget import MusicWidget
from core.ui.developer_widget import DeveloperWidget
from core.ui.voice_control_widget import VoiceControlWidget
from core.ui.theme_manager import ThemeManager

logger = logging.getLogger('Ana.UI.MainWindow')

class MainWindow(QMainWindow):
    """Main window for Ana AI Assistant"""
    
    def __init__(self, assistant, settings):
        """Initialize main window with settings"""
        super().__init__()
        self.assistant = assistant
        self.settings = settings
        self.theme_manager = ThemeManager(settings)
        
        # Set window properties
        self.setWindowTitle("Ana AI Assistant")
        self.setMinimumSize(1000, 700)
        
        # Initialize UI components
        self._init_ui()
        
        # Set up system tray
        self._setup_system_tray()
        
        # Connect to assistant events
        self._connect_assistant_events()
        
        # Set up timers for animations and updates
        self._setup_timers()
        
        logger.info("Main window initialized")
    
    def _init_ui(self):
        """Initialize the user interface"""
        # Set application style
        self._set_application_style()
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Header with title and character
        self._create_header()
        
        # Main content area with tabs
        self._create_content_area()
        
        # Footer with voice control
        self._create_footer()
    
    def _set_application_style(self):
        """Set the application style and theme"""
        # Set theme based on settings
        self.theme_manager.apply_theme(self)
        
        # Load custom fonts
        font_id = QFontDatabase.addApplicationFont("assets/ui/fonts/Oxanium-Regular.ttf")
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            font = QFont(font_family, 10)
            self.setFont(font)
        else:
            logger.warning("Could not load custom font, using system default")
    
    def _create_header(self):
        """Create the header with assistant character and title"""
        self.header_frame = QFrame()
        self.header_frame.setObjectName("headerFrame")
        self.header_frame.setMinimumHeight(140)
        self.header_frame.setMaximumHeight(140)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title and greeting
        title_layout = QVBoxLayout()
        self.title_label = QLabel("Ana AI Assistant")
        self.title_label.setObjectName("titleLabel")
        
        # Time-based greeting
        self.greeting_label = QLabel()
        self.greeting_label.setObjectName("greetingLabel")
        self._update_greeting()
        
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.greeting_label)
        title_layout.addStretch()
        
        # Character widget (right side)
        self.character_widget = CharacterWidget(self.settings)
        
        # Add to header layout
        header_layout.addLayout(title_layout, 2)
        header_layout.addWidget(self.character_widget, 1)
        
        # Add header to main layout
        self.main_layout.addWidget(self.header_frame)
    
    def _create_content_area(self):
        """Create the main content area with tabs"""
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("mainTabs")
        
        # Create and add tab widgets
        self.chat_widget = ChatWidget(self.assistant, self.settings)
        self.task_widget = TaskWidget(self.assistant, self.settings)
        self.calendar_widget = CalendarWidget(self.assistant, self.settings)
        self.music_widget = MusicWidget(self.assistant, self.settings)
        self.developer_widget = DeveloperWidget(self.assistant, self.settings)
        self.settings_widget = SettingsWidget(self.assistant, self.settings, self.theme_manager)
        
        # Add tabs
        self.tab_widget.addTab(self.chat_widget, "Chat")
        self.tab_widget.addTab(self.task_widget, "Tasks")
        self.tab_widget.addTab(self.calendar_widget, "Calendar")
        self.tab_widget.addTab(self.music_widget, "Music")
        
        # Add developer tab if enabled
        if self.settings["features"]["developer_mode"]["enabled"]:
            self.tab_widget.addTab(self.developer_widget, "Developer")
        
        self.tab_widget.addTab(self.settings_widget, "Settings")
        
        content_layout.addWidget(self.tab_widget)
        
        # Add content to main layout
        self.main_layout.addWidget(self.content_frame, 1)  # stretch factor
    
    def _create_footer(self):
        """Create the footer with voice control"""
        self.footer_frame = QFrame()
        self.footer_frame.setObjectName("footerFrame")
        self.footer_frame.setMinimumHeight(60)
        self.footer_frame.setMaximumHeight(60)
        
        footer_layout = QHBoxLayout(self.footer_frame)
        footer_layout.setContentsMargins(10, 5, 10, 5)
        
        # Voice control widget
        self.voice_control = VoiceControlWidget(self.assistant, self.settings)
        footer_layout.addWidget(self.voice_control)
        
        # Add footer to main layout
        self.main_layout.addWidget(self.footer_frame)
    
    def _setup_system_tray(self):
        """Set up system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("assets/ui/icons/ana_tray.png"))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show Ana", self)
        show_action.triggered.connect(self.show)
        
        hide_action = QAction("Hide Ana", self)
        hide_action.triggered.connect(self.hide)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._tray_icon_activated)
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Connect close event to minimize to tray
        self.closeEvent = self._close_event
    
    def _tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def _close_event(self, event):
        """Handle window close event"""
        if self.tray_icon.isVisible():
            # Minimize to tray instead of closing
            self.hide()
            event.ignore()
        else:
            # Actually close the application
            self._quit_application()
    
    def _quit_application(self):
        """Quit the application gracefully"""
        logger.info("Quitting application...")
        
        # Shut down assistant
        self.assistant.shutdown()
        
        # Remove tray icon
        self.tray_icon.hide()
        
        # Quit application
        QTimer.singleShot(500, lambda: sys.exit(0))
    
    def _connect_assistant_events(self):
        """Connect to assistant events"""
        # Listen events
        self.assistant.add_callback("listen", self._on_assistant_listening)
        
        # Processing events
        self.assistant.add_callback("process", self._on_assistant_processing)
        
        # Speak events
        self.assistant.add_callback("speak", self._on_assistant_speaking)
        
        # Idle events
        self.assistant.add_callback("idle", self._on_assistant_idle)
    
    def _on_assistant_listening(self):
        """Handle assistant listening state"""
        # Update character state
        self.character_widget.set_state("listening")
        
        # Update voice control
        self.voice_control.set_listening(True)
    
    def _on_assistant_processing(self):
        """Handle assistant processing state"""
        # Update character state
        self.character_widget.set_state("processing")
        
        # Update voice control
        self.voice_control.set_processing(True)
    
    def _on_assistant_speaking(self):
        """Handle assistant speaking state"""
        # Update character state
        self.character_widget.set_state("speaking")
        
        # Update voice control
        self.voice_control.set_speaking(True)
    
    def _on_assistant_idle(self):
        """Handle assistant idle state"""
        # Update character state
        self.character_widget.set_state("idle")
        
        # Update voice control
        self.voice_control.reset_state()
    
    def _setup_timers(self):
        """Set up timers for animations and updates"""
        # Timer for updating greeting
        self.greeting_timer = QTimer(self)
        self.greeting_timer.timeout.connect(self._update_greeting)
        self.greeting_timer.start(60000)  # Update every minute
    
    def _update_greeting(self):
        """Update the time-based greeting"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            greeting = "Good Morning"
        elif 12 <= hour < 18:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"
            
        self.greeting_label.setText(greeting)
    
    def show_notification(self, title, message):
        """Show a system notification"""
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 5000) 