#!/usr/bin/env python3
# Ana AI Assistant - Settings Widget

import logging
import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTabWidget, QLineEdit, QCheckBox,
    QGroupBox, QGridLayout, QColorDialog, QComboBox,
    QFormLayout, QSpinBox, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from config.settings import save_settings

logger = logging.getLogger('Ana.UI.SettingsWidget')

class SettingsWidget(QWidget):
    """Widget for configuring Ana settings"""
    
    def __init__(self, assistant, settings, theme_manager):
        """Initialize settings widget"""
        super().__init__()
        self.assistant = assistant
        self.settings = settings
        self.theme_manager = theme_manager
        
        # Initialize UI
        self._init_ui()
        
        logger.info("Settings widget initialized")
    
    def _init_ui(self):
        """Initialize the user interface"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # General tab
        self.general_tab = QWidget()
        general_layout = QVBoxLayout(self.general_tab)
        
        # Assistant settings
        assistant_group = QGroupBox("Assistant Settings")
        assistant_form = QFormLayout(assistant_group)
        
        self.name_input = QLineEdit(self.settings["assistant"]["name"])
        self.wake_word_input = QLineEdit(self.settings["assistant"]["wake_word"])
        
        assistant_form.addRow("Assistant Name:", self.name_input)
        assistant_form.addRow("Wake Word:", self.wake_word_input)
        
        # Theme settings
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QGridLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.settings["ui"]["theme"])
        self.theme_combo.currentTextChanged.connect(self._theme_changed)
        
        self.accent_color_button = QPushButton()
        self.accent_color_button.setFixedSize(30, 30)
        self.accent_color_button.setStyleSheet(f"background-color: {self.settings['ui']['accent_color']}")
        self.accent_color_button.clicked.connect(self._select_accent_color)
        
        self.secondary_color_button = QPushButton()
        self.secondary_color_button.setFixedSize(30, 30)
        self.secondary_color_button.setStyleSheet(f"background-color: {self.settings['ui']['secondary_color']}")
        self.secondary_color_button.clicked.connect(self._select_secondary_color)
        
        theme_layout.addWidget(QLabel("Theme:"), 0, 0)
        theme_layout.addWidget(self.theme_combo, 0, 1)
        theme_layout.addWidget(QLabel("Accent Color:"), 1, 0)
        theme_layout.addWidget(self.accent_color_button, 1, 1)
        theme_layout.addWidget(QLabel("Secondary Color:"), 2, 0)
        theme_layout.addWidget(self.secondary_color_button, 2, 1)
        
        # Animation settings
        animation_group = QGroupBox("Animation Settings")
        animation_layout = QVBoxLayout(animation_group)
        
        self.character_animation_checkbox = QCheckBox("Enable Character Animation")
        self.character_animation_checkbox.setChecked(self.settings["ui"]["character_animation"])
        
        self.idle_animations_checkbox = QCheckBox("Enable Idle Animations")
        self.idle_animations_checkbox.setChecked(self.settings["ui"]["idle_animations"])
        
        animation_layout.addWidget(self.character_animation_checkbox)
        animation_layout.addWidget(self.idle_animations_checkbox)
        
        # Add to general layout
        general_layout.addWidget(assistant_group)
        general_layout.addWidget(theme_group)
        general_layout.addWidget(animation_group)
        general_layout.addStretch()
        
        # API tab
        self.api_tab = QWidget()
        api_layout = QVBoxLayout(self.api_tab)
        
        # ElevenLabs settings
        elevenlabs_group = QGroupBox("ElevenLabs Voice Settings")
        elevenlabs_form = QFormLayout(elevenlabs_group)
        
        self.elevenlabs_api_key = QLineEdit(self.settings["assistant"]["elevenlabs"]["api_key"])
        self.elevenlabs_api_key.setEchoMode(QLineEdit.Password)
        self.elevenlabs_voice_id = QLineEdit(self.settings["assistant"]["elevenlabs"]["voice_id"])
        
        elevenlabs_form.addRow("API Key:", self.elevenlabs_api_key)
        elevenlabs_form.addRow("Voice ID:", self.elevenlabs_voice_id)
        
        # OpenAI settings
        openai_group = QGroupBox("OpenAI API Settings")
        openai_form = QFormLayout(openai_group)
        
        self.openai_api_key = QLineEdit(self.settings["assistant"]["openai"]["api_key"])
        self.openai_api_key.setEchoMode(QLineEdit.Password)
        
        self.openai_model = QComboBox()
        self.openai_model.addItems(["gpt-4o", "gpt-4", "gpt-3.5-turbo"])
        self.openai_model.setCurrentText(self.settings["assistant"]["openai"]["model"])
        
        openai_form.addRow("API Key:", self.openai_api_key)
        openai_form.addRow("Model:", self.openai_model)
        
        # Add to API layout
        api_layout.addWidget(elevenlabs_group)
        api_layout.addWidget(openai_group)
        api_layout.addStretch()
        
        # Features tab
        self.features_tab = QWidget()
        features_layout = QVBoxLayout(self.features_tab)
        
        # Calendar settings
        calendar_group = QGroupBox("Calendar Integration")
        calendar_layout = QVBoxLayout(calendar_group)
        
        self.calendar_enabled_checkbox = QCheckBox("Enable Calendar Integration")
        self.calendar_enabled_checkbox.setChecked(self.settings["features"]["calendar"]["enabled"])
        
        calendar_layout.addWidget(self.calendar_enabled_checkbox)
        
        # Health settings
        health_group = QGroupBox("Health Integration")
        health_layout = QVBoxLayout(health_group)
        
        self.health_enabled_checkbox = QCheckBox("Enable Health Integration")
        self.health_enabled_checkbox.setChecked(self.settings["features"]["health"]["enabled"])
        
        health_layout.addWidget(self.health_enabled_checkbox)
        
        # Music settings
        music_group = QGroupBox("Music Integration")
        music_layout = QVBoxLayout(music_group)
        
        self.music_enabled_checkbox = QCheckBox("Enable Music Integration")
        self.music_enabled_checkbox.setChecked(self.settings["features"]["music"]["enabled"])
        
        self.spotify_enabled_checkbox = QCheckBox("Enable Spotify")
        self.spotify_enabled_checkbox.setChecked(self.settings["features"]["music"]["spotify_enabled"])
        
        self.youtube_music_checkbox = QCheckBox("Enable YouTube Music")
        self.youtube_music_checkbox.setChecked(self.settings["features"]["music"]["youtube_music_enabled"])
        
        music_layout.addWidget(self.music_enabled_checkbox)
        music_layout.addWidget(self.spotify_enabled_checkbox)
        music_layout.addWidget(self.youtube_music_checkbox)
        
        # Add to features layout
        features_layout.addWidget(calendar_group)
        features_layout.addWidget(health_group)
        features_layout.addWidget(music_group)
        features_layout.addStretch()
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.general_tab, "General")
        self.tab_widget.addTab(self.api_tab, "API")
        self.tab_widget.addTab(self.features_tab, "Features")
        
        # Save button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self._save_settings)
        
        # Add widgets to layout
        self.layout.addWidget(self.tab_widget)
        self.layout.addWidget(self.save_button)
    
    def _theme_changed(self, theme_name):
        """Handle theme change"""
        if self.theme_manager.set_theme(theme_name):
            self.theme_manager.apply_theme(self.window())
    
    def _select_accent_color(self):
        """Open color dialog to select accent color"""
        current_color = QColor(self.settings["ui"]["accent_color"])
        color = QColorDialog.getColor(current_color, self, "Select Accent Color")
        
        if color.isValid():
            hex_color = color.name()
            self.settings["ui"]["accent_color"] = hex_color
            self.accent_color_button.setStyleSheet(f"background-color: {hex_color}")
            
            # Update theme
            self.theme_manager.set_accent_color(hex_color)
            self.theme_manager.apply_theme(self.window())
    
    def _select_secondary_color(self):
        """Open color dialog to select secondary color"""
        current_color = QColor(self.settings["ui"]["secondary_color"])
        color = QColorDialog.getColor(current_color, self, "Select Secondary Color")
        
        if color.isValid():
            hex_color = color.name()
            self.settings["ui"]["secondary_color"] = hex_color
            self.secondary_color_button.setStyleSheet(f"background-color: {hex_color}")
            
            # Update theme
            self.theme_manager.set_secondary_color(hex_color)
            self.theme_manager.apply_theme(self.window())
    
    def _save_settings(self):
        """Save settings"""
        # Update settings from UI
        self.settings["assistant"]["name"] = self.name_input.text()
        self.settings["assistant"]["wake_word"] = self.wake_word_input.text()
        
        self.settings["ui"]["character_animation"] = self.character_animation_checkbox.isChecked()
        self.settings["ui"]["idle_animations"] = self.idle_animations_checkbox.isChecked()
        
        self.settings["assistant"]["elevenlabs"]["api_key"] = self.elevenlabs_api_key.text()
        self.settings["assistant"]["elevenlabs"]["voice_id"] = self.elevenlabs_voice_id.text()
        
        self.settings["assistant"]["openai"]["api_key"] = self.openai_api_key.text()
        self.settings["assistant"]["openai"]["model"] = self.openai_model.currentText()
        
        self.settings["features"]["calendar"]["enabled"] = self.calendar_enabled_checkbox.isChecked()
        self.settings["features"]["health"]["enabled"] = self.health_enabled_checkbox.isChecked()
        self.settings["features"]["music"]["enabled"] = self.music_enabled_checkbox.isChecked()
        self.settings["features"]["music"]["spotify_enabled"] = self.spotify_enabled_checkbox.isChecked()
        self.settings["features"]["music"]["youtube_music_enabled"] = self.youtube_music_checkbox.isChecked()
        
        # Save to file
        if save_settings(self.settings):
            logger.info("Settings saved successfully")
            
            # Notify user (would be better with a toast notification)
            save_label = QLabel("Settings saved!")
            self.layout.addWidget(save_label)
            
            # Remove notification after a delay
            QTimer.singleShot(3000, lambda: save_label.setParent(None)) 