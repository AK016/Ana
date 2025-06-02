#!/usr/bin/env python3
# Ana AI Assistant - Character Visualization Module

import os
import time
import random
import logging
import math
from threading import Thread, Event
from typing import Dict, List, Any, Optional

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QRadialGradient
from PyQt5.QtSvg import QSvgRenderer

logger = logging.getLogger('Ana.CharacterView')

class CharacterView(QWidget):
    """
    Character visualization for Ana with cyberpunk aesthetics and animations
    
    Features:
    - Procedurally generated character visualization (no external assets needed)
    - Facial expressions and emotions
    - Speech and listening animations
    - Idle animations and gestures
    """
    
    # Signals
    animation_complete = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        
        # Character state
        self.current_emotion = "neutral"  # neutral, happy, sad, surprised, thinking
        self.is_speaking = False
        self.is_listening = False
        self.energy_level = 0.8  # 0.0 to 1.0
        
        # Animation parameters
        self.pulse_opacity = 0.0
        self.pulse_direction = 0.05
        self.eye_size = 1.0
        self.mouth_openness = 0.0
        self.head_tilt = 0.0
        
        # Cyberpunk color scheme
        self.primary_color = QColor(0, 255, 204)  # Cyan/teal
        self.secondary_color = QColor(170, 0, 255)  # Purple
        self.accent_color = QColor(255, 60, 120)  # Pink
        self.bg_color = QColor(10, 10, 25)  # Dark blue-black
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Set up animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(33)  # ~30 fps
        
        # Idle animation thread
        self.idle_stop_event = Event()
        self.idle_thread = Thread(target=self._idle_animation_loop, daemon=True)
        self.idle_thread.start()
        
        logger.info("Character view initialized")
    
    def paintEvent(self, event):
        """Paint the character visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        
        # Paint background
        painter.fillRect(self.rect(), self.bg_color)
        
        # Paint energy aura/halo
        self._paint_energy_aura(painter, center_x, center_y, min(width, height) * 0.45)
        
        # Paint face
        face_radius = min(width, height) * 0.25
        self._paint_face(painter, center_x, center_y, face_radius)
        
        # Paint pulses if speaking or listening
        if self.is_speaking or self.is_listening:
            self._paint_pulses(painter, center_x, center_y, min(width, height) * 0.4)
    
    def _paint_energy_aura(self, painter, center_x, center_y, radius):
        """Paint energy aura around character"""
        # Create gradient for aura
        gradient = QRadialGradient(center_x, center_y, radius * 1.5)
        
        # Set gradient colors based on emotion
        if self.current_emotion == "happy":
            gradient.setColorAt(0, QColor(0, 255, 204, 40))  # Cyan with alpha
            gradient.setColorAt(0.7, QColor(0, 200, 160, 10))
            gradient.setColorAt(1, QColor(0, 150, 120, 0))
        elif self.current_emotion == "sad":
            gradient.setColorAt(0, QColor(50, 100, 200, 40))  # Blue with alpha
            gradient.setColorAt(0.7, QColor(40, 80, 160, 10))
            gradient.setColorAt(1, QColor(30, 60, 120, 0))
        elif self.current_emotion == "surprised":
            gradient.setColorAt(0, QColor(255, 100, 200, 40))  # Pink with alpha
            gradient.setColorAt(0.7, QColor(200, 80, 160, 10))
            gradient.setColorAt(1, QColor(150, 60, 120, 0))
        elif self.current_emotion == "thinking":
            gradient.setColorAt(0, QColor(180, 130, 255, 40))  # Purple with alpha
            gradient.setColorAt(0.7, QColor(150, 100, 200, 10))
            gradient.setColorAt(1, QColor(120, 80, 150, 0))
        else:  # neutral
            gradient.setColorAt(0, QColor(0, 200, 200, 40))  # Teal with alpha
            gradient.setColorAt(0.7, QColor(0, 150, 150, 10))
            gradient.setColorAt(1, QColor(0, 100, 100, 0))
        
        # Apply energy level to aura intensity
        painter.setOpacity(0.3 + (self.energy_level * 0.7))
        
        # Paint aura
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            int(center_x - radius),
            int(center_y - radius),
            int(radius * 2),
            int(radius * 2)
        )
        
        # Reset opacity
        painter.setOpacity(1.0)
    
    def _paint_face(self, painter, center_x, center_y, radius):
        """Paint the character's face"""
        # Draw head shape
        head_color = QColor(30, 30, 45)
        painter.setPen(QPen(self.primary_color, 2))
        painter.setBrush(QBrush(head_color))
        
        # Apply head tilt if any
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.head_tilt)
        painter.translate(-center_x, -center_y)
        
        # Draw slightly elongated head shape for cyberpunk look
        painter.drawEllipse(
            int(center_x - radius * 0.8),
            int(center_y - radius),
            int(radius * 1.6),
            int(radius * 2)
        )
        
        # Draw eyes
        self._paint_eyes(painter, center_x, center_y, radius)
        
        # Draw mouth
        self._paint_mouth(painter, center_x, center_y, radius)
        
        # Draw cyberpunk details
        self._paint_details(painter, center_x, center_y, radius)
        
        # Restore painter
        painter.restore()
    
    def _paint_eyes(self, painter, center_x, center_y, radius):
        """Paint the character's eyes"""
        # Eye positioning
        eye_y = center_y - radius * 0.15
        left_eye_x = center_x - radius * 0.35
        right_eye_x = center_x + radius * 0.35
        
        eye_size_factor = 0.18 * self.eye_size
        
        # Draw eye sockets/outlines with gradient
        eye_gradient = QRadialGradient(center_x, eye_y, radius * 0.25)
        eye_gradient.setColorAt(0, self.primary_color)
        eye_gradient.setColorAt(1, QColor(0, 180, 180, 50))
        
        painter.setPen(QPen(self.primary_color, 1.5))
        painter.setBrush(QBrush(QColor(15, 15, 30)))
        
        # Left eye socket
        painter.drawEllipse(
            int(left_eye_x - radius * 0.2),
            int(eye_y - radius * 0.12),
            int(radius * 0.4),
            int(radius * 0.24)
        )
        
        # Right eye socket
        painter.drawEllipse(
            int(right_eye_x - radius * 0.2),
            int(eye_y - radius * 0.12),
            int(radius * 0.4),
            int(radius * 0.24)
        )
        
        # Draw actual eyes (iris)
        painter.setBrush(QBrush(self.primary_color))
        
        # Modify eye look based on emotion
        eye_offset_x = 0
        eye_offset_y = 0
        
        if self.current_emotion == "surprised":
            eye_size_factor *= 1.3
            eye_offset_y = -radius * 0.02
        elif self.current_emotion == "sad":
            eye_offset_y = radius * 0.03
        elif self.current_emotion == "thinking":
            eye_offset_x = radius * 0.05
            eye_offset_y = -radius * 0.03
        
        # Left eye
        painter.drawEllipse(
            int(left_eye_x - radius * eye_size_factor + eye_offset_x),
            int(eye_y - radius * eye_size_factor + eye_offset_y),
            int(radius * eye_size_factor * 2),
            int(radius * eye_size_factor * 2)
        )
        
        # Right eye
        painter.drawEllipse(
            int(right_eye_x - radius * eye_size_factor - eye_offset_x),
            int(eye_y - radius * eye_size_factor + eye_offset_y),
            int(radius * eye_size_factor * 2),
            int(radius * eye_size_factor * 2)
        )
        
        # Draw glowing pupil
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        pupil_size = eye_size_factor * 0.4
        
        # Left pupil
        painter.drawEllipse(
            int(left_eye_x - radius * pupil_size + eye_offset_x * 1.2),
            int(eye_y - radius * pupil_size + eye_offset_y * 1.2),
            int(radius * pupil_size * 2),
            int(radius * pupil_size * 2)
        )
        
        # Right pupil
        painter.drawEllipse(
            int(right_eye_x - radius * pupil_size - eye_offset_x * 1.2),
            int(eye_y - radius * pupil_size + eye_offset_y * 1.2),
            int(radius * pupil_size * 2),
            int(radius * pupil_size * 2)
        )
    
    def _paint_mouth(self, painter, center_x, center_y, radius):
        """Paint the character's mouth"""
        mouth_y = center_y + radius * 0.3
        mouth_width = radius * 0.6
        
        # Mouth shape changes with emotion and speaking
        if self.current_emotion == "happy":
            # Smiling mouth
            painter.setPen(QPen(self.primary_color, 2.5))
            painter.setBrush(Qt.NoBrush)
            
            # Draw smile arc
            start_angle = 210 * 16  # Qt angles are in 1/16th of a degree
            span_angle = 120 * 16
            
            # If speaking, make mouth open
            if self.is_speaking:
                painter.setBrush(QBrush(QColor(30, 30, 45)))
                mouth_height = radius * 0.2 * (0.5 + self.mouth_openness)
                painter.drawEllipse(
                    int(center_x - mouth_width / 2),
                    int(mouth_y - mouth_height / 2),
                    int(mouth_width),
                    int(mouth_height)
                )
            else:
                painter.drawArc(
                    int(center_x - mouth_width / 2),
                    int(mouth_y - mouth_width / 2),
                    int(mouth_width),
                    int(mouth_width),
                    start_angle,
                    span_angle
                )
                
        elif self.current_emotion == "sad":
            # Sad mouth - inverted curve
            painter.setPen(QPen(self.primary_color, 2.5))
            painter.setBrush(Qt.NoBrush)
            
            # Draw sad arc
            start_angle = 30 * 16
            span_angle = 120 * 16
            
            painter.drawArc(
                int(center_x - mouth_width / 2),
                int(mouth_y - mouth_width / 2),
                int(mouth_width),
                int(mouth_width),
                start_angle,
                span_angle
            )
            
        elif self.current_emotion == "surprised":
            # O shaped mouth
            painter.setPen(QPen(self.primary_color, 2.5))
            painter.setBrush(QBrush(QColor(30, 30, 45)))
            
            mouth_height = radius * 0.3
            painter.drawEllipse(
                int(center_x - mouth_width / 3),
                int(mouth_y - mouth_height / 2),
                int(mouth_width / 1.5),
                int(mouth_height)
            )
            
        else:
            # Neutral or speaking mouth
            painter.setPen(QPen(self.primary_color, 2.5))
            
            if self.is_speaking:
                # Open mouth when speaking
                painter.setBrush(QBrush(QColor(30, 30, 45)))
                mouth_height = radius * 0.15 * (0.5 + self.mouth_openness)
                painter.drawEllipse(
                    int(center_x - mouth_width / 2),
                    int(mouth_y - mouth_height / 2),
                    int(mouth_width),
                    int(mouth_height)
                )
            else:
                # Straight line when not speaking/neutral
                painter.drawLine(
                    int(center_x - mouth_width / 2),
                    int(mouth_y),
                    int(center_x + mouth_width / 2),
                    int(mouth_y)
                )
    
    def _paint_details(self, painter, center_x, center_y, radius):
        """Paint cyberpunk details on the character"""
        # Circuit-like lines on sides of face
        painter.setPen(QPen(self.primary_color, 1.5))
        
        # Left side circuits
        painter.drawLine(
            int(center_x - radius * 0.8),
            int(center_y - radius * 0.2),
            int(center_x - radius * 0.6),
            int(center_y - radius * 0.2)
        )
        
        painter.drawLine(
            int(center_x - radius * 0.6),
            int(center_y - radius * 0.2),
            int(center_x - radius * 0.6),
            int(center_y + radius * 0.2)
        )
        
        painter.drawLine(
            int(center_x - radius * 0.6),
            int(center_y + radius * 0.2),
            int(center_x - radius * 0.8),
            int(center_y + radius * 0.2)
        )
        
        # Right side circuits
        painter.drawLine(
            int(center_x + radius * 0.8),
            int(center_y - radius * 0.2),
            int(center_x + radius * 0.6),
            int(center_y - radius * 0.2)
        )
        
        painter.drawLine(
            int(center_x + radius * 0.6),
            int(center_y - radius * 0.2),
            int(center_x + radius * 0.6),
            int(center_y + radius * 0.2)
        )
        
        painter.drawLine(
            int(center_x + radius * 0.6),
            int(center_y + radius * 0.2),
            int(center_x + radius * 0.8),
            int(center_y + radius * 0.2)
        )
        
        # Draw "circuit nodes"
        painter.setBrush(QBrush(self.primary_color))
        
        # Left nodes
        painter.drawEllipse(
            int(center_x - radius * 0.8) - 2,
            int(center_y - radius * 0.2) - 2,
            4, 4
        )
        
        painter.drawEllipse(
            int(center_x - radius * 0.6) - 2,
            int(center_y - radius * 0.2) - 2,
            4, 4
        )
        
        painter.drawEllipse(
            int(center_x - radius * 0.6) - 2,
            int(center_y + radius * 0.2) - 2,
            4, 4
        )
        
        painter.drawEllipse(
            int(center_x - radius * 0.8) - 2,
            int(center_y + radius * 0.2) - 2,
            4, 4
        )
        
        # Right nodes
        painter.drawEllipse(
            int(center_x + radius * 0.8) - 2,
            int(center_y - radius * 0.2) - 2,
            4, 4
        )
        
        painter.drawEllipse(
            int(center_x + radius * 0.6) - 2,
            int(center_y - radius * 0.2) - 2,
            4, 4
        )
        
        painter.drawEllipse(
            int(center_x + radius * 0.6) - 2,
            int(center_y + radius * 0.2) - 2,
            4, 4
        )
        
        painter.drawEllipse(
            int(center_x + radius * 0.8) - 2,
            int(center_y + radius * 0.2) - 2,
            4, 4
        )
    
    def _paint_pulses(self, painter, center_x, center_y, radius):
        """Paint audio/visual pulses for speaking or listening"""
        # Use different colors for speaking vs listening
        if self.is_speaking:
            pulse_color = self.primary_color
        else:  # listening
            pulse_color = self.accent_color
        
        # Set translucent pulse
        pulse_color.setAlpha(int(self.pulse_opacity * 120))
        
        # Draw pulse rings
        painter.setPen(QPen(pulse_color, 2))
        painter.setBrush(Qt.NoBrush)
        
        # Multiple pulse rings
        for i in range(3):
            scale = 1.0 + (i * 0.2) + (self.pulse_opacity * 0.3)
            painter.drawEllipse(
                int(center_x - radius * scale),
                int(center_y - radius * scale),
                int(radius * 2 * scale),
                int(radius * 2 * scale)
            )
    
    def update_animation(self):
        """Update animation parameters for the next frame"""
        # Update pulse effect
        self.pulse_opacity += self.pulse_direction
        if self.pulse_opacity > 1.0 or self.pulse_opacity < 0.0:
            self.pulse_direction *= -1
            self.pulse_opacity = max(0.0, min(1.0, self.pulse_opacity))
        
        # If speaking, animate mouth
        if self.is_speaking:
            self.mouth_openness = 0.3 + 0.7 * self.pulse_opacity
        else:
            self.mouth_openness = 0.0
        
        # If listening, make eyes slightly larger
        if self.is_listening:
            self.eye_size = 1.0 + 0.2 * self.pulse_opacity
        else:
            self.eye_size = 1.0
        
        # Apply subtle head tilt animation
        if self.current_emotion == "thinking":
            self.head_tilt = 5.0 * math.sin(time.time() * 1.5)
        else:
            # Gradually return to neutral
            self.head_tilt *= 0.9
        
        # Refresh the view
        self.update()
    
    def _idle_animation_loop(self):
        """Background thread for idle animations"""
        while not self.idle_stop_event.is_set():
            # Only do idle animations when not speaking or listening
            if not self.is_speaking and not self.is_listening:
                # Random blinks
                if random.random() < 0.02:  # 2% chance per cycle
                    self._perform_blink()
                
                # Random subtle head movements
                if random.random() < 0.01:  # 1% chance per cycle
                    self._perform_head_movement()
            
            # Sleep to avoid consuming too much CPU
            time.sleep(0.1)
    
    def _perform_blink(self):
        """Perform a blinking animation"""
        for i in range(5):
            # Quick close
            self.eye_size = 1.0 - (i * 0.2)
            time.sleep(0.01)
        
        time.sleep(0.05)  # Hold closed briefly
        
        for i in range(5):
            # Quick open
            self.eye_size = 0.0 + (i * 0.2)
            time.sleep(0.02)
    
    def _perform_head_movement(self):
        """Perform a subtle head movement"""
        # Random tilt angle
        angle = random.uniform(-8, 8)
        
        # Smoothly tilt to that angle
        steps = 10
        start_angle = self.head_tilt
        
        for i in range(steps):
            progress = i / steps
            self.head_tilt = start_angle + (angle - start_angle) * progress
            time.sleep(0.02)
        
        # Hold briefly
        time.sleep(0.2)
        
        # Return to neutral more slowly
        for i in range(15):
            self.head_tilt = angle * (1.0 - (i / 15))
            time.sleep(0.03)
    
    def set_emotion(self, emotion: str):
        """Set character emotion"""
        valid_emotions = ["neutral", "happy", "sad", "surprised", "thinking"]
        if emotion in valid_emotions:
            self.current_emotion = emotion
            logger.info(f"Character emotion set to: {emotion}")
        else:
            logger.warning(f"Invalid emotion: {emotion}")
    
    def animate_speaking(self, duration_ms: int = 1000):
        """Animate character speaking for given duration"""
        # Start speaking animation
        self.is_speaking = True
        
        # Create a timer to stop the speaking animation
        QTimer.singleShot(duration_ms, self._stop_speaking)
        
        # Update immediately
        self.update()
    
    def _stop_speaking(self):
        """Stop speaking animation"""
        self.is_speaking = False
        self.animation_complete.emit()
        
        # Update immediately
        self.update()
    
    def animate_listening(self, active: bool = True):
        """Set listening animation state"""
        self.is_listening = active
        
        # Update immediately
        self.update()
    
    def set_energy_level(self, level: float):
        """Set character energy level (0.0 to 1.0)"""
        self.energy_level = max(0.0, min(1.0, level))
        
        # Update immediately
        self.update()
    
    # Make sure to clean up the thread on close
    def closeEvent(self, event):
        """Clean up threads on close"""
        self.idle_stop_event.set()
        if self.idle_thread.is_alive():
            self.idle_thread.join(timeout=1.0)
        super().closeEvent(event)

# For testing directly
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = CharacterView()
    widget.resize(500, 500)
    widget.show()
    
    # Test animations
    widget.animate_speaking(2000)
    
    sys.exit(app.exec_()) 