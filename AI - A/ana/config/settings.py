#!/usr/bin/env python3
# Ana AI Assistant - Settings Module (Minimal Implementation)

import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger('Ana.Config')

def load_settings() -> Dict[str, Any]:
    """Load application settings from config file or use defaults"""
    config_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(config_dir, "settings.json")
    
    # Default settings
    default_settings = {
        "assistant": {
            "name": "Ana",
            "wake_word": "ana",
            "weather_location": "New York",
            "self_evolution": {
                "auto_update": False
            },
            "openai": {
                "enabled": False,
                "api_key": "",
                "model": "gpt-3.5-turbo"
            }
        },
        "voice": {
            "tts_engine": "pyttsx3",
            "voice_id": "en-US-female-1",
            "language": "en-US",
            "pitch": 1.0,
            "rate": 1.0,
            "volume": 1.0,
            "wake_word": "ana",
            "wake_word_sensitivity": 0.6,
            "continuous_listen": False,
            "auto_adjust_ambient": True
        },
        "memory": {
            "storage_type": "sqlite",
            "max_history_items": 1000,
            "cloud_sync": False
        },
        "features": {
            "facial_recognition": {
                "enabled": False
            }
        },
        "ui": {
            "theme": "cyberpunk",
            "color_scheme": "dark",
            "enable_animations": True,
            "accent_color": "#00E5FF",
            "secondary_color": "#FF3C78"
        },
        "security": {
            "require_google_login": True,
            "allowed_domains": [],  # Empty means all domains are allowed
            "session_timeout_minutes": 60,
            "auto_lock": False
        },
        "user": {
            "email": "",
            "name": "",
            "picture": ""
        }
    }
    
    # Try to load settings from file
    try:
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                user_settings = json.load(f)
                # Merge user settings with defaults
                merged_settings = _merge_dicts(default_settings, user_settings)
                logger.info("Settings loaded from %s", settings_path)
                return merged_settings
    except Exception as e:
        logger.error("Error loading settings: %s", str(e))
    
    # Create default settings file if it doesn't exist
    try:
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        with open(settings_path, 'w') as f:
            json.dump(default_settings, f, indent=4)
        logger.info("Default settings created at %s", settings_path)
    except Exception as e:
        logger.error("Error creating default settings: %s", str(e))
    
    return default_settings

def _merge_dicts(default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge user settings into default settings"""
    result = default.copy()
    
    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def save_settings(settings: Dict[str, Any]) -> bool:
    """Save settings to config file"""
    config_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(config_dir, "settings.json")
    
    try:
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=4)
        logger.info("Settings saved to %s", settings_path)
        return True
    except Exception as e:
        logger.error("Error saving settings: %s", str(e))
        return False

def get_app_data_dir() -> str:
    """Get the application data directory"""
    # For simplicity, just use a 'data' directory in the project
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(app_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir 