#!/usr/bin/env python3
# Ana AI Assistant - Chat Tab

import logging
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QScrollArea, QFrame, QSplitter
)

logger = logging.getLogger('Ana.ChatTab')

class ChatTab(QWidget):
    """Chat interface for Ana AI Assistant"""
    
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self._setup_ui()
        self._setup_connections()
        logger.info("Chat tab initialized")
    
    def _setup_ui(self):
        """Set up the UI components for the chat tab"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Chat area container
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(20, 20, 20, 20)
        self.chat_layout.setSpacing(10)
        
        # Header
        self.header = QFrame()
        self.header.setObjectName("chat_header")
        self.header.setMaximumHeight(60)
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(10, 5, 10, 5)
        
        self.header_label = QLabel("ANA CHAT INTERFACE")
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00E5FF;")
        self.header_layout.addWidget(self.header_label)
        
        self.header_layout.addStretch()
        
        # Add settings button
        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(QIcon("../assets/icons/settings.png"))
        self.settings_btn.setIconSize(QSize(24, 24))
        self.settings_btn.setToolTip("Chat Settings")
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.setObjectName("icon_button")
        self.header_layout.addWidget(self.settings_btn)
        
        self.chat_layout.addWidget(self.header)
        
        # Chat messages area
        self.messages_scroll_area = QScrollArea()
        self.messages_scroll_area.setWidgetResizable(True)
        self.messages_scroll_area.setObjectName("chat_messages_area")
        self.messages_scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(10, 10, 10, 10)
        self.messages_layout.setSpacing(15)
        self.messages_layout.addStretch()
        
        self.messages_scroll_area.setWidget(self.messages_container)
        self.chat_layout.addWidget(self.messages_scroll_area)
        
        # Input area
        self.input_container = QFrame()
        self.input_container.setObjectName("chat_input_container")
        self.input_container.setMinimumHeight(100)
        self.input_container.setMaximumHeight(150)
        
        self.input_layout = QHBoxLayout(self.input_container)
        self.input_layout.setContentsMargins(10, 10, 10, 10)
        self.input_layout.setSpacing(10)
        
        # Text input
        self.input_text = QTextEdit()
        self.input_text.setObjectName("chat_input_text")
        self.input_text.setPlaceholderText("Type a message...")
        self.input_layout.addWidget(self.input_text)
        
        # Button container
        self.input_buttons = QWidget()
        self.input_buttons.setMaximumWidth(120)
        self.buttons_layout = QVBoxLayout(self.input_buttons)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(5)
        
        # Send button
        self.send_btn = QPushButton("SEND")
        self.send_btn.setObjectName("chat_send_button")
        self.send_btn.setMinimumHeight(40)
        self.buttons_layout.addWidget(self.send_btn)
        
        # Voice button
        self.voice_btn = QPushButton("VOICE")
        self.voice_btn.setObjectName("chat_voice_button")
        self.voice_btn.setMinimumHeight(40)
        self.buttons_layout.addWidget(self.voice_btn)
        
        self.input_layout.addWidget(self.input_buttons)
        self.chat_layout.addWidget(self.input_container)
        
        # Add the chat container to the main layout
        self.layout.addWidget(self.chat_container)
    
    def _setup_connections(self):
        """Set up signal/slot connections"""
        self.send_btn.clicked.connect(self._on_send_message)
        self.voice_btn.clicked.connect(self._on_voice_input)
        self.input_text.textChanged.connect(self._on_text_changed)
    
    def _on_send_message(self):
        """Handle sending a message"""
        message = self.input_text.toPlainText().strip()
        if message:
            self._add_user_message(message)
            self.input_text.clear()
            # TODO: Send to assistant and get response
            self._add_assistant_message("I'll implement a real response later!")
    
    def _add_user_message(self, text):
        """Add a user message to the chat"""
        message_widget = self._create_message_bubble(text, is_user=True)
        # Insert before the stretch at the end
        self.messages_layout.insertWidget(self.messages_layout.count()-1, message_widget)
        self._scroll_to_bottom()
    
    def _add_assistant_message(self, text):
        """Add an assistant message to the chat"""
        message_widget = self._create_message_bubble(text, is_user=False)
        # Insert before the stretch at the end
        self.messages_layout.insertWidget(self.messages_layout.count()-1, message_widget)
        self._scroll_to_bottom()
    
    def _create_message_bubble(self, text, is_user=False):
        """Create a message bubble widget"""
        bubble = QFrame()
        bubble.setObjectName("user_message" if is_user else "assistant_message")
        bubble.setMaximumWidth(int(self.width() * 0.7))
        
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(15, 10, 15, 10)
        
        # Message text
        message_label = QLabel(text)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        bubble_layout.addWidget(message_label)
        
        # Container to position the bubble
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 5, 0, 5)
        
        if is_user:
            container_layout.addStretch()
            container_layout.addWidget(bubble)
        else:
            container_layout.addWidget(bubble)
            container_layout.addStretch()
        
        return container
    
    def _on_voice_input(self):
        """Handle voice input button click"""
        # TODO: Implement voice input
        pass
    
    def _on_text_changed(self):
        """Handle input text changes"""
        # Adjust for multiline text
        document_height = self.input_text.document().size().height()
        new_height = min(100, max(40, document_height + 20))
        self.input_text.setMinimumHeight(int(new_height))
    
    def _scroll_to_bottom(self):
        """Scroll the message area to the bottom"""
        self.messages_scroll_area.verticalScrollBar().setValue(
            self.messages_scroll_area.verticalScrollBar().maximum()
        ) 