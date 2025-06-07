#!/usr/bin/env python3
# Ana AI Assistant - Developer Tab

import logging
import os
import json
import sys
import platform
from datetime import datetime
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QFontMetrics, QTextCursor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QTabWidget, QTextEdit, QComboBox, QLineEdit,
    QSplitter, QTreeWidget, QTreeWidgetItem, QGroupBox, QFormLayout
)

logger = logging.getLogger('Ana.DeveloperTab')

class DeveloperTab(QWidget):
    """Developer tools interface for Ana AI Assistant"""
    
    def __init__(self, assistant, settings):
        super().__init__()
        self.assistant = assistant
        self.settings = settings
        self._setup_ui()
        self._setup_connections()
        self._load_system_info()
        self._start_log_monitor()
        logger.info("Developer tab initialized")
    
    def _setup_ui(self):
        """Set up the UI components for the developer tab"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Header
        self.header = QFrame()
        self.header.setObjectName("dev_header")
        self.header.setMaximumHeight(60)
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(10, 5, 10, 5)
        
        self.header_label = QLabel("DEVELOPER MODE")
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00E5FF;")
        self.header_layout.addWidget(self.header_label)
        
        self.header_layout.addStretch()
        
        # Refresh button
        self.refresh_btn = QPushButton("REFRESH")
        self.refresh_btn.setObjectName("primary_button")
        self.refresh_btn.setIcon(QIcon("../assets/icons/refresh.png"))
        self.refresh_btn.setIconSize(QSize(18, 18))
        self.header_layout.addWidget(self.refresh_btn)
        
        self.layout.addWidget(self.header)
        
        # Tab widget for different developer tools
        self.tabs = QTabWidget()
        self.tabs.setObjectName("dev_tabs")
        
        # Console tab
        self.console_tab = QWidget()
        self.console_layout = QVBoxLayout(self.console_tab)
        self.console_layout.setContentsMargins(10, 15, 10, 10)
        
        # Console output
        self.console_output = QTextEdit()
        self.console_output.setObjectName("console_output")
        self.console_output.setReadOnly(True)
        self.console_output.setFont(QFont("Courier New", 10))
        self.console_layout.addWidget(self.console_output)
        
        # Command input area
        self.command_container = QWidget()
        self.command_container.setMaximumHeight(40)
        self.command_layout = QHBoxLayout(self.command_container)
        self.command_layout.setContentsMargins(0, 5, 0, 0)
        self.command_layout.setSpacing(10)
        
        # Command prompt
        self.command_prompt = QLabel(">")
        self.command_prompt.setStyleSheet("color: #00E5FF; font-weight: bold;")
        self.command_layout.addWidget(self.command_prompt)
        
        # Command input
        self.command_input = QLineEdit()
        self.command_input.setObjectName("command_input")
        self.command_input.setPlaceholderText("Enter a command...")
        self.command_layout.addWidget(self.command_input)
        
        # Execute button
        self.execute_btn = QPushButton("RUN")
        self.execute_btn.setObjectName("execute_button")
        self.execute_btn.setFixedWidth(80)
        self.command_layout.addWidget(self.execute_btn)
        
        self.console_layout.addWidget(self.command_container)
        
        # Logs tab
        self.logs_tab = QWidget()
        self.logs_layout = QVBoxLayout(self.logs_tab)
        self.logs_layout.setContentsMargins(10, 15, 10, 10)
        
        # Logs filter controls
        self.logs_control = QWidget()
        self.logs_control.setMaximumHeight(40)
        self.logs_control_layout = QHBoxLayout(self.logs_control)
        self.logs_control_layout.setContentsMargins(0, 0, 0, 5)
        self.logs_control_layout.setSpacing(10)
        
        # Log level filter
        self.log_level = QComboBox()
        self.log_level.setObjectName("log_level_filter")
        self.log_level.addItems(["All", "Debug", "Info", "Warning", "Error", "Critical"])
        self.logs_control_layout.addWidget(QLabel("Log Level:"))
        self.logs_control_layout.addWidget(self.log_level)
        
        # Log component filter
        self.log_component = QComboBox()
        self.log_component.setObjectName("log_component_filter")
        self.log_component.addItems(["All", "Core", "UI", "Voice", "API", "GitHub"])
        self.logs_control_layout.addWidget(QLabel("Component:"))
        self.logs_control_layout.addWidget(self.log_component)
        
        # Search in logs
        self.log_search = QLineEdit()
        self.log_search.setObjectName("log_search")
        self.log_search.setPlaceholderText("Search in logs...")
        self.logs_control_layout.addWidget(self.log_search)
        
        # Clear logs button
        self.clear_logs_btn = QPushButton("CLEAR")
        self.clear_logs_btn.setObjectName("clear_button")
        self.clear_logs_btn.setFixedWidth(80)
        self.logs_control_layout.addWidget(self.clear_logs_btn)
        
        self.logs_layout.addWidget(self.logs_control)
        
        # Log viewer
        self.log_viewer = QTextEdit()
        self.log_viewer.setObjectName("log_viewer")
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setFont(QFont("Courier New", 10))
        self.logs_layout.addWidget(self.log_viewer)
        
        # Debug tab
        self.debug_tab = QWidget()
        self.debug_layout = QVBoxLayout(self.debug_tab)
        self.debug_layout.setContentsMargins(10, 15, 10, 10)
        
        # Split view for system info and memory inspection
        self.debug_splitter = QSplitter(Qt.Horizontal)
        
        # System info panel
        self.system_panel = QWidget()
        self.system_layout = QVBoxLayout(self.system_panel)
        self.system_layout.setContentsMargins(0, 0, 10, 0)
        
        # System info group
        self.system_group = QGroupBox("System Information")
        self.system_group.setObjectName("debug_group")
        self.system_form = QFormLayout(self.system_group)
        self.system_form.setContentsMargins(15, 20, 15, 15)
        self.system_form.setSpacing(10)
        
        # OS info
        self.os_info = QLabel()
        self.system_form.addRow("Operating System:", self.os_info)
        
        # Python version
        self.python_version = QLabel()
        self.system_form.addRow("Python Version:", self.python_version)
        
        # Qt version
        self.qt_version = QLabel()
        self.system_form.addRow("Qt Version:", self.qt_version)
        
        # CPU info
        self.cpu_info = QLabel()
        self.system_form.addRow("CPU:", self.cpu_info)
        
        # Memory info
        self.memory_info = QLabel()
        self.system_form.addRow("Memory Usage:", self.memory_info)
        
        # App version
        self.app_version = QLabel()
        self.system_form.addRow("Ana Version:", self.app_version)
        
        # Uptime
        self.uptime = QLabel()
        self.system_form.addRow("Uptime:", self.uptime)
        
        self.system_layout.addWidget(self.system_group)
        
        # Module versions group
        self.modules_group = QGroupBox("Module Versions")
        self.modules_group.setObjectName("debug_group")
        self.modules_form = QFormLayout(self.modules_group)
        self.modules_form.setContentsMargins(15, 20, 15, 15)
        self.modules_form.setSpacing(10)
        
        # PyQt5 version
        self.pyqt_version = QLabel()
        self.modules_form.addRow("PyQt5:", self.pyqt_version)
        
        # NumPy version
        self.numpy_version = QLabel()
        self.modules_form.addRow("NumPy:", self.numpy_version)
        
        # OpenCV version
        self.opencv_version = QLabel()
        self.modules_form.addRow("OpenCV:", self.opencv_version)
        
        # ElevenLabs version
        self.elevenlabs_version = QLabel()
        self.modules_form.addRow("ElevenLabs:", self.elevenlabs_version)
        
        # OpenAI version
        self.openai_version = QLabel()
        self.modules_form.addRow("OpenAI:", self.openai_version)
        
        self.system_layout.addWidget(self.modules_group)
        
        # Memory inspection panel
        self.memory_panel = QWidget()
        self.memory_layout = QVBoxLayout(self.memory_panel)
        self.memory_layout.setContentsMargins(10, 0, 0, 0)
        
        # Memory tree
        self.memory_tree = QTreeWidget()
        self.memory_tree.setObjectName("memory_tree")
        self.memory_tree.setHeaderLabels(["Object", "Type", "Value"])
        self.memory_layout.addWidget(self.memory_tree)
        
        # Add panels to splitter
        self.debug_splitter.addWidget(self.system_panel)
        self.debug_splitter.addWidget(self.memory_panel)
        
        self.debug_layout.addWidget(self.debug_splitter)
        
        # Test tools
        self.test_group = QGroupBox("Testing Tools")
        self.test_group.setObjectName("debug_group")
        self.test_layout = QHBoxLayout(self.test_group)
        self.test_layout.setContentsMargins(15, 20, 15, 15)
        self.test_layout.setSpacing(15)
        
        # Test buttons
        test_buttons = [
            ("Test Voice", "test_voice"),
            ("Test Camera", "test_camera"),
            ("Test Network", "test_network"),
            ("Unit Tests", "run_tests")
        ]
        
        for label, obj_name in test_buttons:
            btn = QPushButton(label)
            btn.setObjectName(obj_name)
            btn.setMinimumWidth(120)
            self.test_layout.addWidget(btn)
        
        self.debug_layout.addWidget(self.test_group)
        
        # Add tabs to tab widget
        self.tabs.addTab(self.console_tab, "Console")
        self.tabs.addTab(self.logs_tab, "Logs")
        self.tabs.addTab(self.debug_tab, "Debug")
        
        self.layout.addWidget(self.tabs)
    
    def _setup_connections(self):
        """Set up signal/slot connections"""
        self.refresh_btn.clicked.connect(self._refresh_all)
        self.execute_btn.clicked.connect(self._execute_command)
        self.command_input.returnPressed.connect(self._execute_command)
        self.clear_logs_btn.clicked.connect(self._clear_logs)
        self.log_level.currentIndexChanged.connect(self._filter_logs)
        self.log_component.currentIndexChanged.connect(self._filter_logs)
        self.log_search.textChanged.connect(self._filter_logs)
    
    def _load_system_info(self):
        """Load system information"""
        # OS info
        self.os_info.setText(f"{platform.system()} {platform.release()}")
        
        # Python version
        self.python_version.setText(platform.python_version())
        
        # Qt version
        from PyQt5.QtCore import QT_VERSION_STR
        self.qt_version.setText(QT_VERSION_STR)
        
        # CPU info
        if hasattr(platform, "processor"):
            self.cpu_info.setText(platform.processor() or "Unknown")
        else:
            self.cpu_info.setText("Unknown")
        
        # Memory info - this would need psutil in a real implementation
        self.memory_info.setText("Not available (psutil required)")
        
        # App version
        try:
            with open(os.path.join(os.path.dirname(__file__), "..", "version.txt"), 'r') as f:
                version = f.read().strip()
                self.app_version.setText(version)
        except:
            self.app_version.setText("Unknown")
        
        # Uptime - would need to track application start time
        self.uptime.setText("Not available")
        
        # Module versions
        try:
            import PyQt5
            self.pyqt_version.setText(PyQt5.QtCore.PYQT_VERSION_STR)
        except:
            self.pyqt_version.setText("Not installed")
        
        try:
            import numpy
            self.numpy_version.setText(numpy.__version__)
        except:
            self.numpy_version.setText("Not installed")
        
        try:
            import cv2
            self.opencv_version.setText(cv2.__version__)
        except:
            self.opencv_version.setText("Not installed")
        
        try:
            import elevenlabs
            self.elevenlabs_version.setText(elevenlabs.__version__)
        except:
            self.elevenlabs_version.setText("Not installed")
        
        try:
            import openai
            self.openai_version.setText(openai.__version__)
        except:
            self.openai_version.setText("Not installed")
    
    def _populate_memory_tree(self):
        """Populate the memory tree with assistant object structure"""
        self.memory_tree.clear()
        
        # In a real implementation, this would inspect the assistant object
        # and add its properties to the tree. For now, we'll add placeholders.
        
        # Add root item for the assistant
        assistant_item = QTreeWidgetItem(self.memory_tree, ["assistant", "object", "<Ana Assistant>"])
        
        # Add child items for main components
        components = [
            ("voice_module", "object", "<Voice Module>"),
            ("vision_module", "object", "<Vision Module>"),
            ("memory_db", "object", "<Memory Database>"),
            ("nlp_engine", "object", "<NLP Engine>"),
            ("settings", "dict", "{}"),
            ("tasks", "list", "[]"),
            ("events", "list", "[]")
        ]
        
        for name, type_name, value in components:
            QTreeWidgetItem(assistant_item, [name, type_name, value])
        
        # Expand the root item
        assistant_item.setExpanded(True)
    
    def _start_log_monitor(self):
        """Start monitoring the log file"""
        # In a real implementation, this would set up a file watcher
        # For now, just populate with some sample logs
        self._add_sample_logs()
        
        # Set up timer to simulate new logs
        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self._add_new_log)
        self.log_timer.start(5000)  # Add a log every 5 seconds
    
    def _add_sample_logs(self):
        """Add sample logs to the log viewer"""
        sample_logs = [
            "2023-05-15 08:32:10 [INFO] Ana.Core: System initialized",
            "2023-05-15 08:32:11 [INFO] Ana.Voice: Voice module loaded successfully",
            "2023-05-15 08:32:12 [INFO] Ana.UI: UI initialized with theme: cyberpunk",
            "2023-05-15 08:32:14 [DEBUG] Ana.Core: Loading user preferences from data/preferences.json",
            "2023-05-15 08:32:15 [INFO] Ana.Core: User preferences loaded successfully",
            "2023-05-15 08:32:17 [WARNING] Ana.Voice: Microphone access not granted",
            "2023-05-15 08:32:18 [ERROR] Ana.API: Failed to connect to OpenAI API: Invalid API key",
            "2023-05-15 08:32:20 [INFO] Ana.Core: Attempting to use local fallback model",
            "2023-05-15 08:32:22 [INFO] Ana.Core: Local model loaded successfully",
            "2023-05-15 08:32:25 [DEBUG] Ana.UI: Rendering main window components"
        ]
        
        for log in sample_logs:
            self._append_log(log)
    
    def _add_new_log(self):
        """Add a new log entry to simulate real-time logging"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        components = ["Core", "Voice", "UI", "API", "GitHub"]
        levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        messages = [
            "Processing user input",
            "Analyzing image data",
            "API request completed",
            "Memory database updated",
            "Task scheduled",
            "Network connection status checked",
            "Facial recognition processing",
            "Voice synthesis completed"
        ]
        
        import random
        level = random.choice(levels)
        component = random.choice(components)
        message = random.choice(messages)
        
        log = f"{now} [{level}] Ana.{component}: {message}"
        self._append_log(log)
    
    def _append_log(self, log):
        """Append a log entry to the log viewer"""
        # Style the log based on level
        if "[ERROR]" in log:
            style = "color: #ff5252;"
        elif "[WARNING]" in log:
            style = "color: #ffc107;"
        elif "[DEBUG]" in log:
            style = "color: #9e9e9e;"
        else:  # INFO
            style = "color: #ffffff;"
        
        self.log_viewer.append(f"<span style='{style}'>{log}</span>")
        
        # Auto-scroll to bottom
        cursor = self.log_viewer.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_viewer.setTextCursor(cursor)
    
    def _filter_logs(self):
        """Filter logs based on selected criteria"""
        # This would filter the existing logs in the viewer
        # For now, we'll just clear and re-add the sample logs
        self.log_viewer.clear()
        self._add_sample_logs()
    
    def _clear_logs(self):
        """Clear the log viewer"""
        self.log_viewer.clear()
    
    def _execute_command(self):
        """Execute a command entered in the console"""
        command = self.command_input.text().strip()
        if not command:
            return
        
        # Add command to console output
        self.console_output.append(f'<span style="color: #00E5FF;">&gt; {command}</span>')
        
        # Process command (in a real implementation, this would call an interpreter)
        response = self._process_command(command)
        
        # Display response
        self.console_output.append(f'<span style="color: #ffffff;">{response}</span>')
        self.console_output.append('')  # Add empty line for spacing
        
        # Clear input
        self.command_input.clear()
        
        # Auto-scroll to bottom
        cursor = self.console_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.console_output.setTextCursor(cursor)
    
    def _process_command(self, command):
        """Process a console command and return a response"""
        # This is a simple command processor for demonstration
        # In a real implementation, this would be more sophisticated
        
        command_lower = command.lower()
        
        if command_lower == "help":
            return (
                "Available commands:\n"
                "- help: Show this help message\n"
                "- status: Show system status\n"
                "- version: Show application version\n"
                "- restart: Restart the application\n"
                "- clear: Clear the console\n"
                "- exit: Exit the application"
            )
        elif command_lower == "status":
            return "System status: Running normally"
        elif command_lower == "version":
            return "Ana AI Assistant v1.0.0"
        elif command_lower == "restart":
            return "Restart command received (not implemented in demo)"
        elif command_lower == "clear":
            self.console_output.clear()
            return ""
        elif command_lower == "exit":
            return "Exit command received (not implemented in demo)"
        else:
            return f"Unknown command: {command}"
    
    def _refresh_all(self):
        """Refresh all data in the developer tab"""
        self._load_system_info()
        self._populate_memory_tree()
        self._filter_logs()
        
        # Add a message to the console
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.console_output.append(f'<span style="color: #9e9e9e;">[{timestamp}] Refreshed all data</span>')
        self.console_output.append('') 