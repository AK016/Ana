#!/usr/bin/env python3
# Ana AI Assistant - Settings Tab

import json
import logging
import os
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QScrollArea, QFormLayout, QLineEdit, QComboBox,
    QCheckBox, QSpinBox, QDoubleSpinBox, QTabWidget, QGroupBox,
    QFileDialog, QMessageBox
)

logger = logging.getLogger('Ana.SettingsTab')

class SettingsTab(QWidget):
    """Settings interface for Ana AI Assistant"""
    
    def __init__(self, assistant, settings):
        super().__init__()
        self.assistant = assistant
        self.settings = settings
        self._setup_ui()
        self._setup_connections()
        self._load_settings()
        logger.info("Settings tab initialized")
    
    def _setup_ui(self):
        """Set up the UI components for the settings tab"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Header
        self.header = QFrame()
        self.header.setObjectName("settings_header")
        self.header.setMaximumHeight(60)
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(10, 5, 10, 5)
        
        self.header_label = QLabel("SETTINGS")
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00E5FF;")
        self.header_layout.addWidget(self.header_label)
        
        self.header_layout.addStretch()
        
        # Save button
        self.save_btn = QPushButton("SAVE")
        self.save_btn.setObjectName("primary_button")
        self.save_btn.setIcon(QIcon("../assets/icons/save.png"))
        self.save_btn.setIconSize(QSize(18, 18))
        self.header_layout.addWidget(self.save_btn)
        
        # Reset button
        self.reset_btn = QPushButton("RESET")
        self.reset_btn.setObjectName("secondary_button")
        self.reset_btn.setIcon(QIcon("../assets/icons/reset.png"))
        self.reset_btn.setIconSize(QSize(18, 18))
        self.header_layout.addWidget(self.reset_btn)
        
        self.layout.addWidget(self.header)
        
        # Settings tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("settings_tabs")
        
        # General settings tab
        self.general_tab = QWidget()
        self.general_layout = QVBoxLayout(self.general_tab)
        self.general_layout.setContentsMargins(10, 15, 10, 10)
        
        # Assistant settings group
        self.assistant_group = QGroupBox("Assistant Settings")
        self.assistant_group.setObjectName("settings_group")
        self.assistant_form = QFormLayout(self.assistant_group)
        self.assistant_form.setContentsMargins(15, 20, 15, 15)
        self.assistant_form.setSpacing(15)
        
        # Assistant name
        self.assistant_name = QLineEdit()
        self.assistant_name.setObjectName("settings_input")
        self.assistant_form.addRow("Assistant Name:", self.assistant_name)
        
        # Wake word
        self.wake_word = QLineEdit()
        self.wake_word.setObjectName("settings_input")
        self.assistant_form.addRow("Wake Word:", self.wake_word)
        
        # Self evolution toggle
        self.self_evolution = QCheckBox("Enable self-evolution")
        self.self_evolution.setObjectName("settings_checkbox")
        self.assistant_form.addRow("Self Evolution:", self.self_evolution)
        
        # Auto update toggle
        self.auto_update = QCheckBox("Enable auto-update")
        self.auto_update.setObjectName("settings_checkbox")
        self.assistant_form.addRow("Auto Update:", self.auto_update)
        
        self.general_layout.addWidget(self.assistant_group)
        
        # Voice settings group
        self.voice_group = QGroupBox("Voice Settings")
        self.voice_group.setObjectName("settings_group")
        self.voice_form = QFormLayout(self.voice_group)
        self.voice_form.setContentsMargins(15, 20, 15, 15)
        self.voice_form.setSpacing(15)
        
        # ElevenLabs API key
        self.elevenlabs_api_key = QLineEdit()
        self.elevenlabs_api_key.setObjectName("settings_input")
        self.elevenlabs_api_key.setEchoMode(QLineEdit.Password)
        self.voice_form.addRow("ElevenLabs API Key:", self.elevenlabs_api_key)
        
        # English voice ID
        self.voice_id_en = QLineEdit()
        self.voice_id_en.setObjectName("settings_input")
        self.voice_form.addRow("English Voice ID:", self.voice_id_en)
        
        # Hindi voice ID
        self.voice_id_hi = QLineEdit()
        self.voice_id_hi.setObjectName("settings_input")
        self.voice_form.addRow("Hindi Voice ID:", self.voice_id_hi)
        
        # Porcupine access key
        self.porcupine_key = QLineEdit()
        self.porcupine_key.setObjectName("settings_input")
        self.porcupine_key.setEchoMode(QLineEdit.Password)
        self.voice_form.addRow("Porcupine Access Key:", self.porcupine_key)
        
        self.general_layout.addWidget(self.voice_group)
        
        # Add to tabs
        self.tabs.addTab(self.general_tab, "General")
        
        # API settings tab
        self.api_tab = QWidget()
        self.api_layout = QVBoxLayout(self.api_tab)
        self.api_layout.setContentsMargins(10, 15, 10, 10)
        
        # OpenAI settings group
        self.openai_group = QGroupBox("OpenAI Settings")
        self.openai_group.setObjectName("settings_group")
        self.openai_form = QFormLayout(self.openai_group)
        self.openai_form.setContentsMargins(15, 20, 15, 15)
        self.openai_form.setSpacing(15)
        
        # OpenAI toggle
        self.openai_enabled = QCheckBox("Enable OpenAI")
        self.openai_enabled.setObjectName("settings_checkbox")
        self.openai_form.addRow("OpenAI Integration:", self.openai_enabled)
        
        # OpenAI API key
        self.openai_api_key = QLineEdit()
        self.openai_api_key.setObjectName("settings_input")
        self.openai_api_key.setEchoMode(QLineEdit.Password)
        self.openai_form.addRow("API Key:", self.openai_api_key)
        
        # OpenAI model
        self.openai_model = QComboBox()
        self.openai_model.setObjectName("settings_dropdown")
        self.openai_model.addItems(["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"])
        self.openai_form.addRow("Model:", self.openai_model)
        
        self.api_layout.addWidget(self.openai_group)
        
        # GitHub settings group
        self.github_group = QGroupBox("GitHub Settings")
        self.github_group.setObjectName("settings_group")
        self.github_form = QFormLayout(self.github_group)
        self.github_form.setContentsMargins(15, 20, 15, 15)
        self.github_form.setSpacing(15)
        
        # GitHub toggle
        self.github_enabled = QCheckBox("Enable GitHub Integration")
        self.github_enabled.setObjectName("settings_checkbox")
        self.github_form.addRow("GitHub Integration:", self.github_enabled)
        
        # GitHub username
        self.github_username = QLineEdit()
        self.github_username.setObjectName("settings_input")
        self.github_form.addRow("Username:", self.github_username)
        
        # GitHub email
        self.github_email = QLineEdit()
        self.github_email.setObjectName("settings_input")
        self.github_form.addRow("Email:", self.github_email)
        
        # GitHub token
        self.github_token = QLineEdit()
        self.github_token.setObjectName("settings_input")
        self.github_token.setEchoMode(QLineEdit.Password)
        self.github_form.addRow("Token:", self.github_token)
        
        # GitHub repo URL
        self.github_repo = QLineEdit()
        self.github_repo.setObjectName("settings_input")
        self.github_form.addRow("Repository URL:", self.github_repo)
        
        # Auto push toggle
        self.github_auto_push = QCheckBox("Enable auto-push")
        self.github_auto_push.setObjectName("settings_checkbox")
        self.github_form.addRow("Auto Push:", self.github_auto_push)
        
        self.api_layout.addWidget(self.github_group)
        
        # Add to tabs
        self.tabs.addTab(self.api_tab, "API Settings")
        
        # UI settings tab
        self.ui_tab = QWidget()
        self.ui_layout = QVBoxLayout(self.ui_tab)
        self.ui_layout.setContentsMargins(10, 15, 10, 10)
        
        # UI settings group
        self.ui_group = QGroupBox("UI Settings")
        self.ui_group.setObjectName("settings_group")
        self.ui_form = QFormLayout(self.ui_group)
        self.ui_form.setContentsMargins(15, 20, 15, 15)
        self.ui_form.setSpacing(15)
        
        # Theme
        self.ui_theme = QComboBox()
        self.ui_theme.setObjectName("settings_dropdown")
        self.ui_theme.addItems(["cyberpunk", "minimal", "futuristic", "classic"])
        self.ui_form.addRow("Theme:", self.ui_theme)
        
        # Color scheme
        self.ui_color_scheme = QComboBox()
        self.ui_color_scheme.setObjectName("settings_dropdown")
        self.ui_color_scheme.addItems(["dark", "light", "auto"])
        self.ui_form.addRow("Color Scheme:", self.ui_color_scheme)
        
        # Animation level
        self.ui_animation = QComboBox()
        self.ui_animation.setObjectName("settings_dropdown")
        self.ui_animation.addItems(["high", "medium", "low", "off"])
        self.ui_form.addRow("Animation Level:", self.ui_animation)
        
        # Font size
        self.ui_font_size = QComboBox()
        self.ui_font_size.setObjectName("settings_dropdown")
        self.ui_font_size.addItems(["small", "medium", "large"])
        self.ui_form.addRow("Font Size:", self.ui_font_size)
        
        self.ui_layout.addWidget(self.ui_group)
        
        # Feature settings group
        self.features_group = QGroupBox("Feature Settings")
        self.features_group.setObjectName("settings_group")
        self.features_form = QFormLayout(self.features_group)
        self.features_form.setContentsMargins(15, 20, 15, 15)
        self.features_form.setSpacing(15)
        
        # Wake word detection
        self.feature_wake_word = QCheckBox("Enable wake word detection")
        self.feature_wake_word.setObjectName("settings_checkbox")
        self.features_form.addRow("Wake Word Detection:", self.feature_wake_word)
        
        # Wake word sensitivity
        self.wake_word_sensitivity = QDoubleSpinBox()
        self.wake_word_sensitivity.setObjectName("settings_spinner")
        self.wake_word_sensitivity.setRange(0.0, 1.0)
        self.wake_word_sensitivity.setSingleStep(0.1)
        self.wake_word_sensitivity.setDecimals(1)
        self.features_form.addRow("Wake Word Sensitivity:", self.wake_word_sensitivity)
        
        # Facial recognition
        self.feature_facial = QCheckBox("Enable facial recognition")
        self.feature_facial.setObjectName("settings_checkbox")
        self.features_form.addRow("Facial Recognition:", self.feature_facial)
        
        # Emotion detection
        self.feature_emotion = QCheckBox("Enable emotion detection")
        self.feature_emotion.setObjectName("settings_checkbox")
        self.features_form.addRow("Emotion Detection:", self.feature_emotion)
        
        # Multilingual support
        self.feature_multilingual = QCheckBox("Enable multilingual support")
        self.feature_multilingual.setObjectName("settings_checkbox")
        self.features_form.addRow("Multilingual Support:", self.feature_multilingual)
        
        # Default language
        self.default_language = QComboBox()
        self.default_language.setObjectName("settings_dropdown")
        self.default_language.addItems(["en", "hi"])
        self.features_form.addRow("Default Language:", self.default_language)
        
        self.ui_layout.addWidget(self.features_group)
        
        # Add to tabs
        self.tabs.addTab(self.ui_tab, "UI & Features")
        
        # System settings tab
        self.system_tab = QWidget()
        self.system_layout = QVBoxLayout(self.system_tab)
        self.system_layout.setContentsMargins(10, 15, 10, 10)
        
        # System settings group
        self.system_group = QGroupBox("System Settings")
        self.system_group.setObjectName("settings_group")
        self.system_form = QFormLayout(self.system_group)
        self.system_form.setContentsMargins(15, 20, 15, 15)
        self.system_form.setSpacing(15)
        
        # Logging level
        self.logging_level = QComboBox()
        self.logging_level.setObjectName("settings_dropdown")
        self.logging_level.addItems(["debug", "info", "warning", "error"])
        self.system_form.addRow("Logging Level:", self.logging_level)
        
        # Startup sound
        self.startup_sound = QCheckBox("Enable startup sound")
        self.startup_sound.setObjectName("settings_checkbox")
        self.system_form.addRow("Startup Sound:", self.startup_sound)
        
        # Idle timeout
        self.idle_timeout = QSpinBox()
        self.idle_timeout.setObjectName("settings_spinner")
        self.idle_timeout.setRange(60, 3600)
        self.idle_timeout.setSingleStep(60)
        self.idle_timeout.setSuffix(" seconds")
        self.system_form.addRow("Idle Timeout:", self.idle_timeout)
        
        # Memory path
        self.memory_path_container = QWidget()
        self.memory_path_layout = QHBoxLayout(self.memory_path_container)
        self.memory_path_layout.setContentsMargins(0, 0, 0, 0)
        self.memory_path_layout.setSpacing(10)
        
        self.memory_path = QLineEdit()
        self.memory_path.setObjectName("settings_input")
        self.memory_path.setReadOnly(True)
        self.memory_path_layout.addWidget(self.memory_path)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setObjectName("small_button")
        self.memory_path_layout.addWidget(self.browse_btn)
        
        self.system_form.addRow("Memory Database:", self.memory_path_container)
        
        # Auto backup
        self.auto_backup = QCheckBox("Enable automatic backups")
        self.auto_backup.setObjectName("settings_checkbox")
        self.system_form.addRow("Auto Backup:", self.auto_backup)
        
        # Conversation history length
        self.history_length = QSpinBox()
        self.history_length.setObjectName("settings_spinner")
        self.history_length.setRange(10, 500)
        self.history_length.setSingleStep(10)
        self.history_length.setSuffix(" messages")
        self.system_form.addRow("History Length:", self.history_length)
        
        self.system_layout.addWidget(self.system_group)
        
        # Add to tabs
        self.tabs.addTab(self.system_tab, "System")
        
        # Add tabs to main layout
        self.layout.addWidget(self.tabs)
    
    def _setup_connections(self):
        """Set up signal/slot connections"""
        self.save_btn.clicked.connect(self._on_save_settings)
        self.reset_btn.clicked.connect(self._on_reset_settings)
        self.browse_btn.clicked.connect(self._on_browse_memory_path)
    
    def _load_settings(self):
        """Load settings from the settings object"""
        if not self.settings:
            return
        
        # Load Assistant settings
        self.assistant_name.setText(self.settings.get("assistant", {}).get("name", "Ana"))
        self.wake_word.setText(self.settings.get("assistant", {}).get("wake_word", "Ana"))
        self.self_evolution.setChecked(self.settings.get("assistant", {}).get("self_evolution", {}).get("enabled", True))
        self.auto_update.setChecked(self.settings.get("assistant", {}).get("self_evolution", {}).get("auto_update", True))
        
        # Load OpenAI settings
        openai_settings = self.settings.get("assistant", {}).get("openai", {})
        self.openai_enabled.setChecked(openai_settings.get("enabled", True))
        self.openai_api_key.setText(openai_settings.get("api_key", ""))
        self.openai_model.setCurrentText(openai_settings.get("model", "gpt-3.5-turbo"))
        
        # Load Voice settings
        elevenlabs_settings = self.settings.get("voice", {}).get("elevenlabs", {})
        self.elevenlabs_api_key.setText(elevenlabs_settings.get("api_key", ""))
        voice_ids = elevenlabs_settings.get("voice_ids", {})
        self.voice_id_en.setText(voice_ids.get("en", ""))
        self.voice_id_hi.setText(voice_ids.get("hi", ""))
        
        porcupine_settings = self.settings.get("voice", {}).get("porcupine", {})
        self.porcupine_key.setText(porcupine_settings.get("access_key", ""))
        
        # Load GitHub settings
        github_settings = self.settings.get("github", {})
        self.github_enabled.setChecked(github_settings.get("enabled", True))
        self.github_username.setText(github_settings.get("username", ""))
        self.github_email.setText(github_settings.get("email", ""))
        self.github_token.setText(github_settings.get("token", ""))
        self.github_repo.setText(github_settings.get("repo_url", ""))
        self.github_auto_push.setChecked(github_settings.get("auto_push", True))
        
        # Load UI settings
        ui_settings = self.settings.get("ui", {})
        self.ui_theme.setCurrentText(ui_settings.get("theme", "cyberpunk"))
        self.ui_color_scheme.setCurrentText(ui_settings.get("color_scheme", "dark"))
        self.ui_animation.setCurrentText(ui_settings.get("animation_level", "high"))
        self.ui_font_size.setCurrentText(ui_settings.get("font_size", "medium"))
        
        # Load Feature settings
        feature_settings = self.settings.get("features", {})
        wake_word_settings = feature_settings.get("wake_word", {})
        self.feature_wake_word.setChecked(wake_word_settings.get("enabled", True))
        self.wake_word_sensitivity.setValue(wake_word_settings.get("sensitivity", 0.7))
        
        facial_settings = feature_settings.get("facial_recognition", {})
        self.feature_facial.setChecked(facial_settings.get("enabled", True))
        self.feature_emotion.setChecked(facial_settings.get("emotion_detection", True))
        
        multilingual_settings = feature_settings.get("multilingual", {})
        self.feature_multilingual.setChecked(multilingual_settings.get("enabled", True))
        self.default_language.setCurrentText(multilingual_settings.get("default_language", "en"))
        
        # Load System settings
        system_settings = self.settings.get("system", {})
        self.logging_level.setCurrentText(system_settings.get("logging_level", "info"))
        self.startup_sound.setChecked(system_settings.get("startup_sound", True))
        self.idle_timeout.setValue(system_settings.get("idle_timeout", 300))
        
        storage_settings = self.settings.get("storage", {})
        self.memory_path.setText(storage_settings.get("memory_path", "data/memory.db"))
        self.auto_backup.setChecked(storage_settings.get("auto_backup", True))
        self.history_length.setValue(storage_settings.get("conversation_history_length", 50))
    
    def _on_save_settings(self):
        """Save settings to the settings file"""
        # Create a new settings dictionary with updated values
        updated_settings = {
            "assistant": {
                "name": self.assistant_name.text(),
                "wake_word": self.wake_word.text(),
                "version": self.settings.get("assistant", {}).get("version", "1.0.0"),
                "self_evolution": {
                    "enabled": self.self_evolution.isChecked(),
                    "auto_update": self.auto_update.isChecked()
                },
                "openai": {
                    "enabled": self.openai_enabled.isChecked(),
                    "api_key": self.openai_api_key.text(),
                    "model": self.openai_model.currentText()
                }
            },
            "voice": {
                "elevenlabs": {
                    "api_key": self.elevenlabs_api_key.text(),
                    "voice_ids": {
                        "en": self.voice_id_en.text(),
                        "hi": self.voice_id_hi.text()
                    }
                },
                "porcupine": {
                    "access_key": self.porcupine_key.text()
                },
                "audio": self.settings.get("voice", {}).get("audio", {})
            },
            "github": {
                "enabled": self.github_enabled.isChecked(),
                "username": self.github_username.text(),
                "email": self.github_email.text(),
                "token": self.github_token.text(),
                "repo_url": self.github_repo.text(),
                "main_branch": self.settings.get("github", {}).get("main_branch", "main"),
                "auto_push": self.github_auto_push.isChecked(),
                "sync_interval": self.settings.get("github", {}).get("sync_interval", 3600),
                "feature_branches": self.settings.get("github", {}).get("feature_branches", True),
                "create_pull_requests": self.settings.get("github", {}).get("create_pull_requests", True)
            },
            "features": {
                "wake_word": {
                    "enabled": self.feature_wake_word.isChecked(),
                    "sensitivity": self.wake_word_sensitivity.value()
                },
                "facial_recognition": {
                    "enabled": self.feature_facial.isChecked(),
                    "recognition_interval": self.settings.get("features", {}).get("facial_recognition", {}).get("recognition_interval", 0.5),
                    "emotion_detection": self.feature_emotion.isChecked()
                },
                "gestures": self.settings.get("features", {}).get("gestures", {}),
                "multilingual": {
                    "enabled": self.feature_multilingual.isChecked(),
                    "default_language": self.default_language.currentText(),
                    "supported_languages": self.settings.get("features", {}).get("multilingual", {}).get("supported_languages", ["en", "hi"])
                }
            },
            "ui": {
                "theme": self.ui_theme.currentText(),
                "color_scheme": self.ui_color_scheme.currentText(),
                "animation_level": self.ui_animation.currentText(),
                "font_size": self.ui_font_size.currentText()
            },
            "storage": {
                "memory_path": self.memory_path.text(),
                "conversation_history_length": self.history_length.value(),
                "auto_backup": self.auto_backup.isChecked()
            },
            "system": {
                "logging_level": self.logging_level.currentText(),
                "startup_sound": self.startup_sound.isChecked(),
                "idle_timeout": self.idle_timeout.value()
            }
        }
        
        # Save to settings file
        try:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.json")
            with open(config_path, 'w') as f:
                json.dump(updated_settings, f, indent=2)
            
            # Update the settings object
            self.settings.update(updated_settings)
            
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")
            logger.info("Settings saved successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
            logger.error(f"Failed to save settings: {str(e)}")
    
    def _on_reset_settings(self):
        """Reset settings to current values from file"""
        confirm = QMessageBox.question(
            self, 
            "Reset Settings", 
            "Are you sure you want to reset all settings to their current values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self._load_settings()
            logger.info("Settings reset to current values")
    
    def _on_browse_memory_path(self):
        """Open file dialog to browse for memory database path"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Memory Database",
            os.path.dirname(self.memory_path.text()),
            "Database Files (*.db);;All Files (*)"
        )
        
        if file_path:
            self.memory_path.setText(file_path) 