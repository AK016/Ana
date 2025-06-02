#!/usr/bin/env python3
# Ana AI Assistant - Chat Widget

import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal

logger = logging.getLogger('Ana.UI.ChatWidget')

class ChatWidget(QWidget):
    """Widget for chat interactions with Ana"""
    
    def __init__(self, assistant, settings):
        """Initialize chat widget with settings"""
        super().__init__()
        self.assistant = assistant
        self.settings = settings
        
        # Initialize UI
        self._init_ui()
        
        logger.info("Chat widget initialized")
    
    def _init_ui(self):
        """Initialize the user interface"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # Chat history display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setObjectName("chatDisplay")
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.setObjectName("chatInput")
        self.input_field.returnPressed.connect(self._send_message)
        
        self.send_button = QPushButton("Send")
        self.send_button.setObjectName("sendButton")
        self.send_button.clicked.connect(self._send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        
        # Add widgets to layout
        self.layout.addWidget(self.chat_display)
        self.layout.addLayout(input_layout)
    
    def _send_message(self):
        """Handle sending a message"""
        text = self.input_field.text().strip()
        if not text:
            return
            
        # Add user message to display
        self.chat_display.append(f"<b>You:</b> {text}")
        
        # Clear input field
        self.input_field.clear()
        
        # Process with assistant
        self.assistant.process_input(text)
    
    def add_assistant_message(self, message):
        """Add an assistant message to the chat display"""
        self.chat_display.append(f"<b>Ana:</b> {message}")
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        ) 