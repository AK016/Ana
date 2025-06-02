#!/usr/bin/env python3
# Ana AI Assistant - Character Widget

import os
import logging
import random
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QGraphicsOpacityEffect, QSizePolicy
)
from PyQt5.QtCore import (
    Qt, QSize, QTimer, QPropertyAnimation, 
    QEasingCurve, QRect, pyqtSignal, QPoint
)
from PyQt5.QtGui import (
    QPixmap, QMovie, QPainter, QColor,
    QPainterPath, QPen, QBrush, QRadialGradient
)

logger = logging.getLogger('Ana.UI.CharacterWidget')

class CharacterWidget(QWidget):
    """Widget for displaying and animating Ana's character"""
    
    def __init__(self, settings):
        """Initialize character widget with settings"""
        super().__init__()
        self.settings = settings
        self.character_path = settings["paths"]["character_assets"]
        self.current_state = "idle"
        self.animation_enabled = settings["ui"]["character_animation"]
        self.idle_animations = settings["ui"]["idle_animations"]
        
        # Set up widget properties
        self.setMinimumSize(120, 120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Initialize UI
        self._init_ui()
        
        # Set up animation timers
        self._setup_timers()
        
        logger.info("Character widget initialized")
    
    def _init_ui(self):
        """Initialize the user interface"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Character display label
        self.character_label = QLabel()
        self.character_label.setAlignment(Qt.AlignCenter)
        self.character_label.setScaledContents(True)
        self.character_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Add glow effect
        self.glow_effect = QGraphicsOpacityEffect()
        self.glow_effect.setOpacity(1.0)
        self.character_label.setGraphicsEffect(self.glow_effect)
        
        # Add to layout
        self.layout.addWidget(self.character_label)
        
        # Load character images and animations
        self._load_character_assets()
        
        # Set initial state
        self.set_state("idle")
    
    def _load_character_assets(self):
        """Load character images and animations"""
        try:
            # Character state images
            self.state_images = {}
            self.state_movies = {}
            
            # Define states and corresponding image files
            states = ["idle", "listening", "speaking", "processing"]
            
            for state in states:
                # Check for static image
                img_path = os.path.join(self.character_path, f"{state}.png")
                if os.path.exists(img_path):
                    self.state_images[state] = QPixmap(img_path)
                    logger.debug(f"Loaded character image for state: {state}")
                
                # Check for animated GIF
                gif_path = os.path.join(self.character_path, f"{state}.gif")
                if os.path.exists(gif_path):
                    movie = QMovie(gif_path)
                    movie.setCacheMode(QMovie.CacheAll)
                    self.state_movies[state] = movie
                    logger.debug(f"Loaded character animation for state: {state}")
            
            # If we don't have an idle image, create a placeholder
            if "idle" not in self.state_images and "idle" not in self.state_movies:
                # Create a placeholder image
                placeholder = QPixmap(300, 400)
                placeholder.fill(Qt.transparent)
                
                # Draw a silhouette as placeholder
                painter = QPainter(placeholder)
                painter.setRenderHint(QPainter.Antialiasing)
                
                # Draw a face silhouette
                painter.setPen(QPen(QColor("#00b0ff"), 2))
                painter.setBrush(QBrush(QColor(0, 0, 0, 40)))
                
                # Draw silhouette shape
                path = QPainterPath()
                path.addEllipse(100, 50, 100, 120)  # Head
                path.addRect(110, 170, 80, 150)     # Body
                painter.drawPath(path)
                
                # Add text
                painter.setPen(QPen(QColor("#ffffff")))
                painter.drawText(placeholder.rect(), Qt.AlignCenter, "Ana")
                
                painter.end()
                
                self.state_images["idle"] = placeholder
                logger.warning("Using placeholder image for idle state")
        
        except Exception as e:
            logger.error(f"Error loading character assets: {str(e)}")
            # Create a simple placeholder
            placeholder = QPixmap(200, 300)
            placeholder.fill(Qt.transparent)
            self.state_images["idle"] = placeholder
    
    def set_state(self, state):
        """Set the character state and update display"""
        if state not in ["idle", "listening", "speaking", "processing"]:
            logger.warning(f"Invalid character state: {state}")
            state = "idle"
        
        self.current_state = state
        
        # Stop any playing movie
        for movie in self.state_movies.values():
            movie.stop()
        
        # Check for animated state
        if state in self.state_movies and self.animation_enabled:
            movie = self.state_movies[state]
            self.character_label.setMovie(movie)
            movie.start()
            logger.debug(f"Set character state to {state} (animated)")
        
        # Otherwise use static image
        elif state in self.state_images:
            self.character_label.setMovie(None)  # Clear any movie
            self.character_label.setPixmap(self.state_images[state])
            logger.debug(f"Set character state to {state} (static)")
        
        # Apply animations based on state
        self._apply_state_animations()
    
    def _apply_state_animations(self):
        """Apply animations based on current state"""
        # Stop any existing animations
        if hasattr(self, 'glow_animation') and self.glow_animation.state() == QPropertyAnimation.Running:
            self.glow_animation.stop()
        
        # Create and configure glow animation based on state
        self.glow_animation = QPropertyAnimation(self.glow_effect, b"opacity")
        
        if self.current_state == "idle":
            if self.idle_animations:
                # Subtle breathing effect for idle
                self.glow_animation.setStartValue(0.95)
                self.glow_animation.setEndValue(1.0)
                self.glow_animation.setDuration(2000)
                self.glow_animation.setEasingCurve(QEasingCurve.InOutSine)
                self.glow_animation.setLoopCount(-1)  # Infinite loop
                self.glow_animation.start()
        
        elif self.current_state == "listening":
            # Pulsing effect for listening
            self.glow_animation.setStartValue(0.8)
            self.glow_animation.setEndValue(1.0)
            self.glow_animation.setDuration(800)
            self.glow_animation.setEasingCurve(QEasingCurve.InOutSine)
            self.glow_animation.setLoopCount(-1)  # Infinite loop
            self.glow_animation.start()
        
        elif self.current_state == "speaking":
            # Sharp pulses for speaking
            self.glow_animation.setStartValue(0.9)
            self.glow_animation.setEndValue(1.0)
            self.glow_animation.setDuration(300)
            self.glow_animation.setEasingCurve(QEasingCurve.OutCubic)
            self.glow_animation.setLoopCount(-1)  # Infinite loop
            self.glow_animation.start()
        
        elif self.current_state == "processing":
            # Slow, deep pulse for processing
            self.glow_animation.setStartValue(0.7)
            self.glow_animation.setEndValue(1.0)
            self.glow_animation.setDuration(1500)
            self.glow_animation.setEasingCurve(QEasingCurve.InOutCubic)
            self.glow_animation.setLoopCount(-1)  # Infinite loop
            self.glow_animation.start()
    
    def _setup_timers(self):
        """Set up timers for idle animations"""
        # Idle animation timer
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self._idle_animation_tick)
        
        # Only start if idle animations are enabled
        if self.idle_animations and self.animation_enabled:
            self.idle_timer.start(5000)  # Run idle animation every 5 seconds
    
    def _idle_animation_tick(self):
        """Perform a random idle animation"""
        if self.current_state != "idle" or not self.idle_animations:
            return
            
        # Random idle animations
        idle_actions = [
            self._idle_blink,
            self._idle_look_around,
            self._idle_subtle_move
        ]
        
        # Randomly choose an idle action
        if random.random() < 0.3:  # 30% chance of performing an idle action
            random.choice(idle_actions)()
    
    def _idle_blink(self):
        """Blink animation for idle state"""
        # This would be implemented with actual eye animations
        # Here we just do a quick opacity change
        blink_anim = QPropertyAnimation(self.glow_effect, b"opacity")
        blink_anim.setStartValue(1.0)
        blink_anim.setEndValue(0.7)
        blink_anim.setDuration(150)
        blink_anim.setEasingCurve(QEasingCurve.OutQuad)
        
        # Set up return animation
        def blink_return():
            return_anim = QPropertyAnimation(self.glow_effect, b"opacity")
            return_anim.setStartValue(0.7)
            return_anim.setEndValue(1.0)
            return_anim.setDuration(150)
            return_anim.start()
        
        # Connect animations
        blink_anim.finished.connect(blink_return)
        blink_anim.start()
    
    def _idle_look_around(self):
        """Look around animation for idle state"""
        # This would be implemented with actual eye/head movements
        # Here we just do a small shift
        if not hasattr(self, "original_pos"):
            self.original_pos = self.character_label.pos()
        
        # Random direction
        dx = random.randint(-5, 5)
        
        # Move animation
        move_anim = QPropertyAnimation(self.character_label, b"pos")
        move_anim.setStartValue(self.character_label.pos())
        move_anim.setEndValue(self.original_pos + QPoint(dx, 0))
        move_anim.setDuration(500)
        move_anim.setEasingCurve(QEasingCurve.InOutCubic)
        
        # Return animation
        def move_return():
            return_anim = QPropertyAnimation(self.character_label, b"pos")
            return_anim.setStartValue(self.character_label.pos())
            return_anim.setEndValue(self.original_pos)
            return_anim.setDuration(500)
            return_anim.setEasingCurve(QEasingCurve.InOutCubic)
            return_anim.start()
        
        # Connect animations
        move_anim.finished.connect(move_return)
        move_anim.start()
    
    def _idle_subtle_move(self):
        """Subtle movement animation for idle state"""
        # Small scale change to simulate breathing
        scale_anim = QPropertyAnimation(self, b"size")
        scale_anim.setStartValue(self.size())
        scale_anim.setEndValue(QSize(self.width(), int(self.height() * 1.01)))
        scale_anim.setDuration(1000)
        scale_anim.setEasingCurve(QEasingCurve.InOutSine)
        
        # Return animation
        def scale_return():
            return_anim = QPropertyAnimation(self, b"size")
            return_anim.setStartValue(self.size())
            return_anim.setEndValue(QSize(self.width(), self.height()))
            return_anim.setDuration(1000)
            return_anim.setEasingCurve(QEasingCurve.InOutSine)
            return_anim.start()
        
        # Connect animations
        scale_anim.finished.connect(scale_return)
        scale_anim.start()
    
    def paintEvent(self, event):
        """Custom paint event to add effects"""
        super().paintEvent(event)
        
        # For potential custom background effects
        if self.animation_enabled:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw a subtle glow behind the character based on state
            if self.current_state == "idle":
                glow_color = QColor(0, 120, 255, 30)  # Subtle blue
            elif self.current_state == "listening":
                glow_color = QColor(0, 200, 100, 40)  # Green tint
            elif self.current_state == "speaking":
                glow_color = QColor(200, 50, 255, 40)  # Purple tint
            elif self.current_state == "processing":
                glow_color = QColor(255, 150, 0, 40)  # Orange tint
            
            # Create a radial gradient for the glow
            center = self.rect().center()
            radius = min(self.width(), self.height()) * 0.6
            gradient = QRadialGradient(center, radius)
            gradient.setColorAt(0, glow_color)
            gradient.setColorAt(1, QColor(0, 0, 0, 0))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, radius, radius)
            
            painter.end() 