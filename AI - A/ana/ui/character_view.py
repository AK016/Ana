#!/usr/bin/env python3
# Ana AI Assistant - Character Visualization Module

import os
import time
import random
import logging
import math
from threading import Thread, Event
from typing import Dict, List, Any, Optional
import glob

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer, QPropertyAnimation, QPoint, QEasingCurve
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QRadialGradient, QPainterPath, QImage
from PyQt5.QtSvg import QSvgRenderer

logger = logging.getLogger('Ana.CharacterView')

class CharacterView(QWidget):
    """
    Character visualization for Ana using anime-style assets with animations
    
    Features:
    - Pre-made anime-style character assets
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
        self.eye_blink = False
        self.mouth_openness = 0.0
        self.head_offset = QPoint(0, 0)
        self.breath_offset = 0
        self.breath_in = True
        self.head_tilt = 0  # Add head tilt parameter
        
        # Cyberpunk color scheme - adjusted for dark-haired character
        self.primary_color = QColor(0, 220, 200)  # Cyan
        self.secondary_color = QColor(130, 0, 200)  # Purple
        self.accent_color = QColor(220, 50, 100)  # Pink
        self.bg_color = QColor(10, 15, 25)  # Dark blue-black
        
        # Character assets
        self.assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'character')
        self.character_parts = {
            'base': None,  # Base face
            'eyes': {},    # Different eye states
            'mouth': {},   # Different mouth states
            'eyebrows': {},# Different eyebrow states
            'hair': None,  # Hair layer
            'blush': None, # Blush overlay
            'effects': {}  # Special effects like glows
        }
        
        # Debug mode - draw directly rather than using assets if True
        self.debug_mode = True
        
        # Current display layers
        self.current_eyes = 'neutral'
        self.current_mouth = 'neutral'
        self.current_eyebrows = 'neutral'
        self.current_effects = []
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Set up animation timers
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(33)  # ~30 fps
        
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.blink_eyes)
        self.blink_timer.start(random.randint(3000, 6000))  # Random blink interval
        
        # Breathing animation
        self.breath_timer = QTimer(self)
        self.breath_timer.timeout.connect(self.update_breathing)
        self.breath_timer.start(50)  # Smooth breathing
        
        # Idle animation thread
        self.idle_stop_event = Event()
        self.idle_thread = Thread(target=self._idle_animation_loop, daemon=True)
        self.idle_thread.start()
        
        # Load character assets
        self.load_character_assets()
        
        logger.info("Character view initialized")
    
    def load_character_assets(self):
        """Load character assets from the assets folder"""
        logger.info("Loading character assets from: %s", self.assets_path)
        
        # Check if the assets directory exists, if not create placeholder assets
        if not os.path.exists(self.assets_path):
            os.makedirs(self.assets_path, exist_ok=True)
            self.create_placeholder_assets()
            logger.warning("Created placeholder assets as no assets were found")
        
        # Try to load existing assets
        try:
            # Base face
            base_path = os.path.join(self.assets_path, 'base.png')
            if os.path.exists(base_path):
                self.character_parts['base'] = QPixmap(base_path)
            
            # Hair
            hair_path = os.path.join(self.assets_path, 'hair.png')
            if os.path.exists(hair_path):
                self.character_parts['hair'] = QPixmap(hair_path)
            
            # Blush
            blush_path = os.path.join(self.assets_path, 'blush.png')
            if os.path.exists(blush_path):
                self.character_parts['blush'] = QPixmap(blush_path)
            
            # Eyes
            for eye_state in ['neutral', 'happy', 'sad', 'surprised', 'thinking', 'blink']:
                eye_path = os.path.join(self.assets_path, f'eyes_{eye_state}.png')
                if os.path.exists(eye_path):
                    self.character_parts['eyes'][eye_state] = QPixmap(eye_path)
            
            # Mouth
            for mouth_state in ['neutral', 'happy', 'sad', 'surprised', 'thinking', 'speak1', 'speak2', 'speak3']:
                mouth_path = os.path.join(self.assets_path, f'mouth_{mouth_state}.png')
                if os.path.exists(mouth_path):
                    self.character_parts['mouth'][mouth_state] = QPixmap(mouth_path)
            
            # Eyebrows
            for brow_state in ['neutral', 'happy', 'sad', 'surprised', 'thinking']:
                brow_path = os.path.join(self.assets_path, f'eyebrows_{brow_state}.png')
                if os.path.exists(brow_path):
                    self.character_parts['eyebrows'][brow_state] = QPixmap(brow_path)
            
            # Effects
            for effect_type in ['glow_teal', 'glow_purple', 'listening', 'speaking', 'thinking']:
                effect_path = os.path.join(self.assets_path, f'effect_{effect_type}.png')
                if os.path.exists(effect_path):
                    self.character_parts['effects'][effect_type] = QPixmap(effect_path)
            
            logger.info("Character assets loaded successfully")
        
        except Exception as e:
            logger.error(f"Error loading character assets: {str(e)}")
            self.create_placeholder_assets()
    
    def create_placeholder_assets(self):
        """Create placeholder assets for development"""
        logger.info("Creating placeholder character assets")
        
        # Base face - create a simple oval face with skin tone
        base = QPixmap(400, 400)
        base.fill(Qt.transparent)
        painter = QPainter(base)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(40, 30, 35), 2))
        painter.setBrush(QBrush(QColor(245, 230, 225)))
        painter.drawEllipse(100, 80, 200, 260)
        painter.end()
        self.character_parts['base'] = base
        base.save(os.path.join(self.assets_path, 'base.png'), 'PNG')
        
        # Hair - dark with colored highlights
        hair = QPixmap(400, 400)
        hair.fill(Qt.transparent)
        painter = QPainter(hair)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        
        # Create gradient for hair
        gradient = QRadialGradient(220, 150, 200)
        gradient.setColorAt(0.4, QColor(20, 25, 30))
        gradient.setColorAt(0.8, QColor(30, 35, 40))
        painter.setBrush(QBrush(gradient))
        
        # Draw hair shape
        path = QPainterPath()
        path.moveTo(80, 120)
        path.quadTo(160, 40, 240, 50)
        path.quadTo(320, 60, 340, 150)
        path.lineTo(340, 260)
        path.quadTo(300, 350, 200, 360)
        path.quadTo(100, 350, 60, 260)
        path.lineTo(60, 150)
        path.closeSubpath()
        
        painter.drawPath(path)
        
        # Add colored highlights
        painter.setPen(QPen(QColor(0, 220, 200, 120), 5))
        painter.drawLine(80, 150, 90, 250)
        painter.setPen(QPen(QColor(130, 0, 200, 120), 5))
        painter.drawLine(320, 150, 310, 250)
        painter.end()
        
        self.character_parts['hair'] = hair
        hair.save(os.path.join(self.assets_path, 'hair.png'), 'PNG')
        
        # Eyes for different states
        eye_states = {
            'neutral': {'size': 1.0, 'position': 0},
            'happy': {'size': 0.8, 'position': 0},
            'sad': {'size': 0.9, 'position': 5},
            'surprised': {'size': 1.2, 'position': -5},
            'thinking': {'size': 1.0, 'position': -3},
            'blink': {'size': 0.1, 'position': 0}
        }
        
        for state, params in eye_states.items():
            eyes = QPixmap(400, 400)
            eyes.fill(Qt.transparent)
            painter = QPainter(eyes)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Left eye
            painter.setPen(QPen(QColor(40, 40, 50), 2))
            painter.setBrush(QBrush(QColor(245, 245, 250)))
            eye_width = 35 * params['size']
            eye_height = 20 * params['size']
            painter.drawEllipse(150 - eye_width/2, 180 + params['position'] - eye_height/2, eye_width, eye_height)
            
            # Right eye
            painter.drawEllipse(250 - eye_width/2, 180 + params['position'] - eye_height/2, eye_width, eye_height)
            
            # Iris
            if state != 'blink':
                painter.setBrush(QBrush(QColor(30, 40, 50)))
                iris_size = 20 * params['size']
                painter.drawEllipse(150 - iris_size/2, 180 + params['position'] - iris_size/2, iris_size, iris_size)
                painter.drawEllipse(250 - iris_size/2, 180 + params['position'] - iris_size/2, iris_size, iris_size)
                
                # Highlight
                painter.setBrush(QBrush(QColor(0, 220, 200, 180)))
                painter.drawEllipse(145 - iris_size/4, 177 + params['position'] - iris_size/6, iris_size/2, iris_size/4)
                painter.drawEllipse(245 - iris_size/4, 177 + params['position'] - iris_size/6, iris_size/2, iris_size/4)
                
                # Small white highlight
                painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
                highlight_size = iris_size/5
                painter.drawEllipse(155 - highlight_size/2, 175 + params['position'] - highlight_size/2, highlight_size, highlight_size)
                painter.drawEllipse(255 - highlight_size/2, 175 + params['position'] - highlight_size/2, highlight_size, highlight_size)
            
            painter.end()
            self.character_parts['eyes'][state] = eyes
            eyes.save(os.path.join(self.assets_path, f'eyes_{state}.png'), 'PNG')
        
        # Mouth for different states
        mouth_states = {
            'neutral': {'width': 30, 'height': 3, 'curve': 0},
            'happy': {'width': 40, 'height': 10, 'curve': 10},
            'sad': {'width': 30, 'height': 10, 'curve': -10},
            'surprised': {'width': 25, 'height': 25, 'curve': 0},
            'thinking': {'width': 20, 'height': 5, 'curve': -5},
            'speak1': {'width': 35, 'height': 15, 'curve': 5},
            'speak2': {'width': 30, 'height': 20, 'curve': 0},
            'speak3': {'width': 25, 'height': 10, 'curve': -5}
        }
        
        for state, params in mouth_states.items():
            mouth = QPixmap(400, 400)
            mouth.fill(Qt.transparent)
            painter = QPainter(mouth)
            painter.setRenderHint(QPainter.Antialiasing)
            
            painter.setPen(QPen(QColor(80, 50, 50), 2))
            
            if state == 'surprised' or state.startswith('speak'):
                painter.setBrush(QBrush(QColor(50, 20, 20, 180)))
                painter.drawEllipse(200 - params['width']/2, 260 - params['height']/2, params['width'], params['height'])
            else:
                path = QPainterPath()
                path.moveTo(200 - params['width']/2, 260)
                path.quadTo(200, 260 + params['curve'], 200 + params['width']/2, 260)
                painter.drawPath(path)
            
            painter.end()
            self.character_parts['mouth'][state] = mouth
            mouth.save(os.path.join(self.assets_path, f'mouth_{state}.png'), 'PNG')
        
        # Eyebrows for different states
        brow_states = {
            'neutral': {'angle_left': -10, 'angle_right': 10, 'offset': 0},
            'happy': {'angle_left': -5, 'angle_right': 5, 'offset': -2},
            'sad': {'angle_left': 15, 'angle_right': -15, 'offset': 0},
            'surprised': {'angle_left': -20, 'angle_right': 20, 'offset': -10},
            'thinking': {'angle_left': 0, 'angle_right': -20, 'offset': -5}
        }
        
        for state, params in brow_states.items():
            brows = QPixmap(400, 400)
            brows.fill(Qt.transparent)
            painter = QPainter(brows)
            painter.setRenderHint(QPainter.Antialiasing)
            
            painter.setPen(QPen(QColor(20, 25, 30), 3))
            
            # Left eyebrow
            painter.save()
            painter.translate(150, 150 + params['offset'])
            painter.rotate(params['angle_left'])
            painter.drawLine(-20, 0, 20, 0)
            painter.restore()
            
            # Right eyebrow
            painter.save()
            painter.translate(250, 150 + params['offset'])
            painter.rotate(params['angle_right'])
            painter.drawLine(-20, 0, 20, 0)
            painter.restore()
            
            painter.end()
            self.character_parts['eyebrows'][state] = brows
            brows.save(os.path.join(self.assets_path, f'eyebrows_{state}.png'), 'PNG')
        
        # Blush
        blush = QPixmap(400, 400)
        blush.fill(Qt.transparent)
        painter = QPainter(blush)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 150, 150, 80)))
        painter.drawEllipse(110, 220, 60, 30)
        painter.drawEllipse(230, 220, 60, 30)
        
        painter.end()
        self.character_parts['blush'] = blush
        blush.save(os.path.join(self.assets_path, 'blush.png'), 'PNG')
        
        # Effects
        effect_types = {
            'glow_teal': QColor(0, 220, 200, 40),
            'glow_purple': QColor(130, 0, 200, 40),
            'listening': QColor(220, 50, 100, 30),
            'speaking': QColor(0, 220, 200, 30),
            'thinking': QColor(130, 0, 200, 30)
        }
        
        for effect_type, color in effect_types.items():
            effect = QPixmap(400, 400)
            effect.fill(Qt.transparent)
            painter = QPainter(effect)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Create gradient
            gradient = QRadialGradient(200, 200, 150)
            gradient.setColorAt(0, color)
            gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(50, 50, 300, 300)
            
            painter.end()
            self.character_parts['effects'][effect_type] = effect
            effect.save(os.path.join(self.assets_path, f'effect_{effect_type}.png'), 'PNG')
        
        logger.info("Placeholder character assets created")
    
    def paintEvent(self, event):
        """Paint the character visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        
        # Calculate scale factor to fit the character in the widget
        scale_factor = min(width, height) / 400.0
        
        # Paint background
        painter.fillRect(self.rect(), self.bg_color)
        
        # Check if we should use direct drawing mode
        use_direct_drawing = self.debug_mode or not self._check_assets_loaded()
        
        # If in direct drawing mode, draw the character directly
        if use_direct_drawing:
            # Set up the transform for the entire character
            painter.save()
            painter.translate(center_x, center_y)
            painter.translate(self.head_offset.x(), self.head_offset.y() + self.breath_offset)
            
            # Draw cyberpunk lighting effects
            radius = min(width, height) * 0.4
            self._paint_cyberpunk_lighting(painter, 0, 0, radius)
            
            # Draw character face and features
            self._paint_face(painter, 0, 0, radius)
            
            # Draw ambient tech features
            self._paint_ambient_features(painter, 0, 0, radius)
            
            painter.restore()
            return
        
        # From here on, use the asset-based rendering approach
        # Translate to center and apply head movement
        painter.translate(center_x - 200 * scale_factor + self.head_offset.x(), 
                         center_y - 200 * scale_factor + self.head_offset.y())
        painter.scale(scale_factor, scale_factor)
        
        # Draw effect underneath if speaking/listening
        if self.is_speaking and 'speaking' in self.character_parts['effects']:
            effect_pixmap = self.character_parts['effects']['speaking']
            painter.setOpacity(0.3 + 0.7 * self.pulse_opacity)
            painter.drawPixmap(0, 0, effect_pixmap)
            painter.setOpacity(1.0)
        elif self.is_listening and 'listening' in self.character_parts['effects']:
            effect_pixmap = self.character_parts['effects']['listening']
            painter.setOpacity(0.3 + 0.7 * self.pulse_opacity)
            painter.drawPixmap(0, 0, effect_pixmap)
            painter.setOpacity(1.0)
        
        # Apply breathing animation
        painter.translate(0, self.breath_offset)
        
        # Draw base character parts in order
        if self.character_parts['base']:
            painter.drawPixmap(0, 0, self.character_parts['base'])
        
        # Draw eyes
        eye_state = 'blink' if self.eye_blink else self.current_eyes
        if eye_state in self.character_parts['eyes']:
            painter.drawPixmap(0, 0, self.character_parts['eyes'][eye_state])
        
        # Draw eyebrows
        if self.current_eyebrows in self.character_parts['eyebrows']:
            painter.drawPixmap(0, 0, self.character_parts['eyebrows'][self.current_eyebrows])
        
        # Draw mouth
        mouth_state = self.current_mouth
        if self.is_speaking:
            # Cycle through speaking frames
            speak_frames = [k for k in self.character_parts['mouth'].keys() if k.startswith('speak')]
            if speak_frames:
                frame_idx = int(time.time() * 5) % len(speak_frames)
                mouth_state = speak_frames[frame_idx]
        
        if mouth_state in self.character_parts['mouth']:
            painter.drawPixmap(0, 0, self.character_parts['mouth'][mouth_state])
        
        # Draw hair on top
        if self.character_parts['hair']:
            painter.drawPixmap(0, 0, self.character_parts['hair'])
        
        # Draw blush if happy or surprised
        if self.current_emotion in ['happy', 'surprised'] and self.character_parts['blush']:
            painter.drawPixmap(0, 0, self.character_parts['blush'])
        
        # Draw overlay effects based on state
        for effect in self.current_effects:
            if effect in self.character_parts['effects']:
                painter.setOpacity(0.7)
                painter.drawPixmap(0, 0, self.character_parts['effects'][effect])
                painter.setOpacity(1.0)
    
    def update_animation(self):
        """Update animation parameters for the next frame"""
        # Update pulse effect for speaking/listening
        self.pulse_opacity += self.pulse_direction
        if self.pulse_opacity > 1.0 or self.pulse_opacity < 0.0:
            self.pulse_direction *= -1
            self.pulse_opacity = max(0.0, min(1.0, self.pulse_opacity))
        
        # Refresh the view
        self.update()
    
    def update_breathing(self):
        """Update breathing animation"""
        if self.breath_in:
            self.breath_offset -= 0.1
            if self.breath_offset <= -2:
                self.breath_in = False
        else:
            self.breath_offset += 0.1
            if self.breath_offset >= 2:
                self.breath_in = True
    
    def blink_eyes(self):
        """Perform an eye blink"""
        self.eye_blink = True
        QTimer.singleShot(150, self._stop_blink)
        
        # Reset blink timer with random interval
        self.blink_timer.start(random.randint(3000, 6000))
    
    def _stop_blink(self):
        """Stop blinking"""
        self.eye_blink = False
    
    def _idle_animation_loop(self):
        """Background thread for idle animations"""
        while not self.idle_stop_event.is_set():
            # Only do idle animations when not speaking or listening
            if not self.is_speaking and not self.is_listening:
                # Random subtle head movements
                if random.random() < 0.02:  # 2% chance per cycle
                    self._perform_head_movement()
                
                # Random emotion changes when idle for a while
                if random.random() < 0.005:  # 0.5% chance per cycle
                    emotions = ["neutral", "happy", "thinking"]
                    self.set_emotion(random.choice(emotions))
            
            # Sleep to avoid consuming too much CPU
            time.sleep(0.1)
    
    def _perform_head_movement(self):
        """Perform a subtle head movement"""
        # Random movement
        target_x = random.randint(-5, 5)
        target_y = random.randint(-3, 3)
        
        # Create animation for smooth movement
        for i in range(10):
            progress = i / 10.0
            self.head_offset = QPoint(
                int(progress * target_x),
                int(progress * target_y)
            )
            time.sleep(0.02)
        
        # Hold briefly
        time.sleep(0.5)
        
        # Return to center
        for i in range(15):
            progress = i / 15.0
            self.head_offset = QPoint(
                int(target_x * (1.0 - progress)),
                int(target_y * (1.0 - progress))
            )
            time.sleep(0.02)
    
    def set_emotion(self, emotion: str):
        """Set character emotion"""
        valid_emotions = ["neutral", "happy", "sad", "surprised", "thinking"]
        if emotion in valid_emotions:
            self.current_emotion = emotion
            self.current_eyes = emotion
            self.current_mouth = emotion
            self.current_eyebrows = emotion
            
            # Set appropriate effects
            self.current_effects = []
            if emotion == "thinking":
                self.current_effects.append("glow_purple")
            elif emotion == "happy":
                self.current_effects.append("glow_teal")
            
            logger.info(f"Character emotion set to: {emotion}")
        else:
            logger.warning(f"Invalid emotion: {emotion}")
    
    def on_wake_word(self):
        """Handle wake word detection event"""
        # First show surprised emotion
        self.set_emotion("surprised")
        
        # Animate listening
        self.on_listening(True)
        
        # Schedule to stop listening after a delay
        QTimer.singleShot(3000, lambda: self.on_listening(False))
        
        # Log the event
        logger.info("Wake word detected, animating character response")
    
    def on_listening(self, is_listening):
        """Handle listening state changes"""
        self.is_listening = is_listening
        
        if is_listening:
            self.set_emotion("surprised")
            self.current_effects.append("listening")
            logger.info("Listening started, animating character")
        else:
            self.set_emotion("neutral")
            if "listening" in self.current_effects:
                self.current_effects.remove("listening")
            logger.info("Listening stopped, returning to neutral")
    
    def on_processing(self, is_processing):
        """Handle processing state changes"""
        if is_processing:
            self.set_emotion("thinking")
            self.current_effects.append("thinking")
            logger.info("Processing started, showing thinking animation")
        else:
            self.set_emotion("neutral")
            if "thinking" in self.current_effects:
                self.current_effects.remove("thinking")
            logger.info("Processing completed, returning to neutral")
    
    def on_speaking(self, text=None):
        """Handle speaking state changes"""
        self.is_speaking = True
        
        if text:
            # If we have text, estimate duration based on text length
            # Roughly 100 characters per second
            duration = max(1000, len(text) * 10)
            self.set_emotion("happy")
            self.current_effects.append("speaking")
            
            # Create a timer to stop the speaking animation
            QTimer.singleShot(duration, self._stop_speaking)
            
            logger.info(f"Speaking started, animating for {duration}ms")
        else:
            # If no text, use a default duration
            QTimer.singleShot(1000, self._stop_speaking)
            logger.info("Speaking started with default duration")
    
    def _stop_speaking(self):
        """Stop speaking animation"""
        self.is_speaking = False
        if "speaking" in self.current_effects:
            self.current_effects.remove("speaking")
        self.animation_complete.emit()
        logger.info("Speaking animation stopped")
    
    def on_idle(self, is_idle=True):
        """Handle idle state changes"""
        if is_idle:
            self.set_emotion("neutral")
            logger.info("Idle state activated, returning to neutral")
    
    def set_energy_level(self, level: float):
        """Set the character's energy level (0.0 to 1.0)"""
        self.energy_level = max(0.0, min(1.0, level))
        self.update()
    
    # Make sure to clean up the thread on close
    def closeEvent(self, event):
        """Clean up threads on close"""
        self.idle_stop_event.set()
        if self.idle_thread.is_alive():
            self.idle_thread.join(timeout=1.0)
        super().closeEvent(event)

    def _paint_face(self, painter, center_x, center_y, radius):
        """Paint the character's face - realistic anime-style female character"""
        # Draw head shape - more realistic anime face
        skin_color = QColor(245, 230, 225)  # Pale skin tone
        painter.setPen(QPen(QColor(40, 30, 35), 1))  # Darker subtle outline
        painter.setBrush(QBrush(skin_color))
        
        # Apply head tilt if any
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.head_tilt)
        painter.translate(-center_x, -center_y)
        
        # Draw face shape - more realistic oval face
        face_path = QPainterPath()
        
        # Top of head
        face_path.moveTo(center_x - radius * 0.65, center_y - radius * 0.7)
        face_path.quadTo(center_x, center_y - radius * 0.85, center_x + radius * 0.65, center_y - radius * 0.7)
        
        # Right side of face
        face_path.quadTo(center_x + radius * 0.75, center_y, center_x + radius * 0.55, center_y + radius * 0.6)
        
        # Chin (more natural)
        face_path.quadTo(center_x, center_y + radius * 0.75, center_x - radius * 0.55, center_y + radius * 0.6)
        
        # Left side of face
        face_path.quadTo(center_x - radius * 0.75, center_y, center_x - radius * 0.65, center_y - radius * 0.7)
        
        painter.drawPath(face_path)
        
        # Draw dark hair like in the reference image
        self._paint_dark_hair(painter, center_x, center_y, radius)
        
        # Draw realistic eyes
        self._paint_realistic_eyes(painter, center_x, center_y, radius)
        
        # Draw eyebrows
        self._paint_dark_eyebrows(painter, center_x, center_y, radius)
        
        # Draw nose
        self._paint_realistic_nose(painter, center_x, center_y, radius)
        
        # Draw mouth
        self._paint_realistic_mouth(painter, center_x, center_y, radius)
        
        # Draw additional facial details
        self._paint_realistic_details(painter, center_x, center_y, radius)
        
        # Add cyberpunk lighting effects
        self._paint_cyberpunk_lighting(painter, center_x, center_y, radius)
        
        # Restore painter
        painter.restore()

    def _paint_dark_hair(self, painter, center_x, center_y, radius):
        """Paint realistic dark hair like in the reference image"""
        # Hair colors - dark with teal/cyan highlights for cyberpunk effect
        hair_color = QColor(15, 20, 25)  # Very dark hair
        hair_highlight_teal = QColor(0, 220, 200, 120)  # Teal highlight
        hair_highlight_purple = QColor(130, 0, 200, 120)  # Purple highlight
        
        # Create gradient for the cyberpunk effect
        gradient = QRadialGradient(center_x + radius * 0.3, center_y - radius * 0.2, radius * 2.2)
        gradient.setColorAt(0.4, hair_color)
        gradient.setColorAt(0.7, QColor(30, 35, 40))
        gradient.setColorAt(1.0, QColor(10, 15, 20))
        
        # Hair silhouette
        hair_path = QPainterPath()
        
        # Top of hair with volume - slightly messy
        hair_path.moveTo(center_x - radius * 0.8, center_y - radius * 0.5)
        hair_path.quadTo(center_x - radius * 0.4, center_y - radius * 1.1, center_x, center_y - radius * 0.9)
        hair_path.quadTo(center_x + radius * 0.4, center_y - radius * 1.1, center_x + radius * 0.8, center_y - radius * 0.5)
        
        # Right side - longer hair like the reference image
        hair_path.lineTo(center_x + radius * 0.95, center_y + radius * 0.3)
        
        # Medium-length hair with slight wave
        hair_path.quadTo(center_x + radius * 1.0, center_y + radius * 0.8, center_x + radius * 0.7, center_y + radius * 1.3)
        
        # Bottom/back of hair
        hair_path.quadTo(center_x + radius * 0.3, center_y + radius * 1.6, center_x, center_y + radius * 1.5)
        hair_path.quadTo(center_x - radius * 0.3, center_y + radius * 1.6, center_x - radius * 0.7, center_y + radius * 1.3)
        
        # Left side - longer hair with wave
        hair_path.quadTo(center_x - radius * 1.0, center_y + radius * 0.8, center_x - radius * 0.95, center_y + radius * 0.3)
        
        # Close the path
        hair_path.closeSubpath()
        
        # Set gradient brush for the hair
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawPath(hair_path)
        
        # Add some loose strands of hair
        painter.setPen(QPen(hair_color, 1.5))
        
        # Left side loose strand
        strand_path1 = QPainterPath()
        strand_path1.moveTo(center_x - radius * 0.7, center_y - radius * 0.3)
        strand_path1.quadTo(center_x - radius * 0.9, center_y, center_x - radius * 0.8, center_y + radius * 0.4)
        strand_path1.quadTo(center_x - radius * 0.7, center_y + radius * 0.7, center_x - radius * 0.6, center_y + radius * 0.9)
        painter.drawPath(strand_path1)
        
        # Right side loose strand
        strand_path2 = QPainterPath()
        strand_path2.moveTo(center_x + radius * 0.5, center_y - radius * 0.2)
        strand_path2.quadTo(center_x + radius * 0.65, center_y + radius * 0.2, center_x + radius * 0.7, center_y + radius * 0.6)
        strand_path2.quadTo(center_x + radius * 0.8, center_y + radius * 0.9, center_x + radius * 0.6, center_y + radius * 1.2)
        painter.drawPath(strand_path2)
        
        # Face-framing strand
        strand_path3 = QPainterPath()
        strand_path3.moveTo(center_x - radius * 0.2, center_y - radius * 0.5)
        strand_path3.quadTo(center_x - radius * 0.3, center_y - radius * 0.3, center_x - radius * 0.35, center_y - radius * 0.1)
        strand_path3.quadTo(center_x - radius * 0.4, center_y + radius * 0.2, center_x - radius * 0.45, center_y + radius * 0.5)
        painter.drawPath(strand_path3)
        
        # Add cyberpunk-style colored highlights
        # Teal highlight on left
        highlight_path1 = QPainterPath()
        highlight_path1.moveTo(center_x - radius * 0.7, center_y - radius * 0.4)
        highlight_path1.quadTo(center_x - radius * 0.8, center_y, center_x - radius * 0.7, center_y + radius * 0.5)
        
        painter.setPen(QPen(hair_highlight_teal, 5))
        painter.drawPath(highlight_path1)
        
        # Purple highlight on right
        highlight_path2 = QPainterPath()
        highlight_path2.moveTo(center_x + radius * 0.6, center_y - radius * 0.3)
        highlight_path2.quadTo(center_x + radius * 0.7, center_y + radius * 0.2, center_x + radius * 0.65, center_y + radius * 0.7)
        
        painter.setPen(QPen(hair_highlight_purple, 5))
        painter.drawPath(highlight_path2)
        
        # Add bangs over forehead like in the reference image
        bangs_path = QPainterPath()
        
        # Left part of bangs
        bangs_path.moveTo(center_x - radius * 0.5, center_y - radius * 0.6)
        bangs_path.quadTo(center_x - radius * 0.3, center_y - radius * 0.3, center_x - radius * 0.2, center_y - radius * 0.4)
        
        # Center part of bangs
        bangs_path.quadTo(center_x, center_y - radius * 0.3, center_x + radius * 0.2, center_y - radius * 0.4)
        
        # Right part of bangs
        bangs_path.quadTo(center_x + radius * 0.3, center_y - radius * 0.3, center_x + radius * 0.5, center_y - radius * 0.6)
        
        painter.setPen(QPen(hair_color, 2))
        painter.drawPath(bangs_path)

    def _paint_cyberpunk_lighting(self, painter, center_x, center_y, radius):
        """Add cyberpunk-style lighting effects to the character"""
        # Create teal lighting on left side (like the reference image)
        gradient_teal = QRadialGradient(center_x - radius * 0.8, center_y, radius * 1.5)
        gradient_teal.setColorAt(0, QColor(0, 220, 200, 60))  # Teal
        gradient_teal.setColorAt(0.5, QColor(0, 220, 200, 20))
        gradient_teal.setColorAt(1, QColor(0, 0, 0, 0))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient_teal))
        painter.setOpacity(0.7)
        painter.drawEllipse(
            int(center_x - radius * 1.5),
            int(center_y - radius),
            int(radius * 2),
            int(radius * 2)
        )
        
        # Create pink/red lighting on right side (like the reference image)
        gradient_pink = QRadialGradient(center_x + radius * 0.8, center_y, radius * 1.5)
        gradient_pink.setColorAt(0, QColor(220, 50, 100, 60))  # Pink
        gradient_pink.setColorAt(0.5, QColor(220, 50, 100, 20))
        gradient_pink.setColorAt(1, QColor(0, 0, 0, 0))
        
        painter.setBrush(QBrush(gradient_pink))
        painter.drawEllipse(
            int(center_x),
            int(center_y - radius),
            int(radius * 2),
            int(radius * 2)
        )
        
        # Add some small glowing dots for cyberpunk effect
        small_glow_positions = [
            (center_x - radius * 0.9, center_y - radius * 0.5, self.primary_color),
            (center_x + radius * 0.9, center_y - radius * 0.5, self.accent_color),
            (center_x - radius * 0.8, center_y + radius * 0.7, self.primary_color),
            (center_x + radius * 0.8, center_y + radius * 0.7, self.accent_color)
        ]
        
        for x, y, color in small_glow_positions:
            glow = QRadialGradient(x, y, radius * 0.1)
            glow_color = QColor(color)
            glow_color.setAlpha(150)
            glow.setColorAt(0, glow_color)
            glow.setColorAt(1, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 0))
            
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(
                int(x - radius * 0.1),
                int(y - radius * 0.1),
                int(radius * 0.2),
                int(radius * 0.2)
            )
        
        painter.setOpacity(1.0)

    def _paint_ambient_features(self, painter, center_x, center_y, radius):
        """Paint ambient cyberpunk features around the anime character"""
        # Add subtle tech-inspired elements
        painter.setPen(QPen(self.primary_color, 1))
        
        # Left side tech lines
        painter.drawLine(
            int(center_x - radius * 1.1),
            int(center_y - radius * 0.3),
            int(center_x - radius * 0.9),
            int(center_y - radius * 0.3)
        )
        
        painter.drawLine(
            int(center_x - radius * 1.1),
            int(center_y),
            int(center_x - radius * 0.95),
            int(center_y)
        )
        
        painter.drawLine(
            int(center_x - radius * 1.1),
            int(center_y + radius * 0.3),
            int(center_x - radius * 0.9),
            int(center_y + radius * 0.3)
        )
        
        # Right side tech lines
        painter.drawLine(
            int(center_x + radius * 0.9),
            int(center_y - radius * 0.3),
            int(center_x + radius * 1.1),
            int(center_y - radius * 0.3)
        )
        
        painter.drawLine(
            int(center_x + radius * 0.95),
            int(center_y),
            int(center_x + radius * 1.1),
            int(center_y)
        )
        
        painter.drawLine(
            int(center_x + radius * 0.9),
            int(center_y + radius * 0.3),
            int(center_x + radius * 1.1),
            int(center_y + radius * 0.3)
        )
        
        # Add small tech "nodes"
        painter.setBrush(QBrush(self.primary_color))
        
        # Left nodes
        for y_offset in [-0.3, 0, 0.3]:
            painter.drawEllipse(
                int(center_x - radius * 1.1) - 2,
                int(center_y + radius * y_offset) - 2,
                4, 4
            )
        
        # Right nodes
        for y_offset in [-0.3, 0, 0.3]:
            painter.drawEllipse(
                int(center_x + radius * 1.1) - 2,
                int(center_y + radius * y_offset) - 2,
                4, 4
            )
        
        # Add some anime-style tech elements - glowing circles/patterns
        glow_color = QColor(self.accent_color)
        glow_color.setAlpha(50)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow_color))
        
        # Top tech circle
        painter.drawEllipse(
            int(center_x - radius * 0.15),
            int(center_y - radius * 1.2),
            int(radius * 0.3),
            int(radius * 0.3)
        )
        
        # Bottom tech patterns
        pattern_path = QPainterPath()
        pattern_path.moveTo(center_x - radius * 0.2, center_y + radius * 1.1)
        pattern_path.lineTo(center_x, center_y + radius * 1.2)
        pattern_path.lineTo(center_x + radius * 0.2, center_y + radius * 1.1)
        pattern_path.closeSubpath()
        
        painter.drawPath(pattern_path)
        
        # Add cyberpunk lighting effects like in the reference image
        self._paint_cyberpunk_lighting(painter, center_x, center_y, radius)

    def _check_assets_loaded(self):
        """Check if the required assets are loaded"""
        # Check base parts
        if not self.character_parts['base'] or not self.character_parts['hair']:
            return False
            
        # Check if we have at least one of each type of eye, mouth, and eyebrow
        if not self.character_parts['eyes'] or not self.character_parts['mouth'] or not self.character_parts['eyebrows']:
            return False
            
        # Check if we have the current state
        if self.current_eyes not in self.character_parts['eyes']:
            return False
            
        if self.current_mouth not in self.character_parts['mouth']:
            return False
            
        if self.current_eyebrows not in self.character_parts['eyebrows']:
            return False
            
        return True

# For testing directly
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = CharacterView()
    widget.resize(500, 500)
    widget.show()
    
    # Test animations
    widget.on_speaking("Hello, I am Ana, your AI assistant. How can I help you today?")
    
    sys.exit(app.exec_()) 