#!/usr/bin/env python3
# Ana AI Assistant - Voice Control Widget

import os
import logging
import threading
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QHBoxLayout,
    QVBoxLayout, QFrame, QSizePolicy, QSlider
)
from PyQt5.QtCore import (
    Qt, QSize, QTimer, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QRect
)
from PyQt5.QtGui import (
    QIcon, QPixmap, QColor, QPainter, QBrush,
    QLinearGradient, QPen
)

logger = logging.getLogger('Ana.UI.VoiceControl')

class VoiceControlWidget(QWidget):
    """Widget for controlling voice input and output"""
    
    def __init__(self, assistant, settings):
        """Initialize voice control widget with settings"""
        super().__init__()
        self.assistant = assistant
        self.settings = settings
        
        # State variables
        self.listening = False
        self.speaking = False
        self.processing = False
        
        # Initialize UI
        self._init_ui()
        
        logger.info("Voice control widget initialized")
    
    def _init_ui(self):
        """Initialize the user interface"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(10)
        
        # Status frame
        self.status_frame = QFrame()
        self.status_frame.setObjectName("voiceStatusFrame")
        self.status_frame.setFixedWidth(200)
        
        status_layout = QVBoxLayout(self.status_frame)
        status_layout.setContentsMargins(5, 5, 5, 5)
        status_layout.setSpacing(2)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("voiceStatusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Add to status layout
        status_layout.addWidget(self.status_label)
        
        # Microphone button
        self.mic_button = QPushButton()
        self.mic_button.setObjectName("micButton")
        self.mic_button.setToolTip("Click to start listening")
        self.mic_button.setFixedSize(48, 48)
        self.mic_button.setIconSize(QSize(24, 24))
        self.mic_button.setIcon(QIcon("assets/ui/icons/mic.png"))
        self.mic_button.clicked.connect(self._on_mic_button_clicked)
        
        # Audio visualization frame
        self.viz_frame = QFrame()
        self.viz_frame.setObjectName("audioVizFrame")
        self.viz_frame.setMinimumHeight(30)
        
        # Audio output volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setObjectName("volumeSlider")
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(80)  # Default volume
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        
        # Add widgets to main layout
        self.layout.addWidget(self.status_frame)
        self.layout.addWidget(self.mic_button)
        self.layout.addWidget(self.viz_frame, 1)  # stretch
        self.layout.addWidget(self.volume_slider)
        
        # Set up visualization timer
        self.viz_timer = QTimer(self)
        self.viz_timer.timeout.connect(self.update)  # Trigger paint event for visualization
        
        # Visualization data (placeholder)
        self.viz_data = [0] * 20
        self.viz_active = False
    
    def _on_mic_button_clicked(self):
        """Handle microphone button click"""
        if self.listening or self.speaking:
            # Currently active, do nothing
            return
            
        # Start listening in a separate thread
        self.set_listening(True)
        threading.Thread(target=self._listen_thread, daemon=True).start()
    
    def _listen_thread(self):
        """Background thread for listening"""
        try:
            # Call the assistant's listen method
            self.assistant.listen()
        except Exception as e:
            logger.error(f"Error in listen thread: {str(e)}")
        finally:
            # Reset state when done
            self.set_listening(False)
    
    def _on_volume_changed(self, value):
        """Handle volume slider change"""
        # Implement volume control logic
        # This would interact with the voice engine
        logger.debug(f"Volume changed to {value}%")
    
    def set_listening(self, is_listening):
        """Set the listening state"""
        self.listening = is_listening
        
        if is_listening:
            self.status_label.setText("Listening...")
            self.mic_button.setIcon(QIcon("assets/ui/icons/mic_active.png"))
            
            # Start visualization
            self.viz_active = True
            self.viz_timer.start(50)  # Update every 50ms
        else:
            self.viz_active = False
            self.viz_timer.stop()
    
    def set_speaking(self, is_speaking):
        """Set the speaking state"""
        self.speaking = is_speaking
        
        if is_speaking:
            self.status_label.setText("Speaking...")
            
            # Start visualization
            self.viz_active = True
            self.viz_timer.start(50)  # Update every 50ms
        else:
            self.viz_active = False
            self.viz_timer.stop()
            
            # Reset status if not processing
            if not self.processing:
                self.reset_state()
    
    def set_processing(self, is_processing):
        """Set the processing state"""
        self.processing = is_processing
        
        if is_processing:
            self.status_label.setText("Processing...")
            self.viz_active = False
            self.viz_timer.stop()
        else:
            # Reset status if not speaking
            if not self.speaking:
                self.reset_state()
    
    def reset_state(self):
        """Reset to idle state"""
        self.listening = False
        self.speaking = False
        self.processing = False
        
        self.status_label.setText("Ready")
        self.mic_button.setIcon(QIcon("assets/ui/icons/mic.png"))
        
        # Stop visualization
        self.viz_active = False
        self.viz_timer.stop()
    
    def paintEvent(self, event):
        """Custom paint event for audio visualization"""
        super().paintEvent(event)
        
        # Only draw visualization when active
        if not self.viz_active:
            return
            
        # Get visualization frame rect
        rect = self.viz_frame.rect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        
        # Create painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set up pen and brush
        if self.listening:
            # Green color scheme for listening
            color1 = QColor(0, 200, 100)
            color2 = QColor(0, 140, 70)
        elif self.speaking:
            # Purple color scheme for speaking
            color1 = QColor(170, 50, 220)
            color2 = QColor(120, 20, 160)
        else:
            # Blue color scheme for idle
            color1 = QColor(0, 120, 255)
            color2 = QColor(0, 80, 180)
        
        # Update visualization data (simulated here)
        import random
        if self.listening or self.speaking:
            # Simulate audio levels
            for i in range(len(self.viz_data)):
                # More movement when active
                target = random.random() * 0.8 + 0.2
                # Smooth transition
                self.viz_data[i] = self.viz_data[i] * 0.7 + target * 0.3
        else:
            # Idle state - low movement
            for i in range(len(self.viz_data)):
                target = random.random() * 0.3 + 0.1
                self.viz_data[i] = self.viz_data[i] * 0.9 + target * 0.1
        
        # Draw bars
        bar_width = w / (len(self.viz_data) * 2)
        for i, value in enumerate(self.viz_data):
            # Calculate bar position and size
            bar_height = value * h
            bar_x = x + i * bar_width * 2 + bar_width / 2
            bar_y = y + (h - bar_height)
            
            # Create gradient for bar
            gradient = QLinearGradient(
                bar_x, bar_y, 
                bar_x, bar_y + bar_height
            )
            gradient.setColorAt(0, color1)
            gradient.setColorAt(1, color2)
            
            # Draw bar
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(
                bar_x, bar_y, 
                bar_width, bar_height, 
                2, 2
            )
        
        painter.end() 