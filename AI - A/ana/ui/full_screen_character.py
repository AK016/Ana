#!/usr/bin/env python3
# Ana AI Assistant - Full Screen Character View

import os
import time
import random
import logging
import requests
import json
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect,
    QPushButton, QDialog, QFrame, QHBoxLayout, QComboBox,
    QApplication
)
from PyQt5.QtCore import (
    Qt, QSize, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QRect
)
from PyQt5.QtGui import (
    QPixmap, QPainter, QColor, QPen, QBrush, QRadialGradient,
    QLinearGradient, QFont, QIcon, QImage
)

from ui.character_view import CharacterView

logger = logging.getLogger('Ana.FullScreenCharacter')

class BackgroundType(Enum):
    """Types of backgrounds for the character view"""
    SOLID = "solid"
    GRADIENT = "gradient"
    CYBERPUNK_CITY = "cyberpunk_city"
    MATRIX = "matrix"
    WEATHER = "weather"
    CUSTOM = "custom"

class FullScreenCharacter(QDialog):
    """
    Full screen character view for Ana with animated backgrounds
    
    Features:
    - Full screen display of Ana character
    - Dynamic backgrounds based on weather or context
    - Transition animations
    - Customizable themes
    """
    
    # Signals
    closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initialize properties
        self.background_type = BackgroundType.GRADIENT
        self.background_color = QColor(10, 10, 25)  # Dark blue-black
        self.weather_condition = "clear"
        self.custom_background_path = ""
        self.time_of_day = "day"
        self.text_message = ""
        
        # Cyberpunk colors
        self.neon_pink = QColor(255, 60, 120)
        self.neon_blue = QColor(0, 255, 204)
        self.neon_purple = QColor(170, 0, 255)
        
        # Setup UI
        self._setup_ui()
        
        # Animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)  # 20 fps
        
        # Animation parameters
        self.particle_positions = []
        self.matrix_columns = []
        self.weather_particles = []
        self._init_particles()
        
        logger.info("Full screen character view initialized")
    
    def _setup_ui(self):
        """Set up the UI components"""
        # Full screen
        self.showFullScreen()
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Character view (in the center)
        self.character_view = CharacterView(self)
        self.character_view.setMinimumSize(600, 600)
        self.character_view.setMaximumSize(800, 800)
        
        # Center the character
        character_container = QWidget()
        character_container.setObjectName("character_container")
        character_layout = QHBoxLayout(character_container)
        character_layout.addStretch()
        character_layout.addWidget(self.character_view)
        character_layout.addStretch()
        
        # Text message display
        self.message_label = QLabel(self.text_message)
        self.message_label.setObjectName("fullscreen_message")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet(
            "color: #00E5FF; font-size: 24px; padding: 30px; "
            "background-color: rgba(0, 20, 40, 0.7); border-radius: 20px; "
            "border: 2px solid #00E5FF; margin: 40px;"
        )
        self.message_label.setMinimumHeight(100)
        self.message_label.setMaximumHeight(200)
        
        # Control panel at the bottom
        self.control_panel = QFrame()
        self.control_panel.setObjectName("control_panel")
        self.control_panel.setStyleSheet(
            "background-color: rgba(10, 14, 23, 0.8); "
            "border-top: 1px solid #00E5FF; "
            "padding: 10px;"
        )
        self.control_panel.setMaximumHeight(70)
        
        control_layout = QHBoxLayout(self.control_panel)
        
        # Background selector
        bg_label = QLabel("Background:")
        bg_label.setStyleSheet("color: #00E5FF;")
        self.bg_selector = QComboBox()
        self.bg_selector.addItems([
            "Gradient", "Cyberpunk City", "Matrix", "Weather", "Solid Color"
        ])
        self.bg_selector.setStyleSheet(
            "color: #00E5FF; background-color: rgba(0, 20, 40, 0.7); "
            "border: 1px solid #00E5FF; padding: 5px;"
        )
        self.bg_selector.currentIndexChanged.connect(self._on_background_changed)
        
        # Close button
        self.close_button = QPushButton("Exit Full Screen")
        self.close_button.setStyleSheet(
            "background-color: rgba(255, 60, 120, 0.3); "
            "color: #FFFFFF; padding: 10px; "
            "border: 1px solid #FF3C78; border-radius: 5px;"
        )
        self.close_button.clicked.connect(self.close)
        
        # Add widgets to control layout
        control_layout.addWidget(bg_label)
        control_layout.addWidget(self.bg_selector)
        control_layout.addStretch()
        control_layout.addWidget(self.close_button)
        
        # Add widgets to main layout
        self.layout.addStretch()
        self.layout.addWidget(character_container)
        self.layout.addWidget(self.message_label)
        self.layout.addStretch()
        self.layout.addWidget(self.control_panel)
        
        # Hide message if empty
        if not self.text_message:
            self.message_label.hide()
    
    def _init_particles(self):
        """Initialize particles for background effects"""
        # Cyberpunk city particles (lights in windows)
        self.particle_positions = []
        width, height = self.width(), self.height()
        
        # Generate random particle positions for cyberpunk city
        for _ in range(200):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(2, 6)
            blink_speed = random.uniform(0.02, 0.1)
            color_choice = random.choice([
                self.neon_pink, self.neon_blue, self.neon_purple,
                QColor(255, 255, 100), QColor(0, 255, 0)
            ])
            opacity = random.uniform(0.2, 1.0)
            
            self.particle_positions.append({
                'x': x, 'y': y, 'size': size, 
                'color': color_choice, 'opacity': opacity,
                'blink_speed': blink_speed, 'blink_direction': 1
            })
        
        # Matrix-style falling code
        self.matrix_columns = []
        col_width = 20
        num_columns = width // col_width
        
        for i in range(num_columns):
            length = random.randint(5, 30)
            speed = random.uniform(1, 5)
            x = i * col_width
            y = random.randint(-500, 0)
            
            self.matrix_columns.append({
                'x': x, 'y': y, 'length': length, 'speed': speed,
                'chars': [random.choice("01") for _ in range(length)]
            })
        
        # Weather particles (rain, snow, etc.)
        self.weather_particles = []
        
        if self.weather_condition in ["rain", "drizzle", "thunderstorm"]:
            # Rain drops
            for _ in range(300):
                x = random.randint(0, width)
                y = random.randint(-100, height)
                length = random.randint(10, 30)
                speed = random.uniform(10, 20)
                
                self.weather_particles.append({
                    'x': x, 'y': y, 'length': length, 'speed': speed,
                    'type': 'rain'
                })
                
        elif self.weather_condition in ["snow"]:
            # Snowflakes
            for _ in range(200):
                x = random.randint(0, width)
                y = random.randint(-100, height)
                size = random.uniform(2, 6)
                speed = random.uniform(1, 3)
                drift = random.uniform(-1, 1)
                
                self.weather_particles.append({
                    'x': x, 'y': y, 'size': size, 'speed': speed,
                    'drift': drift, 'type': 'snow'
                })
    
    def set_background(self, bg_type: BackgroundType, **kwargs):
        """
        Set the background type and parameters
        
        Args:
            bg_type: Background type
            **kwargs: Additional parameters for the background
        """
        self.background_type = bg_type
        
        # Process additional parameters
        if "color" in kwargs:
            self.background_color = kwargs["color"]
        
        if "weather" in kwargs:
            self.weather_condition = kwargs["weather"]
            # Reinitialize weather particles
            self.weather_particles = []
            self._init_particles()
        
        if "custom_path" in kwargs:
            self.custom_background_path = kwargs["custom_path"]
        
        if "time_of_day" in kwargs:
            self.time_of_day = kwargs["time_of_day"]
        
        # Update background
        self.update()
    
    def set_message(self, message: str):
        """Set the message text"""
        self.text_message = message
        self.message_label.setText(message)
        
        # Show message if not empty, hide if empty
        if message:
            self.message_label.show()
        else:
            self.message_label.hide()
    
    def animate_speaking(self, duration_ms: int = 0):
        """Animate character speaking"""
        self.character_view.animate_speaking(duration_ms)
    
    def animate_listening(self, active: bool = True):
        """Set character listening animation state"""
        self.character_view.animate_listening(active)
    
    def set_emotion(self, emotion: str):
        """Set character emotion"""
        self.character_view.set_emotion(emotion)
    
    def update_animation(self):
        """Update animation parameters"""
        # Update cyberpunk city lights
        for particle in self.particle_positions:
            # Update blink effect
            particle['opacity'] += particle['blink_speed'] * particle['blink_direction']
            
            if particle['opacity'] >= 1.0:
                particle['opacity'] = 1.0
                particle['blink_direction'] = -1
            elif particle['opacity'] <= 0.2:
                particle['opacity'] = 0.2
                particle['blink_direction'] = 1
        
        # Update matrix columns
        for column in self.matrix_columns:
            column['y'] += column['speed']
            
            # Reset if off screen
            if column['y'] > self.height():
                column['y'] = random.randint(-500, -50)
                column['chars'] = [random.choice("01") for _ in range(column['length'])]
        
        # Update weather particles
        width, height = self.width(), self.height()
        
        for particle in self.weather_particles:
            if particle['type'] == 'rain':
                # Move rain down
                particle['y'] += particle['speed']
                
                # Reset if off screen
                if particle['y'] > height:
                    particle['y'] = random.randint(-100, -10)
                    particle['x'] = random.randint(0, width)
                    
            elif particle['type'] == 'snow':
                # Move snow down with drift
                particle['y'] += particle['speed']
                particle['x'] += particle['drift']
                
                # Add some randomness to drift
                particle['drift'] += random.uniform(-0.1, 0.1)
                if abs(particle['drift']) > 1:
                    particle['drift'] *= 0.9
                
                # Reset if off screen
                if particle['y'] > height or particle['x'] < -10 or particle['x'] > width + 10:
                    particle['y'] = random.randint(-100, -10)
                    particle['x'] = random.randint(0, width)
                    particle['drift'] = random.uniform(-1, 1)
        
        # Trigger repaint
        self.update()
    
    def paintEvent(self, event):
        """Paint the background and effects"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Paint background based on type
        if self.background_type == BackgroundType.SOLID:
            painter.fillRect(self.rect(), self.background_color)
            
        elif self.background_type == BackgroundType.GRADIENT:
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(10, 10, 30))
            gradient.setColorAt(1, QColor(40, 10, 60))
            painter.fillRect(self.rect(), gradient)
            
            # Add a bit of noise/stars
            painter.setPen(QPen(QColor(255, 255, 255, 20)))
            for _ in range(300):
                x = random.randint(0, self.width())
                y = random.randint(0, self.height())
                size = random.randint(1, 2)
                painter.drawRect(x, y, size, size)
            
        elif self.background_type == BackgroundType.CYBERPUNK_CITY:
            self._paint_cyberpunk_city(painter)
            
        elif self.background_type == BackgroundType.MATRIX:
            self._paint_matrix_background(painter)
            
        elif self.background_type == BackgroundType.WEATHER:
            self._paint_weather_background(painter)
            
        elif self.background_type == BackgroundType.CUSTOM and os.path.exists(self.custom_background_path):
            # Load and draw custom background image
            bg_pixmap = QPixmap(self.custom_background_path)
            painter.drawPixmap(self.rect(), bg_pixmap)
    
    def _paint_cyberpunk_city(self, painter):
        """Paint cyberpunk city skyline background"""
        width, height = self.width(), self.height()
        
        # Draw night sky gradient
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(5, 5, 20))  # Dark blue at top
        gradient.setColorAt(0.5, QColor(20, 5, 40))  # Purplish in middle
        gradient.setColorAt(1, QColor(50, 10, 40))  # Reddish at bottom
        painter.fillRect(self.rect(), gradient)
        
        # Draw stars
        painter.setPen(QPen(QColor(255, 255, 255, 120)))
        for _ in range(100):
            x = random.randint(0, width)
            y = random.randint(0, height // 2)
            size = random.randint(1, 2)
            painter.drawRect(x, y, size, size)
        
        # Draw city silhouette
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.setPen(Qt.NoPen)
        
        # Ground
        painter.drawRect(0, height * 0.7, width, height * 0.3)
        
        # Buildings
        building_base_y = height * 0.7
        building_count = width // 40
        
        for i in range(building_count):
            building_x = i * 40
            building_height = random.randint(height // 6, height // 2)
            building_width = random.randint(30, 50)
            
            # Draw building silhouette
            painter.setBrush(QBrush(QColor(10, 10, 20)))
            painter.drawRect(
                building_x, building_base_y - building_height,
                building_width, building_height
            )
            
            # Draw windows
            window_rows = building_height // 15
            window_cols = building_width // 10
            
            for row in range(window_rows):
                for col in range(window_cols):
                    # Only draw some windows (random pattern)
                    if random.random() < 0.7:
                        continue
                        
                    window_x = building_x + col * 10 + 2
                    window_y = building_base_y - building_height + row * 15 + 2
                    
                    painter.setBrush(QBrush(QColor(255, 255, 100, random.randint(50, 150))))
                    painter.drawRect(window_x, window_y, 6, 10)
        
        # Draw light particles
        for particle in self.particle_positions:
            painter.setOpacity(particle['opacity'])
            painter.setBrush(QBrush(particle['color']))
            painter.setPen(Qt.NoPen)
            
            painter.drawEllipse(
                int(particle['x']), int(particle['y']),
                int(particle['size']), int(particle['size'])
            )
        
        painter.setOpacity(1.0)
    
    def _paint_matrix_background(self, painter):
        """Paint Matrix-style falling code background"""
        width, height = self.width(), self.height()
        
        # Draw black background
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        
        # Draw falling code
        for column in self.matrix_columns:
            x = column['x']
            y = column['y']
            chars = column['chars']
            
            # Draw each character in the column
            for i, char in enumerate(chars):
                # Fade as they fall
                opacity = 1.0 - (i / len(chars))
                
                # Lead character is brightest
                if i == 0:
                    painter.setPen(QPen(QColor(220, 255, 220)))
                else:
                    green = int(min(255, 180 * opacity + 30))
                    painter.setPen(QPen(QColor(30, green, 30, int(255 * opacity))))
                
                # Draw character
                painter.setFont(QFont("Courier New", 12))
                painter.drawText(
                    x, y + i * 20,
                    char
                )
    
    def _paint_weather_background(self, painter):
        """Paint weather-based background"""
        width, height = self.width(), self.height()
        
        # Background based on weather and time
        if self.time_of_day == "night":
            # Night sky
            gradient = QLinearGradient(0, 0, 0, height)
            gradient.setColorAt(0, QColor(5, 10, 30))  # Dark blue at top
            gradient.setColorAt(1, QColor(20, 20, 40))  # Lighter blue at bottom
            
        elif self.time_of_day == "sunset":
            # Sunset
            gradient = QLinearGradient(0, 0, 0, height)
            gradient.setColorAt(0, QColor(50, 20, 60))  # Purple at top
            gradient.setColorAt(0.5, QColor(200, 80, 50))  # Orange in middle
            gradient.setColorAt(1, QColor(250, 150, 50))  # Yellow at bottom
            
        else:  # day
            if self.weather_condition in ["clear", "few clouds"]:
                # Clear day
                gradient = QLinearGradient(0, 0, 0, height)
                gradient.setColorAt(0, QColor(100, 180, 255))  # Blue at top
                gradient.setColorAt(1, QColor(200, 230, 255))  # Lighter blue at bottom
                
            elif self.weather_condition in ["clouds", "overcast"]:
                # Cloudy day
                gradient = QLinearGradient(0, 0, 0, height)
                gradient.setColorAt(0, QColor(100, 100, 150))  # Grayish blue at top
                gradient.setColorAt(1, QColor(180, 180, 200))  # Lighter gray at bottom
                
            elif self.weather_condition in ["rain", "drizzle", "thunderstorm"]:
                # Rainy day
                gradient = QLinearGradient(0, 0, 0, height)
                gradient.setColorAt(0, QColor(60, 70, 90))  # Dark gray at top
                gradient.setColorAt(1, QColor(100, 110, 130))  # Medium gray at bottom
                
            elif self.weather_condition in ["snow"]:
                # Snowy day
                gradient = QLinearGradient(0, 0, 0, height)
                gradient.setColorAt(0, QColor(180, 190, 200))  # Light gray at top
                gradient.setColorAt(1, QColor(220, 225, 235))  # Almost white at bottom
                
            else:
                # Default day
                gradient = QLinearGradient(0, 0, 0, height)
                gradient.setColorAt(0, QColor(100, 180, 255))
                gradient.setColorAt(1, QColor(200, 230, 255))
        
        # Draw background
        painter.fillRect(self.rect(), gradient)
        
        # Draw weather particles
        for particle in self.weather_particles:
            if particle['type'] == 'rain':
                # Draw rain drops
                painter.setPen(QPen(QColor(200, 230, 255, 180), 1))
                painter.drawLine(
                    particle['x'], particle['y'],
                    particle['x'], particle['y'] + particle['length']
                )
                
            elif particle['type'] == 'snow':
                # Draw snowflakes
                painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(
                    particle['x'], particle['y'],
                    particle['size'], particle['size']
                )
    
    def _on_background_changed(self, index):
        """Handle background selection change"""
        bg_types = [
            BackgroundType.GRADIENT,
            BackgroundType.CYBERPUNK_CITY,
            BackgroundType.MATRIX,
            BackgroundType.WEATHER,
            BackgroundType.SOLID
        ]
        
        if index < len(bg_types):
            self.set_background(bg_types[index])
    
    def get_weather(self, city="New York"):
        """Get weather data for a given city"""
        try:
            # This would normally use a proper API key and service
            # For demo, just return a random weather condition
            conditions = ["clear", "clouds", "rain", "snow", "thunderstorm", "drizzle"]
            self.weather_condition = random.choice(conditions)
            
            # Update weather particles
            self.weather_particles = []
            self._init_particles()
            
            # Update background if weather type
            if self.background_type == BackgroundType.WEATHER:
                self.update()
                
            return self.weather_condition
            
        except Exception as e:
            logger.error(f"Error getting weather: {str(e)}")
            return "clear"
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            self.close()
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.animation_timer.stop()
        self.closed.emit()
        super().closeEvent(event)


# For testing directly
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    window = FullScreenCharacter()
    window.show()
    
    # Test different backgrounds
    # window.set_background(BackgroundType.CYBERPUNK_CITY)
    # window.set_background(BackgroundType.MATRIX)
    # window.set_background(BackgroundType.WEATHER, weather="rain")
    
    # Test messaging
    window.set_message("Hello, I am Ana. How can I help you today?")
    
    # Test speaking animation
    window.animate_speaking(2000)
    
    sys.exit(app.exec_()) 